"""
Batch-ingest a folder of judgment PDFs into the shared Legal Mind AI
database, using app.core.db for the connection/schema and app.core.config
for the default paths.

Usage:
    python3 -m app.retrieval.ingest                     # uses config defaults
    python3 -m app.retrieval.ingest /path/to/pdf_folder  # override folder
"""
import os
import sys
import json
import traceback

from app.core.db import get_connection
from app.core.config import RAW_PDF_DIR
from app.retrieval.parser import parse_judgment_pdf


def ingest_folder(folder: str, limit: int | None = None):
    conn = get_connection()
    cur = conn.cursor()

    pdf_paths = []
    for root, _, files in os.walk(folder):
        for f in files:
            if f.lower().endswith(".pdf"):
                pdf_paths.append(os.path.join(root, f))

    if limit:
        pdf_paths = pdf_paths[:limit]

    print(f"Found {len(pdf_paths)} PDFs in {folder}")

    ok, failed, partial = 0, 0, 0
    for i, path in enumerate(pdf_paths, 1):
        try:
            cur.execute("SELECT 1 FROM judgments WHERE file_path = ?", (path,))
            if cur.fetchone():
                continue  # already ingested -- safe to re-run

            record = parse_judgment_pdf(path)
            cur.execute(
                """INSERT INTO judgments
                   (file_path, source_doc_id, title, court, citations, author_judge,
                    bench_judges, petitioner, respondent, date_of_judgment, full_text, num_chars, is_partial)
                   VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)""",
                (
                    path, record["source_doc_id"], record["title"], record["court"],
                    record["citations"], record["author_judge"],
                    json.dumps(record["bench_judges"], ensure_ascii=False),
                    record["petitioner"], record["respondent"], record["date_of_judgment"],
                    record["full_text"], record["num_chars"], int(record["is_partial"]),
                ),
            )
            ok += 1
            if record["is_partial"]:
                partial += 1
        except Exception as e:
            failed += 1
            print(f"[FAILED] {path}: {e}")
            traceback.print_exc(limit=1)

        if i % 200 == 0:
            conn.commit()
            print(f"  ...{i}/{len(pdf_paths)} processed ({ok} ok, {failed} failed, {partial} partial)")

    conn.commit()
    conn.close()
    print(f"Done. {ok} ingested ({partial} with missing fields), {failed} failed.")


if __name__ == "__main__":
    folder = sys.argv[1] if len(sys.argv) > 1 else RAW_PDF_DIR
    limit = int(sys.argv[2]) if len(sys.argv) > 2 else None
    ingest_folder(folder, limit)
