from flask import Blueprint, jsonify, request, current_app
import os
import time

from working_media_downloader import media_downloader
from db_job_manager import db_job_manager


debug_bp = Blueprint("debug", __name__)


@debug_bp.route("/api/debug/check-permissions", methods=["GET"])
def check_permissions():
    """Check write permissions to the downloads directory."""
    try:
        base_dir = os.path.abspath(os.path.join(os.getcwd(), "downloads"))
        os.makedirs(base_dir, exist_ok=True)
        test_path = os.path.join(base_dir, f"perm_test_{int(time.time())}.tmp")
        with open(test_path, "w", encoding="utf-8") as f:
            f.write("ok")
        size = os.path.getsize(test_path)
        os.remove(test_path)
        return jsonify({
            "success": True,
            "downloads_dir": base_dir,
            "writable": True,
            "test_size": size,
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "downloads_dir": base_dir if 'base_dir' in locals() else None,
            "writable": False,
            "error": str(e),
        }), 500


@debug_bp.route("/api/debug/download-direct", methods=["POST"])
def debug_download_direct():
    """Download a direct URL and report status in a debug job."""
    data = request.get_json() or {}
    url = data.get("url")
    source = data.get("source", "debug")
    title = data.get("title", os.path.basename(url or "") or "download")

    if not url:
        return jsonify({"success": False, "error": "url is required"}), 400

    # Create a temp debug job
    job_id = db_job_manager.create_job("debug_download", {"url": url, "source": source, "title": title})
    db_job_manager.update_job(job_id, status="running", message=f"Downloading {title}…")

    def progress_cb(msg: str):
        try:
            db_job_manager.add_progress_update(job_id, message=msg, progress=0, current_file=msg)
        except Exception:
            pass

    try:
        file_info = media_downloader.download_direct_url(
            url=url,
            title=title,
            source=source,
            user_id=None,
            progress_callback=progress_cb,
        )
        if file_info and file_info.get("filepath"):
            db_job_manager.update_job(
                job_id,
                status="completed",
                message=f"Downloaded {os.path.basename(file_info['filepath'])}",
                progress=100,
                downloaded=1,
            )
            return jsonify({"success": True, "job_id": job_id, "file": file_info}), 200
        else:
            db_job_manager.update_job(job_id, status="error", message="Download failed", progress=0)
            return jsonify({"success": False, "job_id": job_id, "error": "download failed"}), 500
    except Exception as e:
        db_job_manager.update_job(job_id, status="error", message=str(e), progress=0)
        return jsonify({"success": False, "job_id": job_id, "error": str(e)}), 500

