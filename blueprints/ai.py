from flask import Blueprint, current_app, jsonify, request
from flask_login import current_user, login_required

from auth import optional_auth

ai_bp = Blueprint("ai", __name__)


@ai_bp.route("/api/ai-assistant", methods=["POST"])
@login_required
def ai_assistant_chat():
    try:
        from enhanced_ai_service import get_ai_service

        data = request.json or {}
        message = data.get("message", "").strip()
        api_key = data.get("api_key", "").strip()
        if not message:
            return jsonify({"success": False, "error": "Message is required"})
        ai_service = get_ai_service()
        response = ai_service.process_message(
            message=message,
            user_id=current_user.id,
            user_api_key=api_key,
        )
        return jsonify(response)
    except ImportError:
        try:
            from real_ai_assistant import get_ai_service

            ai_service = get_ai_service()
            response = ai_service.process_message(
                message=message,
                user_id=current_user.id,
                user_api_key=api_key,
            )
            return jsonify(response)
        except Exception as e:
            current_app.logger.error(f"AI assistant fallback error: {e}")
            return jsonify(
                {
                    "success": False,
                    "error": "AI assistant temporarily unavailable",
                    "message": (
                        "I'm having trouble right now. You can still use basic "
                        "commands like 'search for cats' or 'show my assets'."
                    ),
                }
            )
    except Exception as e:
        current_app.logger.error(f"AI assistant error: {e}")
        return jsonify(
            {
                "success": False,
                "error": "AI assistant temporarily unavailable",
                "message": (
                    "I'm having trouble right now. You can still use basic "
                    "commands like 'search for cats' or 'show my assets'."
                ),
            }
        )


@ai_bp.route("/api/ai-assistant/status", methods=["GET"])
@login_required
def ai_assistant_status():
    try:
        from enhanced_ai_service import get_ai_service

        user_api_key = request.headers.get("X-OpenAI-API-Key", "").strip()
        ai_service = get_ai_service()
        access = ai_service.check_access(user_api_key)
        access["user"] = {
            "email": current_user.email,
            "subscription_tier": getattr(current_user, "subscription_tier", "trial"),
            "is_max_subscriber": getattr(current_user, "subscription_tier", "")
            == "ultra",
        }
        return jsonify({"success": True, **access})
    except Exception as e:
        current_app.logger.error(f"AI status check error: {e}")
        return jsonify(
            {"success": False, "error": "Failed to check AI assistant status"}
        )


@ai_bp.route("/api/ai-optimize-query", methods=["POST"])
@optional_auth
def ai_optimize_query():
    try:
        from ai_assistant import ai_assistant

        data = request.get_json() or {}
        query = data.get("query", "").strip()
        search_type = data.get("search_type", "comprehensive")
        filters = data.get("filters", {})
        if not query:
            return jsonify({"success": False, "error": "Query is required"}), 400
        optimized = ai_assistant.optimize_query(query, search_type, filters)
        return jsonify(
            {
                "success": True,
                "optimized_query": optimized["query"],
                "optimization_score": optimized["score"],
                "suggestions": optimized["suggestions"],
                "explanation": optimized["explanation"],
            }
        )
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})
