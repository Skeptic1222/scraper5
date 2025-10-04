import mimetypes
import os
import zipfile
import io
import secrets
import urllib.parse
import uuid
from datetime import datetime

from flask import (
    Blueprint,
    Response,
    current_app,
    jsonify,
    make_response,
    request,
    send_file,
)
from flask_login import current_user

from auth import optional_auth, user_or_admin_required
from models import Asset, MediaBlob, User, db
from watermark import watermark_overlay

# Import the correct database-backed asset manager
import db_asset_manager


assets_bp = Blueprint("assets", __name__)

# Track download progress (in-memory, for simplicity)
download_progress = {}


@assets_bp.route("/api/assets")
@optional_auth
def get_assets():
    """Get all downloaded assets with user-based filtering"""
    try:
        try:
            from simple_media_server import get_simple_assets

            result = get_simple_assets()
            if result.get("success"):
                return jsonify(result)
        except Exception as e:
            current_app.logger.debug(
                f"[ASSETS] Simple asset server failed: {e}; using database"
            )

        file_type = request.args.get("type")
        page = int(request.args.get("page", 1))
        limit = int(request.args.get("limit", 100))
        offset = (page - 1) * limit
        admin_view = request.args.get("admin") == "true"

        if current_user.is_authenticated:
            if admin_view and getattr(current_user, "is_admin", lambda: False)():
                user_id = "admin_all"
            elif getattr(current_user, "is_admin", lambda: False)():
                user_id = None
            else:
                user_id = current_user.id
        else:
            user_id = None

        print(f"[ASSETS API] Calling get_assets with user_id={user_id}, file_type={file_type}")
        assets_data = db_asset_manager.get_assets(
            user_id=user_id, file_type=file_type, limit=limit, offset=offset
        )
        print(f"[ASSETS API] Got {len(assets_data)} assets back")

        stats = db_asset_manager.get_asset_statistics(user_id=user_id)

        assets = []
        for asset_data in assets_data:
            user_email = None
            if admin_view and asset_data.get("user_id"):
                user = (
                    db.session.query(User).filter_by(id=asset_data["user_id"]).first()
                )
                user_email = user.email if user else None

            assets.append(
                {
                    "name": asset_data["filename"],
                    "filename": asset_data["filename"],
                    "path": asset_data["file_path"],
                    "size": asset_data["file_size"] or 0,
                    "file_size": asset_data["file_size"] or 0,
                    "modified": asset_data.get("created_at"),
                    "downloaded_at": asset_data.get("created_at"),
                    "type": asset_data["file_type"],
                    "file_type": asset_data["file_type"],
                    "extension": asset_data["file_extension"],
                    "file_extension": asset_data["file_extension"],
                    "id": asset_data["id"],
                    "source": asset_data.get("source_name", "unknown"),
                    "source_name": asset_data.get("source_name", "unknown"),
                    "source_url": asset_data.get("source_url", ""),
                    "user_id": asset_data.get("user_id"),
                    "user_email": user_email,
                    "job_id": asset_data.get("job_id"),
                    "url": f"/scraper/serve/{asset_data['id']}",
                }
            )

        return jsonify(
            {
                "success": True,
                "assets": assets,
                "total": len(assets),
                "counts": {
                    "all": stats.get("all", len(assets)),
                    "images": stats.get("images", 0),
                    "videos": stats.get("videos", 0),
                },
                "page": page,
                "limit": limit,
            }
        )
    except Exception as e:
        current_app.logger.exception("Error getting assets")
        return jsonify(
            {
                "success": False,
                "error": str(e),
                "assets": [],
                "counts": {"all": 0, "images": 0, "videos": 0},
            }
        )


@assets_bp.route("/api/assets/<int:asset_id>", methods=["DELETE"])
@user_or_admin_required
def delete_asset(asset_id):
    try:
        success = db_asset_manager.delete_asset(
            asset_id=asset_id,
            user_id=current_user.id if not current_user.is_admin() else None,
        )
        if success:
            return jsonify({"success": True, "message": "Asset deleted successfully"})
        return (
            jsonify({"success": False, "error": "Asset not found or access denied"}),
            404,
        )
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})


