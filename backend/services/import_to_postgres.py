from pathlib import Path
import json
import psycopg2


# ============================================================
# DATABASE CONFIGURATION
# ============================================================

DB_CONFIG = {
    "host": "localhost",
    "port": 5432,
    "database": "legal_mind_ai",
    "user": "postgres",
    "password": "Ziy@1234"
}


# ============================================================
# DATA VALIDATION
# ============================================================

def validate_document(data):
    """
    Validate a processed JSON document before importing it.

    Only clearly broken documents are rejected.

    Optional metadata such as:
        petitioner
        respondent
        judges
        court
        case_number
        citations
        legal_topics
        acts
        headnote
        verdict

    is allowed to be missing.
    """

    reasons = []

    # --------------------------------------------------------
    # Document ID
    # --------------------------------------------------------

    document_id = data.get("document_id")

    if not document_id:
        reasons.append("missing document_id")

    # --------------------------------------------------------
    # Filename
    # --------------------------------------------------------

    filename = data.get("filename")

    if not filename:
        reasons.append("missing filename")

    # --------------------------------------------------------
    # Case Name
    # --------------------------------------------------------

    case_name = data.get("case_name")

    if not case_name:

        reasons.append("missing case_name")

    else:

        case_lower = case_name.strip().lower()

        # Clearly invalid extracted case names
        invalid_case_names = {
            "vs",
            "v",
            "v.",
            "versus",
            "re",
            "reportable",
            "judgment",
            "order"
        }

        if case_lower in invalid_case_names:

            reasons.append(
                "invalid case_name"
            )

        # PDF extraction artifacts
        if "...appe" in case_lower:

            reasons.append(
                "case_name contains ...APPE artifact"
            )

        if "....re" in case_lower:

            reasons.append(
                "case_name contains ....RE artifact"
            )

    # --------------------------------------------------------
    # Judgment
    # --------------------------------------------------------

    judgment = data.get("judgment")

    if not judgment:

        reasons.append(
            "missing judgment"
        )

    elif not isinstance(judgment, str):

        reasons.append(
            "judgment is not text"
        )

    return reasons


# ============================================================
# MAIN IMPORT FUNCTION
# ============================================================

