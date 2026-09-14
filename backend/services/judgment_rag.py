"""
Judgment-specific RAG retrieval.

This service retrieves chunks only from the selected judgment.
"""

from services.database import get_connection
from services.search import (
    create_query_embedding,
    reranker,
    merge_chunks,
    clean_boundary_text
)


# ============================================================
# GET ALL CHUNKS OF A JUDGMENT
# ============================================================

def get_judgment_chunks(document_id):
    """
    Retrieve all chunks belonging to one judgment.

    Chunks are returned in their original document order.
    """

    conn = get_connection()

    try:
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT
                id,
                document_id,
                chunk_index,
                chunk_text
            FROM document_chunks
            WHERE document_id = %s
            ORDER BY chunk_index ASC
            """,
            (document_id,)
        )

        rows = cursor.fetchall()

        return [
            {
                "id": row[0],
                "document_id": row[1],
                "chunk_index": row[2],
                "chunk_text": row[3],
            }
            for row in rows
        ]

    finally:
        conn.close()


# ============================================================
# BUILD ORDERED JUDGMENT CONTEXT
# ============================================================

def build_judgment_context(chunks):
    """
    Build ordered context from all judgment chunks.
    """

    context_parts = []

    for chunk in chunks:

        context_parts.append(
            f"[CHUNK {chunk['chunk_index']}]\n"
            f"{chunk['chunk_text']}"
        )

    return "\n\n".join(context_parts)


# ============================================================
# SEARCH INSIDE ONE JUDGMENT
# ============================================================

def search_judgment_chunks(
    document_id,
    query,
    top_k=5,
    context_chunks=1
):
    """
    Retrieve the most relevant chunks from ONLY one judgment.

    Process:

        1. Create query embedding.
        2. Search pgvector restricted to document_id.
        3. Retrieve candidate chunks.
        4. Rerank candidates using CrossEncoder.
        5. Select top_k chunks.
        6. Expand selected chunks with neighboring chunks.
    """

    query = (query or "").strip()

    if not document_id:
        return []

    if not query:
        return []

    # ========================================================
    # CREATE QUERY EMBEDDING
    # ========================================================

    query_vector = create_query_embedding(query)

    conn = get_connection()

    try:

        cursor = conn.cursor()

        # ====================================================
        # STEP 1: VECTOR SEARCH
        # ====================================================

        candidate_limit = max(
            top_k * 4,
            20
        )

        cursor.execute(
            """
            SELECT
                id,
                document_id,
                chunk_index,
                chunk_text,
                1 - (embedding <=> %s::vector) AS similarity
            FROM document_chunks
            WHERE document_id = %s
              AND embedding IS NOT NULL
            ORDER BY embedding <=> %s::vector
            LIMIT %s;
            """,
            (
                query_vector,
                document_id,
                query_vector,
                candidate_limit
            )
        )

        matches = cursor.fetchall()

        # ====================================================
        # PREPARE CANDIDATES
        # ====================================================

        candidates = []

        for (
            chunk_id,
            matched_document_id,
            chunk_index,
            chunk_text,
            similarity
        ) in matches:

            candidates.append({
                "id": chunk_id,
                "document_id": matched_document_id,
                "matched_chunk": chunk_index,
                "chunk_text": chunk_text,
                "similarity": float(similarity)
            })

        # ====================================================
        # STEP 2: CROSSENCODER RERANKING
        # ====================================================

        if candidates:

            rerank_pairs = [
                (
                    query,
                    candidate["chunk_text"]
                )
                for candidate in candidates
            ]

            rerank_scores = reranker.predict(
                rerank_pairs
            )

            for candidate, score in zip(
                candidates,
                rerank_scores
            ):

                candidate["rerank_score"] = float(score)

            candidates.sort(
                key=lambda item: item["rerank_score"],
                reverse=True
            )

        # ====================================================
        # STEP 3: SELECT TOP RESULTS
        # ====================================================

        selected_candidates = candidates[:top_k]

        results = []

        # ====================================================
        # STEP 4: ADD NEIGHBORING CHUNKS
        # ====================================================

        for candidate in selected_candidates:

            chunk_index = candidate["matched_chunk"]

            start_chunk = max(
                0,
                chunk_index - context_chunks
            )

            end_chunk = (
                chunk_index + context_chunks
            )

            cursor.execute(
                """
                SELECT
                    chunk_index,
                    chunk_text
                FROM document_chunks
                WHERE document_id = %s
                  AND chunk_index BETWEEN %s AND %s
                ORDER BY chunk_index ASC;
                """,
                (
                    document_id,
                    start_chunk,
                    end_chunk
                )
            )

            neighboring_chunks = cursor.fetchall()

            combined_text = merge_chunks(
                neighboring_chunks
            )

            combined_text = clean_boundary_text(
                combined_text
            )

            results.append({

                "id": candidate["id"],

                "document_id": document_id,

                "matched_chunk": chunk_index,

                "similarity": candidate["similarity"],

                "rerank_score": candidate["rerank_score"],

                "context_start": start_chunk,

                "context_end": end_chunk,

                "text": combined_text

            })

        return results

    finally:

        conn.close()