@assets_bp.route("/api/assets/bulk-delete", methods=["POST"])
@optional_auth
def bulk_delete_assets():
    try:
        data = request.get_json() or {}
        asset_ids = data.get("asset_ids", [])
        if not asset_ids:
            return jsonify({"success": False, "error": "No asset IDs provided"}), 400

        # Determine user_id for access control
        if current_user and current_user.is_authenticated:
            user_id = current_user.id if not current_user.is_admin() else None
        else:
            user_id = None  # Guest user - allow deleting guest assets only

        deleted_count = db_asset_manager.bulk_delete_assets(
            asset_ids=asset_ids,
            user_id=user_id,
        )
        return jsonify(
            {
                "success": True,
                "message": f"Successfully deleted {deleted_count} assets",
                "deleted_count": deleted_count,
            }
        )
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})


@assets_bp.route("/api/assets/bulk-move", methods=["POST"])
@user_or_admin_required
def bulk_move_assets():
    try:
        data = request.get_json() or {}
        asset_ids = data.get("asset_ids", [])
        container = data.get("container", "default")
        if not asset_ids:
            return jsonify({"success": False, "error": "No asset IDs provided"}), 400
        moved_count = db_asset_manager.move_assets_to_container(
            asset_ids=asset_ids,
            container_name=container,
            user_id=current_user.id if not current_user.is_admin() else None,
        )
        return jsonify(
            {
                "success": True,
                "message": f"Successfully moved {moved_count} assets to {container}",
                "moved_count": moved_count,
            }
        )
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})


@assets_bp.route("/api/containers")
@user_or_admin_required
def get_user_containers():
    try:
        containers = db_asset_manager.get_user_containers(current_user.id)
        return jsonify({"success": True, "containers": containers})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})


@assets_bp.route("/api/assets/<path:asset_path>", methods=["DELETE"])
@user_or_admin_required
def delete_asset_by_path(asset_path):
    try:
        asset = (
            db.session.query(Asset)
            .filter_by(file_path=asset_path, is_deleted=False)
            .first()
        )
        if not asset:
            return jsonify({"success": False, "error": "Asset not found"}), 404
        return delete_asset(asset.id)
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})


@assets_bp.route("/serve/<int:asset_id>")
@assets_bp.route("/api/media/<int:asset_id>")
@optional_auth
def serve_media_blob(asset_id):
    try:
        asset = Asset.query.get_or_404(asset_id)

        MAX_MEMORY_SIZE = 50 * 1024 * 1024
        media_blob = MediaBlob.query.filter_by(asset_id=asset_id).first()

        if media_blob:
            blob_size = len(media_blob.media_data) if media_blob.media_data else 0
            if blob_size > MAX_MEMORY_SIZE:

                def generate_blob_chunks():
                    chunk_size = 8192
                    data = media_blob.media_data
                    for i in range(0, len(data), chunk_size):
                        yield data[i : i + chunk_size]

                return Response(
                    generate_blob_chunks(),
                    mimetype=media_blob.mime_type,
                    headers={
                        "Content-Length": str(blob_size),
                        "Accept-Ranges": "bytes",
                        "Cache-Control": "private, max-age=3600",
                        "ETag": f'"{asset.id}-{asset.file_size}"',
                    },
                )
            else:
                file_data = media_blob.get_file_data()
                mime_type = media_blob.mime_type
        else:
            if not asset.file_path or not os.path.exists(asset.file_path):
                return jsonify({"error": "Media file not found"}), 404
            file_size = os.path.getsize(asset.file_path)
            if file_size > MAX_MEMORY_SIZE:
                mime_type, _ = mimetypes.guess_type(asset.file_path)
                if not mime_type:
                    mime_type = "application/octet-stream"
                return send_file(
                    asset.file_path,
                    mimetype=mime_type,
                    as_attachment=request.args.get("download") == "true",
                    download_name=asset.filename,
                    conditional=True,
                    etag=f"{asset.id}-{asset.file_size}",
                )
            else:
                with open(asset.file_path, "rb") as f:
                    file_data = f.read()
                mime_type, _ = mimetypes.guess_type(asset.file_path)
                if not mime_type:
                    mime_type = "application/octet-stream"

        should_watermark = False
        if current_user.is_authenticated:
            if (
                current_user.subscription_plan == "trial"
                or not current_user.is_subscribed()
            ):
                should_watermark = True
        else:
            should_watermark = True

        if (
            should_watermark
            and asset.file_type == "image"
            and "file_data" in locals()
            and len(file_data) < MAX_MEMORY_SIZE
        ):
            try:
                file_data = watermark_overlay.apply_watermark_to_image_bytes(file_data)
            except Exception as e:
                current_app.logger.warning(f"Watermark application failed: {e}")

        if "file_data" in locals():
            response = make_response(file_data)
            response.headers["Content-Type"] = mime_type
            if request.args.get("download") == "true":
                response.headers["Content-Disposition"] = (
                    f'attachment; filename="{asset.filename}"'
                )
            else:
                response.headers["Content-Disposition"] = (
                    f'inline; filename="{asset.filename}"'
                )
            response.headers["Cache-Control"] = "private, max-age=3600"
            response.headers["ETag"] = f'"{asset.id}-{asset.file_size}"'
            if should_watermark:
                response.headers["X-Watermarked"] = "true"
            del file_data
            return response

        # If streaming, a response was already returned
        return jsonify({"error": "Unexpected state"}), 500
    except Exception as e:
        current_app.logger.exception("Error serving media")
        return jsonify({"error": str(e)}), 500


