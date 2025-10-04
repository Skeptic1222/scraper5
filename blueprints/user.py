from flask import Blueprint, jsonify, make_response, request
from flask_login import current_user, login_required

from auth import optional_auth
from db_job_manager import db_job_manager
from models import db
from subscription import TRIAL_SOURCES, check_subscription_status
from watermark import get_watermark_css

try:
    from fixed_asset_manager import db_asset_manager
except Exception:
    try:
        from database_asset_manager import db_asset_manager
    except Exception:
        from db_asset_manager import db_asset_manager


user_bp = Blueprint("user", __name__)


@user_bp.route("/api/user-info")
@optional_auth
def get_user_info():
    if current_user.is_authenticated:
        check_subscription_status(current_user)
        return jsonify(
            {
                "authenticated": True,
                "user": current_user.to_dict(),
                "subscription": {
                    "plan": current_user.subscription_plan,
                    "status": current_user.subscription_status,
                    "credits": current_user.credits,
                    "is_subscribed": current_user.is_subscribed(),
                    "can_use_nsfw": current_user.can_use_nsfw(),
                    "sources_enabled": current_user.get_enabled_sources(),
                },
            }
        )
    else:
        return jsonify(
            {
                "authenticated": False,
                "subscription": {
                    "plan": "trial",
                    "credits": 0,
                    "is_subscribed": False,
                    "can_use_nsfw": False,
                    "sources_enabled": TRIAL_SOURCES,
                },
            }
        )


@user_bp.route("/api/user/info")
@login_required
def get_user_info_v2():
    return jsonify(
        {
            "success": True,
            "user": {
                "id": current_user.id,
                "email": current_user.email,
                "name": current_user.name,
                "credits": current_user.credits,
                "subscription_plan": current_user.subscription_plan,
                "is_subscribed": current_user.is_subscribed(),
                "signin_bonus_claimed": getattr(
                    current_user, "signin_bonus_claimed", False
                ),
                "is_admin": getattr(current_user, "is_admin", lambda: False)(),
            },
        }
    )


@user_bp.route("/api/claim-signin-bonus", methods=["POST"])
@login_required
def claim_signin_bonus():
    try:
        if getattr(current_user, "signin_bonus_claimed", False):
            return jsonify({"success": False, "error": "Sign-in bonus already claimed"})
        success = current_user.claim_signin_bonus()
        if success:
            return jsonify(
                {
                    "success": True,
                    "message": "Welcome! You received 50 free credits!",
                    "new_credits": current_user.credits,
                }
            )
        return jsonify({"success": False, "error": "Failed to claim bonus"})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})


@user_bp.route("/api/subscription/status")
@login_required
def subscription_status():
    return jsonify(
        {
            "success": True,
            "is_premium": getattr(current_user, "is_premium", False),
            "credits": current_user.credits,
            "daily_downloads": getattr(current_user, "daily_downloads", 0),
            "max_daily_downloads": (
                25 if not getattr(current_user, "is_premium", False) else 999999
            ),
        }
    )


@user_bp.route("/api/subscription/upgrade", methods=["POST"])
@login_required
def upgrade_subscription():
    return jsonify({"success": False, "message": "Payment processing coming soon!"})


