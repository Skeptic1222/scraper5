from flask import Blueprint, jsonify, request
from flask_login import current_user

from auth import optional_auth, user_or_admin_required
from db_job_manager import db_job_manager

jobs_bp = Blueprint("jobs", __name__)


@jobs_bp.route("/api/job-status/<job_id>")
@optional_auth
def get_job_status(job_id):
    try:
        job_data = db_job_manager.get_job_status(job_id)
        if not job_data or job_data.get("status") == "not_found":
            status_obj = {
                "id": job_id,
                "type": "",
                "progress": 100,
                "message": "Job not found",
                "downloaded": 0,
                "detected": 0,
                "images": 0,
                "videos": 0,
                "updated_at": None,
                "completed": True,
            }
            return jsonify({"success": True, "status": status_obj})
        status_obj = {
            "id": job_data.get("id", job_id),
            "type": job_data.get("type", ""),
            "progress": job_data.get("progress", 0),
            "message": job_data.get("message", ""),
            "downloaded": job_data.get("downloaded", 0),
            "detected": job_data.get("detected", 0),
            "images": job_data.get("images", 0),
            "videos": job_data.get("videos", 0),
            "updated_at": job_data.get("updated_at"),
            "completed": job_data.get("status")
            in ["completed", "failed", "error", "cancelled"],
        }
        return jsonify({"success": True, "status": status_obj})
    except Exception:
        status_obj = {
            "id": job_id,
            "type": "",
            "progress": 100,
            "message": "Job not available",
            "downloaded": 0,
            "detected": 0,
            "images": 0,
            "videos": 0,
            "updated_at": None,
            "completed": True,
        }
        return jsonify({"success": True, "status": status_obj})


# Compatibility alias for legacy route shape
@jobs_bp.route("/api/job/<job_id>/status")
def job_status_alias(job_id):
    return get_job_status(job_id)


@jobs_bp.route("/api/jobs")
@optional_auth
def get_jobs():
    try:
        limit = int(request.args.get("limit", 20))
        status_filter = request.args.get("status")
        if current_user.is_authenticated:
            user_id = None if current_user.is_admin() else current_user.id
        else:
            return jsonify(
                {"jobs": [], "total": 0, "message": "Login to view job history"}
            )
        jobs = db_job_manager.get_user_jobs(
            user_id=user_id, limit=limit, status_filter=status_filter
        )
        stats = db_job_manager.get_job_statistics(user_id=user_id)
        return jsonify(
            {"success": True, "jobs": jobs, "statistics": stats, "total": len(jobs)}
        )
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})


@jobs_bp.route("/api/jobs/<job_id>", methods=["DELETE"])
@user_or_admin_required
def cancel_job(job_id):
    try:
        success = db_job_manager.cancel_job(
            job_id=job_id,
            user_id=current_user.id if not current_user.is_admin() else None,
        )
        if success:
            return jsonify({"success": True, "message": "Job cancelled successfully"})
        return (
            jsonify(
                {
                    "success": False,
                    "error": "Unable to cancel job (may not exist or already completed)",
                }
            ),
            400,
        )
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})
