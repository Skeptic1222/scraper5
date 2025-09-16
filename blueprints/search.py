import json
import os
import threading

from flask import Blueprint, current_app, jsonify, request
from flask_login import current_user

from db_job_manager import db_job_manager
from models import AppSetting, db
from sources_data import get_content_sources
from subscription import check_subscription_status, get_user_sources

try:
    from fixed_asset_manager import db_asset_manager
except Exception:
    try:
        from database_asset_manager import db_asset_manager
    except Exception:
        from db_asset_manager import db_asset_manager


# Downloader availability (mirrors app.py pattern)
try:
    from optimized_downloader import comprehensive_multi_source_scrape

    REAL_DOWNLOADER_AVAILABLE = True
except Exception:
    try:
        from working_downloader import comprehensive_multi_source_scrape

        REAL_DOWNLOADER_AVAILABLE = True
    except Exception:
        REAL_DOWNLOADER_AVAILABLE = False

        def comprehensive_multi_source_scrape(**kwargs):
            return {
                "total_detected": 0,
                "total_downloaded": 0,
                "total_images": 0,
                "total_videos": 0,
                "sources": {},
            }


search_bp = Blueprint("search", __name__)


def create_progress_callback(job_id, metadata=None):
    def progress_callback(
        message, progress=0, downloaded=0, images=0, videos=0, current_file=None
    ):
        with current_app.app_context():
            try:
                db_job_manager.add_progress_update(
                    job_id, message, progress, downloaded, images, videos, current_file
                )
                if current_file and os.path.exists(current_file):
                    file_extension = os.path.splitext(current_file)[1].lower()
                    file_type = (
                        "video"
                        if file_extension in [".mp4", ".webm", ".avi", ".mov", ".mkv"]
                        else "image"
                    )
                    asset_metadata = {
                        "source_name": "scraper",
                        "downloaded_via": "comprehensive_search",
                    }
                    if metadata:
                        asset_metadata.update(
                            {
                                "source_url": metadata.get("source_url"),
                                "content_type": metadata.get("content_type"),
                                "file_size": metadata.get("file_size"),
                                "is_video": metadata.get("is_video", False),
                            }
                        )
                    db_asset_manager.add_asset(
                        job_id=job_id,
                        filepath=current_file,
                        file_type=file_type,
                        metadata=asset_metadata,
                    )
            except Exception as e:
                current_app.logger.warning(
                    f"Progress callback error for job {job_id}: {e}"
                )

    return progress_callback


def run_comprehensive_search_job(
    job_id, query, search_type, max_content, enabled_sources, safe_search=True, app=None
):
    # Get the Flask app instance if not provided
    if app is None:
        from app import app

    with app.app_context():
        try:
            job = db_job_manager.get_job(job_id)
            user_id = job.get("data", {}).get("user_id") if job else None
            db_job_manager.update_job(
                job_id,
                status="running",
                message=f'Starting {search_type} search (Safe search: {"ON" if safe_search else "OFF"})...',
            )
            try:
                from enhanced_working_downloader import run_download_job

                run_download_job(
                    job_id=job_id,
                    query=query,
                    sources=enabled_sources,
                    max_content=max_content,
                    safe_search=safe_search,
                    user_id=user_id,
                )
                return
            except ImportError:
                try:
                    from working_downloader import run_download_job

                    run_download_job(
                        job_id=job_id,
                        query=query,
                        sources=enabled_sources,
                        max_content=max_content,
                        safe_search=safe_search,
                        user_id=user_id,
                    )
                    return
                except ImportError:
                    pass

            progress_callback = create_progress_callback(job_id)
            results = comprehensive_multi_source_scrape(
                query=query,
                search_type=search_type,
                enabled_sources=enabled_sources,
                max_content_per_source=max_content,
                output_dir=None,
                progress_callback=progress_callback,
                safe_search=safe_search,
                use_queue=True,
                job_id=job_id,
            )
            db_job_manager.update_job(
                job_id,
                status="completed",
                progress=100,
                message=f'{search_type.capitalize()} search completed successfully! (Safe search: {"ON" if safe_search else "OFF"})',
                detected=results.get("total_detected", 0),
                downloaded=results.get("total_downloaded", 0),
                images=results.get("total_images", 0),
                videos=results.get("total_videos", 0),
                sources=results.get("sources", {}),
                results=results,
            )
        except Exception as e:
            db_job_manager.update_job(
                job_id, status="error", message=f"Error: {str(e)}", progress=0
            )


