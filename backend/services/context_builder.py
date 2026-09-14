from services.search import search_documents


def clean_text(text):
    """Clean retrieved legal text."""

    if not text:
        return ""

    text = text.replace("\r\n", "\n")
    text = text.replace("\r", "\n")

    lines = [line.strip() for line in text.split("\n")]

    cleaned_lines = []

    for line in lines:
        if line:
            cleaned_lines.append(line)

    return "\n".join(cleaned_lines)


def build_context(results, max_results=5):
    """
    Build dynamic RAG context from search results.
    """

    if not results:
        return "No relevant legal documents were found."

    context_parts = []

    for i, result in enumerate(
        results[:max_results],
        start=1
    ):

        document_id = result.get(
            "document_id",
            "Unknown"
        )

        matched_chunk = result.get(
            "matched_chunk",
            "Unknown"
        )

        similarity = result.get(
            "similarity",
            0
        )

        text = clean_text(
            result.get("text", "")
        )

        case_name = document_id.replace(
            "_",
            " "
        )

        if case_name.endswith(" 1"):
            case_name = case_name[:-2]

        section = f"""
SOURCE {i}

Case:
{case_name}

Matched Chunk:
{matched_chunk}

Similarity:
{similarity:.4f}

LEGAL TEXT:
{text}
"""

        context_parts.append(
            section.strip()
        )

    return "\n\n".join(
        context_parts
    )


def get_rag_context(
    query,
    top_k=5,
    context_chunks=1
):
    """
    Dynamically search PostgreSQL and
    build the RAG context.
    """

    results = search_documents(
        query,
        top_k=top_k,
        context_chunks=context_chunks
    )

    return build_context(
        results,
        max_results=top_k
    )


# ======================================================
# DYNAMIC TEST
# ======================================================

if __name__ == "__main__":

    query = input(
        "\nEnter your legal question: "
    ).strip()

    if not query:
        print("Please enter a question.")
        exit()

    print("\nSearching legal database...")

    context = get_rag_context(
        query,
        top_k=5,
        context_chunks=1
    )

    print("\n")
    print("=" * 80)
    print("DYNAMIC RAG CONTEXT")
    print("=" * 80)

    print(context)

    print("\n" + "=" * 80)