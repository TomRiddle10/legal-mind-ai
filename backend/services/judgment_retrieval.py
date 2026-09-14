from services.database import get_connection
import re


# ============================================================
# CLEAN RESPONDENT
# ============================================================

def clean_respondent(value):
    """
    Clean respondent names extracted from judgments.

    Example:
        'Nasreen Ahmed on 6 March, 2017'
        ->
        'Nasreen Ahmed'
    """

    if not value:
        return value

    value = value.strip()

    value = re.sub(
        r"\s+on\s+\d{1,2}\s+[A-Za-z]+,?\s+\d{4}.*$",
        "",
        value,
        flags=re.IGNORECASE
    )

    return value.strip()


# ============================================================
# SEARCH JUDGMENTS
# ============================================================

def search_judgments(query, page=1, limit=20):
    """
    Search judgments using document-level metadata
    from documents_v2.

    This search is separate from the RAG/vector search
    used by the chatbot.

    Searches:
        - case_name
        - petitioner
        - respondent
        - judges
        - court
        - case_number
        - citations
        - legal_topics
        - acts
        - judgment_date

    Supports pagination.
    """

    query = (query or "").strip()

    if not query:
        return {
            "results": [],
            "total": 0,
            "page": page,
            "limit": limit,
            "total_pages": 0
        }

    # ========================================================
    # VALIDATE PAGINATION
    # ========================================================

    try:
        page = int(page)
    except (TypeError, ValueError):
        page = 1

    try:
        limit = int(limit)
    except (TypeError, ValueError):
        limit = 20

    page = max(page, 1)

    # Prevent extremely large requests
    limit = min(max(limit, 1), 100)

    offset = (page - 1) * limit

    search_pattern = f"%{query}%"

    conn = get_connection()
    cursor = conn.cursor()

    try:

        # ====================================================
        # TOTAL COUNT
        # ====================================================

        cursor.execute(
            """
            SELECT COUNT(*)
            FROM documents_v2

            WHERE
                case_name ILIKE %s

                OR petitioner ILIKE %s

                OR respondent ILIKE %s

                OR court ILIKE %s

                OR EXISTS (
                    SELECT 1
                    FROM unnest(judges) AS judge
                    WHERE judge ILIKE %s
                )

                OR case_number ILIKE %s

                OR EXISTS (
                    SELECT 1
                    FROM unnest(citations) AS citation
                    WHERE citation ILIKE %s
                )

                OR EXISTS (
                    SELECT 1
                    FROM unnest(legal_topics) AS topic
                    WHERE topic ILIKE %s
                )

                OR EXISTS (
                    SELECT 1
                    FROM unnest(acts) AS act
                    WHERE act ILIKE %s
                )

                OR TO_CHAR(
                    judgment_date,
                    'DD Month YYYY'
                ) ILIKE %s

                OR TO_CHAR(
                    judgment_date,
                    'YYYY'
                ) ILIKE %s
            """,
            (
                search_pattern,   # case_name
                search_pattern,   # petitioner
                search_pattern,   # respondent
                search_pattern,   # court
                search_pattern,   # judges
                search_pattern,   # case_number
                search_pattern,   # citations
                search_pattern,   # legal_topics
                search_pattern,   # acts
                search_pattern,   # date
                search_pattern    # year
            )
        )

        total = cursor.fetchone()[0]

        # ====================================================
        # SEARCH RESULTS
        # ====================================================

        cursor.execute(
            """
            SELECT
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
                verdict,

                (
                    CASE

                        -- Exact case name
                        WHEN LOWER(case_name) = LOWER(%s)
                            THEN 100

                        -- Case name contains query
                        WHEN case_name ILIKE %s
                            THEN 90

                        -- Petitioner
                        WHEN petitioner ILIKE %s
                            THEN 80

                        -- Respondent
                        WHEN respondent ILIKE %s
                            THEN 80

                        -- Judge
                        WHEN EXISTS (
                            SELECT 1
                            FROM unnest(judges) AS judge
                            WHERE judge ILIKE %s
                        )
                            THEN 75

                        -- Citation
                        WHEN EXISTS (
                            SELECT 1
                            FROM unnest(citations) AS citation
                            WHERE citation ILIKE %s
                        )
                            THEN 70

                        -- Case number
                        WHEN case_number ILIKE %s
                            THEN 65

                        -- Legal topic
                        WHEN EXISTS (
                            SELECT 1
                            FROM unnest(legal_topics) AS topic
                            WHERE topic ILIKE %s
                        )
                            THEN 60

                        -- Act
                        WHEN EXISTS (
                            SELECT 1
                            FROM unnest(acts) AS act
                            WHERE act ILIKE %s
                        )
                            THEN 55

                        -- Court
                        WHEN court ILIKE %s
                            THEN 50

                        -- Judgment date
                        WHEN TO_CHAR(
                            judgment_date,
                            'DD Month YYYY'
                        ) ILIKE %s
                            THEN 45

                        -- Year
                        WHEN TO_CHAR(
                            judgment_date,
                            'YYYY'
                        ) ILIKE %s
                            THEN 40

                        ELSE 10

                    END
                ) AS relevance_score

            FROM documents_v2

            WHERE
                case_name ILIKE %s

                OR petitioner ILIKE %s

                OR respondent ILIKE %s

                OR court ILIKE %s

                OR EXISTS (
                    SELECT 1
                    FROM unnest(judges) AS judge
                    WHERE judge ILIKE %s
                )

                OR case_number ILIKE %s

                OR EXISTS (
                    SELECT 1
                    FROM unnest(citations) AS citation
                    WHERE citation ILIKE %s
                )

                OR EXISTS (
                    SELECT 1
                    FROM unnest(legal_topics) AS topic
                    WHERE topic ILIKE %s
                )

                OR EXISTS (
                    SELECT 1
                    FROM unnest(acts) AS act
                    WHERE act ILIKE %s
                )

                OR TO_CHAR(
                    judgment_date,
                    'DD Month YYYY'
                ) ILIKE %s

                OR TO_CHAR(
                    judgment_date,
                    'YYYY'
                ) ILIKE %s

            ORDER BY
                relevance_score DESC,
                judgment_date DESC NULLS LAST,
                case_name ASC

            LIMIT %s
            OFFSET %s
            """,
            (
                # =================================================
                # RELEVANCE PARAMETERS
                # =================================================

                query,            # exact case name
                search_pattern,   # case name
                search_pattern,   # petitioner
                search_pattern,   # respondent
                search_pattern,   # judge
                search_pattern,   # citation
                search_pattern,   # case number
                search_pattern,   # legal topic
                search_pattern,   # act
                search_pattern,   # court
                search_pattern,   # date
                search_pattern,   # year

                # =================================================
                # WHERE PARAMETERS
                # =================================================

                search_pattern,   # case name
                search_pattern,   # petitioner
                search_pattern,   # respondent
                search_pattern,   # court
                search_pattern,   # judge
                search_pattern,   # case number
                search_pattern,   # citation
                search_pattern,   # legal topic
                search_pattern,   # act
                search_pattern,   # date
                search_pattern,   # year

                # =================================================
                # PAGINATION
                # =================================================

                limit,
                offset
            )
        )

        rows = cursor.fetchall()

    finally:

        cursor.close()
        conn.close()

    # ========================================================
    # FORMAT RESULTS
    # ========================================================

    results = []

    for row in rows:

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
            verdict,
            relevance_score
        ) = row

        results.append({

            "document_id": document_id,

            "filename": filename,

            "case_name": case_name,

            "petitioner": petitioner,

            "respondent": clean_respondent(
                respondent
            ),

            "judges": judges or [],

            "court": court,

            "judgment_date": (
                judgment_date.isoformat()
                if judgment_date
                else None
            ),

            "case_number": case_number,

            "citations": citations or [],

            "legal_topics": legal_topics or [],

            "acts": acts or [],

            "headnote": headnote,

            "verdict": verdict,

            "relevance_score": relevance_score

        })

    # ========================================================
    # TOTAL PAGES
    # ========================================================

    total_pages = (
        (total + limit - 1) // limit
        if total > 0
        else 0
    )

    return {

        "results": results,

        "total": total,

        "page": page,

        "limit": limit,

        "total_pages": total_pages

    }