@assets_bp.route("/api/media/<int:asset_id>/thumbnail")
@optional_auth
def serve_media_thumbnail(asset_id):
    try:
        asset = Asset.query.filter_by(id=asset_id, is_deleted=False).first()
        if not asset:
            return "Asset not found", 404

        # Check authorization
        if current_user.is_authenticated:
            if (
                asset.user_id
                and asset.user_id != current_user.id
                and not current_user.is_admin()
            ):
                return "Access denied", 403
        else:
            if asset.user_id is not None:
                return "Authentication required", 401

        # Get thumbnail size from query param (default: medium)
        size = request.args.get('size', 'medium')
        if size not in ['small', 'medium', 'large']:
            size = 'medium'

        # Try to serve thumbnail from MediaBlob
        media_blob = MediaBlob.query.filter_by(asset_id=asset_id).first()
        if media_blob and media_blob.thumbnail_data:
            response = make_response(media_blob.thumbnail_data)
            response.headers["Content-Type"] = media_blob.thumbnail_mime_type or "image/jpeg"
            response.headers["Cache-Control"] = "public, max-age=86400"
            response.headers["ETag"] = f'thumb-{asset.id}-{size}'
            response.headers["Content-Disposition"] = f'inline; filename="thumb_{asset.filename}"'
            return response

        # For images, generate optimized thumbnail
        if asset.file_type == "image":
            try:
                # Import thumbnail generator
                from utils.thumbnail_generator import generate_thumbnail, get_thumbnail_path

                # Check if file exists
                if not asset.file_path or not os.path.exists(asset.file_path):
                    # Fallback to full image from blob
                    if media_blob:
                        return serve_media_blob(asset_id)
                    return "Image file not found", 404

                # Check if thumbnail exists in cache
                thumbnail_path = get_thumbnail_path(asset.file_path, size)

                if not os.path.exists(thumbnail_path):
                    # Generate thumbnail
                    thumbnail_path = generate_thumbnail(asset.file_path, size)

                if thumbnail_path and os.path.exists(thumbnail_path):
                    # Serve cached thumbnail with aggressive caching
                    return send_file(
                        thumbnail_path,
                        mimetype='image/jpeg',
                        as_attachment=False,
                        download_name=f'thumb_{asset.filename}',
                        conditional=True,
                        etag=f'thumb-{asset.id}-{size}',
                        max_age=86400  # Cache for 24 hours
                    )
                else:
                    # Fallback to full image
                    current_app.logger.warning(f"Thumbnail generation failed for asset {asset_id}, serving full image")
                    return serve_media_blob(asset_id)

            except ImportError:
                # Thumbnail generator not available, serve full image
                current_app.logger.warning("Thumbnail generator not available, serving full image")
                return serve_media_blob(asset_id)
            except Exception as e:
                current_app.logger.warning(f"Error generating thumbnail for asset {asset_id}: {e}")
                return serve_media_blob(asset_id)

        # Try filesystem thumbnail path
        if asset.thumbnail_path and os.path.exists(asset.thumbnail_path):
            return send_file(
                asset.thumbnail_path,
                conditional=True,
                etag=f'thumb-{asset.id}',
                max_age=86400
            )

        # Default placeholder for videos
        default_thumbnail = "static/images/video-placeholder.png"
        if os.path.exists(default_thumbnail):
            return send_file(default_thumbnail, max_age=86400)

        return "No thumbnail available", 404
    except Exception as e:
        current_app.logger.warning(f"Error serving thumbnail for asset {asset_id}: {e}")
        return "Error serving thumbnail", 500


