from sentence_transformers import SentenceTransformer, CrossEncoder
from services.database import get_connection
import re

MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"

RERANKER_MODEL_NAME = "cross-encoder/ms-marco-MiniLM-L-6-v2"

model = SentenceTransformer(
    MODEL_NAME,
    device="cuda"
)

reranker = CrossEncoder(
    RERANKER_MODEL_NAME,
    device="cuda"
)


def create_query_embedding(query):
    """Convert the user's query into a 384-dimensional vector."""

    embedding = model.encode(
        query,
        normalize_embeddings=True
    )

    vector = "[" + ",".join(
        str(float(value))
        for value in embedding
    ) + "]"

    return vector


def merge_chunks(chunks):
    """
    Merge neighboring chunks while avoiding obvious
    duplicated text at chunk boundaries.
    """

    if not chunks:
        return ""

    texts = [
        text.strip()
        for _, text in chunks
        if text and text.strip()
    ]

    if not texts:
        return ""

    merged = texts[0]

    for current in texts[1:]:

        # Look for overlap between the end of the previous
        # chunk and the beginning of the current chunk.
        max_overlap = min(
            len(merged),
            len(current),
            300
        )

        overlap_found = 0

        for size in range(max_overlap, 20, -1):

            if merged[-size:] == current[:size]:
                overlap_found = size
                break

        if overlap_found:
            merged += current[overlap_found:]

        else:
            # Normal chunk boundary
            merged += "\n\n" + current

    return merged


def clean_boundary_text(text):
    """
    Clean obvious formatting problems caused by chunk boundaries.
    """

    # Fix excessive spaces
    text = re.sub(r"[ \t]+", " ", text)

    # Fix spaces before punctuation
    text = re.sub(r"\s+([,.;:!?])", r"\1", text)

    # Fix spaces immediately after opening brackets
    text = re.sub(r"([\(\[\{])\s+", r"\1", text)

    # Fix spaces immediately before closing brackets
    text = re.sub(r"\s+([\)\]\}])", r"\1", text)

    return text.strip()


def search_documents(query, top_k=5, context_chunks=1):
    """
    Search for relevant chunks and include neighboring chunks.

    context_chunks=1 means:
        previous chunk + matched chunk + next chunk

    Process:
        1. Retrieve initial candidates using vector similarity.
        2. Rerank the candidates using CrossEncoder.
        3. Keep the best top_k results.
        4. Expand the selected results with neighboring chunks.
    """

    query_vector = create_query_embedding(query)

    conn = get_connection()
    cursor = conn.cursor()

    # --------------------------------------------------
    # STEP 1: Retrieve candidate chunks
    # --------------------------------------------------
    #
    # We retrieve more candidates than we finally need.
    #
    # Example:
    # top_k = 5
    #
    # PostgreSQL retrieves 20 candidates.
    # Reranker then selects the best 5.
    # --------------------------------------------------

    candidate_limit = max(
        top_k * 4,
        20
    )

    cursor.execute(
        """
        SELECT
            document_id,
            chunk_index,
            chunk_text,
            1 - (embedding <=> %s::vector) AS similarity
        FROM document_chunks
        WHERE embedding IS NOT NULL
        ORDER BY embedding <=> %s::vector
        LIMIT %s;
        """,
        (
            query_vector,
            query_vector,
            candidate_limit
        )
    )

    matches = cursor.fetchall()

    # --------------------------------------------------
    # STEP 2: Prepare candidates for reranking
    # --------------------------------------------------

    candidates = []

    for (
        document_id,
        chunk_index,
        chunk_text,
        similarity
    ) in matches:

        candidates.append({
            "document_id": document_id,
            "matched_chunk": chunk_index,
            "chunk_text": chunk_text,
            "similarity": float(similarity)
        })

    # --------------------------------------------------
    # STEP 3: Rerank candidates
    # --------------------------------------------------

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

            candidate["rerank_score"] = float(
                score
            )

        # Highest reranker score = most relevant
        candidates.sort(
            key=lambda x: x["rerank_score"],
            reverse=True
        )

    # --------------------------------------------------
    # STEP 4: Keep only the best results
    # --------------------------------------------------

    selected_candidates = candidates[:top_k]

    results = []

    # --------------------------------------------------
    # STEP 5: Expand selected results
    # --------------------------------------------------

    for candidate in selected_candidates:

        document_id = candidate["document_id"]
        chunk_index = candidate["matched_chunk"]
        similarity = candidate["similarity"]
        rerank_score = candidate["rerank_score"]

        start_chunk = max(
            0,
            chunk_index - context_chunks
        )

        end_chunk = chunk_index + context_chunks

        cursor.execute(
            """
            SELECT
                chunk_index,
                chunk_text
            FROM document_chunks
            WHERE document_id = %s
              AND chunk_index BETWEEN %s AND %s
            ORDER BY chunk_index;
            """,
            (
                document_id,
                start_chunk,
                end_chunk
            )
        )

        neighboring_chunks = cursor.fetchall()

        # --------------------------------------------------
        # Merge neighboring chunks
        # --------------------------------------------------

        combined_text = merge_chunks(
            neighboring_chunks
        )

        # --------------------------------------------------
        # Clean formatting
        # --------------------------------------------------

        combined_text = clean_boundary_text(
            combined_text
        )

        # --------------------------------------------------
        # Final result
        # --------------------------------------------------

        results.append({
            "document_id": document_id,
            "matched_chunk": chunk_index,
            "similarity": similarity,
            "rerank_score": rerank_score,
            "context_start": start_chunk,
            "context_end": end_chunk,
            "text": combined_text
        })

    cursor.close()
    conn.close()

    return results


# ======================================================
# TEST SEARCH
# ======================================================

if __name__ == "__main__":

    query = input(
        "\nEnter your legal question: "
    ).strip()

    if not query:
        print("Please enter a question.")
        exit()

    results = search_documents(
        query,
        top_k=5,
        context_chunks=1
    )

    print("\n")
    print("=" * 80)
    print("RERANKED SEMANTIC SEARCH RESULTS")
    print("=" * 80)

    for i, result in enumerate(
        results,
        start=1
    ):

        print(f"\n## Result {i}")
        print("-" * 80)

        print(
            "Document:",
            result["document_id"]
        )

        print(
            "Matched chunk:",
            result["matched_chunk"]
        )

        print(
            "Context:",
            f"{result['context_start']} "
            f"→ "
            f"{result['context_end']}"
        )

        print(
            "Similarity:",
            round(
                result["similarity"],
                4
            )
        )

        print(
            "Rerank Score:",
            round(
                result["rerank_score"],
                4
            )
        )

        print("\nText:")
        print(result["text"])

        print("-" * 80)