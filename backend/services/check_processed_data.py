from pathlib import Path
import json
from collections import Counter


def check_data():

    folder = Path("data/processed_v2")

    print("\n" + "=" * 80)
    print("LEGAL MIND AI - JSON DATA QUALITY CHECK")
    print("=" * 80)

    if not folder.exists():
        print(f"\nERROR: Folder not found: {folder}")
        return

    # --------------------------------------------------------
    # Find JSON files
    # --------------------------------------------------------

    json_files = [
        f for f in folder.glob("*.json")
        if f.name != "processing_errors.json"
    ]

    json_files.sort()

    total = len(json_files)

    print(f"\nFolder: {folder}")
    print(f"JSON files found: {total}")

    if total == 0:
        print("\nNo JSON files found.")
        return

    # --------------------------------------------------------
    # Counters
    # --------------------------------------------------------

    valid_json = 0
    invalid_json = 0

    missing_case_name = 0
    missing_petitioner = 0
    missing_respondent = 0
    missing_judges = 0
    missing_court = 0
    missing_date = 0
    missing_case_number = 0
    missing_judgment = 0
    missing_verdict = 0

    empty_citations = 0
    empty_legal_topics = 0
    empty_acts = 0
    empty_headnote = 0

    short_judgments = 0

    suspicious_data = []

    document_ids = []
    filenames = []

    # --------------------------------------------------------
    # Process JSON files
    # --------------------------------------------------------

    for index, json_path in enumerate(json_files, start=1):

        try:

            with open(
                json_path,
                "r",
                encoding="utf-8"
            ) as file:

                data = json.load(file)

            valid_json += 1

            # ----------------------------------------------
            # Basic fields
            # ----------------------------------------------

            case_name = data.get("case_name")
            petitioner = data.get("petitioner")
            respondent = data.get("respondent")
            judges = data.get("judges")
            court = data.get("court")
            judgment_date = data.get("judgment_date")
            case_number = data.get("case_number")
            judgment = data.get("judgment")
            verdict = data.get("verdict")

            citations = data.get("citations")
            legal_topics = data.get("legal_topics")
            acts = data.get("acts")
            headnote = data.get("headnote")

            document_id = data.get("document_id")
            filename = data.get("filename")

            # ----------------------------------------------
            # Missing values
            # ----------------------------------------------

            if not case_name:
                missing_case_name += 1

            if not petitioner:
                missing_petitioner += 1

            if not respondent:
                missing_respondent += 1

            if not judges:
                missing_judges += 1

            if not court:
                missing_court += 1

            if not judgment_date:
                missing_date += 1

            if not case_number:
                missing_case_number += 1

            if not judgment:
                missing_judgment += 1

            if not verdict:
                missing_verdict += 1

            # ----------------------------------------------
            # Optional fields
            # ----------------------------------------------

            if not citations:
                empty_citations += 1

            if not legal_topics:
                empty_legal_topics += 1

            if not acts:
                empty_acts += 1

            if not headnote:
                empty_headnote += 1

            # ----------------------------------------------
            # Short judgment detection
            # ----------------------------------------------

            if judgment:

                if len(judgment.strip()) < 500:
                    short_judgments += 1

            # ----------------------------------------------
            # Suspicious extraction
            # ----------------------------------------------

            suspicious_reasons = []

            combined_text = " ".join(
                str(data.get(field) or "")
                for field in [
                    "case_name",
                    "petitioner",
                    "respondent",
                    "judgment",
                    "verdict"
                ]
            )

            if "Indian Kanoon -" in combined_text:
                suspicious_reasons.append(
                    "Indian Kanoon footer"
                )

            if "http://" in combined_text or \
               "https://" in combined_text:
                suspicious_reasons.append(
                    "URL present"
                )

            if case_name and (
                "...APPE" in case_name or
                "....RE" in case_name or
                case_name.strip() == "RE"
            ):
                suspicious_reasons.append(
                    "PDF extraction artifact in case name"
                )

            if judgment and case_name:

                # Check whether the exact case title
                # appears repeatedly in the judgment.
                occurrences = judgment.lower().count(
                    case_name.lower()
                )

                if occurrences > 1:
                    suspicious_reasons.append(
                        f"Repeated case title ({occurrences} times)"
                    )

            if suspicious_reasons:

                suspicious_data.append({
                    "file": json_path.name,
                    "case_name": case_name,
                    "reasons": suspicious_reasons
                })

            # ----------------------------------------------
            # Duplicate detection
            # ----------------------------------------------

            if document_id:
                document_ids.append(document_id)

            if filename:
                filenames.append(filename)

        except Exception as e:

            invalid_json += 1

            suspicious_data.append({
                "file": json_path.name,
                "case_name": None,
                "reasons": [
                    f"INVALID JSON: {str(e)}"
                ]
            })

        # ----------------------------------------------
        # Progress
        # ----------------------------------------------

        if index % 1000 == 0 or index == total:
            print(
                f"Checked {index}/{total} files..."
            )

    # ========================================================
    # DUPLICATES
    # ========================================================

    document_counter = Counter(document_ids)
    filename_counter = Counter(filenames)

    duplicate_document_ids = {
        key: count
        for key, count in document_counter.items()
        if count > 1
    }

    duplicate_filenames = {
        key: count
        for key, count in filename_counter.items()
        if count > 1
    }

    # ========================================================
    # FINAL REPORT
    # ========================================================

    print("\n")
    print("=" * 80)
    print("DATA QUALITY REPORT")
    print("=" * 80)

    print(f"\nTotal JSON files       : {total}")
    print(f"Valid JSON             : {valid_json}")
    print(f"Invalid JSON           : {invalid_json}")

    print("\n" + "-" * 80)
    print("REQUIRED / IMPORTANT FIELDS")
    print("-" * 80)

    print(f"Missing case_name      : {missing_case_name}")
    print(f"Missing petitioner     : {missing_petitioner}")
    print(f"Missing respondent     : {missing_respondent}")
    print(f"Missing judges         : {missing_judges}")
    print(f"Missing court          : {missing_court}")
    print(f"Missing judgment_date  : {missing_date}")
    print(f"Missing case_number    : {missing_case_number}")
    print(f"Missing judgment      : {missing_judgment}")

    print("\n" + "-" * 80)
    print("OPTIONAL / FREQUENTLY EMPTY FIELDS")
    print("-" * 80)

    print(f"Missing verdict        : {missing_verdict}")
    print(f"Empty citations       : {empty_citations}")
    print(f"Empty legal_topics    : {empty_legal_topics}")
    print(f"Empty acts            : {empty_acts}")
    print(f"Empty headnote        : {empty_headnote}")

    print("\n" + "-" * 80)
    print("CONTENT QUALITY")
    print("-" * 80)

    print(f"Very short judgments  : {short_judgments}")
    print(f"Suspicious files      : {len(suspicious_data)}")

    print("\n" + "-" * 80)
    print("DUPLICATES")
    print("-" * 80)

    print(
        f"Duplicate document IDs : "
        f"{len(duplicate_document_ids)}"
    )

    print(
        f"Duplicate filenames    : "
        f"{len(duplicate_filenames)}"
    )

    # ========================================================
    # SHOW SUSPICIOUS FILES
    # ========================================================

    if suspicious_data:

        print("\n" + "-" * 80)
        print("FIRST 30 SUSPICIOUS FILES")
        print("-" * 80)

        for item in suspicious_data[:30]:

            print(f"\nFile: {item['file']}")
            print(f"Case: {item['case_name']}")
            print(
                "Reason: " +
                ", ".join(item["reasons"])
            )

    # ========================================================
    # SAVE REPORT
    # ========================================================

    report_path = folder / "data_quality_report.json"

    report = {

        "total_files": total,

        "valid_json": valid_json,
        "invalid_json": invalid_json,

        "missing_case_name": missing_case_name,
        "missing_petitioner": missing_petitioner,
        "missing_respondent": missing_respondent,
        "missing_judges": missing_judges,
        "missing_court": missing_court,
        "missing_judgment_date": missing_date,
        "missing_case_number": missing_case_number,
        "missing_judgment": missing_judgment,

        "missing_verdict": missing_verdict,
        "empty_citations": empty_citations,
        "empty_legal_topics": empty_legal_topics,
        "empty_acts": empty_acts,
        "empty_headnote": empty_headnote,

        "short_judgments": short_judgments,

        "suspicious_files": suspicious_data,

        "duplicate_document_ids":
            duplicate_document_ids,

        "duplicate_filenames":
            duplicate_filenames
    }

    with open(
        report_path,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            report,
            file,
            ensure_ascii=False,
            indent=4
        )

    print("\n")
    print("=" * 80)
    print("CHECK COMPLETE")
    print("=" * 80)

    print(
        f"\nFull report saved to:\n"
        f"{report_path}"
    )


if __name__ == "__main__":
    check_data()