@assets_bp.route("/downloads/<path:asset_path>")
@optional_auth
def download_asset_legacy(asset_path):
    try:
        asset_id = None
        try:
            asset_id = int(asset_path)
        except ValueError:
            asset = (
                Asset.query.filter(
                    (Asset.filename == asset_path) | (Asset.file_path == asset_path)
                )
                .filter_by(is_deleted=False)
                .first()
            )
            if asset:
                asset_id = asset.id
            else:
                return "Asset not found", 404
        return serve_media_blob(asset_id)
    except Exception:
        current_app.logger.exception("Error in legacy download")
        return "Error downloading file", 500


@assets_bp.route("/api/media/<int:asset_id>/download")
@optional_auth
def download_media(asset_id):
    try:
        asset = Asset.query.get_or_404(asset_id)
        # Basic access control: allow owner or admin; public assets allowed
        if asset.user_id is not None:
            not_owner = asset.user_id != getattr(current_user, "id", None)
            not_admin = not getattr(current_user, "is_admin", lambda: False)()
            if not current_user.is_authenticated or (not_owner and not_admin):
                return jsonify({"error": "Access denied"}), 403
        media_blob = MediaBlob.query.filter_by(asset_id=asset_id).first()
        if media_blob:
            file_data = media_blob.get_file_data()
            mime_type = media_blob.mime_type
        else:
            if not asset.file_path or not os.path.exists(asset.file_path):
                return jsonify({"error": "Media file not found"}), 404
            with open(asset.file_path, "rb") as f:
                file_data = f.read()
            mime_type, _ = mimetypes.guess_type(asset.file_path)
            if not mime_type:
                mime_type = "application/octet-stream"
        should_watermark = False
        if current_user.is_authenticated:
            if (
                current_user.subscription_plan == "trial"
                or not current_user.is_subscribed()
            ):
                should_watermark = True
        else:
            should_watermark = True
        if should_watermark and asset.file_type == "image":
            file_data = watermark_overlay.apply_watermark_to_image_bytes(file_data)
        response = make_response(file_data)
        response.headers["Content-Type"] = mime_type
        response.headers["Content-Disposition"] = (
            f'attachment; filename="{asset.filename}"'
        )
        response.headers["Cache-Control"] = "private, max-age=3600"
        response.headers["ETag"] = f'"{asset.id}-{asset.file_size}"'
        if should_watermark:
            response.headers["X-Watermarked"] = "true"
        return response
    except Exception as e:
        current_app.logger.error(f"Download error: {e}")
        return jsonify({"error": "Download failed"}), 500


