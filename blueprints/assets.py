import mimetypes
import os

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
                    "url": f"/serve/{asset_data['id']}",
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
@user_or_admin_required
def bulk_delete_assets():
    try:
        data = request.get_json() or {}
        asset_ids = data.get("asset_ids", [])
        if not asset_ids:
            return jsonify({"success": False, "error": "No asset IDs provided"}), 400
        deleted_count = db_asset_manager.bulk_delete_assets(
            asset_ids=asset_ids,
            user_id=current_user.id if not current_user.is_admin() else None,
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
        if asset.file_type == "image":
            return serve_media_blob(asset_id)
        if asset.thumbnail_path and os.path.exists(asset.thumbnail_path):
            return send_file(asset.thumbnail_path)
        default_thumbnail = "static/images/video-placeholder.png"
        if os.path.exists(default_thumbnail):
            return send_file(default_thumbnail)
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
