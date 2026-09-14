import json
import re
from pathlib import Path
from datetime import datetime


# ============================================================
# PATHS
# ============================================================

BASE_DIR = Path(__file__).resolve().parent.parent

INPUT_DIR = BASE_DIR / "data" / "processed"
OUTPUT_DIR = BASE_DIR / "data" / "processed_v2"
ERROR_LOG = OUTPUT_DIR / "preprocessing_errors.txt"


# ============================================================
# TEXT CLEANING
# ============================================================

def clean_text(text):
    """Clean and normalize judgment text."""

    if not text:
        return ""

    # Normalize line endings
    text = text.replace("\r\n", "\n")
    text = text.replace("\r", "\n")

    # Remove null characters
    text = text.replace("\x00", "")

    # Normalize spaces/tabs
    text = re.sub(r"[ \t]+", " ", text)

    # Remove excessive blank lines
    text = re.sub(r"\n\s*\n+", "\n\n", text)

    # Remove spaces at beginning/end of lines
    text = "\n".join(line.strip() for line in text.split("\n"))

    # Remove excessive blank lines again
    text = re.sub(r"\n{3,}", "\n\n", text)

    return text.strip()


# ============================================================
# EXTRACT TEXT FROM PAGES
# ============================================================

def extract_full_text(data):
    """
    Extract complete judgment text from the pages list.

    We intentionally use pages instead of sections['verdict']
    because verdict extraction is inconsistent in the dataset.
    """

    pages = data.get("pages", [])

    if not isinstance(pages, list):
        return ""

    page_texts = []

    for page in pages:

        if not isinstance(page, dict):
            continue

        page_text = page.get("text", "")

        if isinstance(page_text, str) and page_text.strip():
            page_texts.append(page_text)

    return "\n\n".join(page_texts)


# ============================================================
# PROCESS ONE FILE
# ============================================================

def preprocess_file(input_file, output_file):

    with open(input_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    # Extract complete text from pages
    full_text = extract_full_text(data)

    # Clean text
    cleaned_text = clean_text(full_text)

    # Basic validation
    if not cleaned_text:
        raise ValueError("No usable text found")

    # Preserve important metadata
    processed_data = {
        "id": data.get("id"),
        "filename": data.get("filename"),
        "metadata": data.get("metadata", {}),
        "text": cleaned_text
    }

    # Save processed JSON
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(
            processed_data,
            f,
            ensure_ascii=False,
            indent=2
        )


# ============================================================
# MAIN
# ============================================================

def main():

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    # Find all input JSON files
    input_files = list(INPUT_DIR.glob("*.json"))

    total = len(input_files)

    print("=" * 70)
    print("LEGAL MIND AI - DATA PREPROCESSING")
    print("=" * 70)
    print(f"Input directory : {INPUT_DIR}")
    print(f"Output directory: {OUTPUT_DIR}")
    print(f"Total files     : {total}")
    print("=" * 70)

    if total == 0:
        print("No JSON files found.")
        return

    processed = 0
    skipped = 0
    failed = 0
    short_text = 0

    start_time = datetime.now()

    # Open error log
    with open(ERROR_LOG, "w", encoding="utf-8") as error_file:

        for index, input_file in enumerate(input_files, start=1):

            output_file = OUTPUT_DIR / input_file.name

            # Skip if already successfully processed
            if output_file.exists():

                skipped += 1

            else:

                try:

                    preprocess_file(input_file, output_file)

                    processed += 1

                    # Check resulting text length
                    with open(output_file, "r", encoding="utf-8") as f:
                        result = json.load(f)

                    text_length = len(result.get("text", ""))

                    if text_length < 500:
                        short_text += 1

                except Exception as e:

                    failed += 1

                    error_message = (
                        f"{input_file.name} | "
                        f"{type(e).__name__}: {e}\n"
                    )

                    error_file.write(error_message)

            # Progress
            if index % 100 == 0 or index == total:

                elapsed = datetime.now() - start_time

                print(
                    f"[{index}/{total}] "
                    f"Processed: {processed} | "
                    f"Skipped: {skipped} | "
                    f"Failed: {failed} | "
                    f"Short: {short_text} | "
                    f"Time: {elapsed}"
                )

    # ========================================================
    # FINAL REPORT
    # ========================================================

    elapsed = datetime.now() - start_time

    print("\n")
    print("=" * 70)
    print("PREPROCESSING COMPLETE")
    print("=" * 70)

    print(f"Total input files : {total}")
    print(f"Processed         : {processed}")
    print(f"Skipped           : {skipped}")
    print(f"Failed            : {failed}")
    print(f"Short documents   : {short_text}")
    print(f"Time taken        : {elapsed}")

    print(f"\nOutput directory:")
    print(OUTPUT_DIR)

    if failed > 0:
        print(f"\nError log:")
        print(ERROR_LOG)

    print("=" * 70)


if __name__ == "__main__":
    main()