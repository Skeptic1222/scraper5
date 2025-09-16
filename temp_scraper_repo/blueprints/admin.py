from flask import Blueprint, request
from flask_login import current_user

from auth import admin_required
from db_job_manager import db_job_manager
from models import AppSetting, User, db
from utils.responses import fail, success

try:
    from fixed_asset_manager import db_asset_manager
except Exception:
    try:
        from database_asset_manager import db_asset_manager
    except Exception:
        from db_asset_manager import db_asset_manager


admin_bp = Blueprint("admin", __name__, url_prefix="/api/admin")


@admin_bp.route("/cleanup")
@admin_required
def cleanup():
    """Admin endpoint to cleanup old jobs and missing files."""
    try:
        cleanup_days = int(request.args.get("days", 30))
        cleaned_jobs = db_job_manager.cleanup_old_jobs(cleanup_days)
        cleaned_assets = db_asset_manager.cleanup_missing_files()
        return success(
            message=f"Cleaned up {cleaned_jobs} old jobs and {cleaned_assets} missing assets",
            cleaned_jobs=cleaned_jobs,
            cleaned_assets=cleaned_assets,
        )
    except Exception as e:
        return fail(str(e))


@admin_bp.route("/users")
@admin_required
def list_users():
    try:
        users = User.query.all()
        return success(users=[u.to_dict() for u in users], total=len(users))
    except Exception as e:
        return fail(str(e))


@admin_bp.route("/user/<int:user_id>")
@admin_required
def get_user(user_id: int):
    try:
        user = User.query.get(user_id)
        if not user:
            return fail("User not found", status=404)
        return success(
            user={
                "id": user.id,
                "email": user.email,
                "display_name": user.name,
                "subscription_plan": user.subscription_plan,
                "credits": user.credits,
                "created_at": user.created_at.isoformat() if user.created_at else None,
                "last_login": user.last_login.isoformat() if user.last_login else None,
                "is_admin": user.is_admin(),
            }
        )
    except Exception as e:
        return fail(str(e))


@admin_bp.route("/user/<int:user_id>", methods=["PUT"])
@admin_required
def update_user(user_id: int):
    try:
        user = User.query.get(user_id)
        if not user:
            return fail("User not found", status=404)
        data = request.json or {}
        if "subscription_plan" in data:
            user.subscription_plan = data["subscription_plan"]
            user.subscription_status = (
                "active" if data["subscription_plan"] != "trial" else "trial"
            )
            from subscription import ALL_SOURCES, SUBSCRIPTION_PLANS, TRIAL_SOURCES

            if data["subscription_plan"] == "ultra":
                user.set_enabled_sources(ALL_SOURCES)
                user.is_nsfw_enabled = True
            elif data["subscription_plan"] in SUBSCRIPTION_PLANS:
                plan = SUBSCRIPTION_PLANS[data["subscription_plan"]]
                user.set_enabled_sources(plan["sources"])
                user.is_nsfw_enabled = False
            else:
                user.set_enabled_sources(TRIAL_SOURCES)
                user.is_nsfw_enabled = False
        if "credits" in data:
            user.credits = int(data["credits"])
        db.session.commit()
        return success(
            message="User updated successfully",
            user={
                "id": user.id,
                "subscription_plan": user.subscription_plan,
                "credits": user.credits,
            },
        )
    except Exception as e:
        return fail(str(e))


@admin_bp.route("/settings")
@admin_required
def get_settings():
    try:
        settings = AppSetting.query.all()
        settings_dict = {}
        for setting in settings:
            settings_dict[setting.key] = {
                "value": setting.get_value(),
                "description": setting.description,
                "type": setting.setting_type,
                "updated_at": (
                    setting.updated_at.isoformat() if setting.updated_at else None
                ),
            }
        return success(settings=settings_dict)
    except Exception as e:
        return fail(str(e))


@admin_bp.route("/settings", methods=["PUT"])
@admin_required
def update_settings():
    try:
        data = request.get_json() or {}
        for key, value in data.items():
            AppSetting.set_setting(key=key, value=value, user_id=current_user.id)
        return success(message=f"Updated {len(data)} settings")
    except Exception as e:
        return fail(str(e))