# ============================================================
# TEST
# ============================================================

if __name__ == "__main__":

    query = input(
        "\nEnter judgment search query: "
    ).strip()

    if not query:
        print("Please enter a search query.")
        exit()

    print("\nSearching judgments...")

    response = search_judgments(
        query,
        page=1,
        limit=20
    )

    results = response["results"]

    print("\n")
    print("=" * 80)
    print("JUDGMENT SEARCH RESULTS")
    print("=" * 80)

    print(
        f"\nFound {response['total']} judgments."
    )

    print(
        f"Showing page {response['page']} "
        f"of {response['total_pages']}."
    )

    for index, result in enumerate(
        results,
        start=1
    ):

        print("\n" + "-" * 80)

        print(
            f"Result {index}"
        )

        print(
            "Case:",
            result["case_name"]
        )

        print(
            "Petitioner:",
            result["petitioner"]
        )

        print(
            "Respondent:",
            result["respondent"]
        )

        print(
            "Judges:",
            ", ".join(
                result["judges"]
            )
        )

        print(
            "Court:",
            result["court"]
        )

        print(
            "Date:",
            result["judgment_date"]
        )

        print(
            "Case Number:",
            result["case_number"]
        )

        print(
            "Document ID:",
            result["document_id"]
        )

        print(
            "Relevance:",
            result["relevance_score"]
        )

        if result["citations"]:

            print(
                "Citations:",
                ", ".join(
                    result["citations"]
                )
            )

        if result["legal_topics"]:

            print(
                "Legal Topics:",
                ", ".join(
                    result["legal_topics"]
                )
            )

        if result["acts"]:

            print(
                "Acts:",
                ", ".join(
                    result["acts"]
                )
            )

    print("\n" + "=" * 80)