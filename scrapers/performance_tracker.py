"""
Performance Tracking and Metrics System

Tracks download performance, success rates, and generates detailed reports
for continuous improvement of scraping methods.
"""

import os
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any
from collections import defaultdict

logger = logging.getLogger(__name__)

class PerformanceTracker:
    """Tracks and analyzes scraping performance metrics"""

    def __init__(self, metrics_file: str = 'logs/performance_metrics.json'):
        self.metrics_file = metrics_file
        self.current_job = {
            'job_id': None,
            'start_time': None,
            'query': None,
            'sources_attempted': [],
            'sources_completed': [],
            'total_files': 0,
            'total_images': 0,
            'total_videos': 0,
            'total_duration': 0,
            'placeholders_filtered': 0,
            'sources_blacklisted': 0
        }
        self.source_metrics = {}

    def start_job(self, job_id: str, query: str, sources: List[str]):
        """Start tracking a new scraping job"""
        self.current_job = {
            'job_id': job_id,
            'start_time': datetime.now().isoformat(),
            'query': query,
            'sources_attempted': sources,
            'sources_completed': [],
            'total_files': 0,
            'total_images': 0,
            'total_videos': 0,
            'total_duration': 0,
            'placeholders_filtered': 0,
            'sources_blacklisted': 0,
            'source_details': {}
        }

        logger.info(f"[METRICS] Started tracking job {job_id} with {len(sources)} sources")

    def record_source_attempt(self, source: str, method: str, duration: float,
                             files_downloaded: int, images: int, videos: int,
                             success: bool, error: str = None):
        """Record metrics for a single source attempt"""

        if source not in self.current_job['source_details']:
            self.current_job['source_details'][source] = []

        attempt = {
            'method': method,
            'duration': round(duration, 2),
            'files': files_downloaded,
            'images': images,
            'videos': videos,
            'success': success,
            'error': error,
            'timestamp': datetime.now().isoformat()
        }

        self.current_job['source_details'][source].append(attempt)

        # Update totals
        if success and files_downloaded > 0:
            self.current_job['sources_completed'].append(source)
            self.current_job['total_files'] += files_downloaded
            self.current_job['total_images'] += images
            self.current_job['total_videos'] += videos

        self.current_job['total_duration'] += duration

        logger.info(f"[METRICS] {source}: {files_downloaded} files in {duration:.1f}s via {method} ({'✅ SUCCESS' if success else '❌ FAILED'})")

    def record_filtering(self, placeholders_removed: int, sources_blacklisted: int):
        """Record filtering metrics"""
        self.current_job['placeholders_filtered'] = placeholders_removed
        self.current_job['sources_blacklisted'] = sources_blacklisted

        if placeholders_removed > 0:
            logger.info(f"[METRICS] Filtered {placeholders_removed} placeholder images")
        if sources_blacklisted > 0:
            logger.info(f"[METRICS] Blacklisted {sources_blacklisted} inappropriate sources")

    def end_job(self):
        """Finalize job tracking and save metrics"""
        if not self.current_job['job_id']:
            return

        self.current_job['end_time'] = datetime.now().isoformat()

        # Calculate summary statistics
        sources_attempted = len(self.current_job['sources_attempted'])
        sources_completed = len(set(self.current_job['sources_completed']))
        success_rate = (sources_completed / sources_attempted * 100) if sources_attempted > 0 else 0

        self.current_job['summary'] = {
            'sources_attempted': sources_attempted,
            'sources_completed': sources_completed,
            'success_rate': round(success_rate, 1),
            'files_per_source': round(self.current_job['total_files'] / sources_completed, 1) if sources_completed > 0 else 0,
            'avg_duration_per_source': round(self.current_job['total_duration'] / sources_attempted, 1) if sources_attempted > 0 else 0
        }

        # Save to metrics file
        self._save_metrics()

        # Log summary
        logger.info(f"[METRICS] ========== JOB COMPLETE ==========")
        logger.info(f"[METRICS] Job ID: {self.current_job['job_id']}")
        logger.info(f"[METRICS] Query: {self.current_job['query']}")
        logger.info(f"[METRICS] Success Rate: {success_rate:.1f}% ({sources_completed}/{sources_attempted} sources)")
        logger.info(f"[METRICS] Files Downloaded: {self.current_job['total_files']} ({self.current_job['total_images']} images, {self.current_job['total_videos']} videos)")
        logger.info(f"[METRICS] Duration: {self.current_job['total_duration']:.1f}s")
        logger.info(f"[METRICS] Placeholders Filtered: {self.current_job['placeholders_filtered']}")
        logger.info(f"[METRICS] =====================================")

    def _save_metrics(self):
        """Save metrics to JSON file"""
        try:
            # Load existing metrics
            if os.path.exists(self.metrics_file):
                with open(self.metrics_file, 'r') as f:
                    all_metrics = json.load(f)
            else:
                all_metrics = {'jobs': []}

            # Append current job
            all_metrics['jobs'].append(self.current_job)

            # Keep only last 100 jobs
            all_metrics['jobs'] = all_metrics['jobs'][-100:]

            # Save updated metrics
            os.makedirs(os.path.dirname(self.metrics_file), exist_ok=True)
            with open(self.metrics_file, 'w') as f:
                json.dump(all_metrics, f, indent=2)

            logger.debug(f"[METRICS] Saved to {self.metrics_file}")

        except Exception as e:
            logger.error(f"[METRICS] Failed to save metrics: {e}")

    def get_source_performance_report(self, days: int = 7) -> Dict[str, Any]:
        """Generate performance report for all sources over specified period"""
        try:
            if not os.path.exists(self.metrics_file):
                return {'error': 'No metrics data available'}

            with open(self.metrics_file, 'r') as f:
                all_metrics = json.load(f)

            # Filter jobs from last N days
            cutoff_date = datetime.now() - timedelta(days=days)
            recent_jobs = [
                job for job in all_metrics.get('jobs', [])
                if datetime.fromisoformat(job.get('start_time', '2000-01-01')) > cutoff_date
            ]

            # Aggregate source statistics
            source_stats = defaultdict(lambda: {
                'attempts': 0,
                'successes': 0,
                'total_files': 0,
                'total_duration': 0,
                'methods_used': defaultdict(int),
                'errors': []
            })

            for job in recent_jobs:
                for source, attempts in job.get('source_details', {}).items():
                    for attempt in attempts:
                        source_stats[source]['attempts'] += 1
                        if attempt['success']:
                            source_stats[source]['successes'] += 1
                            source_stats[source]['total_files'] += attempt['files']
                        source_stats[source]['total_duration'] += attempt['duration']
                        source_stats[source]['methods_used'][attempt['method']] += 1
                        if attempt.get('error'):
                            source_stats[source]['errors'].append(attempt['error'])

            # Calculate derived metrics
            report = {
                'period': f'Last {days} days',
                'total_jobs': len(recent_jobs),
                'sources': {}
            }

            for source, stats in source_stats.items():
                success_rate = (stats['successes'] / stats['attempts'] * 100) if stats['attempts'] > 0 else 0
                avg_files = stats['total_files'] / stats['successes'] if stats['successes'] > 0 else 0
                avg_duration = stats['total_duration'] / stats['attempts'] if stats['attempts'] > 0 else 0

                report['sources'][source] = {
                    'attempts': stats['attempts'],
                    'successes': stats['successes'],
                    'success_rate': round(success_rate, 1),
                    'total_files': stats['total_files'],
                    'avg_files_per_success': round(avg_files, 1),
                    'avg_duration': round(avg_duration, 1),
                    'primary_method': max(stats['methods_used'].items(), key=lambda x: x[1])[0] if stats['methods_used'] else 'unknown',
                    'common_errors': list(set(stats['errors'][:5]))  # Top 5 unique errors
                }

            return report

        except Exception as e:
            logger.error(f"[METRICS] Failed to generate report: {e}")
            return {'error': str(e)}

    def print_performance_summary(self, days: int = 7):
        """Print human-readable performance summary"""
        report = self.get_source_performance_report(days)

        if 'error' in report:
            print(f"Error: {report['error']}")
            return

        print("\n" + "="*80)
        print(f"PERFORMANCE REPORT - {report['period']}")
        print(f"Total Jobs: {report['total_jobs']}")
        print("="*80)

        # Sort sources by success rate
        sorted_sources = sorted(
            report['sources'].items(),
            key=lambda x: (x[1]['success_rate'], x[1]['total_files']),
            reverse=True
        )

        # High performers (>60% success)
        high_performers = [(s, d) for s, d in sorted_sources if d['success_rate'] >= 60]
        if high_performers:
            print("\n🟢 HIGH PERFORMERS (60%+ success rate):")
            for source, data in high_performers:
                print(f"  {source:20} | {data['success_rate']:5.1f}% | {data['total_files']:4} files | {data['avg_duration']:6.1f}s avg | {data['primary_method']}")

        # Medium performers (30-60%)
        medium_performers = [(s, d) for s, d in sorted_sources if 30 <= d['success_rate'] < 60]
        if medium_performers:
            print("\n🟡 MEDIUM PERFORMERS (30-60% success rate):")
            for source, data in medium_performers:
                print(f"  {source:20} | {data['success_rate']:5.1f}% | {data['total_files']:4} files | {data['avg_duration']:6.1f}s avg | {data['primary_method']}")

        # Low performers (<30%)
        low_performers = [(s, d) for s, d in sorted_sources if d['success_rate'] < 30]
        if low_performers:
            print("\n🔴 LOW PERFORMERS (<30% success rate - NEEDS IMPROVEMENT):")
            for source, data in low_performers:
                errors = ', '.join(data['common_errors'][:2]) if data['common_errors'] else 'No specific errors'
                print(f"  {source:20} | {data['success_rate']:5.1f}% | {data['total_files']:4} files | {errors[:50]}")

        print("\n" + "="*80)


# Global performance tracker instance
performance_tracker = PerformanceTracker()


def track_job_start(job_id: str, query: str, sources: List[str]):
    """Convenience function to start tracking a job"""
    performance_tracker.start_job(job_id, query, sources)


def track_source_result(source: str, method: str, duration: float,
                       files: int, images: int, videos: int,
                       success: bool, error: str = None):
    """Convenience function to track a source result"""
    performance_tracker.record_source_attempt(
        source, method, duration, files, images, videos, success, error
    )


def track_filtering(placeholders: int, blacklisted: int):
    """Convenience function to track filtering"""
    performance_tracker.record_filtering(placeholders, blacklisted)


def track_job_end():
    """Convenience function to end job tracking"""
    performance_tracker.end_job()


def generate_performance_report(days: int = 7) -> Dict[str, Any]:
    """Generate performance report"""
    return performance_tracker.get_source_performance_report(days)


def print_performance_report(days: int = 7):
    """Print performance report to console"""
    performance_tracker.print_performance_summary(days)


# CLI entry point for manual reporting
if __name__ == '__main__':
    import sys

    days = int(sys.argv[1]) if len(sys.argv) > 1 else 7
    print_performance_report(days)