@user_bp.route("/api/download-asset", methods=["POST"])
@login_required
def download_asset():
    try:
        data = request.json or {}
        url = data.get("url")
        filename = data.get("filename")
        if not url or not filename:
            return (
                jsonify({"success": False, "error": "URL and filename are required"}),
                400,
            )
        if not current_user.has_credits():
            return (
                jsonify(
                    {
                        "success": False,
                        "error": "You have no credits remaining. Please upgrade to continue.",
                        "upgrade_required": True,
                    }
                ),
                402,
            )
        current_user.use_credit()
        db.session.commit()
        return jsonify(
            {
                "success": True,
                "message": f"Download initiated for {filename}",
                "credits_remaining": current_user.credits,
            }
        )
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@user_bp.route("/api/stats")
@optional_auth
def get_stats():
    try:
        # Default values
        total_downloads = 0
        total_images = 0
        total_videos = 0
        total_size = 0
        success_rate = 85

        if current_user.is_authenticated:
            user_id = current_user.id

            # Try to get asset statistics
            try:
                stats = db_asset_manager.get_asset_statistics(user_id=user_id)
                total_downloads = stats.get("total_assets", 0)
                total_images = stats.get("total_images", 0)
                total_videos = stats.get("total_videos", 0)
                total_size = stats.get("total_size_bytes", 0)
            except Exception:
                # Use defaults if asset manager fails
                pass

            # Try to get job statistics
            try:
                user_jobs = db_job_manager.get_user_jobs(user_id, limit=100)
                if user_jobs:
                    completed_jobs = [j for j in user_jobs if j.get("status") == "completed"]
                    success_rate = int((len(completed_jobs) / len(user_jobs)) * 100)
            except Exception:
                # Use default success rate if job manager fails
                pass

        # Always return success with whatever data we have
        return jsonify(
            {
                "success": True,
                "stats": {
                    "total_downloads": total_downloads,
                    "total_images": total_images,
                    "total_videos": total_videos,
                    "total_size": total_size,
                    "success_rate": success_rate,
                },
            }
        )
    except Exception as e:
        # Even on error, return safe defaults
        return jsonify(
            {
                "success": True,
                "stats": {
                    "total_downloads": 0,
                    "total_images": 0,
                    "total_videos": 0,
                    "total_size": 0,
                    "success_rate": 85,
                },
            }
        )


@user_bp.route("/api/current-user")
@optional_auth
def current_user_info():
    try:
        if current_user and current_user.is_authenticated:
            return jsonify(
                {
                    "authenticated": True,
                    "user": {
                        "id": current_user.id,
                        "email": current_user.email,
                        "name": current_user.name,
                        "credits": current_user.credits,
                        "subscription_plan": current_user.subscription_plan,
                        "is_admin": getattr(current_user, "is_admin", lambda: False)(),
                    },
                }
            )
        else:
            return jsonify({"authenticated": False})
    except Exception as e:
        return jsonify({"authenticated": False, "error": str(e)})


@user_bp.route("/api/update-nsfw", methods=["POST"])
@login_required
def update_nsfw_setting():
    try:
        data = request.json or {}
        enabled = data.get("enabled", False)
        if not current_user.can_use_nsfw():
            return (
                jsonify(
                    {
                        "success": False,
                        "error": "NSFW content requires Ultra subscription",
                    }
                ),
                403,
            )
        current_user.is_nsfw_enabled = enabled
        db.session.commit()
        return jsonify({"success": True, "enabled": current_user.is_nsfw_enabled})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})


# This is API CSS; keep path stable under /api
@user_bp.route("/api/watermark-css")
def get_watermark_styles():
    return make_response(get_watermark_css(), 200, {"Content-Type": "text/css"})


@user_bp.route("/api/user/preferences", methods=["GET"])
@optional_auth
def get_user_preferences():
    """Get user preferences from database or return defaults"""
    try:
        if current_user and current_user.is_authenticated:
            preferences = current_user.get_preferences()
            return jsonify({"success": True, "preferences": preferences})
        else:
            # Return default preferences for non-authenticated users
            return jsonify({
                "success": True,
                "preferences": {
                    "safeSearch": True,
                    "downloadQuality": "medium",
                    "concurrentDownloads": 5,
                    "theme": "light",
                    "autoPlay": False,
                    "notifications": True
                }
            })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})


@user_bp.route("/api/user/preferences", methods=["POST"])
@optional_auth
def save_user_preferences():
    """Save user preferences to database"""
    try:
        if current_user and current_user.is_authenticated:
            data = request.json or {}
            current_user.set_preferences(data)
            db.session.commit()
            return jsonify({"success": True, "message": "Preferences saved"})
        else:
            # Non-authenticated users can't save to backend
            return jsonify({"success": False, "message": "Login required to save preferences"})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})