def main():

    print("\n" + "=" * 80)
    print("LEGAL MIND AI - IMPORT DOCUMENTS V2")
    print("=" * 80)

    # --------------------------------------------------------
    # JSON FOLDER
    # --------------------------------------------------------

    processed_folder = Path(
        "data/processed_v2"
    )

    if not processed_folder.exists():

        print(
            "\nERROR: Folder not found:"
        )

        print(
            processed_folder
        )

        return

    # --------------------------------------------------------
    # FIND JSON FILES
    # --------------------------------------------------------

    json_files = sorted(
        f
        for f in processed_folder.glob("*.json")
        if f.name != "processing_errors.json"
        and f.name != "data_quality_report.json"
        and f.name != "import_rejections.json"
    )

    total = len(json_files)

    print(
        f"\nJSON files found: {total}"
    )

    if total == 0:

        print(
            "\nNo JSON files found."
        )

        return

    # --------------------------------------------------------
    # CONNECT TO POSTGRESQL
    # --------------------------------------------------------

    print(
        "\nConnecting to PostgreSQL..."
    )

    try:

        connection = psycopg2.connect(
            **DB_CONFIG
        )

        cursor = connection.cursor()

        print(
            "PostgreSQL connection successful."
        )

    except Exception as e:

        print(
            "\nDATABASE CONNECTION FAILED"
        )

        print(e)

        return

    # --------------------------------------------------------
    # COUNTERS
    # --------------------------------------------------------

    imported = 0
    rejected = 0
    invalid_json = 0
    database_errors = 0

    rejection_reasons = {}

    rejected_files = []

    # --------------------------------------------------------
    # PROCESS JSON FILES
    # --------------------------------------------------------

    for index, json_path in enumerate(
        json_files,
        start=1
    ):

        # ----------------------------------------------------
        # Progress
        # ----------------------------------------------------

        if index == 1 or index % 500 == 0:

            print(
                f"\nProcessing "
                f"[{index}/{total}]"
            )

        # ----------------------------------------------------
        # READ JSON
        # ----------------------------------------------------

        try:

            with open(
                json_path,
                "r",
                encoding="utf-8"
            ) as file:

                data = json.load(file)

        except Exception as e:

            invalid_json += 1

            rejected_files.append({
                "file": json_path.name,
                "reasons": [
                    f"invalid JSON: {str(e)}"
                ]
            })

            continue

        # ----------------------------------------------------
        # VALIDATE JSON
        # ----------------------------------------------------

        reasons = validate_document(
            data
        )

        if reasons:

            rejected += 1

            for reason in reasons:

                rejection_reasons[reason] = (
                    rejection_reasons.get(
                        reason,
                        0
                    ) + 1
                )

            rejected_files.append({
                "file": json_path.name,
                "document_id": data.get(
                    "document_id"
                ),
                "case_name": data.get(
                    "case_name"
                ),
                "reasons": reasons
            })

            continue

        # ----------------------------------------------------
        # GET VALUES
        # ----------------------------------------------------

        document_id = data.get(
            "document_id"
        )

        filename = data.get(
            "filename"
        )

        case_name = data.get(
            "case_name"
        )

        petitioner = data.get(
            "petitioner"
        )

        respondent = data.get(
            "respondent"
        )

        judges = data.get(
            "judges"
        ) or []

        court = data.get(
            "court"
        )

        judgment_date = data.get(
            "judgment_date"
        )

        case_number = data.get(
            "case_number"
        )

        citations = data.get(
            "citations"
        ) or []

        legal_topics = data.get(
            "legal_topics"
        ) or []

        acts = data.get(
            "acts"
        ) or []

        headnote = data.get(
            "headnote"
        )

        judgment = data.get(
            "judgment"
        )

        verdict = data.get(
            "verdict"
        )

        # ----------------------------------------------------
        # DATABASE INSERT
        # ----------------------------------------------------

        try:

            # Create savepoint for this document
            cursor.execute(
                "SAVEPOINT document_insert"
            )

            cursor.execute(
                """
                INSERT INTO documents_v2 (
                    document_id,
                    filename,
                    case_name,
                    petitioner,
                    respondent,
                    judges,
                    court,
                    judgment_date,
                    case_number,
                    citations,
                    legal_topics,
                    acts,
                    headnote,
                    judgment,
                    verdict
                )
                VALUES (
                    %s, %s, %s, %s, %s,
                    %s, %s, %s, %s, %s,
                    %s, %s, %s, %s, %s
                )

                ON CONFLICT (document_id)
                DO UPDATE SET

                    filename = EXCLUDED.filename,

                    case_name = EXCLUDED.case_name,

                    petitioner = EXCLUDED.petitioner,

                    respondent = EXCLUDED.respondent,

                    judges = EXCLUDED.judges,

                    court = EXCLUDED.court,

                    judgment_date = EXCLUDED.judgment_date,

                    case_number = EXCLUDED.case_number,

                    citations = EXCLUDED.citations,

                    legal_topics = EXCLUDED.legal_topics,

                    acts = EXCLUDED.acts,

                    headnote = EXCLUDED.headnote,

                    judgment = EXCLUDED.judgment,

                    verdict = EXCLUDED.verdict
                """,

                (
                    document_id,
                    filename,
                    case_name,
                    petitioner,
                    respondent,
                    judges,
                    court,
                    judgment_date,
                    case_number,
                    citations,
                    legal_topics,
                    acts,
                    headnote,
                    judgment,
                    verdict
                )
            )

            # Release savepoint
            cursor.execute(
                "RELEASE SAVEPOINT document_insert"
            )

            imported += 1

        except Exception as e:

            # Roll back ONLY this document
            try:

                cursor.execute(
                    "ROLLBACK TO SAVEPOINT document_insert"
                )

                cursor.execute(
                    "RELEASE SAVEPOINT document_insert"
                )

            except Exception:
                pass

            database_errors += 1
            rejected += 1

            reason = (
                f"database error: {str(e)}"
            )

            rejection_reasons[reason] = (
                rejection_reasons.get(
                    reason,
                    0
                ) + 1
            )

            rejected_files.append({
                "file": json_path.name,
                "document_id": document_id,
                "case_name": case_name,
                "reasons": [
                    reason
                ]
            })

            continue

        # ----------------------------------------------------
        # COMMIT EVERY 500 SUCCESSFUL RECORDS
        # ----------------------------------------------------

        if imported > 0 and imported % 500 == 0:

            connection.commit()

            print(
                f"Imported {imported} documents..."
            )

    # --------------------------------------------------------
    # FINAL COMMIT
    # --------------------------------------------------------

    connection.commit()

    # --------------------------------------------------------
    # CLOSE DATABASE
    # --------------------------------------------------------

    cursor.close()
    connection.close()

    # ========================================================
    # SAVE REJECTION LOG
    # ========================================================

    if rejected_files:

        rejection_log = (
            processed_folder /
            "import_rejections.json"
        )

        with open(
            rejection_log,
            "w",
            encoding="utf-8"
        ) as file:

            json.dump(
                rejected_files,
                file,
                ensure_ascii=False,
                indent=4
            )

    # ========================================================
    # FINAL REPORT
    # ========================================================

    print("\n")
    print("=" * 80)
    print("IMPORT COMPLETE")
    print("=" * 80)

    print(
        f"\nTotal JSON files : {total}"
    )

    print(
        f"Imported         : {imported}"
    )

    print(
        f"Rejected         : {rejected}"
    )

    print(
        f"Invalid JSON     : {invalid_json}"
    )

    print(
        f"Database errors  : {database_errors}"
    )

    # --------------------------------------------------------
    # Rejection reasons
    # --------------------------------------------------------

    if rejection_reasons:

        print("\n" + "-" * 80)
        print("REJECTION REASONS")
        print("-" * 80)

        for reason, count in sorted(
            rejection_reasons.items(),
            key=lambda item: item[1],
            reverse=True
        ):

            print(
                f"{reason}: {count}"
            )

    # --------------------------------------------------------
    # Rejection log
    # --------------------------------------------------------

    if rejected_files:

        print(
            "\nRejected file details saved to:"
        )

        print(
            processed_folder /
            "import_rejections.json"
        )

    print("\n" + "=" * 80)


# ============================================================
# RUN
# ============================================================

if __name__ == "__main__":
    main()