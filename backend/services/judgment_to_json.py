import json
from pathlib import Path

from services.document_service import (
    extract_text_from_pdf,
    extract_metadata,
    extract_document_sections
)


# ============================================================
# CONFIGURATION
# ============================================================

BASE_DIR = Path(__file__).resolve().parent.parent

INPUT_FOLDER = BASE_DIR / "data" / "raw"
OUTPUT_FOLDER = BASE_DIR / "data" / "processed"

OUTPUT_FOLDER.mkdir(
    parents=True,
    exist_ok=True
)


# ============================================================
# SELECT PDF AUTOMATICALLY
# ============================================================

def select_pdf_from_raw():
    """
    Automatically find PDFs inside data/raw
    and allow the user to select one.
    """

    # Support both .pdf and .PDF
    pdf_files = sorted(
        [
            file
            for file in INPUT_FOLDER.iterdir()
            if file.is_file()
            and file.suffix.lower() == ".pdf"
        ]
    )

    if not pdf_files:

        print("\n")
        print("=" * 70)
        print("NO PDF FILES FOUND")
        print("=" * 70)

        print(
            f"\nNo PDF files were found in:\n"
            f"{INPUT_FOLDER}"
        )

        return None

    print("\n")
    print("=" * 70)
    print("AVAILABLE JUDGMENTS")
    print("=" * 70)

    for index, pdf in enumerate(
        pdf_files,
        start=1
    ):

        print(
            f"{index}. {pdf.name}"
        )

    print("=" * 70)

    while True:

        choice = input(
            "\nSelect PDF number: "
        ).strip()

        try:

            choice = int(choice)

            if 1 <= choice <= len(pdf_files):

                return pdf_files[
                    choice - 1
                ]

            print(
                f"\nPlease enter a number between "
                f"1 and {len(pdf_files)}."
            )

        except ValueError:

            print(
                "\nPlease enter a valid number."
            )


# ============================================================
# DISPLAY HELPERS
# ============================================================

def display_metadata(metadata):

    print("\n")
    print("=" * 70)
    print("EXTRACTED JUDGMENT METADATA")
    print("=" * 70)

    fields = [
        ("case_name", "Case Name"),
        ("petitioner", "Petitioner"),
        ("respondent", "Respondent"),
        ("court", "Court"),
        ("judgment_date", "Judgment Date"),
        ("case_number", "Case Number"),
    ]

    for key, label in fields:

        value = metadata.get(key)

        if not value:
            value = "[NOT FOUND]"

        print(f"\n{label}:")
        print(f"  {value}")

    print("\nJudges:")

    judges = metadata.get(
        "judges",
        []
    )

    if judges:

        for judge in judges:

            print(
                f"  - {judge}"
            )

    else:

        print(
            "  [NOT FOUND]"
        )

    print("\nCitations:")

    citations = metadata.get(
        "citations",
        []
    )

    if citations:

        for citation in citations:

            print(
                f"  - {citation}"
            )

    else:

        print(
            "  [NOT FOUND]"
        )

    print("\nLegal Topics:")

    topics = metadata.get(
        "legal_topics",
        []
    )

    if topics:

        for topic in topics:

            print(
                f"  - {topic}"
            )

    else:

        print(
            "  [NOT FOUND]"
        )


# ============================================================
# EDIT METADATA
# ============================================================

def edit_metadata(metadata):

    fields = [
        ("case_name", "Case Name"),
        ("petitioner", "Petitioner"),
        ("respondent", "Respondent"),
        ("court", "Court"),
        ("judgment_date", "Judgment Date"),
        ("case_number", "Case Number"),
    ]

    while True:

        print("\n")
        print("=" * 70)
        print("EDIT JUDGMENT")
        print("=" * 70)

        for index, (key, label) in enumerate(
            fields,
            start=1
        ):

            value = metadata.get(key)

            if not value:

                value = "[EMPTY]"

            print(
                f"{index}. {label}: {value}"
            )

        print("7. Judges")
        print("8. Citations")
        print("9. Legal Topics")
        print("10. Continue")

        choice = input(
            "\nSelect field to edit: "
        ).strip()

        # ----------------------------------------------------
        # Standard fields
        # ----------------------------------------------------

        if choice in {
            "1",
            "2",
            "3",
            "4",
            "5",
            "6"
        }:

            index = int(choice) - 1

            key, label = fields[index]

            current = metadata.get(key)

            print(
                f"\nCurrent {label}: "
                f"{current or '[EMPTY]'}"
            )

            new_value = input(
                f"Enter new {label}: "
            ).strip()

            if new_value:

                metadata[key] = new_value

                print(
                    f"\n✓ {label} updated."
                )

        # ----------------------------------------------------
        # Judges
        # ----------------------------------------------------

        elif choice == "7":

            print("\nCurrent judges:")

            for i, judge in enumerate(
                metadata.get("judges", []),
                start=1
            ):

                print(
                    f"{i}. {judge}"
                )

            print(
                "\nEnter judges separated by |"
            )

            value = input(
                "Judges: "
            ).strip()

            if value:

                metadata["judges"] = [
                    item.strip()
                    for item in value.split("|")
                    if item.strip()
                ]

                print(
                    "\n✓ Judges updated."
                )

        # ----------------------------------------------------
        # Citations
        # ----------------------------------------------------

        elif choice == "8":

            print(
                "\nCurrent citations:"
            )

            for citation in metadata.get(
                "citations",
                []
            ):

                print(
                    f"- {citation}"
                )

            print(
                "\nEnter citations separated by |"
            )

            value = input(
                "Citations: "
            ).strip()

            if value:

                metadata["citations"] = [
                    item.strip()
                    for item in value.split("|")
                    if item.strip()
                ]

                print(
                    "\n✓ Citations updated."
                )

        # ----------------------------------------------------
        # Legal Topics
        # ----------------------------------------------------

        elif choice == "9":

            print(
                "\nCurrent legal topics:"
            )

            for topic in metadata.get(
                "legal_topics",
                []
            ):

                print(
                    f"- {topic}"
                )

            print(
                "\nEnter topics separated by |"
            )

            value = input(
                "Legal Topics: "
            ).strip()

            if value:

                metadata["legal_topics"] = [
                    item.strip()
                    for item in value.split("|")
                    if item.strip()
                ]

                print(
                    "\n✓ Legal topics updated."
                )

        # ----------------------------------------------------
        # Continue
        # ----------------------------------------------------

        elif choice == "10":

            break

        else:

            print(
                "\nInvalid choice."
            )

    return metadata


