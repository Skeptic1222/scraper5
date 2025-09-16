"""
Assets API Blueprint - SQL Server-backed asset management
"""
from __future__ import annotations

import os
from typing import Any, Dict, Optional

from flask import Blueprint, jsonify, request
from flask_login import current_user

from models import Asset, MediaBlob, User, db

assets_bp = Blueprint('assets', __name__)


def _is_admin() -> bool:
    try:
        return bool(current_user.is_authenticated and current_user.is_admin())
    except Exception:
        return False


def _asset_to_api(a: Asset) -> Dict[str, Any]:
    return {
        'name': a.filename,
        'filename': a.filename,
        'path': a.file_path,
        'size': a.file_size or 0,
        'file_size': a.file_size or 0,
        'modified': a.downloaded_at,
        'downloaded_at': a.downloaded_at,
        'type': a.file_type,
        'file_type': a.file_type,
        'extension': a.file_extension,
        'file_extension': a.file_extension,
        'id': a.id,
        'source': a.source_name or 'unknown',
        'source_name': a.source_name or 'unknown',
        'source_url': a.source_url or '',
        'thumbnail_path': a.thumbnail_path or None,
        'user_id': a.user_id,
        'user_email': None,  # populated for admin only in list
        'job_id': a.job_id,
        'url': f"/serve/{a.id}",
    }


@assets_bp.route('/')
@assets_bp.route('')
def list_assets():
    """List assets for the current user (or all for admin)."""
    try:
        file_type = request.args.get('type')  # 'image' or 'video'
        page = int(request.args.get('page', 1))
        limit = int(request.args.get('limit', 100))
        offset = (page - 1) * limit
        admin_view = request.args.get('admin', 'false').lower() == 'true'

        q = Asset.query.filter_by(is_deleted=False)
        scope_user_id: Optional[int] = None

        if current_user.is_authenticated:
            if admin_view and _is_admin():
                scope_user_id = None  # all users
            elif _is_admin():
                scope_user_id = None  # admin sees all by default
            else:
                scope_user_id = current_user.id
                q = q.filter(Asset.user_id == scope_user_id)
        else:
            # Guests: return empty set to avoid exposing others' assets
            return jsonify({'success': True, 'assets': [], 'counts': {'all': 0, 'images': 0, 'videos': 0}, 'total': 0})

        if file_type in ('image', 'video'):
            q = q.filter(Asset.file_type == file_type)

        total_all = q.count()
        assets = (
            q.order_by(Asset.downloaded_at.desc())
             .offset(offset)
             .limit(limit)
             .all()
        )

        # Counts per type for the scoped user/admin
        base = Asset.query.filter_by(is_deleted=False)
        if scope_user_id is not None:
            base = base.filter(Asset.user_id == scope_user_id)
        images_count = base.filter(Asset.file_type == 'image').count()
        videos_count = base.filter(Asset.file_type == 'video').count()

        items = []
        for a in assets:
            data = _asset_to_api(a)
            if _is_admin() and a.user_id:
                u = db.session.get(User, a.user_id)
                data['user_email'] = u.email if u else None
            items.append(data)

        return jsonify({
            'success': True,
            'assets': items,
            'counts': {
                'all': total_all,
                'images': images_count,
                'videos': videos_count
            },
            'total': len(items)
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e), 'assets': [], 'counts': {'all': 0, 'images': 0, 'videos': 0}}), 500


@assets_bp.route('/<int:asset_id>')
def get_asset(asset_id: int):
    """Get an individual asset if the user may access it."""
    a = Asset.query.filter_by(id=asset_id, is_deleted=False).first()
    if not a:
        return jsonify({'success': False, 'error': 'Asset not found'}), 404

    if not _is_admin():
        if not current_user.is_authenticated or (a.user_id and a.user_id != current_user.id):
            return jsonify({'success': False, 'error': 'Forbidden'}), 403

    return jsonify({'success': True, 'asset': _asset_to_api(a)})


@assets_bp.route('/<int:asset_id>', methods=['DELETE'])
def delete_asset(asset_id: int):
    """Delete an asset (owner or admin)."""
    if not current_user.is_authenticated:
        return jsonify({'success': False, 'error': 'Authentication required'}), 401

    a = Asset.query.filter_by(id=asset_id, is_deleted=False).first()
    if not a:
        return jsonify({'success': False, 'error': 'Asset not found'}), 404

    if not _is_admin() and a.user_id != current_user.id:
        return jsonify({'success': False, 'error': 'Forbidden'}), 403

    try:
        # Remove MediaBlob if present
        try:
            blob = MediaBlob.query.filter_by(asset_id=asset_id).first()
            if blob:
                db.session.delete(blob)
        except Exception:
            # Continue even if blob deletion fails; transaction rollback below
            pass

        # Remove file from filesystem (best-effort)
        file_removed = False
        if a.file_path:
            try:
                # Only remove if file exists and within downloads or known safe path
                path = a.file_path
                if os.path.isabs(path):
                    # Allow absolute; ensure it exists
                    if os.path.exists(path):
                        os.remove(path)
                        file_removed = True
                else:
                    abs_path = os.path.abspath(path)
                    if os.path.exists(abs_path):
                        os.remove(abs_path)
                        file_removed = True
            except Exception:
                # Non-fatal
                pass

        # Soft-delete record; the UI expects it to disappear
        a.is_deleted = True
        db.session.commit()
        return jsonify({'success': True, 'message': 'Asset deleted', 'file_removed': file_removed})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500


@assets_bp.route('/cleanup-missing', methods=['POST'])
def cleanup_missing_assets():
    """Admin: mark assets whose files are missing as deleted and remove blobs.

    Returns a count of updated items. Requires admin.
    """
    if not _is_admin():
        return jsonify({'success': False, 'error': 'Admin required'}), 403

    try:
        updated = 0
        assets = Asset.query.filter_by(is_deleted=False).all()
        for a in assets:
            if a.file_path and not os.path.exists(a.file_path):
                # Remove any blob and mark deleted
                blob = MediaBlob.query.filter_by(asset_id=a.id).first()
                if blob:
                    db.session.delete(blob)
                a.is_deleted = True
                updated += 1
        db.session.commit()
        return jsonify({'success': True, 'updated': updated})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500


@assets_bp.route('/bulk-delete', methods=['POST'])
def bulk_delete_assets():
    """Bulk delete assets by IDs. Admin may delete any; users only their own."""
    if not current_user.is_authenticated:
        return jsonify({'success': False, 'error': 'Authentication required'}), 401

    try:
        data = request.get_json(silent=True) or {}
        ids = data.get('ids', [])
        if not isinstance(ids, list) or not ids:
            return jsonify({'success': False, 'error': 'No asset IDs provided'}), 400

        is_admin = _is_admin()
        deleted = 0
        file_removed_count = 0

        for asset_id in ids:
            a = Asset.query.filter_by(id=asset_id, is_deleted=False).first()
            if not a:
                continue
            if (not is_admin) and a.user_id != current_user.id:
                continue

            # Delete blob
            blob = MediaBlob.query.filter_by(asset_id=a.id).first()
            if blob:
                db.session.delete(blob)

            # Delete file
            if a.file_path and os.path.exists(a.file_path):
                try:
                    os.remove(a.file_path)
                    file_removed_count += 1
                except Exception:
                    pass

            a.is_deleted = True
            deleted += 1

        db.session.commit()
        return jsonify({'success': True, 'deleted': deleted, 'files_removed': file_removed_count})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500
