from flask import Flask, jsonify, request
from flask_cors import CORS

from services.search import search_documents
from services.context_builder import build_context
from services.llm import generate_answer
from services.judgment_retrieval import search_judgments
from routes.judgment_routes import judgment_bp



# ============================================================
# LEGAL MIND AI - FLASK BACKEND
# ============================================================

app = Flask(__name__)

app.register_blueprint(judgment_bp)

CORS(app)


# ============================================================
# HEALTH CHECK
# ============================================================

@app.route("/api/health", methods=["GET"])
def health():

    return jsonify({
        "status": "success",
        "message": "Legal Mind AI backend is running"
    })


# ============================================================
# CHAT API
# ============================================================

# ============================================================
# JUDGMENT SEARCH API
# ============================================================

@app.route("/api/judgments/search", methods=["GET"])
def judgment_search():

    try:

        query = (
            request.args.get("q") or ""
        ).strip()

        if not query:

            return jsonify({
                "status": "success",
                "query": "",
                "count": 0,
                "results": []
            })

        print("\n")
        print("=" * 80)
        print("LEGAL MIND AI - JUDGMENT SEARCH")
        print("=" * 80)

        print("\nSearch query:")
        print(query)

        results = search_judgments(
            query
        )

        print(
            f"\n✓ Found {len(results)} judgments."
        )

        return jsonify({
            "status": "success",
            "query": query,
            "count": len(results),
            "results": results
        })

    except Exception as error:

        print("\nJUDGMENT SEARCH ERROR:")
        print(str(error))

        return jsonify({
            "status": "error",
            "message": "Failed to search judgments.",
            "details": str(error)
        }), 500

@app.route("/api/chat", methods=["POST"])
def chat():

    try:

        # ----------------------------------------------------
        # GET REQUEST DATA
        # ----------------------------------------------------

        data = request.get_json(silent=True)

        if not data:

            return jsonify({
                "status": "error",
                "message": "Request body is required."
            }), 400

        question = (
            data.get("question") or ""
        ).strip()

        if not question:

            return jsonify({
                "status": "error",
                "message": "Question is required."
            }), 400

        print("\n")
        print("=" * 80)
        print("LEGAL MIND AI - CHAT REQUEST")
        print("=" * 80)

        print("\nQuestion:")
        print(question)

        # ----------------------------------------------------
        # STEP 1: SEARCH LEGAL DATABASE
        # ----------------------------------------------------

        print("\nSearching legal judgments...")

        results = search_documents(
            question,
            top_k=5,
            context_chunks=1
        )

        print(
            f"✓ Retrieved {len(results)} reranked results."
        )

        # ----------------------------------------------------
        # STEP 2: BUILD RAG CONTEXT
        # ----------------------------------------------------

        print("\nBuilding RAG context...")

        context = build_context(
            results,
            max_results=5
        )

        print("✓ RAG context built.")

        # ----------------------------------------------------
        # STEP 3: GENERATE ANSWER
        # ----------------------------------------------------

        print("\nGenerating answer with Qwen3...")

        answer = generate_answer(
            context,
            question
        )

        print("✓ Answer generated.")

        # ----------------------------------------------------
        # STEP 4: BUILD SOURCES
        # ----------------------------------------------------

        sources = []

        for index, result in enumerate(
            results,
            start=1
        ):

            document_id = result.get(
                "document_id"
            )

            # Convert document ID into readable case name

            case_name = (
                document_id.replace("_", " ")
                if document_id
                else "Unknown Case"
            )

            # Remove final dataset suffix

            if case_name.endswith(" 1"):
                case_name = case_name[:-2]

            sources.append({

                "source_number": index,

                "document_id": document_id,

                "case_name": case_name,

                "matched_chunk": result.get(
                    "matched_chunk"
                ),

                "similarity": result.get(
                    "similarity"
                ),

                "rerank_score": result.get(
                    "rerank_score"
                ),

                "context_start": result.get(
                    "context_start"
                ),

                "context_end": result.get(
                    "context_end"
                )

            })

        # ----------------------------------------------------
        # STEP 5: RETURN RESPONSE
        # ----------------------------------------------------

        response = {

            "status": "success",

            "question": question,

            "answer": answer,

            "sources": sources

        }

        print("\n")
        print("=" * 80)
        print("CHAT RESPONSE READY")
        print("=" * 80)

        return jsonify(response)

    except Exception as error:

        print("\n")
        print("=" * 80)
        print("CHAT API ERROR")
        print("=" * 80)

        print(
            str(error)
        )

        return jsonify({

            "status": "error",

            "message":
                "Failed to generate legal answer.",

            "details":
                str(error)

        }), 500


# ============================================================
# SHOW REGISTERED ROUTES
# ============================================================

print("\n")
print("=" * 80)
print("REGISTERED FLASK ROUTES")
print("=" * 80)

for route in app.url_map.iter_rules():

    print(
        route,
        "->",
        route.endpoint,
        "->",
        sorted(route.methods)
    )

print("=" * 80)


# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":

    app.run(
        host="127.0.0.1",
        port=5000,
        debug=False,
        use_reloader=False
    )