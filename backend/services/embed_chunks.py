from sentence_transformers import SentenceTransformer
from services.database import get_connection
from psycopg2.extras import execute_values

import time


MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"

# PostgreSQL batch
DB_BATCH_SIZE = 2000

# GPU batch
EMBED_BATCH_SIZE = 128


def generate_embeddings():

    print("=" * 60)
    print("LEGAL MIND AI - GPU EMBEDDING GENERATION")
    print("=" * 60)

    print(f"Loading model: {MODEL_NAME}")

    # ----------------------------------------------------
    # Load model on GPU
    # ----------------------------------------------------

    model = SentenceTransformer(
        MODEL_NAME,
        device="cuda"
    )

    print("Using device:", model.device)

    dimension = model.get_embedding_dimension()

    print("Embedding dimension:", dimension)

    if dimension != 384:
        raise ValueError(
            f"Expected 384 dimensions, got {dimension}"
        )

    # ----------------------------------------------------
    # Database connection
    # ----------------------------------------------------

    conn = get_connection()
    cursor = conn.cursor()

    # ----------------------------------------------------
    # Count remaining chunks
    # ----------------------------------------------------

    cursor.execute("""
        SELECT COUNT(*)
        FROM document_chunks
        WHERE embedding IS NULL;
    """)

    remaining = cursor.fetchone()[0]

    print(f"Chunks remaining: {remaining:,}")

    if remaining == 0:

        print("All chunks already have embeddings.")

        cursor.close()
        conn.close()

        return

    processed = 0
    failed_batches = 0

    start_time = time.time()

    # ----------------------------------------------------
    # Process until everything is embedded
    # ----------------------------------------------------

    while True:

        # ------------------------------------------------
        # Reconnect if PostgreSQL connection was closed
        # ------------------------------------------------

        if conn.closed:

            print(
                "\nDatabase connection closed."
            )

            print(
                "Reconnecting to PostgreSQL..."
            )

            conn = get_connection()
            cursor = conn.cursor()

            print(
                "PostgreSQL connection restored."
            )

        # ------------------------------------------------
        # Fetch chunks without embeddings
        # ------------------------------------------------

        cursor.execute("""
            SELECT id, chunk_text
            FROM document_chunks
            WHERE embedding IS NULL
            ORDER BY id
            LIMIT %s;
        """, (DB_BATCH_SIZE,))

        rows = cursor.fetchall()

        if not rows:
            break

        ids = [row[0] for row in rows]
        texts = [row[1] for row in rows]

        print(
            f"\nGenerating embeddings for "
            f"{len(rows):,} chunks..."
        )

        # ------------------------------------------------
        # GPU embedding
        # ------------------------------------------------

        try:

            embeddings = model.encode(
                texts,
                batch_size=EMBED_BATCH_SIZE,
                show_progress_bar=False,
                normalize_embeddings=True,
                convert_to_numpy=True
            )

        except Exception as error:

            print(
                f"GPU embedding failed: {error}"
            )

            failed_batches += 1

            # Don't lose the entire process
            time.sleep(2)

            continue

        # ------------------------------------------------
        # Prepare PostgreSQL data
        # ------------------------------------------------

        update_data = []

        for chunk_id, embedding in zip(
            ids,
            embeddings
        ):

            vector = "[" + ",".join(
                str(float(value))
                for value in embedding
            ) + "]"

            update_data.append(
                (vector, chunk_id)
            )

        # ------------------------------------------------
        # Bulk update
        # ------------------------------------------------

        try:

            execute_values(
                cursor,
                """
                UPDATE document_chunks AS d
                SET embedding = data.embedding::vector
                FROM (
                    VALUES %s
                ) AS data(embedding, id)
                WHERE d.id = data.id;
                """,
                update_data,
                page_size=1000
            )

            conn.commit()

        except Exception as error:

            print(
                f"Database update failed: {error}"
            )

            failed_batches += 1

            # --------------------------------------------
            # Safely rollback
            # --------------------------------------------

            try:

                if not conn.closed:
                    conn.rollback()

            except Exception as rollback_error:

                print(
                    f"Rollback failed: {rollback_error}"
                )

            # --------------------------------------------
            # Reconnect
            # --------------------------------------------

            try:

                if conn.closed:

                    print(
                        "Reconnecting to PostgreSQL..."
                    )

                    conn = get_connection()
                    cursor = conn.cursor()

                    print(
                        "PostgreSQL connection restored."
                    )

            except Exception as reconnect_error:

                print(
                    f"Reconnect failed: "
                    f"{reconnect_error}"
                )

                raise

            # --------------------------------------------
            # Retry this batch
            # --------------------------------------------

            print(
                "Retrying current batch..."
            )

            continue

        # ------------------------------------------------
        # Update progress
        # ------------------------------------------------

        processed += len(rows)

        elapsed = time.time() - start_time

        percentage = (
            processed / remaining
        ) * 100

        rate = (
            processed / elapsed
            if elapsed > 0
            else 0
        )

        print(
            f"Processed: "
            f"{processed:,}/{remaining:,} "
            f"({percentage:.2f}%) | "
            f"Speed: {rate:.2f} chunks/sec"
        )

    # ----------------------------------------------------
    # Final verification
    # ----------------------------------------------------

    # Make sure connection is alive
    if conn.closed:

        conn = get_connection()
        cursor = conn.cursor()

    cursor.execute("""
        SELECT COUNT(*)
        FROM document_chunks
        WHERE embedding IS NULL;
    """)

    remaining_after = cursor.fetchone()[0]

    cursor.execute("""
        SELECT COUNT(*)
        FROM document_chunks
        WHERE embedding IS NOT NULL;
    """)

    embedded = cursor.fetchone()[0]

    elapsed = time.time() - start_time

    print()
    print("=" * 60)
    print("EMBEDDING GENERATION COMPLETE")
    print("=" * 60)

    print(f"Embedded chunks: {embedded:,}")
    print(f"Remaining:       {remaining_after:,}")
    print(f"Failed batches:  {failed_batches}")
    print(f"Time:            {elapsed / 60:.2f} minutes")

    cursor.close()
    conn.close()


if __name__ == "__main__":
    generate_embeddings()