@assets_bp.route("/api/media/bulk-download", methods=["POST"])
@optional_auth
def bulk_download_media():
    """Download multiple assets as a ZIP file using streaming"""
    import tempfile
    import time

    # Security limits
    MAX_BULK_DOWNLOAD_COUNT = 100
    MAX_TOTAL_DOWNLOAD_SIZE = 20 * 1024 * 1024 * 1024  # 20GB (increased for video files)
    MAX_SINGLE_FILE_SIZE = 1024 * 1024 * 1024  # 1GB (increased to support large videos)

    start_time = time.time()

    # Generate unique job ID for progress tracking
    job_id = str(uuid.uuid4())

    try:
        data = request.get_json()
        asset_ids = data.get('asset_ids', [])
        select_all_used = data.get('select_all_used', False)

        if not asset_ids:
            return jsonify({"error": "No assets specified"}), 400

        # Initialize progress tracking
        download_progress[job_id] = {
            'total': len(asset_ids),
            'processed': 0,
            'status': 'preparing',
            'message': 'Preparing download...'
        }

        # Bypass limit if Select All was explicitly used
        if not select_all_used and len(asset_ids) > MAX_BULK_DOWNLOAD_COUNT:
            return jsonify({
                "error": f"Too many assets requested. Maximum: {MAX_BULK_DOWNLOAD_COUNT}. Use 'Select All' to download all files."
            }), 400

        if select_all_used:
            current_app.logger.info(f"Select All used - bypassing {MAX_BULK_DOWNLOAD_COUNT} file limit")

        current_app.logger.info(
            f"Bulk download: user={getattr(current_user, 'id', 'anonymous')}, "
            f"ip={request.remote_addr}, count={len(asset_ids)}"
        )

        # Fetch all assets and blobs at once (fix N+1 query problem)
        assets = Asset.query.filter(Asset.id.in_(asset_ids)).all()
        asset_map = {a.id: a for a in assets}

        blobs = MediaBlob.query.filter(MediaBlob.asset_id.in_(asset_ids)).all()
        blob_map = {b.asset_id: b for b in blobs}

        # Create secure temporary directory and file
        temp_dir = tempfile.mkdtemp(prefix='bulk_download_')
        temp_path = os.path.join(temp_dir, f'assets_{secrets.token_hex(8)}.zip')

        try:
            with zipfile.ZipFile(temp_path, 'w', zipfile.ZIP_DEFLATED) as zip_file:
                added_count = 0
                failed_count = 0
                total_size = 0

                for asset_id in asset_ids:
                    try:
                        # Validate asset_id
                        try:
                            asset_id = int(asset_id)
                        except (ValueError, TypeError):
                            current_app.logger.warning(f"Invalid asset_id: {asset_id}")
                            failed_count += 1
                            continue

                        asset = asset_map.get(asset_id)
                        if not asset:
                            current_app.logger.warning(f"Asset {asset_id} not found")
                            failed_count += 1
                            continue

                        # Access control
                        if asset.user_id is not None:
                            not_owner = asset.user_id != getattr(current_user, "id", None)
                            not_admin = not getattr(current_user, "is_admin", lambda: False)()
                            if not current_user.is_authenticated or (not_owner and not_admin):
                                current_app.logger.warning(f"Access denied for asset {asset_id}")
                                failed_count += 1
                                continue

                        # Size checks
                        file_size = asset.file_size or 0
                        if file_size > MAX_SINGLE_FILE_SIZE:
                            current_app.logger.warning(f"File too large: {asset_id} ({file_size} bytes)")
                            failed_count += 1
                            continue

                        total_size += file_size
                        if total_size > MAX_TOTAL_DOWNLOAD_SIZE:
                            current_app.logger.warning(f"Total size limit exceeded at asset {asset_id}")
                            break

                        # Get file data
                        media_blob = blob_map.get(asset_id)
                        if media_blob:
                            file_data = media_blob.get_file_data()
                        else:
                            if not asset.file_path or not os.path.exists(asset.file_path):
                                current_app.logger.warning(f"File not found for asset {asset_id}")
                                failed_count += 1
                                continue

                            with open(asset.file_path, "rb") as f:
                                file_data = f.read()

                        # Sanitize filename to prevent path traversal
                        base_filename = asset.filename or f"asset_{asset_id}"
                        base_filename = os.path.basename(base_filename)  # Remove path components
                        base_filename = base_filename.replace('..', '')   # Remove parent refs
                        base_filename = ''.join(c for c in base_filename if c.isprintable() and c not in '"\\')
                        base_filename = base_filename[:200]  # Limit length
                        if not base_filename:
                            base_filename = f"asset_{asset_id}"

                        zip_filename = base_filename

                        # Handle duplicates
                        counter = 1
                        while zip_filename in zip_file.namelist():
                            name, ext = os.path.splitext(base_filename)
                            zip_filename = f"{name}_{counter}{ext}"
                            counter += 1

                        # Add file to ZIP
                        zip_file.writestr(zip_filename, file_data)
                        added_count += 1

                        # Update progress
                        download_progress[job_id] = {
                            'total': len(asset_ids),
                            'processed': added_count + failed_count,
                            'added': added_count,
                            'failed': failed_count,
                            'status': 'processing',
                            'message': f'Adding files to ZIP... ({added_count}/{len(asset_ids)})'
                        }

                    except (IOError, OSError) as e:
                        current_app.logger.error(f"I/O error for asset {asset_id}: {e}")
                        failed_count += 1
                    except Exception as e:
                        current_app.logger.error(f"Error adding asset {asset_id} to ZIP: {e}")
                        failed_count += 1

            # Update progress to complete
            download_progress[job_id] = {
                'total': len(asset_ids),
                'processed': len(asset_ids),
                'added': added_count,
                'failed': failed_count,
                'status': 'complete' if added_count > 0 else 'failed',
                'message': f'ZIP created: {added_count} files' if added_count > 0 else 'No files added'
            }

            if added_count == 0:
                os.unlink(temp_path)
                os.rmdir(temp_dir)
                # Clean up progress
                download_progress.pop(job_id, None)
                return jsonify({"error": "No files could be added to download"}), 404

            # Create filename with timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            zip_filename = f"assets_download_{timestamp}.zip"

            duration = time.time() - start_time
            current_app.logger.info(
                f"Bulk download complete: user={getattr(current_user, 'id', 'anonymous')}, "
                f"added={added_count}, failed={failed_count}, size={total_size} bytes, "
                f"duration={duration:.2f}s"
            )

            # Stream the file and delete after
            def generate():
                try:
                    with open(temp_path, 'rb') as f:
                        while True:
                            chunk = f.read(8192)
                            if not chunk:
                                break
                            yield chunk
                finally:
                    # Clean up temp file and directory
                    try:
                        os.unlink(temp_path)
                        os.rmdir(temp_dir)
                    except Exception as e:
                        current_app.logger.error(f"Failed to cleanup temp files: {e}")

            # Use RFC 5987 encoding for filename to prevent header injection
            encoded_filename = urllib.parse.quote(zip_filename.encode('utf-8'))

            response = Response(generate(), mimetype='application/zip')
            response.headers['Content-Disposition'] = f"attachment; filename*=UTF-8''{encoded_filename}"
            response.headers['X-Files-Added'] = str(added_count)
            response.headers['X-Files-Failed'] = str(failed_count)
            response.headers['X-Job-ID'] = job_id  # Send job_id for progress tracking

            # Clean up progress after a delay (30 seconds)
            import threading
            def cleanup_progress():
                import time
                time.sleep(30)
                download_progress.pop(job_id, None)
            threading.Thread(target=cleanup_progress, daemon=True).start()

            return response

        except Exception as e:
            # Clean up on error
            try:
                if os.path.exists(temp_path):
                    os.unlink(temp_path)
                if os.path.exists(temp_dir):
                    os.rmdir(temp_dir)
            except Exception as cleanup_error:
                current_app.logger.error(f"Cleanup error: {cleanup_error}")
            raise

    except Exception as e:
        current_app.logger.error(f"Bulk download error: {e}")
        # Clean up progress on error
        download_progress.pop(job_id, None)
        return jsonify({"error": "Bulk download failed", "details": str(e)}), 500


@assets_bp.route("/api/media/bulk-download/progress/<job_id>", methods=["GET"])
@optional_auth
def get_download_progress(job_id):
    """Get progress of a bulk download job"""
    progress = download_progress.get(job_id)

    if not progress:
        return jsonify({
            "error": "Job not found",
            "status": "unknown"
        }), 404

    return jsonify(progress)


