from flask import Blueprint, jsonify
from flask_login import current_user
from datetime import datetime, timedelta
from sqlalchemy import func

from auth import optional_auth
from models import db, ScrapeJob, Asset, User
from sources_data import get_content_sources

dashboard_bp = Blueprint("dashboard", __name__)


@dashboard_bp.route("/api/dashboard/summary")
@optional_auth
def get_dashboard_summary():
    """Get dashboard summary data"""
    try:
        # Get total source count dynamically
        sources = get_content_sources()
        all_sources = [s for cat in sources.values() for s in cat]
        total_sources = len(all_sources)

        summary_data = {
            "active_downloads": 0,
            "total_assets": 0,
            "content_sources": total_sources,  # Dynamic count from sources_data.py
            "queue_length": 0,
            "recent_activity": [],
            "system_status": {
                "database": "connected",
                "apis": "online",
                "navigation": "working"
            }
        }

        if current_user and current_user.is_authenticated:
            # Get user's stats
            user_id = current_user.id

            # Count total assets - ONLY non-deleted assets
            total_assets = db.session.query(func.count(Asset.id)).filter_by(user_id=user_id, is_deleted=False).scalar() or 0
            summary_data["total_assets"] = total_assets

            # Count active jobs
            active_jobs = db.session.query(func.count(ScrapeJob.id)).filter_by(
                user_id=user_id
            ).filter(
                ScrapeJob.status.in_(['pending', 'running', 'downloading'])
            ).scalar() or 0
            summary_data["active_downloads"] = active_jobs

            # Count queued jobs
            queued_jobs = db.session.query(func.count(ScrapeJob.id)).filter_by(
                user_id=user_id,
                status='pending'
            ).scalar() or 0
            summary_data["queue_length"] = queued_jobs

            # Get recent activity (last 5 jobs)
            recent_jobs = db.session.query(ScrapeJob).filter_by(
                user_id=user_id
            ).order_by(ScrapeJob.created_at.desc()).limit(5).all()

            summary_data["recent_activity"] = [
                {
                    "id": job.id,
                    "query": job.query,
                    "status": job.status,
                    "progress": job.progress,
                    "created_at": job.created_at.isoformat() if job.created_at else None,
                    "message": job.message
                }
                for job in recent_jobs
            ]

        return jsonify({"success": True, "summary": summary_data})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})


@dashboard_bp.route("/api/jobs/recent")
@optional_auth
def get_recent_jobs():
    """Get recent job activity"""
    try:
        jobs = []

        if current_user and current_user.is_authenticated:
            user_id = current_user.id

            # Get recent jobs (last 10)
            recent_jobs = db.session.query(ScrapeJob).filter_by(
                user_id=user_id
            ).order_by(ScrapeJob.created_at.desc()).limit(10).all()

            jobs = [
                {
                    "id": job.id,
                    "query": job.query,
                    "status": job.status,
                    "progress": job.progress,
                    "created_at": job.created_at.isoformat() if job.created_at else None,
                    "updated_at": job.updated_at.isoformat() if job.updated_at else None,
                    "message": job.message,
                    "downloaded": job.downloaded,
                    "detected": job.detected
                }
                for job in recent_jobs
            ]

        return jsonify({"success": True, "jobs": jobs})
    except Exception as e:
        return jsonify({"success": False, "error": str(e), "jobs": []})