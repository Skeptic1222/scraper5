import json
import os
import threading

from flask import Blueprint, current_app, jsonify, request
from flask_login import current_user

from db_job_manager import db_job_manager
from models import AppSetting, db
from sources_data import get_content_sources
from working_media_downloader import media_downloader
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

# Enhanced scraper import
try:
    import sys
    sys.path.insert(0, 'scrapers')
    from enhanced_scraper import perform_enhanced_search, enhanced_scraper
    ENHANCED_SCRAPER_AVAILABLE = True
except Exception as e:
    print(f"[WARNING] Enhanced scraper not available: {e}")
    ENHANCED_SCRAPER_AVAILABLE = False


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
    job_id, query, search_type, max_content, total_file_limit, total_size_limit, timeout_seconds, content_types, quality_settings, enabled_sources, safe_search=True, app=None
):
    # Get the actual Flask app instance
    if app is None:
        from flask import current_app
        # Get the underlying app from the proxy
        app = current_app._get_current_object()

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

                # DEBUG: Log sources being passed
                import logging
                logger = logging.getLogger(__name__)
                logger.info(f"[SOURCE DEBUG] Passing {len(enabled_sources)} sources to run_download_job: {enabled_sources}")
                logger.info(f"[TOTAL LIMIT] Total file limit set to: {total_file_limit if total_file_limit > 0 else 'No limit'}")
                logger.info(f"[SIZE LIMIT] Total size limit set to: {total_size_limit if total_size_limit > 0 else 'No limit'} MB")

                run_download_job(
                    job_id=job_id,
                    query=query,
                    sources=enabled_sources,
                    max_content=max_content,
                    total_file_limit=total_file_limit,
                    total_size_limit=total_size_limit,
                    timeout_seconds=timeout_seconds,
                    content_types=content_types,
                    quality_settings=quality_settings,
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
                        total_file_limit=total_file_limit,
                        total_size_limit=total_size_limit,
                        timeout_seconds=timeout_seconds,
                        content_types=content_types,
                        quality_settings=quality_settings,
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


@search_bp.route("/api/enhanced-search", methods=["POST"])
def start_enhanced_search():
    """Enhanced search with safe-search bypass and video support"""
    try:
        data = request.json
        query = data.get("query", "").strip()
        include_videos = data.get("include_videos", False)
        include_adult = data.get("include_adult", False)
        force_bypass_safe_search = data.get("bypass_safe_search", False)
        max_content = min(data.get("max_content", 20), 100)
        sources = data.get("sources", ["google", "bing", "duckduckgo"])
        
        if not query:
            return jsonify({"success": False, "error": "Query is required"})
        
        # Check authentication and permissions
        user_id = None
        safe_search = True
        
        if not current_user.is_authenticated:
            # Limit guest users
            sources = sources[:2]
            max_content = min(max_content, 10)
            include_adult = False
            force_bypass_safe_search = False
        else:
            user_id = current_user.id
            # Check NSFW permissions
            if current_user.can_use_nsfw() and current_user.is_nsfw_enabled:
                safe_search = False
            
            # Apply bypass if requested and allowed
            if force_bypass_safe_search and current_user.can_use_nsfw():
                safe_search = False
        
        # Create job
        job_id = db_job_manager.create_job(
            "enhanced_search",
            {
                "query": query,
                "sources": sources,
                "max_content": max_content,
                "include_videos": include_videos,
                "include_adult": include_adult and not safe_search,
                "safe_search": safe_search,
                "user_id": user_id,
            },
        )
        
        # Start background thread with actual Flask app instance
        app_instance = current_app._get_current_object()
        thread = threading.Thread(
            target=run_enhanced_search_job,
            args=(job_id, query, sources, max_content, safe_search, include_videos, include_adult, app_instance),
        )
        thread.daemon = True
        thread.start()
        
        return jsonify({
            "success": True,
            "job_id": job_id,
            "message": f"Enhanced search started (Safe search: {'BYPASSED' if not safe_search else 'ON'})",
            "safe_search_enabled": safe_search,
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})


def run_enhanced_search_job(job_id, query, sources, max_content, safe_search, include_videos, include_adult, app_instance):
    """Run enhanced search in background"""
    with app_instance.app_context():
        try:
            db_job_manager.update_job(
                job_id, status="running", message=f"Starting enhanced search for '{query}'..."
            )
            
            # Map frontend source names to backend names (enhanced scraper supports only these)
            source_map = {
                'google_images': 'google',
                'bing_images': 'bing',
                'yahoo_images': 'yahoo',
                'duckduckgo_images': 'duckduckgo',
                'yandex_images': 'yandex'
            }
            mapped_sources = [source_map.get(s, s) for s in sources]

            # If selection includes sources not supported by enhanced scraper (e.g., erogarga, unsplash, etc.),
            # fall back to the comprehensive downloader which handles broad sets reliably
            enhanced_supported = { 'google', 'bing', 'yahoo', 'duckduckgo', 'yandex' }
            unsupported = [s for s in mapped_sources if s not in enhanced_supported]
            if unsupported:
                current_app.logger.info(
                    f"[ENHANCED SEARCH] Unsupported sources detected ({unsupported}); falling back to comprehensive job"
                )
                return run_comprehensive_search_job(
                    job_id, query, "all", max_content, sources, safe_search, app_instance
                )
            
            if not ENHANCED_SCRAPER_AVAILABLE:
                print(f"[ENHANCED SEARCH] Falling back to regular search - enhanced scraper not available")
                # Fallback to regular comprehensive search
                return run_comprehensive_search_job(
                    job_id, query, "all", max_content, sources, safe_search, app_instance
                )
            
            try:
                # Use enhanced scraper
                results = perform_enhanced_search(
                    query=query,
                    sources=mapped_sources,
                    limit_per_source=max_content // len(mapped_sources) if mapped_sources else 10,
                    safe_search=safe_search,
                    include_videos=include_videos,
                    include_adult=include_adult and not safe_search
                )
            except Exception as e:
                print(f"[ENHANCED SEARCH] Error calling enhanced scraper: {e}")
                # Fallback to regular search on error
                return run_comprehensive_search_job(
                    job_id, query, "all", max_content, sources, safe_search, app_instance
                )

            # If enhanced scraper returned no results, fall back to comprehensive job
            if not results:
                current_app.logger.info("[ENHANCED SEARCH] No results from enhanced scraper; falling back to comprehensive job")
                return run_comprehensive_search_job(
                    job_id, query, "all", max_content, sources, safe_search, app_instance
                )
            
            # Download results
            downloaded = 0
            images = 0
            videos = 0
            
            for idx, result in enumerate(results):
                progress = int((idx / len(results)) * 100) if results else 0
                
                db_job_manager.update_job(
                    job_id,
                    status="running",
                    progress=progress,
                    message=f"Downloading {result['type']} from {result['source']}...",
                    downloaded=downloaded,
                    images=images,
                    videos=videos
                )
                
                # Handle video downloads
                if result['type'] == 'video':
                    try:
                        if hasattr(enhanced_scraper, 'check_ytdlp_support') and enhanced_scraper.check_ytdlp_support(result['url']):
                            video_file = enhanced_scraper.download_with_ytdlp(result['url'])
                            if video_file:
                                videos += 1
                                downloaded += 1
                                # Save to database
                                try:
                                    if hasattr(db_asset_manager, 'save_downloaded_asset'):
                                        db_asset_manager.save_downloaded_asset(
                                            file_path=video_file,
                                            user_id=None,
                                            source_name=result['source'],
                                            query=query,
                                            is_video=True
                                        )
                                except Exception as e:
                                    print(f"Failed to save video to DB: {e}")
                    except Exception as e:
                        print(f"Error downloading video: {e}")
                        
                # Handle image downloads
                elif result['type'] in ['image', 'adult']:
                    try:
                        title = f"{query}_{result.get('source','image')}"
                        file_info = media_downloader.download_direct_url(
                            url=result['url'],
                            title=title,
                            source=result.get('source', 'enhanced'),
                            user_id=None,
                            progress_callback=None,
                            output_dir=None,
                        )

                        if file_info and file_info.get('filepath'):
                            # Save to database if available
                            try:
                                if hasattr(db_asset_manager, 'save_downloaded_asset'):
                                    db_asset_manager.save_downloaded_asset(
                                        file_path=file_info['filepath'],
                                        user_id=None,
                                        source_name=result.get('source', 'enhanced'),
                                        query=query,
                                        is_video=False,
                                    )
                            except Exception as e:
                                print(f"Failed to save image to DB: {e}")

                            images += 1
                            downloaded += 1
                    except Exception as e:
                        print(f"Failed to download {result['url']}: {e}")
            
            # Update final status
            db_job_manager.update_job(
                job_id,
                status="completed",
                progress=100,
                message=f"Enhanced search completed! Downloaded {downloaded} files ({images} images, {videos} videos)",
                downloaded=downloaded,
                images=images,
                videos=videos,
                detected=len(results)
            )
            
        except Exception as e:
            print(f"[ENHANCED SEARCH] Critical error: {e}")
            db_job_manager.update_job(
                job_id,
                status="error",
                message=f"Enhanced search error: {str(e)}",
                progress=0
            )


@search_bp.route("/api/comprehensive-search", methods=["POST"])
def start_comprehensive_search():
    try:
        data = request.json or {}

        # DEBUG: Print raw request data
        from datetime import datetime as dt
        with open('debug_sources.txt', 'a') as f:
            f.write(f"\n[{dt.now()}] RAW REQUEST DATA:\n")
            f.write(f"Full data: {data}\n")
            f.write(f"enabled_sources: {data.get('enabled_sources')}\n")
            f.write(f"enabled_sources length: {len(data.get('enabled_sources', []))}\n")

        query = data.get("query", "").strip()
        search_type = data.get("search_type", "comprehensive")
        max_content = int(data.get("max_content", 25))
        total_file_limit = int(data.get("total_file_limit", 0))  # 0 means no limit
        total_size_limit = int(data.get("total_size_limit", 0))  # 0 means no limit (in MB)
        timeout_seconds = int(data.get("timeout_seconds", 0))  # 0 means unlimited
        content_types = data.get("content_types", {"images": True, "videos": True})
        quality_settings = data.get("quality_settings", {})
        enabled_sources = data.get("enabled_sources", [])
        safe_search = data.get("safe_search", True)

        # DEBUG: Log received sources
        import logging
        logger = logging.getLogger(__name__)
        logger.info(f"[COMPREHENSIVE] Received {len(enabled_sources)} sources: {enabled_sources}")
        logger.info(f"[COMPREHENSIVE] Content types: {content_types}")
        logger.info(f"[COMPREHENSIVE] Quality settings: {quality_settings}")
        logger.info(f"[COMPREHENSIVE] Total size limit: {total_size_limit if total_size_limit > 0 else 'No limit'} MB")

        if not query:
            return jsonify({"success": False, "error": "Query is required"})
        if not current_user.is_authenticated:
            # Guest users: respect selected sources and safe_search toggle
            user_id = None
            safe_search = bool(safe_search)
        else:
            # Enable premium for now: do not enforce subscription/credits/permissions
            user_id = current_user.id
            safe_search = not (current_user.can_use_nsfw() and getattr(current_user, 'is_nsfw_enabled', False))
        if safe_search:
            # Build lookup of source metadata by id to filter NSFW sources correctly
            src_meta = {}
            try:
                srcs = get_content_sources()
                for cat, arr in srcs.items():
                    if isinstance(arr, list):
                        for src in arr:
                            if isinstance(src, dict) and 'id' in src:
                                src_meta[src['id']] = src
            except Exception:
                src_meta = {}

            before_filter = len(enabled_sources)
            enabled_sources = [
                s for s in enabled_sources
                if not src_meta.get(s, {}).get('nsfw', False)
            ]
            logger.info(f"[COMPREHENSIVE] After NSFW filter: {before_filter} -> {len(enabled_sources)} sources: {enabled_sources}")
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
                "total_file_limit": total_file_limit,
                "total_size_limit": total_size_limit,
                "timeout_seconds": timeout_seconds,
                "content_types": content_types,
                "quality_settings": quality_settings,
                "enabled_sources": enabled_sources,
                "safe_search": safe_search,
                "user_id": user_id,
            },
        )
        # Get the actual Flask app instance to pass to the thread
        app_instance = current_app._get_current_object()

        thread = threading.Thread(
            target=run_comprehensive_search_job,
            args=(
                job_id,
                query,
                search_type,
                max_content,
                total_file_limit,
                total_size_limit,
                timeout_seconds,
                content_types,
                quality_settings,
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
        # Admin users bypass permission check
        if current_user.is_authenticated and not current_user.is_admin() and not current_user.has_permission(
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
            # Admin users can view any job, regular users can only view their own
            if not current_user.is_admin() and job.get("user_id") != current_user.id:
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
        # Calculate elapsed time
        import time as time_module
        job_data = job.get("data", {})
        created_at = job.get("created_at")
        elapsed_seconds = 0
        if created_at:
            try:
                from datetime import datetime
                if isinstance(created_at, str):
                    created_time = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
                else:
                    created_time = created_at
                elapsed_seconds = int((datetime.now(created_time.tzinfo) - created_time).total_seconds())
            except:
                elapsed_seconds = 0

        # Get timeout from job data
        timeout_seconds = job_data.get("timeout_seconds", 0)

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
                "elapsed_seconds": elapsed_seconds,
                "timeout_seconds": timeout_seconds,
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


def detect_source_from_url(url):
    """
    Detect the source and scraping method from a URL

    Returns:
        tuple: (source_name, scraper_method, scraper_config)
    """
    url_lower = url.lower()

    # Video platforms (use yt-dlp)
    if 'youtube.com' in url_lower or 'youtu.be' in url_lower:
        return 'youtube', 'ytdlp', {'format': 'best'}
    elif 'pornhub.com' in url_lower:
        return 'pornhub', 'ytdlp', {'format': 'best'}
    elif 'xvideos.com' in url_lower:
        return 'xvideos', 'ytdlp', {'format': 'best'}
    elif 'redtube.com' in url_lower:
        return 'redtube', 'ytdlp', {'format': 'best'}
    elif 'xhamster.com' in url_lower:
        return 'xhamster', 'ytdlp', {'format': 'best'}
    elif 'youporn.com' in url_lower:
        return 'youporn', 'ytdlp', {'format': 'best'}
    elif 'spankbang.com' in url_lower:
        return 'spankbang', 'ytdlp', {'format': 'best'}
    elif 'vimeo.com' in url_lower:
        return 'vimeo', 'ytdlp', {'format': 'best'}
    elif 'erogarga.com' in url_lower:
        return 'erogarga', 'erogarga', {}

    # Image platforms (use gallery-dl)
    elif 'imgur.com' in url_lower:
        return 'imgur', 'gallerydl', {}
    elif 'reddit.com' in url_lower or 'redd.it' in url_lower:
        return 'reddit', 'gallerydl', {}
    elif 'pinterest.com' in url_lower:
        return 'pinterest', 'gallerydl', {}
    elif 'artstation.com' in url_lower:
        return 'artstation', 'gallerydl', {}
    elif 'deviantart.com' in url_lower:
        return 'deviantart', 'gallerydl', {}
    elif 'flickr.com' in url_lower:
        return 'flickr', 'gallerydl', {}
    elif 'tumblr.com' in url_lower:
        return 'tumblr', 'gallerydl', {}

    # Instagram (special handling)
    elif 'instagram.com' in url_lower:
        return 'instagram', 'ytdlp', {'format': 'best'}

    # Twitter/X
    elif 'twitter.com' in url_lower or 'x.com' in url_lower:
        return 'twitter', 'gallerydl', {}

    # Booru sites
    elif 'gelbooru.com' in url_lower:
        return 'gelbooru', 'gallerydl', {}
    elif 'rule34.xxx' in url_lower:
        return 'rule34', 'gallerydl', {}
    elif 'danbooru.donmai.us' in url_lower:
        return 'danbooru', 'gallerydl', {}

    # Direct image/video URLs (use direct download)
    elif any(url_lower.endswith(ext) for ext in ['.jpg', '.jpeg', '.png', '.gif', '.webp', '.mp4', '.webm', '.avi', '.mov']):
        return 'direct_url', 'direct', {}

    # Default: try yt-dlp (supports 1000+ sites)
    else:
        return 'unknown', 'ytdlp', {'format': 'best'}


def run_url_scrape_job(job_id, url, user_id, app_instance):
    """Run URL scraping in background"""
    with app_instance.app_context():
        try:
            db_job_manager.update_job(
                job_id, status="running", message=f"Analyzing URL..."
            )

            # Detect source and method
            source_name, method, config = detect_source_from_url(url)

            db_job_manager.update_job(
                job_id,
                status="running",
                progress=10,
                message=f"Detected {source_name}, using {method} method..."
            )

            downloaded = 0
            images = 0
            videos = 0
            files = []

            # Use appropriate scraping method
            if method == 'ytdlp':
                try:
                    import sys
                    sys.path.insert(0, 'scrapers')
                    from ytdlp_scraper import download_with_ytdlp

                    db_job_manager.update_job(
                        job_id,
                        status="running",
                        progress=30,
                        message=f"Downloading from {source_name} with yt-dlp..."
                    )

                    # Create output directory
                    output_dir = os.path.join('downloads', f'url_scrape_{job_id}')
                    os.makedirs(output_dir, exist_ok=True)

                    # Download using yt-dlp
                    filepath = download_with_ytdlp(url, output_dir)

                    if filepath and os.path.exists(filepath):
                        files.append(filepath)
                        downloaded = 1

                        # Determine if video or image
                        if any(filepath.lower().endswith(ext) for ext in ['.mp4', '.webm', '.avi', '.mov', '.mkv']):
                            videos = 1
                        else:
                            images = 1

                        # Save to database
                        try:
                            db_asset_manager.add_asset(
                                job_id=job_id,
                                filepath=filepath,
                                file_type='video' if videos else 'image',
                                metadata={
                                    'source_name': source_name,
                                    'source_url': url,
                                    'downloaded_via': 'url_scrape',
                                    'method': 'ytdlp'
                                }
                            )
                        except Exception as e:
                            current_app.logger.warning(f"Failed to save asset: {e}")

                except Exception as e:
                    current_app.logger.error(f"yt-dlp download failed: {e}")
                    db_job_manager.update_job(
                        job_id,
                        status="error",
                        message=f"yt-dlp failed: {str(e)}"
                    )
                    return

            elif method == 'gallerydl':
                try:
                    import subprocess

                    db_job_manager.update_job(
                        job_id,
                        status="running",
                        progress=30,
                        message=f"Downloading from {source_name} with gallery-dl..."
                    )

                    # Create output directory
                    output_dir = os.path.join('downloads', f'url_scrape_{job_id}')
                    os.makedirs(output_dir, exist_ok=True)

                    # Run gallery-dl
                    cmd = [
                        'gallery-dl',
                        '--dest', output_dir,
                        '--quiet',
                        url
                    ]

                    result = subprocess.run(
                        cmd,
                        capture_output=True,
                        text=True,
                        timeout=300
                    )

                    if result.returncode == 0:
                        # Count downloaded files
                        for root, dirs, filenames in os.walk(output_dir):
                            for filename in filenames:
                                filepath = os.path.join(root, filename)
                                files.append(filepath)
                                downloaded += 1

                                if any(filename.lower().endswith(ext) for ext in ['.jpg', '.jpeg', '.png', '.gif', '.webp']):
                                    images += 1
                                elif any(filename.lower().endswith(ext) for ext in ['.mp4', '.webm', '.avi', '.mov']):
                                    videos += 1

                                # Save to database
                                try:
                                    db_asset_manager.add_asset(
                                        job_id=job_id,
                                        filepath=filepath,
                                        file_type='video' if filepath.lower().endswith(('.mp4', '.webm', '.avi', '.mov')) else 'image',
                                        metadata={
                                            'source_name': source_name,
                                            'source_url': url,
                                            'downloaded_via': 'url_scrape',
                                            'method': 'gallerydl'
                                        }
                                    )
                                except Exception as e:
                                    current_app.logger.warning(f"Failed to save asset: {e}")

                except Exception as e:
                    current_app.logger.error(f"gallery-dl download failed: {e}")
                    db_job_manager.update_job(
                        job_id,
                        status="error",
                        message=f"gallery-dl failed: {str(e)}"
                    )
                    return

            elif method == 'erogarga':
                try:
                    import sys
                    sys.path.insert(0, 'scrapers')
                    from erogarga_scraper import extract_video_from_page

                    db_job_manager.update_job(
                        job_id,
                        status="running",
                        progress=30,
                        message=f"Extracting content from erogarga.com..."
                    )

                    # Extract video information
                    results = extract_video_from_page(url)

                    if not results['success']:
                        db_job_manager.update_job(
                            job_id,
                            status="error",
                            message=f"Erogarga extraction failed: {results.get('error', 'Unknown error')}"
                        )
                        return

                    db_job_manager.update_job(
                        job_id,
                        status="running",
                        progress=50,
                        message=f"Downloading media from erogarga.com..."
                    )

                    # Create output directory
                    output_dir = os.path.join('downloads', f'url_scrape_{job_id}')
                    os.makedirs(output_dir, exist_ok=True)

                    # Download thumbnail if available
                    if results['thumbnail']:
                        try:
                            import requests
                            thumb_response = requests.get(results['thumbnail'], timeout=10)
                            if thumb_response.status_code == 200:
                                thumb_ext = results['thumbnail'].split('.')[-1].split('?')[0] or 'jpg'
                                thumb_path = os.path.join(output_dir, f'thumbnail.{thumb_ext}')
                                with open(thumb_path, 'wb') as f:
                                    f.write(thumb_response.content)
                                files.append(thumb_path)
                                images += 1
                                downloaded += 1

                                # Save thumbnail to database
                                try:
                                    db_asset_manager.save_asset(
                                        user_id=user_id,
                                        filename=os.path.basename(thumb_path),
                                        file_path=thumb_path,
                                        source='erogarga',
                                        content_type='image/png',
                                        original_url=url,
                                        title=results.get('title'),
                                        metadata={
                                            'job_id': job_id,
                                            'source_url': url,
                                            'downloaded_via': 'url_scrape',
                                            'method': 'erogarga',
                                            'description': results.get('description')
                                        }
                                    )
                                except Exception as e:
                                    current_app.logger.warning(f"Failed to save thumbnail asset: {e}")

                        except Exception as e:
                            current_app.logger.warning(f"Thumbnail download failed: {e}")

                    # Try to download video URLs if available
                    for idx, video_url in enumerate(results.get('video_urls', [])):
                        try:
                            import requests
                            current_app.logger.info(f"Downloading video from {video_url}")

                            video_response = requests.get(video_url, timeout=60, stream=True)
                            if video_response.status_code == 200:
                                # Determine file extension
                                video_ext = 'mp4'
                                if '.m3u8' in video_url:
                                    video_ext = 'm3u8'
                                elif video_url.split('?')[0].split('.')[-1] in ['mp4', 'webm', 'avi', 'mov', 'mkv']:
                                    video_ext = video_url.split('?')[0].split('.')[-1]

                                video_path = os.path.join(output_dir, f'video_{idx}.{video_ext}')
                                with open(video_path, 'wb') as f:
                                    for chunk in video_response.iter_content(chunk_size=8192):
                                        f.write(chunk)

                                files.append(video_path)
                                videos += 1
                                downloaded += 1

                                # Save video to database
                                try:
                                    db_asset_manager.save_asset(
                                        user_id=user_id,
                                        filename=os.path.basename(video_path),
                                        file_path=video_path,
                                        source='erogarga',
                                        content_type=f'video/{video_ext}',
                                        original_url=url,
                                        title=results.get('title'),
                                        metadata={
                                            'job_id': job_id,
                                            'source_url': url,
                                            'downloaded_via': 'url_scrape',
                                            'method': 'erogarga',
                                            'description': results.get('description')
                                        }
                                    )
                                except Exception as e:
                                    current_app.logger.warning(f"Failed to save video asset: {e}")

                                break  # Only download first working video

                        except Exception as e:
                            current_app.logger.warning(f"Video download failed: {e}")
                            continue

                    # If no video URLs but we have player URL, log it
                    if not results.get('video_urls') and results.get('player_url'):
                        current_app.logger.info(f"Erogarga: Found player URL but couldn't extract video: {results['player_url']}")

                    # Finalize job status
                    if downloaded > 0:
                        db_job_manager.update_job(
                            job_id,
                            status="completed",
                            progress=100,
                            message=f"Downloaded {downloaded} file(s) from erogarga ({images} images, {videos} videos)",
                            downloaded=downloaded,
                            images=images,
                            videos=videos,
                            detected=downloaded
                        )
                    else:
                        db_job_manager.update_job(
                            job_id,
                            status="error",
                            message="No files downloaded from erogarga (video extraction failed)",
                            progress=0
                        )

                except Exception as e:
                    current_app.logger.error(f"Erogarga scraper failed: {e}")
                    db_job_manager.update_job(
                        job_id,
                        status="error",
                        message=f"Erogarga scraper failed: {str(e)}"
                    )
                    return

            elif method == 'direct':
                try:
                    import requests
                    import uuid

                    db_job_manager.update_job(
                        job_id,
                        status="running",
                        progress=30,
                        message=f"Downloading direct URL..."
                    )

                    # Create output directory
                    output_dir = os.path.join('downloads', f'url_scrape_{job_id}')
                    os.makedirs(output_dir, exist_ok=True)

                    # Download file
                    response = requests.get(url, stream=True, timeout=30)
                    response.raise_for_status()

                    # Determine filename
                    from urllib.parse import urlparse
                    parsed = urlparse(url)
                    filename = os.path.basename(parsed.path) or f"download_{uuid.uuid4().hex[:8]}"

                    # Ensure extension
                    if not any(filename.endswith(ext) for ext in ['.jpg', '.jpeg', '.png', '.gif', '.mp4', '.webm']):
                        content_type = response.headers.get('content-type', '')
                        ext_map = {
                            'image/jpeg': '.jpg',
                            'image/png': '.png',
                            'image/gif': '.gif',
                            'video/mp4': '.mp4',
                            'video/webm': '.webm'
                        }
                        for mime, ext in ext_map.items():
                            if mime in content_type:
                                filename += ext
                                break

                    filepath = os.path.join(output_dir, filename)

                    # Save file
                    with open(filepath, 'wb') as f:
                        for chunk in response.iter_content(chunk_size=8192):
                            if chunk:
                                f.write(chunk)

                    files.append(filepath)
                    downloaded = 1

                    if any(filename.lower().endswith(ext) for ext in ['.mp4', '.webm', '.avi', '.mov']):
                        videos = 1
                    else:
                        images = 1

                    # Save to database
                    try:
                        db_asset_manager.add_asset(
                            job_id=job_id,
                            filepath=filepath,
                            file_type='video' if videos else 'image',
                            metadata={
                                'source_name': 'direct_url',
                                'source_url': url,
                                'downloaded_via': 'url_scrape',
                                'method': 'direct'
                            }
                        )
                    except Exception as e:
                        current_app.logger.warning(f"Failed to save asset: {e}")

                except Exception as e:
                    current_app.logger.error(f"Direct download failed: {e}")
                    db_job_manager.update_job(
                        job_id,
                        status="error",
                        message=f"Direct download failed: {str(e)}"
                    )
                    return

            # Update final status
            if downloaded > 0:
                db_job_manager.update_job(
                    job_id,
                    status="completed",
                    progress=100,
                    message=f"Downloaded {downloaded} file(s) from {source_name} ({images} images, {videos} videos)",
                    downloaded=downloaded,
                    images=images,
                    videos=videos,
                    detected=downloaded
                )
            else:
                db_job_manager.update_job(
                    job_id,
                    status="error",
                    message=f"No files downloaded from {url}",
                    progress=0
                )

        except Exception as e:
            current_app.logger.error(f"URL scrape job error: {e}")
            db_job_manager.update_job(
                job_id,
                status="error",
                message=f"URL scrape error: {str(e)}",
                progress=0
            )


@search_bp.route("/api/scrape-url", methods=["POST"])
def start_url_scrape():
    """
    Scrape media from a single URL

    Request JSON:
        {
            "url": "https://youtube.com/watch?v=xxxxx"
        }
    """
    try:
        data = request.json or {}
        url = data.get("url", "").strip()

        if not url:
            return jsonify({"success": False, "error": "URL is required"}), 400

        # Basic URL validation
        if not url.startswith(('http://', 'https://')):
            return jsonify({"success": False, "error": "Invalid URL format. Must start with http:// or https://"}), 400

        # Get user ID if authenticated
        user_id = current_user.id if current_user.is_authenticated else None

        # Detect source from URL
        source_name, method, config = detect_source_from_url(url)

        # Create job
        job_id = db_job_manager.create_job(
            "url_scrape",
            {
                "url": url,
                "source": source_name,
                "method": method,
                "user_id": user_id,
            },
        )

        # Start background thread
        app_instance = current_app._get_current_object()
        thread = threading.Thread(
            target=run_url_scrape_job,
            args=(job_id, url, user_id, app_instance),
        )
        thread.daemon = True
        thread.start()

        return jsonify({
            "success": True,
            "job_id": job_id,
            "message": f"URL scraping started for {source_name}",
            "source": source_name,
            "method": method
        })

    except Exception as e:
        current_app.logger.error(f"URL scrape error: {e}")
        return jsonify({"success": False, "error": str(e)}), 500
