from services.search import search_documents
from services.llm import generate_answer


def build_context(results):
    """
    Convert retrieved search results into context
    for the LLM.
    """

    context_parts = []

    for i, result in enumerate(results, start=1):

        context_parts.append(
            f"""
SOURCE {i}

Case:
{result['document_id']}

Matched Chunk:
{result['matched_chunk']}

Similarity:
{result['similarity']:.4f}

LEGAL TEXT:
{result['text']}
"""
        )

    return "\n".join(context_parts)


def ask_legal_question(question):
    """
    Complete RAG pipeline:

    Question
        ↓
    Embedding
        ↓
    PostgreSQL HNSW search
        ↓
    Relevant chunks
        ↓
    Qwen3
        ↓
    Answer
    """

    # --------------------------------------------------
    # STEP 1: Search PostgreSQL
    # --------------------------------------------------

    results = search_documents(
        question,
        top_k=5,
        context_chunks=1
    )

    if not results:
        return {
            "answer": "No relevant legal judgments were found.",
            "sources": []
        }

    # --------------------------------------------------
    # STEP 2: Build dynamic context
    # --------------------------------------------------

    context = build_context(results)

    print("\n")
    print("=" * 80)
    print("RAG CONTEXT")
    print("=" * 80)
    print(context)

    # --------------------------------------------------
    # STEP 3: Send context to Qwen3
    # --------------------------------------------------

    answer = generate_answer(
        context,
        question
    )

    return {
        "answer": answer,
        "sources": results
    }


# ======================================================
# TEST RAG
# ======================================================

if __name__ == "__main__":

    print("=" * 80)
    print("LEGAL MIND AI - LOCAL RAG")
    print("=" * 80)

    question = input(
        "\nEnter your legal question: "
    ).strip()

    if not question:
        print("Please enter a question.")
        exit()

    print("\nSearching legal judgments...")

    result = ask_legal_question(question)

    print("\n")
    print("=" * 80)
    print("LEGAL MIND AI ANSWER")
    print("=" * 80)

    print("\n")
    print(result["answer"])

    print("\n")
    print("=" * 80)
    print("SOURCES")
    print("=" * 80)

    for i, source in enumerate(
        result["sources"],
        start=1
    ):

        print(
            f"\n{i}. {source['document_id']}"
        )

        print(
            f"   Chunk: {source['matched_chunk']}"
        )

        print(
            f"   Similarity: "
            f"{source['similarity']:.4f}"
        )