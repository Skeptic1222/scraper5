"""
Method Configuration Model - Stores successful scraping methods for optimization
"""
import json
from datetime import datetime
from typing import Optional

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Boolean, Column, DateTime, Float, Integer, String, Text

db = SQLAlchemy()


class MethodConfig(db.Model):
    """Stores configuration for successful scraping methods"""

    __tablename__ = 'method_configs'

    id = Column(Integer, primary_key=True)
    source = Column(String(50), nullable=False, index=True)
    url_pattern = Column(String(500), nullable=False, index=True)
    method_name = Column(String(100), nullable=False)
    success_count = Column(Integer, default=0)
    failure_count = Column(Integer, default=0)
    avg_response_time = Column(Float, default=0.0)
    last_success = Column(DateTime)
    last_failure = Column(DateTime)
    is_active = Column(Boolean, default=True)
    extra_metadata = Column(Text)  # JSON field for additional data
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    @property
    def success_rate(self) -> float:
        """Calculate success rate"""
        total = self.success_count + self.failure_count
        return (self.success_count / total * 100) if total > 0 else 0.0

    @property
    def reliability_score(self) -> float:
        """Calculate reliability score based on success rate and recency"""
        base_score = self.success_rate

        # Reduce score if no recent success
        if self.last_success:
            days_since_success = (datetime.utcnow() - self.last_success).days
            if days_since_success > 7:
                base_score *= 0.8
            elif days_since_success > 30:
                base_score *= 0.5

        return base_score

    def record_success(self, response_time: float = None):
        """Record a successful method execution"""
        self.success_count += 1
        self.last_success = datetime.utcnow()

        if response_time:
            # Update average response time
            total_time = self.avg_response_time * (self.success_count - 1)
            self.avg_response_time = (total_time + response_time) / self.success_count

    def record_failure(self):
        """Record a failed method execution"""
        self.failure_count += 1
        self.last_failure = datetime.utcnow()

        # Deactivate if too many failures
        if self.failure_count > 10 and self.success_rate < 20:
            self.is_active = False

    def get_metadata(self) -> dict:
        """Get metadata as dictionary"""
        if self.extra_metadata:
            try:
                return json.loads(self.extra_metadata)
            except:
                return {}
        return {}

    def set_metadata(self, data: dict):
        """Set metadata from dictionary"""
        self.extra_metadata = json.dumps(data)

    def __repr__(self):
        return f'<MethodConfig {self.source}:{self.method_name} success_rate={self.success_rate:.1f}%>'


class SmartMethodSelector:
    """Intelligent method selection based on historical data"""

    @staticmethod
    def get_best_method(source: str, url: str, threshold: float = 80.0) -> Optional[str]:
        """
        Get the best method for a source and URL
        
        Args:
            source: Source name (e.g., 'reddit', 'youtube')
            url: Target URL
            threshold: Minimum success rate to consider (default 80%)
            
        Returns:
            Method name if found, None otherwise
        """
        # Extract URL pattern
        url_pattern = SmartMethodSelector._extract_pattern(url)

        # Query for successful configurations
        config = MethodConfig.query.filter_by(
            source=source.lower(),
            url_pattern=url_pattern,
            is_active=True
        ).filter(
            MethodConfig.success_rate >= threshold
        ).order_by(
            MethodConfig.reliability_score.desc()
        ).first()

        if config:
            return config.method_name

        # Try broader pattern match
        configs = MethodConfig.query.filter_by(
            source=source.lower(),
            is_active=True
        ).filter(
            MethodConfig.success_rate >= threshold
        ).order_by(
            MethodConfig.success_count.desc()
        ).all()

        for config in configs:
            if SmartMethodSelector._pattern_matches(url, config.url_pattern):
                return config.method_name

        return None

    @staticmethod
    def record_attempt(source: str, url: str, method: str,
                      success: bool, response_time: float = None):
        """
        Record a method attempt for learning
        
        Args:
            source: Source name
            url: Target URL
            method: Method name that was used
            success: Whether the attempt succeeded
            response_time: Time taken in seconds
        """
        url_pattern = SmartMethodSelector._extract_pattern(url)

        # Find or create configuration
        config = MethodConfig.query.filter_by(
            source=source.lower(),
            url_pattern=url_pattern,
            method_name=method
        ).first()

        if not config:
            config = MethodConfig(
                source=source.lower(),
                url_pattern=url_pattern,
                method_name=method
            )
            db.session.add(config)

        # Record result
        if success:
            config.record_success(response_time)
        else:
            config.record_failure()

        db.session.commit()

    @staticmethod
    def get_method_stats(source: str = None) -> list:
        """Get statistics for all methods or specific source"""
        query = MethodConfig.query

        if source:
            query = query.filter_by(source=source.lower())

        configs = query.order_by(
            MethodConfig.success_rate.desc(),
            MethodConfig.success_count.desc()
        ).all()

        return [{
            'source': c.source,
            'url_pattern': c.url_pattern,
            'method': c.method_name,
            'success_rate': c.success_rate,
            'success_count': c.success_count,
            'failure_count': c.failure_count,
            'avg_response_time': c.avg_response_time,
            'is_active': c.is_active,
            'last_success': c.last_success.isoformat() if c.last_success else None
        } for c in configs]

    @staticmethod
    def _extract_pattern(url: str) -> str:
        """Extract a pattern from URL for matching"""
        from urllib.parse import urlparse

        parsed = urlparse(url)
        path_parts = parsed.path.split('/')

        # Create pattern based on URL structure
        if 'reddit.com' in parsed.netloc:
            if '/r/' in parsed.path:
                # Pattern: reddit.com/r/subreddit/...
                return f"{parsed.netloc}/r/*"
            elif '/user/' in parsed.path:
                return f"{parsed.netloc}/user/*"
        elif 'youtube.com' in parsed.netloc or 'youtu.be' in parsed.netloc:
            if '/watch' in parsed.path:
                return f"{parsed.netloc}/watch"
            elif '/playlist' in parsed.path:
                return f"{parsed.netloc}/playlist"
        elif 'instagram.com' in parsed.netloc:
            if '/p/' in parsed.path:
                return f"{parsed.netloc}/p/*"
            elif '/reel/' in parsed.path:
                return f"{parsed.netloc}/reel/*"

        # Default pattern
        return parsed.netloc

    @staticmethod
    def _pattern_matches(url: str, pattern: str) -> bool:
        """Check if URL matches a pattern"""
        import fnmatch
        from urllib.parse import urlparse

        parsed = urlparse(url)
        url_path = f"{parsed.netloc}{parsed.path}"

        return fnmatch.fnmatch(url_path, pattern)
