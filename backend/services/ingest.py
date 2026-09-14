from pathlib import Path
import json

from services.document_service import (
    extract_text_from_pdf,
    extract_metadata,
    extract_document_sections
)


BASE_DIR = Path(__file__).resolve().parent.parent

RAW_DIR = BASE_DIR / "data" / "raw"
OUTPUT_DIR = BASE_DIR / "data" / "processed"


def get_pdf_files():

    unique_files = {}

    for pdf_path in RAW_DIR.iterdir():

        if pdf_path.is_file() and pdf_path.suffix.lower() == ".pdf":

            unique_files[
                pdf_path.name.lower()
            ] = pdf_path

    return sorted(
        unique_files.values(),
        key=lambda path: path.name.lower()
    )


def process_pdf(pdf_path):

    # Output JSON path
    output_path = (
        OUTPUT_DIR /
        f"{pdf_path.stem}.json"
    )

    # --------------------------------------------------
    # Skip if already processed
    # --------------------------------------------------

    if output_path.exists():

        print(
            f"Skipping already processed: "
            f"{pdf_path.name}"
        )

        return "skipped"

    print(
        f"\nProcessing: {pdf_path.name}"
    )

    try:

        pages = extract_text_from_pdf(
            pdf_path
        )

        metadata = extract_metadata(
            pages
        )

        sections = extract_document_sections(
            pages
        )

        document = {
            "id": pdf_path.stem,
            "filename": pdf_path.name,
            "metadata": metadata,
            "sections": sections,
            "pages": pages
        }

        with open(
            output_path,
            "w",
            encoding="utf-8"
        ) as file:

            json.dump(
                document,
                file,
                ensure_ascii=False,
                indent=2
            )

        print(
            f"Saved: {output_path}"
        )

        print("\nMetadata:")

        print(
            json.dumps(
                metadata,
                indent=2,
                ensure_ascii=False
            )
        )

        print("\nSections:")

        print(
            f"Headnote: "
            f"{bool(sections['headnote'])}"
        )

        print(
            f"Judgment: "
            f"{bool(sections['judgment'])}"
        )

        print(
            f"Verdict: "
            f"{sections['verdict']}"
        )

        return "success"

    except Exception as error:

        print(
            f"Failed: {pdf_path.name}"
        )

        print(
            f"Error: {error}"
        )

        return "failed"


def ingest_documents(limit=None):

    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    # --------------------------------------------------
    # Find all PDFs
    # --------------------------------------------------

    pdf_files = get_pdf_files()

    print(
        f"Found {len(pdf_files)} PDF files."
    )

    if not pdf_files:

        print(
            "No PDF files found."
        )

        return

    # --------------------------------------------------
    # Find ONLY unprocessed PDFs
    # --------------------------------------------------

    unprocessed_files = []

    for pdf_path in pdf_files:

        output_path = (
            OUTPUT_DIR /
            f"{pdf_path.stem}.json"
        )

        if not output_path.exists():

            unprocessed_files.append(
                pdf_path
            )

    already_processed = (
        len(pdf_files) -
        len(unprocessed_files)
    )

    print(
        f"Already processed: "
        f"{already_processed}"
    )

    print(
        f"Remaining: "
        f"{len(unprocessed_files)}"
    )

    # --------------------------------------------------
    # Apply limit ONLY to unprocessed files
    # --------------------------------------------------

    if limit is not None:

        pdf_files = unprocessed_files[:limit]

    else:

        pdf_files = unprocessed_files

    print(
        f"Processing "
        f"{len(pdf_files)} "
        f"new PDF file(s)."
    )

    # --------------------------------------------------
    # Counters
    # --------------------------------------------------

    successful = 0
    failed = 0

    # --------------------------------------------------
    # Process PDFs
    # --------------------------------------------------

    for index, pdf_path in enumerate(
        pdf_files,
        start=1
    ):

        print(
            f"\n[{index}/{len(pdf_files)}]"
        )

        result = process_pdf(
            pdf_path
        )

        if result == "success":

            successful += 1

        elif result == "failed":

            failed += 1

    # --------------------------------------------------
    # Final report
    # --------------------------------------------------

    print(
        "\n=============================="
    )

    print(
        "INGESTION COMPLETE"
    )

    print(
        "=============================="
    )

    print(
        f"Total PDFs found: "
        f"{len(get_pdf_files())}"
    )

    print(
        f"Already processed: "
        f"{already_processed}"
    )

    print(
        f"Processed this run: "
        f"{successful}"
    )

    print(
        f"Failed this run: "
        f"{failed}"
    )

    print(
        f"Remaining: "
        f"{len(unprocessed_files) - successful}"
    )
    print("ingest.py loaded")


if __name__ == "__main__":
    print("Starting ingestion...")
    ingest_documents()