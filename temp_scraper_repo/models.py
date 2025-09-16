"""
Database Models for Enhanced Media Scraper
SQLAlchemy models for user management, job tracking, and asset management
"""

import json
import os
from datetime import datetime

from flask_login import UserMixin
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class User(UserMixin, db.Model):
    """User model for authentication and authorization"""

    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    google_id = db.Column(db.String(100), unique=True, nullable=False)
    email = db.Column(db.String(255), unique=True, nullable=False)
    name = db.Column(db.String(255), nullable=False)  # Use name instead of username
    picture = db.Column(db.String(500))
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime)

    # Subscription fields
    credits = db.Column(db.Integer, default=50)  # Free trial credits
    subscription_plan = db.Column(db.String(50), default="trial")  # trial, basic, pro, ultra
    subscription_status = db.Column(db.String(50), default="active")  # active, cancelled, expired
    is_nsfw_enabled = db.Column(db.Boolean, default=False)
    paypal_subscription_id = db.Column(db.String(255))
    subscription_start_date = db.Column(db.DateTime)
    subscription_end_date = db.Column(db.DateTime)
    sources_enabled = db.Column(db.Text)  # JSON array of enabled sources
    signin_bonus_claimed = db.Column(db.Boolean, default=False)  # Track if user claimed sign-in bonus

    # Relationships
    scrape_jobs = db.relationship("ScrapeJob", backref="user", lazy=True)
    assets = db.relationship("Asset", backref="user", lazy=True)
    user_roles = db.relationship("UserRole", foreign_keys="UserRole.user_id", backref="user", lazy=True)

    def __repr__(self):
        return f"<User {self.email}>"

    def get_id(self):
        """Required for Flask-Login"""
        return str(self.id)

    def has_role(self, role_name):
        """Check if user has a specific role"""
        return any(ur.role.name == role_name for ur in self.user_roles if ur.role)

    def has_permission(self, permission_name):
        """Check if user has a specific permission through their roles"""
        for user_role in self.user_roles:
            if user_role.role and permission_name in user_role.role.permissions:
                return True
        return False

    def get_roles(self):
        """Get all role names for this user"""
        return [ur.role.name for ur in self.user_roles if ur.role]

    def is_admin(self):
        """Check if user has admin role"""
        # Hard-coded admin override for sop1973@gmail.com
        if self.email == os.getenv("ADMIN_EMAIL", "admin@example.com"):
            return True

        return any(ur.role.name == "admin" for ur in self.user_roles if ur.role)

    def get_enabled_sources(self):
        """Get enabled sources as list"""
        if self.sources_enabled:
            try:
                return json.loads(self.sources_enabled)
            except json.JSONDecodeError:
                # Return default trial sources if invalid
                return ["reddit", "imgur", "wikimedia", "deviantart"]
        # Return default trial sources for new users
        return ["reddit", "imgur", "wikimedia", "deviantart"]

    def set_enabled_sources(self, sources_list):
        """Set enabled sources from list"""
        self.sources_enabled = json.dumps(sources_list)

    def is_subscribed(self):
        """Check if user has an active subscription"""
        return self.subscription_plan in ["basic", "pro", "ultra"] and self.subscription_status == "active"

    def can_use_nsfw(self):
        """Check if user can use NSFW features"""
        return self.subscription_plan == "ultra" and self.subscription_status == "active"

    def has_credits(self):
        """Check if user has credits remaining"""
        return self.credits > 0 or self.is_subscribed()

    def use_credit(self):
        """Use a credit if on trial"""
        if self.subscription_plan == "trial" and self.credits > 0:
            self.credits -= 1
            return True
        return self.is_subscribed()

    def claim_signin_bonus(self):
        """Claim sign-in bonus atomically"""
        if self.signin_bonus_claimed:
            return False

        from sqlalchemy import text

        result = db.session.execute(
            text(
                """
                UPDATE users
                SET credits = credits + 50, signin_bonus_claimed = 1
                WHERE id = :user_id AND signin_bonus_claimed = 0
            """
            ),
            {"user_id": self.id},
        )

        if result.rowcount > 0:
            db.session.commit()
            db.session.refresh(self)
            return True
        return False

    def to_dict(self):
        """Convert user to dictionary for API responses"""
        return {
            "id": self.id,
            "email": self.email,
            "name": self.name,
            "picture": self.picture,
            "roles": self.get_roles(),
            "is_active": self.is_active,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "last_login": self.last_login.isoformat() if self.last_login else None,
            "credits": self.credits,
            "subscription_plan": self.subscription_plan,
            "subscription_status": self.subscription_status,
            "is_nsfw_enabled": self.is_nsfw_enabled and self.can_use_nsfw(),
            "sources_enabled": self.get_enabled_sources(),
            "is_subscribed": self.is_subscribed(),
        }


