from sentence_transformers import SentenceTransformer
import psycopg2
import time

MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"

DB_CONFIG = {
    "host": "localhost",
    "port": 5432,
    "database": "legal_mind_ai",
    "user": "postgres",
    "password": "Ziy@1234"
}

# Adjust this if GPU memory becomes an issue
BATCH_SIZE = 128

# Commit after this many batches
COMMIT_EVERY = 10


def get_connection():
    return psycopg2.connect(**DB_CONFIG)


def load_model():
    print(f"Loading embedding model: {MODEL_NAME}")

    model = SentenceTransformer(
        MODEL_NAME,
        device="cuda"
    )

    print("Embedding dimension:", model.get_embedding_dimension())
    print("Using device:", model.device)

    return model


def generate_embeddings():

    connection = get_connection()
    cursor = connection.cursor()

    model = load_model()

    print("\n==========================================")
    print("GPU EMBEDDING GENERATION")
    print("==========================================")

    # Count remaining chunks
    cursor.execute("""
        SELECT COUNT(*)
        FROM document_chunks
        WHERE embedding IS NULL
    """)

    remaining = cursor.fetchone()[0]

    print(f"Chunks without embeddings: {remaining:,}")

    if remaining == 0:
        print("All chunks already have embeddings.")
        cursor.close()
        connection.close()
        return

    processed = 0
    failed = 0
    batch_number = 0

    start_time = time.time()

    try:

        while True:

            # Fetch one batch
            cursor.execute("""
                SELECT
                    id,
                    chunk_text
                FROM document_chunks
                WHERE embedding IS NULL
                ORDER BY id
                LIMIT %s
            """, (BATCH_SIZE,))

            rows = cursor.fetchall()

            if not rows:
                break

            batch_number += 1

            ids = [row[0] for row in rows]
            texts = [row[1] for row in rows]

            print(
                f"\nBatch {batch_number} | "
                f"{len(rows)} chunks"
            )

            try:

                # GPU embedding
                embeddings = model.encode(
                    texts,
                    batch_size=BATCH_SIZE,
                    show_progress_bar=True,
                    normalize_embeddings=True,
                    convert_to_numpy=True
                )

                # Store embeddings
                for chunk_id, embedding in zip(
                    ids,
                    embeddings
                ):

                    cursor.execute(
                        """
                        UPDATE document_chunks
                        SET embedding = %s
                        WHERE id = %s
                        """,
                        (
                            embedding.tolist(),
                            chunk_id
                        )
                    )

                processed += len(rows)

                # Commit periodically
                if batch_number % COMMIT_EVERY == 0:

                    connection.commit()

                    elapsed = time.time() - start_time

                    rate = processed / elapsed if elapsed > 0 else 0

                    print(
                        f"COMMITTED | "
                        f"Processed: {processed:,} | "
                        f"Rate: {rate:.2f} chunks/sec"
                    )

                else:
                    connection.commit()

            except Exception as error:

                connection.rollback()

                failed += len(rows)

                print(
                    f"Batch failed: {error}"
                )

                # Continue with next batch
                continue

            # Progress
            total = remaining

            percentage = (
                processed / total * 100
                if total > 0
                else 100
            )

            print(
                f"Progress: "
                f"{processed:,}/{total:,} "
                f"({percentage:.2f}%)"
            )

    finally:

        cursor.close()
        connection.close()

    elapsed = time.time() - start_time

    print("\n==========================================")
    print("GPU EMBEDDING GENERATION COMPLETE")
    print("==========================================")

    print(f"Processed: {processed:,}")
    print(f"Failed:    {failed:,}")
    print(f"Time:      {elapsed / 60:.2f} minutes")


if __name__ == "__main__":
    generate_embeddings()