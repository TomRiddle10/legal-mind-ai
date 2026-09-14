from flask import Blueprint, request, jsonify

from services.judgment_retrieval import search_judgments
from services.judgment_rag import (
    search_judgment_chunks,
    get_judgment_chunks,
    build_judgment_context
)
from services.llm import (
    generate_judgment_answer,
    generate_summary
)
from services.database import get_connection


judgment_bp = Blueprint(
    "judgments",
    __name__,
    url_prefix="/api/judgments"
)


# ============================================================
# SEARCH JUDGMENTS
# ============================================================

@judgment_bp.route("/search", methods=["GET"])
def search():

    query = request.args.get(
        "q",
        ""
    ).strip()

    page = request.args.get(
        "page",
        1
    )

    limit = request.args.get(
        "limit",
        20
    )

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


# ============================================================
# GET SINGLE JUDGMENT
# ============================================================

@judgment_bp.route(
    "/<document_id>",
    methods=["GET"]
)
def get_judgment(document_id):

    conn = get_connection()

    try:

        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT
                document_id,
                filename,
                case_name,
                petitioner,
                respondent,
                judges,
                court,
                judgment_date,
                case_number,
                citations,
                legal_topics,
                acts,
                headnote,
                judgment,
                verdict
            FROM documents_v2
            WHERE document_id = %s
            """,
            (document_id,)
        )

        row = cursor.fetchone()

        if not row:

            return jsonify({
                "status": "error",
                "message": "Judgment not found."
            }), 404

        (
            document_id,
            filename,
            case_name,
            petitioner,
            respondent,
            judges,
            court,
            judgment_date,
            case_number,
            citations,
            legal_topics,
            acts,
            headnote,
            judgment,
            verdict
        ) = row

        return jsonify({

            "status": "success",

            "judgment": {

                "document_id": document_id,

                "filename": filename,

                "case_name": case_name,

                "petitioner": petitioner,

                "respondent": respondent,

                "judges": judges or [],

                "court": court,

                "judgment_date": (
                    judgment_date.isoformat()
                    if judgment_date
                    else None
                ),

                "case_number": case_number,

                "citations": citations or [],

                "legal_topics": legal_topics or [],

                "acts": acts or [],

                "headnote": headnote,

                "judgment": judgment,

                "verdict": verdict

            }

        })

    except Exception as e:

        print("Get judgment error:", e)

        return jsonify({
            "status": "error",
            "message": "Failed to retrieve judgment.",
            "details": str(e)
        }), 500

    finally:

        conn.close()


# ============================================================
# ASK QUESTION ABOUT ONE JUDGMENT
# ============================================================

@judgment_bp.route(
    "/<document_id>/ask",
    methods=["POST"]
)
def ask_judgment(document_id):

    try:

        data = request.get_json(
            silent=True
        )

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

        # ====================================================
        # GET CASE NAME
        # ====================================================

        conn = get_connection()

        try:

            cursor = conn.cursor()

            cursor.execute(
                """
                SELECT case_name
                FROM documents_v2
                WHERE document_id = %s
                """,
                (document_id,)
            )

            row = cursor.fetchone()

        finally:

            conn.close()

        if not row:

            return jsonify({
                "status": "error",
                "message": "Judgment not found."
            }), 404

        case_name = row[0] or document_id

        # ====================================================
        # JUDGMENT-SPECIFIC RAG
        # ====================================================

        retrieved_chunks = search_judgment_chunks(
            document_id=document_id,
            query=question,
            top_k=5,
            context_chunks=1
        )

        if not retrieved_chunks:

            return jsonify({
                "status": "success",
                "document_id": document_id,
                "case_name": case_name,
                "question": question,
                "answer": (
                    "No relevant portions of this judgment "
                    "were found for the question."
                ),
                "sources": []
            })

        # ====================================================
        # BUILD LLM CONTEXT
        # ====================================================

        context_parts = []

        for index, chunk in enumerate(
            retrieved_chunks,
            start=1
        ):

            context_parts.append(
                f"""
[SOURCE {index}]
[CHUNK {chunk['matched_chunk']}]
[CHUNKS {chunk['context_start']} - {chunk['context_end']}]

{chunk['text']}
"""
            )

        context = "\n\n".join(
            context_parts
        )

        # ====================================================
        # GENERATE ANSWER
        # ====================================================

        answer = generate_judgment_answer(
            context=context,
            question=question,
            case_name=case_name
        )

        # ====================================================
        # REFERENCES
        # ====================================================

        sources = []

        for index, chunk in enumerate(
            retrieved_chunks,
            start=1
        ):

            sources.append({

                "source_number": index,

                "chunk_id": chunk["id"],

                "chunk_index": chunk["matched_chunk"],

                "context_start": chunk["context_start"],

                "context_end": chunk["context_end"],

                "similarity": chunk["similarity"],

                "rerank_score": chunk["rerank_score"],

                "text": chunk["text"]

            })

        return jsonify({

            "status": "success",

            "document_id": document_id,

            "case_name": case_name,

            "question": question,

            "answer": answer,

            "sources": sources

        })

    except Exception as e:

        print("Judgment Ask error:", e)

        return jsonify({

            "status": "error",

            "message": "Failed to answer question.",

            "details": str(e)

        }), 500


# ============================================================
# SUMMARIZE ONE JUDGMENT
# ============================================================

@judgment_bp.route(
    "/<document_id>/summarize",
    methods=["POST"]
)
def summarize_judgment(document_id):

    try:

        # ====================================================
        # GET CASE NAME
        # ====================================================

        conn = get_connection()

        try:

            cursor = conn.cursor()

            cursor.execute(
                """
                SELECT case_name
                FROM documents_v2
                WHERE document_id = %s
                """,
                (document_id,)
            )

            row = cursor.fetchone()

        finally:

            conn.close()

        if not row:

            return jsonify({
                "status": "error",
                "message": "Judgment not found."
            }), 404

        case_name = row[0] or document_id

        # ====================================================
        # GET ALL CHUNKS FOR THIS JUDGMENT
        # ====================================================

        chunks = get_judgment_chunks(
            document_id
        )

        if not chunks:

            return jsonify({
                "status": "error",
                "message": (
                    "No chunks found for this judgment."
                )
            }), 404

        print()
        print("=" * 70)
        print("JUDGMENT SUMMARY REQUEST")
        print("=" * 70)
        print("Document ID:", document_id)
        print("Case:", case_name)
        print("Chunks retrieved:", len(chunks))
        print("=" * 70)

        # ====================================================
        # BUILD LLM CONTEXT FROM ALL CHUNKS
        # ====================================================

        context = build_judgment_context(
            chunks
        )

        # ====================================================
        # GENERATE SUMMARY FROM CONTEXT
        # ====================================================

        summary = generate_summary(
            context=context,
            case_name=case_name
        )

        # ====================================================
        # RETURN SUMMARY
        # ====================================================

        return jsonify({

            "status": "success",

            "document_id": document_id,

            "case_name": case_name,

            "chunk_count": len(chunks),

            "summary": summary

        })

    except Exception as e:

        print("Judgment Summary error:", e)

        return jsonify({

            "status": "error",

            "message": (
                "Failed to generate judgment summary."
            ),

            "details": str(e)

        }), 500