class Role(db.Model):
    """Role model for RBAC"""

    __tablename__ = "roles"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    description = db.Column(db.String(255))
    permissions = db.Column(db.Text)  # JSON string of permissions
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def get_permissions(self):
        """Get permissions as list"""
        if self.permissions:
            try:
                return json.loads(self.permissions)
            except json.JSONDecodeError:
                return []
        return []

    def set_permissions(self, permissions_list):
        """Set permissions from list"""
        self.permissions = json.dumps(permissions_list)

    def has_permission(self, permission):
        """Check if role has specific permission"""
        return permission in self.get_permissions()


class ScrapeJob(db.Model):
    """Model for tracking scraping jobs with progress"""

    __tablename__ = "scrape_jobs"

    id = db.Column(db.String(100), primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True)  # Nullable for guest jobs
    job_type = db.Column(db.String(50), nullable=False)
    status = db.Column(db.String(20), nullable=False, default="starting")
    progress = db.Column(db.Integer, default=0)
    query = db.Column(db.String(500))
    max_content = db.Column(db.Integer)
    safe_search = db.Column(db.Boolean, default=True)
    detected = db.Column(db.Integer, default=0)
    downloaded = db.Column(db.Integer, default=0)
    failed = db.Column(db.Integer, default=0)
    images = db.Column(db.Integer, default=0)
    videos = db.Column(db.Integer, default=0)
    current_file = db.Column(db.String(255))
    message = db.Column(db.String(500))
    start_time = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    end_time = db.Column(db.DateTime)
    results = db.Column(db.Text)  # JSON string
    enabled_sources = db.Column(db.Text)  # JSON array
    live_updates = db.Column(db.Text)  # JSON array of recent updates
    recent_files = db.Column(db.Text)  # JSON array of recent file names
    sources_data = db.Column(db.Text)  # JSON object of source-specific data
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def get_results(self):
        """Get results as dictionary"""
        if self.results:
            try:
                return json.loads(self.results)
            except json.JSONDecodeError:
                return {}
        return {}

    def set_results(self, results_dict):
        """Set results from dictionary"""
        self.results = json.dumps(results_dict)

    def get_enabled_sources(self):
        """Get enabled sources as list"""
        if self.enabled_sources:
            try:
                return json.loads(self.enabled_sources)
            except json.JSONDecodeError:
                return []
        return []

    def set_enabled_sources(self, sources_list):
        """Set enabled sources from list"""
        self.enabled_sources = json.dumps(sources_list)

    def get_live_updates(self):
        """Get live updates as list"""
        if self.live_updates:
            try:
                return json.loads(self.live_updates)
            except json.JSONDecodeError:
                return []
        return []

    def add_live_update(self, message):
        """Add a live update message"""
        updates = self.get_live_updates()
        timestamp = datetime.now().strftime("%H:%M:%S")
        update = {"timestamp": timestamp, "message": message}
        updates.insert(0, update)

        # Keep only last 20 updates
        if len(updates) > 20:
            updates = updates[:20]

        self.live_updates = json.dumps(updates)

    def get_recent_files(self):
        """Get recent files as list"""
        if self.recent_files:
            try:
                return json.loads(self.recent_files)
            except json.JSONDecodeError:
                return []
        return []

    def add_recent_file(self, filename):
        """Add a file to recent files"""
        files = self.get_recent_files()
        if filename not in files:
            files.insert(0, filename)
            # Keep only last 10 files
            if len(files) > 10:
                files = files[:10]
            self.recent_files = json.dumps(files)

    def get_runtime_seconds(self):
        """Get job runtime in seconds"""
        if self.start_time:
            end_time = self.end_time or datetime.utcnow()
            runtime = end_time - self.start_time
            return int(runtime.total_seconds())
        return 0

    def to_dict(self):
        """Convert job to dictionary for JSON responses"""
        return {
            "id": self.id,
            "user_id": self.user_id,
            "type": self.job_type,
            "status": self.status,
            "progress": self.progress,
            "query": self.query,
            "max_content": self.max_content,
            "safe_search": self.safe_search,
            "detected": self.detected,
            "downloaded": self.downloaded,
            "failed": self.failed,
            "images": self.images,
            "videos": self.videos,
            "current_file": self.current_file,
            "message": self.message,
            "start_time": self.start_time.isoformat() if self.start_time else None,
            "end_time": self.end_time.isoformat() if self.end_time else None,
            "results": self.get_results(),
            "enabled_sources": self.get_enabled_sources(),
            "live_updates": self.get_live_updates(),
            "recent_files": self.get_recent_files(),
            "sources": json.loads(self.sources_data) if self.sources_data else {},
            "runtime_seconds": self.get_runtime_seconds(),
            "params": {
                "query": self.query,
                "max_content": self.max_content,
                "safe_search": self.safe_search,
                "enabled_sources": self.get_enabled_sources(),
            },
        }


