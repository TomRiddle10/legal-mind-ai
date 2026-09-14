import json
import os
import re
from pathlib import Path

from services.database import get_connection


# ============================================================
# CONFIGURATION
# ============================================================

DATA_DIR = Path("data/processed")

BATCH_SIZE = 100

CHUNK_SIZE = 1000
CHUNK_OVERLAP = 150


# ============================================================
# TEXT CLEANING
# ============================================================

def clean_text(text):
    if not text:
        return ""

    text = text.replace("\x00", " ")

    # Normalize spaces/tabs but preserve paragraphs
    text = re.sub(r"[ \t]+", " ", text)

    # Remove excessive blank lines
    text = re.sub(r"\n\s*\n+", "\n\n", text)

    return text.strip()


# ============================================================
# LEGAL-AWARE CHUNKING
# ============================================================

def chunk_text(text, chunk_size=CHUNK_SIZE, overlap=CHUNK_OVERLAP):

    text = clean_text(text)

    if not text:
        return []

    chunks = []

    start = 0
    text_length = len(text)

    while start < text_length:

        end = min(start + chunk_size, text_length)

        # Try to end at a sentence boundary
        if end < text_length:

            search_start = max(start, end - 250)

            sentence_positions = [
                text.rfind(". ", search_start, end),
                text.rfind("? ", search_start, end),
                text.rfind("! ", search_start, end),
            ]

            best_position = max(sentence_positions)

            if best_position > start:
                end = best_position + 1

        chunk = text[start:end].strip()

        if chunk:
            chunks.append(chunk)

        if end >= text_length:
            break

        # Move backwards by overlap
        start = max(end - overlap, start + 1)

    return chunks


# ============================================================
# EXTRACT TEXT FROM JSON
# ============================================================

def extract_text(data):
    """
    Extract complete judgment text from all pages.
    """

    pages = data.get("pages", [])

    if not isinstance(pages, list):
        return ""

    page_texts = []

    for page in pages:

        if not isinstance(page, dict):
            continue

        text = page.get("text", "")

        if isinstance(text, str) and text.strip():
            page_texts.append(text)

    return "\n".join(page_texts)

# ============================================================
# GET DOCUMENT ID
# ============================================================

def get_document_id(data, filename):

    document_id = data.get("id")

    if document_id:
        return str(document_id)

    return Path(filename).stem


# ============================================================
# CHECK EXISTING DOCUMENT
# ============================================================

def already_chunked(cursor, document_id):

    cursor.execute(
        """
        SELECT EXISTS (
            SELECT 1
            FROM document_chunks
            WHERE document_id = %s
        );
        """,
        (document_id,)
    )

    return cursor.fetchone()[0]


# ============================================================
# INSERT CHUNKS
# ============================================================

def insert_chunks(cursor, document_id, chunks):

    values = []

    for index, chunk in enumerate(chunks):

        values.append(
            (
                document_id,
                index,
                chunk
            )
        )

    cursor.executemany(
        """
        INSERT INTO document_chunks
        (
            document_id,
            chunk_index,
            chunk_text
        )
        VALUES (%s, %s, %s)
        ON CONFLICT (document_id, chunk_index)
        DO NOTHING;
        """,
        values
    )


# ============================================================
# MAIN
# ============================================================

def chunk_all_documents():

    print("=" * 60)
    print("LEGAL MIND AI - FULL DOCUMENT CHUNKING")
    print("=" * 60)

    if not DATA_DIR.exists():

        print(f"ERROR: Directory not found: {DATA_DIR}")
        return

    files = sorted(DATA_DIR.glob("*.json"))

    total_files = len(files)

    print(f"JSON files found: {total_files}")
    print(f"Batch size: {BATCH_SIZE}")
    print(f"Chunk size: {CHUNK_SIZE}")
    print(f"Chunk overlap: {CHUNK_OVERLAP}")
    print("=" * 60)

    if total_files == 0:

        print("No JSON files found.")
        return

    conn = get_connection()
    cursor = conn.cursor()

    processed = 0
    skipped = 0
    failed = 0
    total_chunks_created = 0

    for batch_start in range(0, total_files, BATCH_SIZE):

        batch = files[
            batch_start:
            batch_start + BATCH_SIZE
        ]

        batch_number = (
            batch_start // BATCH_SIZE
        ) + 1

        total_batches = (
            (total_files + BATCH_SIZE - 1)
            // BATCH_SIZE
        )

        print()
        print(
            f"========== BATCH "
            f"{batch_number}/{total_batches} =========="
        )

        for file_number, file_path in enumerate(
            batch,
            start=batch_start + 1
        ):

            try:

                # --------------------------------------------
                # Read JSON
                # --------------------------------------------

                with open(
                    file_path,
                    "r",
                    encoding="utf-8"
                ) as f:

                    data = json.load(f)

                document_id = get_document_id(
                    data,
                    file_path.name
                )

                # --------------------------------------------
                # Skip if already chunked
                # --------------------------------------------

                if already_chunked(
                    cursor,
                    document_id
                ):

                    skipped += 1

                    print(
                        f"[{file_number}/{total_files}] "
                        f"SKIP: {file_path.name}"
                    )

                    continue

                # --------------------------------------------
                # Extract text
                # --------------------------------------------

                text = extract_text(data)

                if not text:

                    print(
                        f"[{file_number}/{total_files}] "
                        f"NO TEXT: {file_path.name}"
                    )

                    failed += 1
                    continue

                # --------------------------------------------
                # Create chunks
                # --------------------------------------------

                chunks = chunk_text(text)

                if not chunks:

                    print(
                        f"[{file_number}/{total_files}] "
                        f"NO CHUNKS: {file_path.name}"
                    )

                    failed += 1
                    continue

                # --------------------------------------------
                # Insert chunks
                # --------------------------------------------

                insert_chunks(
                    cursor,
                    document_id,
                    chunks
                )

                processed += 1
                total_chunks_created += len(chunks)

                print(
                    f"[{file_number}/{total_files}] "
                    f"OK: {file_path.name} "
                    f"→ {len(chunks)} chunks"
                )

            except Exception as e:

                failed += 1

                print(
                    f"[{file_number}/{total_files}] "
                    f"FAILED: {file_path.name}"
                )

                print(f"Error: {e}")

        # ====================================================
        # COMMIT AFTER EVERY BATCH
        # ====================================================

        conn.commit()

        print()
        print(
            f"Batch {batch_number} committed."
        )

        print(
            f"Progress: "
            f"{min(batch_start + BATCH_SIZE, total_files)}"
            f"/{total_files}"
        )

        print(
            f"Processed: {processed} | "
            f"Skipped: {skipped} | "
            f"Failed: {failed}"
        )

        print(
            f"Chunks created so far: "
            f"{total_chunks_created}"
        )

    cursor.close()
    conn.close()

    # ========================================================
    # FINAL REPORT
    # ========================================================

    print()
    print("=" * 60)
    print("CHUNKING COMPLETE")
    print("=" * 60)

    print(f"Total JSON files:       {total_files}")
    print(f"Documents processed:    {processed}")
    print(f"Documents skipped:      {skipped}")
    print(f"Documents failed:       {failed}")
    print(f"Chunks created:         {total_chunks_created}")

    print("=" * 60)


if __name__ == "__main__":
    chunk_all_documents()