# ============================================================
# SAVE JSON
# ============================================================

def save_json(
    output_path,
    metadata,
    sections,
    source_pdf
):

    document = {

        "source_pdf": str(
            source_pdf
        ),

        "metadata": metadata,

        "sections": sections
    }

    with open(
        output_path,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            document,
            file,
            indent=4,
            ensure_ascii=False
        )


# ============================================================
# PROCESS ONE PDF
# ============================================================

def process_pdf(pdf_path):

    print("\n")
    print("=" * 70)
    print("LEGAL MIND AI - JUDGMENT JSON BUILDER")
    print("=" * 70)

    print(
        f"\nPDF:\n{pdf_path}"
    )

    # --------------------------------------------------------
    # Extract PDF
    # --------------------------------------------------------

    print(
        "\nExtracting PDF..."
    )

    pages = extract_text_from_pdf(
        pdf_path
    )

    print(
        f"✓ Extracted {len(pages)} pages."
    )

    # --------------------------------------------------------
    # Extract metadata
    # --------------------------------------------------------

    print(
        "\nExtracting metadata..."
    )

    metadata = extract_metadata(
        pages
    )

    print(
        "✓ Metadata extracted."
    )

    display_metadata(
        metadata
    )

    # --------------------------------------------------------
    # Edit metadata
    # --------------------------------------------------------

    answer = input(
        "\nDo you want to edit the metadata? (y/n): "
    ).strip().lower()

    if answer == "y":

        metadata = edit_metadata(
            metadata
        )

    # --------------------------------------------------------
    # Extract sections
    # --------------------------------------------------------

    print(
        "\nExtracting judgment sections..."
    )

    sections = extract_document_sections(
        pages
    )

    # --------------------------------------------------------
    # Final verification
    # --------------------------------------------------------

    print("\n")
    print("=" * 70)
    print("FINAL VERIFICATION")
    print("=" * 70)

    display_metadata(
        metadata
    )

    print("\nSections:")

    print(
        "  Acts:",
        len(
            sections.get(
                "acts",
                []
            )
        )
    )

    print(
        "  Headnote:",
        "YES"
        if sections.get("headnote")
        else "NO"
    )

    print(
        "  Judgment:",
        "YES"
        if sections.get("judgment")
        else "NO"
    )

    print(
        "  Verdict:",
        "YES"
        if sections.get("verdict")
        else "NO"
    )

    # --------------------------------------------------------
    # Save confirmation
    # --------------------------------------------------------

    confirm = input(
        "\nSave this verified JSON? (y/n): "
    ).strip().lower()

    if confirm != "y":

        print(
            "\n✗ JSON was not saved."
        )

        return

    # ========================================================
    # AUTOMATIC OUTPUT FILE NAME
    # ========================================================

    print("\n")
    print("=" * 70)
    print("SAVE VERIFIED JSON")
    print("=" * 70)

    print(
        f"\nOutput folder:"
        f"\n{OUTPUT_FOLDER}"
    )

    # Same filename as PDF,
    # only extension changes to .json.
    output_name = (
        pdf_path.stem
        + ".json"
    )

    output_path = (
        OUTPUT_FOLDER
        / output_name
    )

    print(
        f"\nOutput file:"
        f"\n{output_path}"
    )

    # --------------------------------------------------------
    # Existing file check
    # --------------------------------------------------------

    if output_path.exists():

        overwrite = input(
            "\nThis JSON already exists. "
            "Overwrite? (y/n): "
        ).strip().lower()

        if overwrite != "y":

            print(
                "\n✗ JSON was not saved."
            )

            return

    # --------------------------------------------------------
    # SAVE
    # --------------------------------------------------------

    save_json(
        output_path,
        metadata,
        sections,
        pdf_path
    )

    print("\n")
    print("=" * 70)
    print("✓ VERIFIED JSON SAVED")
    print("=" * 70)

    print(
        f"\n{output_path}"
    )


# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":

    print("\n")
    print("=" * 70)
    print("LEGAL MIND AI - SINGLE JUDGMENT PROCESSOR")
    print("=" * 70)

    # --------------------------------------------------------
    # Automatically find PDFs
    # --------------------------------------------------------

    pdf_path = select_pdf_from_raw()

    if pdf_path is None:

        exit()

    print(
        f"\nSelected PDF:"
        f"\n{pdf_path}"
    )

    process_pdf(
        Path(pdf_path)
    )