@search_bp.route("/api/comprehensive-search", methods=["POST"])
def start_comprehensive_search():
    try:
        data = request.json or {}
        query = data.get("query", "").strip()
        search_type = data.get("search_type", "comprehensive")
        max_content = int(data.get("max_content", 25))
        enabled_sources = data.get("enabled_sources", [])
        safe_search = data.get("safe_search", True)
        if not query:
            return jsonify({"success": False, "error": "Query is required"})
        if not current_user.is_authenticated:
            user_id = None
            guest_sources = [
                "google_images",
                "bing_images",
                "reddit",
                "imgur",
                "unsplash",
            ]
            enabled_sources = [s for s in enabled_sources if s in guest_sources][
                :3
            ] or ["google_images", "bing_images"]
            safe_search = True
        else:
            try:
                check_subscription_status(current_user)
                if not current_user.has_credits():
                    return (
                        jsonify(
                            {
                                "success": False,
                                "error": "You have no credits remaining. Please upgrade to continue.",
                                "upgrade_required": True,
                                "credits": 0,
                            }
                        ),
                        402,
                    )
                if not current_user.has_permission("start_jobs"):
                    return (
                        jsonify(
                            {
                                "success": False,
                                "error": "You do not have permission to start download jobs",
                            }
                        ),
                        403,
                    )
                allowed_sources = get_user_sources(current_user)
                enabled_sources = [s for s in enabled_sources if s in allowed_sources]
                if not enabled_sources:
                    return (
                        jsonify(
                            {
                                "success": False,
                                "error": "No valid sources selected. Please check your subscription level.",
                                "upgrade_required": True,
                            }
                        ),
                        402,
                    )
                if current_user.can_use_nsfw() and current_user.is_nsfw_enabled:
                    safe_search = False
                else:
                    safe_search = True
                user_id = current_user.id
            except Exception:
                user_id = None
                enabled_sources = ["google_images", "bing_images"]
                safe_search = True
        if safe_search:
            sources = get_content_sources()
            enabled_sources = [
                s
                for s in enabled_sources
                if s not in sources or not sources[s].requires_no_safe_search
            ]
        if current_user.is_authenticated and user_id:
            try:
                current_user.use_credit()
                db.session.commit()
            except Exception:
                pass
        job_id = db_job_manager.create_job(
            "comprehensive_search",
            {
                "query": query,
                "search_type": search_type,
                "max_content": max_content,
                "enabled_sources": enabled_sources,
                "safe_search": safe_search,
                "user_id": user_id,
            },
        )
        # Get the current app instance to pass to the thread
        app_instance = current_app._get_current_object()

        thread = threading.Thread(
            target=run_comprehensive_search_job,
            args=(
                job_id,
                query,
                search_type,
                max_content,
                enabled_sources,
                safe_search,
                app_instance,
            ),
        )
        thread.daemon = True
        thread.start()
        credits_remaining = current_user.credits if current_user.is_authenticated else 0
        return jsonify(
            {
                "success": True,
                "job_id": job_id,
                "message": f'Comprehensive search started (Safe search: {"ON" if safe_search else "OFF"})',
                "safe_search_enabled": safe_search,
                "user_authenticated": current_user.is_authenticated,
                "credits_remaining": credits_remaining,
            }
        )
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})


def run_instagram_search_job(job_id, username, max_content):
    with current_app.app_context():
        try:
            progress_callback = create_progress_callback(job_id)
            db_job_manager.update_job(
                job_id, status="running", message=f"Scraping Instagram @{username}..."
            )
            from enhanced_instagram_scrape import enhanced_instagram_scrape

            results = enhanced_instagram_scrape(
                username_or_url=username,
                max_content=max_content,
                output_dir=None,
                progress_callback=progress_callback,
            )
            downloaded_count = results.get("downloaded", 0)
            images = results.get("images", 0)
            videos = results.get("videos", 0)
            db_job_manager.update_job(
                job_id,
                status="completed",
                progress=100,
                message=f"Instagram scraping completed! Downloaded {downloaded_count} files ({images} images, {videos} videos)",
                downloaded=downloaded_count,
                images=images,
                videos=videos,
                detected=downloaded_count,
            )
        except Exception as e:
            db_job_manager.update_job(
                job_id, status="error", message=f"Instagram error: {str(e)}", progress=0
            )


