from flask import Blueprint, current_app, jsonify, request
from flask_login import current_user

from auth import optional_auth
from sources_data import get_content_sources
from subscription import TRIAL_SOURCES, check_subscription_status, get_user_sources

sources_bp = Blueprint("sources", __name__)


@sources_bp.route("/api/sources")
@optional_auth
def get_sources():
    """Get available content sources with categories and safe search filtering."""
    try:
        current_app.logger.info(
            "[SOURCES API] Loading sources for user: %s",
            current_user.email if current_user.is_authenticated else "Guest",
        )
        sources_data = get_content_sources()
        safe_search = request.args.get("safe_search", "true").lower() == "true"
        current_app.logger.info("[SOURCES API] Safe search enabled: %s", safe_search)

        # Get all source IDs from sources_data
        all_source_ids = []
        for category_sources in sources_data.values():
            if isinstance(category_sources, list):
                for source in category_sources:
                    if isinstance(source, dict) and 'id' in source:
                        all_source_ids.append(source['id'])
        
        allowed_sources = []
        try:
            if current_user.is_authenticated:
                check_subscription_status(current_user)
                allowed_sources = get_user_sources(current_user)
                if current_user.can_use_nsfw() and current_user.is_nsfw_enabled:
                    safe_search = False
            else:
                # For guest users, show ALL sources (78+) except adult content
                allowed_sources = all_source_ids  # Show all sources for guests
        except Exception as e:
            current_app.logger.warning(
                "[SOURCES API] Error getting user sources: %s", e
            )
            # On error, still show all sources
            allowed_sources = all_source_ids

        categorized = {
            "Search Engines": [],
            "Image Galleries": [],
            "Stock Photos": [],
            "Social Media": [],
            "Video Platforms": [],
            "Art Platforms": [],
            "Adult Content": [],
            "News Media": [],
            "E-Commerce": [],
            "Entertainment": [],
            "Academic": [],
            "Tech Forums": [],
        }

        category_mapping = {
            "search_engines": "Search Engines",
            "galleries": "Image Galleries",
            "stock_photos": "Stock Photos",
            "social_media": "Social Media",
            "video_platforms": "Video Platforms",
            "art_platforms": "Art Platforms",
            "adult_content": "Adult Content",
            "news_media": "News Media",
            "e_commerce": "E-Commerce",
            "entertainment": "Entertainment",
            "academic": "Academic",
            "tech_forums": "Tech Forums",
        }

        for key, source_list in sources_data.items():
            display_name = category_mapping.get(key, key.replace("_", " ").title())
            for source in source_list:
                if source["id"] in allowed_sources:
                    if safe_search and source.get("nsfw", False):
                        continue
                    categorized.setdefault(display_name, []).append(source)

        sources_list = []
        for category_name, sources in categorized.items():
            if sources:
                sources_list.append({"category": category_name, "sources": sources})
        sources_list.sort(key=lambda x: len(x["sources"]), reverse=True)

        subscription_info = {
            "is_subscribed": False,
            "plan": "trial",
            "credits": 50,
            "can_use_nsfw": False,
        }

        if current_user.is_authenticated:
            subscription_info = {
                "is_subscribed": current_user.is_subscribed(),
                "plan": current_user.subscription_plan,
                "credits": current_user.credits,
                "can_use_nsfw": current_user.can_use_nsfw(),
            }
        else:
            subscription_info["credits"] = 50

        return jsonify(
            {
                "success": True,
                "sources": sources_list,
                "safe_search_enabled": safe_search,
                "adult_sources_available": not safe_search,
                "user_authenticated": current_user.is_authenticated,
                "subscription_info": subscription_info,
                "total_categories": len(sources_list),
                "total_sources": sum(len(cat["sources"]) for cat in sources_list),
            }
        )
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})
