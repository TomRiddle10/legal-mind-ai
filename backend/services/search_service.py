from flask import Blueprint, request, jsonify

from services.judgment_retrieval import search_judgments


judgment_bp = Blueprint(
    "judgments",
    __name__,
    url_prefix="/api/judgments"
)


@judgment_bp.route("/search", methods=["GET"])
def search():

    query = request.args.get("q", "").strip()

    page = request.args.get("page", 1)

    limit = request.args.get("limit", 20)

    try:

        result = search_judgments(
            query=query,
            page=page,
            limit=limit
        )

        return jsonify(result)

    except Exception as e:

        print("Search error:", e)

        return jsonify({
            "error": "Failed to search judgments",
            "message": str(e)
        }), 500