@search_bp.route("/api/instagram-search", methods=["POST"])
def start_instagram_search():
    try:
        data = request.json or {}
        username = data.get("username", "").strip().replace("@", "")
        max_content = int(data.get("max_content", 25))
        if not username:
            return jsonify({"success": False, "error": "Username is required"})
        if not current_user.is_authenticated:
            allow_guest = AppSetting.get_setting("allow_guest_downloads", False)
            if not allow_guest:
                return (
                    jsonify(
                        {
                            "success": False,
                            "error": "Authentication required to start downloads",
                            "login_required": True,
                        }
                    ),
                    401,
                )
        else:
            if not current_user.has_permission("start_jobs"):
                return (
                    jsonify(
                        {
                            "success": False,
                            "error": "You do not have permission to start download jobs",
                        }
                    ),
                    403,
                )
        user_id = current_user.id if current_user.is_authenticated else None
        job_id = db_job_manager.create_job(
            "instagram_search",
            {"username": username, "max_content": max_content, "user_id": user_id},
        )
        thread = threading.Thread(
            target=run_instagram_search_job, args=(job_id, username, max_content)
        )
        thread.daemon = True
        thread.start()
        return jsonify(
            {
                "success": True,
                "job_id": job_id,
                "message": f"Instagram search started for @{username}",
            }
        )
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})


# Compatibility endpoint for legacy health check
@search_bp.route('/api/search', methods=['GET', 'POST'])
def search_get():
    if request.method == 'POST':
        # Redirect POST requests to comprehensive search
        return start_comprehensive_search()
    return jsonify({'success': True, 'message': 'Use POST /api/comprehensive-search'})


