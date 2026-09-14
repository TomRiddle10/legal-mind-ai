from flask import Blueprint, request, jsonify

from services.search import search_documents
from services.llm import generate_answer


# ============================================================
# CHAT BLUEPRINT
# ============================================================

chat_bp = Blueprint(
    "chat",
    __name__,
    url_prefix="/api"
)


# ============================================================
# CHAT API
# ============================================================

@chat_bp.route("/chat", methods=["POST"])
def chat():

    try:

        # ====================================================
        # GET REQUEST DATA
        # ====================================================

        data = request.get_json()

        if not data:

            return jsonify({
                "error": "Request body is required."
            }), 400


        question = (
            data.get("question") or ""
        ).strip()


        if not question:

            return jsonify({
                "error": "Question is required."
            }), 400


        print("\n")
        print("=" * 70)
        print("LEGAL MIND AI - CHAT REQUEST")
        print("=" * 70)

        print("\nQuestion:")
        print(question)


        # ====================================================
        # STEP 1
        # RETRIEVE LEGAL DOCUMENTS
        # ====================================================

        print("\nSearching legal judgments...")


        results = search_documents(
            question,
            top_k=5,
            context_chunks=1
        )


        if not results:

            print(
                "\nNo relevant judgments found."
            )

            return jsonify({

                "question": question,

                "answer": (
                    "The provided judgments do not "
                    "contain enough information to "
                    "answer this question."
                ),

                "sources": []

            })


        print(
            f"\n✓ Retrieved {len(results)} sources."
        )


        # ====================================================
        # STEP 2
        # BUILD LEGAL CONTEXT
        # ====================================================

        context_parts = []

        sources = []


        for index, result in enumerate(
            results,
            start=1
        ):

            document_id = result.get(
                "document_id"
            )

            matched_chunk = result.get(
                "matched_chunk"
            )

            similarity = result.get(
                "similarity"
            )

            legal_text = result.get(
                "text",
                ""
            )


            # ------------------------------------------------
            # CONTEXT FOR QWEN
            # ------------------------------------------------

            context_parts.append(
                f"""
SOURCE {index}

CASE:
{document_id}

MATCHED CHUNK:
{matched_chunk}

SIMILARITY:
{similarity}

LEGAL TEXT:
{legal_text}

--------------------------------------------------
"""
            )


            # ------------------------------------------------
            # SOURCE FOR FRONTEND
            # ------------------------------------------------

            sources.append({

                "source_number":
                    index,

                "id":
                    document_id,

                "case_name":
                    document_id,

                "matched_chunk":
                    matched_chunk,

                "similarity":
                    similarity,

                "text":
                    legal_text

            })


        legal_context = "\n".join(
            context_parts
        )


        print(
            "\n✓ Legal context prepared."
        )


        # ====================================================
        # STEP 3
        # SEND CONTEXT TO QWEN3
        # ====================================================

        print(
            "\nGenerating answer using Qwen3..."
        )


        # IMPORTANT:
        #
        # Your llm.py function is:
        #
        # generate_answer(context, question)
        #
        # Therefore context comes FIRST.

        answer = generate_answer(
            legal_context,
            question
        )


        print(
            "\n✓ Answer generated."
        )


        # ====================================================
        # STEP 4
        # RETURN RESPONSE
        # ====================================================

        response = {

            "question":
                question,

            "answer":
                answer,

            "sources":
                sources

        }


        print("\n")
        print("=" * 70)
        print("CHAT RESPONSE READY")
        print("=" * 70)


        return jsonify(
            response
        )


    except Exception as error:

        print("\n")
        print("=" * 70)
        print("CHAT API ERROR")
        print("=" * 70)

        print(error)


        return jsonify({

            "error":
                "Failed to generate legal answer.",

            "details":
                str(error)

        }), 500