class Asset(db.Model):
    """Model for tracking downloaded assets"""

    __tablename__ = "assets"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True)  # Nullable for guest assets
    job_id = db.Column(db.String(100), db.ForeignKey("scrape_jobs.id"), nullable=True)
    filename = db.Column(db.String(255), nullable=False)
    file_path = db.Column(db.String(500), nullable=False)
    file_type = db.Column(db.String(10), nullable=False)  # 'image' or 'video'
    file_size = db.Column(db.BigInteger)
    file_extension = db.Column(db.String(10))
    source_url = db.Column(db.String(1000))
    source_name = db.Column(db.String(100))
    width = db.Column(db.Integer)
    height = db.Column(db.Integer)
    duration = db.Column(db.Float)  # Video duration in seconds
    thumbnail_path = db.Column(db.String(500))
    downloaded_at = db.Column(db.DateTime, default=lambda: datetime.utcnow())
    is_deleted = db.Column(db.Boolean, default=False)
    stored_in_db = db.Column(db.Boolean, default=False)  # Track if file is stored in MediaBlob
    asset_metadata = db.Column(db.Text)  # JSON metadata

    # Relationships
    job = db.relationship("ScrapeJob", backref="assets")
    media_blob = db.relationship("MediaBlob", uselist=False, back_populates="asset")

    def get_metadata(self):
        """Get metadata as dictionary"""
        if self.asset_metadata:
            try:
                return json.loads(self.asset_metadata)
            except json.JSONDecodeError:
                return {}
        return {}

    def set_metadata(self, metadata_dict):
        """Set metadata from dictionary"""
        self.asset_metadata = json.dumps(metadata_dict)

    def to_dict(self):
        """Convert asset to dictionary for JSON responses"""
        return {
            "id": self.id,
            "user_id": self.user_id,
            "job_id": self.job_id,
            "filename": self.filename,
            "file_path": self.file_path,
            "file_type": self.file_type,
            "file_size": self.file_size,
            "file_extension": self.file_extension,
            "source_url": self.source_url,
            "source_name": self.source_name,
            "width": self.width,
            "height": self.height,
            "duration": self.duration,
            "thumbnail_path": self.thumbnail_path,
            "downloaded_at": self.downloaded_at.isoformat() if self.downloaded_at else None,
            "is_deleted": self.is_deleted,
            "stored_in_db": self.stored_in_db,
            "metadata": self.get_metadata(),
        }