@search_bp.route("/api/bulletproof-search", methods=["POST"])
def start_bulletproof_search():
    try:
        data = request.get_json() or {}
        query = data.get("query", "").strip()
        sources = data.get("sources", [])
        max_results = int(data.get("maxResults", 25))
        safe_search = data.get("safeSearch", True)
        content_types = data.get("contentTypes", {"images": True, "videos": True})
        quality_settings = data.get("qualitySettings", {})
        if not query:
            return jsonify({"success": False, "error": "Query is required"})
        if not sources:
            return jsonify(
                {"success": False, "error": "At least one source must be selected"}
            )
        if not current_user.is_authenticated:
            allow_guest = AppSetting.get_setting("allow_guest_downloads", False)
            if not allow_guest:
                return (
                    jsonify(
                        {
                            "success": False,
                            "error": "Authentication required",
                            "login_required": True,
                        }
                    ),
                    401,
                )
        if current_user.is_authenticated and not current_user.has_permission(
            "start_jobs"
        ):
            return jsonify({"success": False, "error": "Insufficient permissions"}), 403
        user_id = current_user.id if current_user.is_authenticated else None
        job_id = db_job_manager.create_job(
            "bulletproof_multi",
            {
                "user_id": user_id,
                "query": query,
                "max_content": max_results,
                "safe_search": safe_search,
                "enabled_sources": sources,
                "content_types": content_types,
                "quality_settings": quality_settings,
                "engine": "bulletproof",
            },
        )

        def run_bulletproof_search():
            try:
                db_job_manager.update_job(job_id, status="running")
                db_job_manager.add_progress_update(
                    job_id,
                    message="Bulletproof engine initialized",
                    progress=10,
                    downloaded=0,
                    images=0,
                    videos=0,
                    current_file="Bulletproof engine initialized",
                )
                if REAL_DOWNLOADER_AVAILABLE:
                    try:
                        results = comprehensive_multi_source_scrape(
                            query=query,
                            search_type="comprehensive",
                            enabled_sources=sources,
                            max_content_per_source=(
                                max(1, max_results // len(sources))
                                if sources
                                else max_results
                            ),
                            output_dir=None,
                            safe_search=safe_search,
                            use_queue=False,
                            job_id=job_id,
                            progress_callback=lambda msg, progress=0, downloaded=0, images=0, videos=0, current_file="": db_job_manager.add_progress_update(
                                job_id,
                                message=msg,
                                progress=progress,
                                downloaded=downloaded,
                                images=images,
                                videos=videos,
                                current_file=current_file,
                            ),
                        )
                    except Exception:
                        from simple_downloader import simple_multi_source_search

                        results = simple_multi_source_search(
                            query=query,
                            sources=sources,
                            max_results_per_source=(
                                max(1, max_results // len(sources)) if sources else 5
                            ),
                            safe_search=safe_search,
                            progress_callback=lambda msg, progress=0: db_job_manager.add_progress_update(
                                job_id,
                                message=msg,
                                progress=progress,
                                downloaded=0,
                                images=0,
                                videos=0,
                                current_file=msg,
                            ),
                        )
                else:
                    from simple_downloader import simple_multi_source_search

                    results = simple_multi_source_search(
                        query=query,
                        sources=sources,
                        max_results_per_source=(
                            max(1, max_results // len(sources)) if sources else 5
                        ),
                        safe_search=safe_search,
                        progress_callback=lambda msg, progress=0: db_job_manager.add_progress_update(
                            job_id,
                            message=msg,
                            progress=progress,
                            downloaded=0,
                            images=0,
                            videos=0,
                            current_file=msg,
                        ),
                    )
                results_count = len(results) if results else 0
                saved_count = 0
                if results:
                    for result in results:
                        try:
                            asset = db_asset_manager.save_asset(
                                url=result.get("url"),
                                title=result.get("title", "Untitled"),
                                source=result.get("source", "unknown"),
                                content_type=result.get("type", "unknown"),
                                file_path=result.get("local_path"),
                                metadata=result.get("metadata", {}),
                                user_id=user_id,
                                job_id=job_id,
                            )
                            if asset:
                                saved_count += 1
                        except Exception as save_error:
                            current_app.logger.warning(
                                f"Asset save error: {save_error}"
                            )
                db_job_manager.update_job(job_id, status="completed")
                success_message = (
                    "Download completed! {} items saved successfully".format(
                        saved_count
                    )
                    if saved_count > 0
                    else "Search completed (found {} results, but none could be saved)".format(
                        results_count
                    )
                )
                db_job_manager.add_progress_update(
                    job_id,
                    message=success_message,
                    progress=100,
                    downloaded=saved_count,
                    images=(
                        len([r for r in results if r.get("type") == "image"])
                        if results
                        else 0
                    ),
                    videos=(
                        len([r for r in results if r.get("type") == "video"])
                        if results
                        else 0
                    ),
                    current_file=f"{saved_count} items saved to database",
                )
            except Exception as e:
                db_job_manager.update_job(job_id, status="failed", message=str(e))
                db_job_manager.add_progress_update(
                    job_id,
                    message=f"Download failed: {str(e)}",
                    progress=0,
                    downloaded=0,
                    images=0,
                    videos=0,
                    current_file="Error occurred",
                )

        thread = threading.Thread(target=run_bulletproof_search)
        thread.daemon = True
        thread.start()
        return jsonify(
            {
                "success": True,
                "job_id": job_id,
                "message": "Bulletproof search started with AI monitoring",
                "engine": "bulletproof",
                "selected_sources": len(sources),
            }
        )
    except Exception as e:
        current_app.logger.error(f"Bulletproof search error: {e}")
        return jsonify({"success": False, "error": str(e)})


@search_bp.route("/api/job-progress/<job_id>")
def get_job_progress(job_id):
    try:
        job = db_job_manager.get_job(job_id)
        if not job:
            return jsonify({"error": "Job not found"}), 404
        if current_user.is_authenticated:
            if job.get("user_id") != current_user.id and not current_user.has_role(
                "admin"
            ):
                return jsonify({"error": "Access denied"}), 403
        try:
            # Not all deployments define a bulletproof engine; guard usage
            from bulletproof_engine import get_bulletproof_engine  # optional

            engine_stats = get_bulletproof_engine().get_statistics()
        except Exception:
            engine_stats = {
                "total_retries": 0,
                "total_downloads": 0,
                "success_rate": 0,
                "error": "Engine unavailable",
            }
        metadata = {}
        try:
            if job.get("sources_data"):
                metadata = json.loads(job.get("sources_data"))
            elif job.get("live_updates"):
                metadata = {"log_entries": json.loads(job.get("live_updates"))}
        except Exception:
            metadata = {}
        return jsonify(
            {
                "job_id": job_id,
                "status": job.get("status"),
                "overall_progress": job.get("progress", 0),
                "source_progress": metadata.get("source_progress", 0),
                "current_source": metadata.get("current_source", ""),
                "current_file": job.get("current_file", ""),
                "downloaded_count": job.get("downloaded", 0),
                "success_count": job.get("downloaded", 0),
                "retry_count": engine_stats.get("total_retries", 0),
                "error_count": job.get("failed", 0),
                "engine_stats": engine_stats,
                "log_entries": metadata.get("log_entries", []),
            }
        )
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@search_bp.route("/api/bulletproof-cancel/<job_id>", methods=["POST"])
def cancel_bulletproof_job(job_id):
    try:
        job = db_job_manager.get_job(job_id)
        if not job:
            return jsonify({"error": "Job not found"}), 404
        if current_user.is_authenticated:
            if job.get("user_id") != current_user.id and not current_user.has_role(
                "admin"
            ):
                return jsonify({"error": "Access denied"}), 403
        db_job_manager.update_job_progress(job_id, status="cancelled")
        return jsonify({"success": True, "message": "Job cancelled successfully"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@search_bp.route("/api/bulletproof-stats")
def get_bulletproof_stats():
    try:
        try:
            from bulletproof_engine import get_bulletproof_engine  # optional

            stats = get_bulletproof_engine().get_statistics()
        except Exception:
            stats = {
                "total_retries": 0,
                "total_downloads": 0,
                "success_rate": 0,
                "error": "Engine unavailable",
            }
        return jsonify({"success": True, "stats": stats})
    except Exception as e:
        return jsonify({"error": str(e)}), 500