class AppSetting(db.Model):
    """Model for application settings"""

    __tablename__ = "app_settings"

    key = db.Column(db.String(100), primary_key=True)
    value = db.Column(db.Text)
    description = db.Column(db.String(255))
    setting_type = db.Column(db.String(20), default="string")  # string, int, bool, json
    updated_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_by = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True)

    def get_value(self):
        """Get typed value based on setting_type"""
        if not self.value:
            return None

        if self.setting_type == "int":
            try:
                return int(self.value)
            except ValueError:
                return 0
        elif self.setting_type == "bool":
            return self.value.lower() in ("true", "1", "yes", "on")
        elif self.setting_type == "json":
            try:
                return json.loads(self.value)
            except json.JSONDecodeError:
                return {}
        else:
            return self.value

    def set_value(self, value):
        """Set value with automatic type conversion"""
        if self.setting_type == "json":
            self.value = json.dumps(value)
        else:
            self.value = str(value)
        self.updated_at = datetime.utcnow()

    @classmethod
    def get_setting(cls, key, default=None):
        """Get setting value by key"""
        setting = cls.query.filter_by(key=key).first()
        if setting:
            return setting.get_value()
        return default

    @classmethod
    def set_setting(cls, key, value, description=None, setting_type="string", user_id=None):
        """Set or update setting"""
        setting = cls.query.filter_by(key=key).first()
        if not setting:
            setting = cls(key=key, setting_type=setting_type, description=description)
            db.session.add(setting)

        setting.set_value(value)
        if description:
            setting.description = description
        if user_id:
            setting.updated_by = user_id

        db.session.commit()
        return setting


class UserRole(db.Model):
    """Many-to-many relationship between users and roles"""

    __tablename__ = "user_roles"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    role_id = db.Column(db.Integer, db.ForeignKey("roles.id"), nullable=False)
    assigned_at = db.Column(db.DateTime, default=datetime.utcnow)
    assigned_by = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True)

    # Relationships without backref to avoid conflicts
    role = db.relationship("Role", lazy="joined")

    def __repr__(self):
        return f"<UserRole user_id={self.user_id} role_id={self.role_id}>"


# Simplified OAuth model without Flask-Dance dependency for now
class OAuth(db.Model):
    """Store OAuth tokens for users"""

    __tablename__ = "oauth"

    id = db.Column(db.Integer, primary_key=True)
    provider = db.Column(db.String(50), nullable=False)
    provider_user_id = db.Column(db.String(256), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    token = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    user = db.relationship("User")


class MediaBlob(db.Model):
    """Model for storing media files as BLOBs in the database for enhanced security"""

    __tablename__ = "media_blobs"

    id = db.Column(db.Integer, primary_key=True)
    asset_id = db.Column(db.Integer, db.ForeignKey("assets.id"), nullable=False, unique=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)  # Enforce user ownership
    media_data = db.Column(db.LargeBinary, nullable=False)  # The actual file data
    mime_type = db.Column(db.String(100), nullable=False)
    file_hash = db.Column(db.String(64))  # SHA-256 hash for deduplication
    compressed = db.Column(db.Boolean, default=False)  # Whether data is compressed
    encryption_key = db.Column(db.String(64))  # Optional encryption key
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_accessed = db.Column(db.DateTime, default=datetime.utcnow)
    access_count = db.Column(db.Integer, default=0)

    # Relationships
    asset = db.relationship("Asset", back_populates="media_blob")
    user = db.relationship("User")

    def __repr__(self):
        return f"<MediaBlob id={self.id} asset_id={self.asset_id} user_id={self.user_id}>"

    def record_access(self):
        """Record access to this media blob"""
        self.last_accessed = datetime.utcnow()
        self.access_count += 1
        try:
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            print(f"Error recording media blob access: {e}")

    def get_file_data(self):
        """Get the media file data, recording access"""
        self.record_access()
        return self.media_data

    def get_file_data_stream(self, chunk_size=8192):
        """Get the media file data as a generator for streaming large files"""
        self.record_access()
        if self.media_data:
            for i in range(0, len(self.media_data), chunk_size):
                yield self.media_data[i : i + chunk_size]

    def get_file_size(self):
        """Get file size without loading data into memory"""
        return len(self.media_data) if self.media_data else 0

    @classmethod
    def store_media_file(cls, asset_id, user_id, file_path, mime_type=None):
        """Store a file as a media blob"""
        import hashlib
        import mimetypes

        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")

        # Read file data
        with open(file_path, "rb") as f:
            file_data = f.read()

        # Calculate hash for deduplication
        file_hash = hashlib.sha256(file_data).hexdigest()

        # Check if this asset already has a MediaBlob
        existing_for_asset = cls.query.filter_by(asset_id=asset_id).first()
        if existing_for_asset:
            print(f"⚠️ Asset {asset_id} already has a MediaBlob")
            return existing_for_asset

        # Note: We used to check for duplicate files by hash, but this caused issues
        # because MediaBlob has a unique constraint on asset_id. Each asset needs
        # its own MediaBlob, even if the file content is identical.

        # Determine MIME type
        if mime_type is None:
            mime_type, _ = mimetypes.guess_type(file_path)
            if mime_type is None:
                # Default based on file extension
                ext = os.path.splitext(file_path)[1].lower()
                mime_type_map = {
                    ".jpg": "image/jpeg",
                    ".jpeg": "image/jpeg",
                    ".png": "image/png",
                    ".gif": "image/gif",
                    ".webp": "image/webp",
                    ".bmp": "image/bmp",
                    ".mp4": "video/mp4",
                    ".webm": "video/webm",
                    ".avi": "video/avi",
                    ".mov": "video/quicktime",
                    ".mkv": "video/x-matroska",
                }
                mime_type = mime_type_map.get(ext, "application/octet-stream")

        # Create media blob
        media_blob = cls(
            asset_id=asset_id, user_id=user_id, media_data=file_data, mime_type=mime_type, file_hash=file_hash
        )

        db.session.add(media_blob)

        try:
            db.session.commit()

            # Update asset to indicate it's stored in database
            asset = Asset.query.get(asset_id)
            if asset:
                asset.stored_in_db = True
                db.session.commit()

            # Optional: Remove the file from filesystem for security
            # os.remove(file_path)

            return media_blob
        except Exception as e:
            db.session.rollback()
            raise e

    @classmethod
    def cleanup_old_blobs(cls, days_old=90):
        """Clean up old media blobs that haven't been accessed recently"""
        from datetime import timedelta

        cutoff_date = datetime.utcnow() - timedelta(days=days_old)
        old_blobs = cls.query.filter(cls.last_accessed < cutoff_date).all()

        deleted_count = 0
        for blob in old_blobs:
            # Also mark the associated asset as deleted
            if blob.asset:
                blob.asset.is_deleted = True
            db.session.delete(blob)
            deleted_count += 1

        try:
            db.session.commit()
            return deleted_count
        except Exception as e:
            db.session.rollback()
            raise e


# Database initialization function
def init_db():
    """Initialize database with default data"""
    # Create default roles
    if not Role.query.filter_by(name="admin").first():
        admin_role = Role(
            name="admin",
            description="Administrator with full access",
            permissions=json.dumps(
                [
                    "admin_access",
                    "manage_users",
                    "manage_settings",
                    "start_jobs",
                    "delete_assets",
                    "view_all_jobs",
                    "view_all_assets",
                ]
            ),
        )
        db.session.add(admin_role)

    if not Role.query.filter_by(name="user").first():
        user_role = Role(
            name="user",
            description="Standard user with limited access",
            permissions=json.dumps(["start_jobs", "delete_own_assets", "view_own_jobs", "view_own_assets"]),
        )
        db.session.add(user_role)

    if not Role.query.filter_by(name="guest").first():
        guest_role = Role(
            name="guest", description="Guest with read-only access", permissions=json.dumps(["view_public_assets"])
        )
        db.session.add(guest_role)

    # Ensure sop1973@gmail.com is admin
    admin_user = User.query.filter_by(email=os.getenv("ADMIN_EMAIL", "admin@example.com")).first()
    admin_role = Role.query.filter_by(name="admin").first()
    if admin_user and admin_role:
        if not any(ur.role_id == admin_role.id for ur in admin_user.user_roles):
            db.session.add(UserRole(user_id=admin_user.id, role_id=admin_role.id))
            print("✅ sop1973@gmail.com assigned admin role")

    # Create default settings
    default_settings = [
        ("max_content_per_source", "25", "Maximum content to download per source", "int"),
        ("default_safe_search", "true", "Default safe search setting", "bool"),
        ("allow_guest_downloads", "false", "Allow guests to start download jobs", "bool"),
        ("max_job_history", "100", "Maximum number of jobs to keep in history", "int"),
        ("cleanup_interval_days", "30", "Days after which to clean up old jobs", "int"),
        ("enable_thumbnails", "true", "Enable thumbnail generation for videos", "bool"),
        ("max_file_size_mb", "100", "Maximum file size for downloads in MB", "int"),
    ]

    for key, value, description, setting_type in default_settings:
        if not AppSetting.query.filter_by(key=key).first():
            setting = AppSetting(key=key, value=value, description=description, setting_type=setting_type)
            db.session.add(setting)

    db.session.commit()
    print("✅ Database initialized with default roles and settings")
