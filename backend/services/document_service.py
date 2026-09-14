from pathlib import Path
import re

import pymupdf


# ============================================================
# PDF EXTRACTION
# ============================================================

def extract_text_from_pdf(pdf_path):
    pdf_path = Path(pdf_path)

    if not pdf_path.exists():
        raise FileNotFoundError(f"PDF not found: {pdf_path}")

    document = pymupdf.open(pdf_path)

    pages = []

    for page_number, page in enumerate(document, start=1):

        raw_text = page.get_text("text").strip()

        cleaned_text = clean_page_text(raw_text)

        pages.append({
            "page": page_number,
            "raw_text": raw_text,
            "text": cleaned_text
        })

    document.close()

    # ---------------------------------------------------------
    # Find the case name from page 1
    # ---------------------------------------------------------
    full_initial_text = pages[0]["text"] if pages else ""

    case_name = extract_case_name(full_initial_text)

    # ---------------------------------------------------------
    # Remove repeated case title from pages 2+
    # ---------------------------------------------------------
    if case_name:

        for page in pages[1:]:

            page["text"] = remove_repeated_case_header(
                page["text"],
                case_name
            )

    return pages

def remove_repeated_case_header(text, case_name):
    """
    Remove the repeated case-name header/footer from a page.

    Only removes the exact known case name.
    It does NOT remove arbitrary sentences containing
    'vs', 'v.' or 'versus'.
    """

    if not text or not case_name:
        return text

    # ---------------------------------------------------------
    # Normalize case name for regex
    # ---------------------------------------------------------
    escaped_case_name = re.escape(case_name)

    # ---------------------------------------------------------
    # Case title + date on the SAME line
    #
    # Example:
    # United India Insurance Co. Ltd. vs Sushil Kumar Godara
    # on 30 September, 2021
    # ---------------------------------------------------------
    pattern_same_line = (
        escaped_case_name +
        r"\s+on\s+\d{1,2}\s+[A-Za-z]+,?\s*\d{4}"
    )

    text = re.sub(
        pattern_same_line,
        "",
        text,
        flags=re.IGNORECASE
    )

    # ---------------------------------------------------------
    # Case title + date SPLIT across lines
    #
    # Example:
    # United India Insurance Co. Ltd. vs Sushil Kumar Godara on 30
    # September, 2021
    # ---------------------------------------------------------
    pattern_split = (
        escaped_case_name +
        r"\s+on\s+\d{1,2}\s*\n"
        r"\s*[A-Za-z]+,?\s*\d{4}"
    )

    text = re.sub(
        pattern_split,
        "",
        text,
        flags=re.IGNORECASE
    )

    # ---------------------------------------------------------
    # Clean resulting whitespace
    # ---------------------------------------------------------
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)

    return text.strip()
# ============================================================
# PAGE CLEANING
# ============================================================

def clean_page_text(text, remove_case_header=True):
    """
    Basic PDF text cleaning.

    Does NOT try to identify arbitrary case titles.
    """

    if not text:
        return ""

    lines = text.splitlines()
    cleaned_lines = []

    for line in lines:
        line = line.strip()

        if not line:
            continue

        # Remove Indian Kanoon footer
        if re.search(r"Indian\s+Kanoon\s*-", line, re.IGNORECASE):
            continue

        # Remove URL
        if re.search(r"https?://", line, re.IGNORECASE):
            continue

        # Remove standalone page numbers
        if re.fullmatch(r"\d+", line):
            continue

        cleaned_lines.append(line)

    text = "\n".join(cleaned_lines)

    # Normalize spaces
    text = re.sub(r"[ \t]+", " ", text)

    # Normalize blank lines
    text = re.sub(r"\n{3,}", "\n\n", text)

    return text.strip()

# ============================================================
# FULL TEXT
# ============================================================

def get_full_text(pages):
    """
    Combine cleaned text from all pages.
    """

    return "\n\n".join(
        page["text"]
        for page in pages
        if page.get("text")
    )


# ============================================================
# CASE NAME
# ============================================================

def extract_case_name(full_text):
    """
    Extract case name from the beginning of the judgment.

    Handles both:
        Party A vs Party B on 15 November, 2017

    and:
        Party A vs Party B on 30
        September, 2021
    """

    lines = [
        line.strip()
        for line in full_text.splitlines()
        if line.strip()
    ]

    if not lines:
        return None

    # Look only near the beginning of the document
    for i, line in enumerate(lines[:25]):

        if not re.search(
            r"\b(?:vs\.?|v\.|versus)\b",
            line,
            re.IGNORECASE
        ):
            continue

        case_name = line

        # ---------------------------------------------------------
        # Handle date split across two lines
        #
        # Example:
        # United India ... Godara on 30
        # September, 2021
        # ---------------------------------------------------------
        if re.search(
            r"\bon\s+\d{1,2}\s*$",
            case_name,
            re.IGNORECASE
        ):
            if i + 1 < len(lines):
                next_line = lines[i + 1]

                if re.match(
                    r"^[A-Za-z]+\s*,?\s*\d{4}",
                    next_line
                ):
                    case_name += " " + next_line

        # ---------------------------------------------------------
        # Remove date
        # ---------------------------------------------------------
        case_name = re.sub(
            r"\s+on\s+\d{1,2}\s+[A-Za-z]+,?\s*\d{4}.*$",
            "",
            case_name,
            flags=re.IGNORECASE
        )

        # ---------------------------------------------------------
        # Remove metadata if it appears on same line
        # ---------------------------------------------------------
        case_name = re.split(
            r"\b(?:Equivalent citations?|Author|Bench|REPORTABLE|JUDGMENT)\b",
            case_name,
            maxsplit=1,
            flags=re.IGNORECASE
        )[0]

        case_name = clean_value(case_name)

        if case_name:
            return case_name

    return None
# ============================================================
# PETITIONER
# ============================================================

def extract_petitioner(full_text):
    """
    Extract petitioner from the case name.

    Example:
        Chirag M. Pathak vs Dollyben Kantilal Patel

    Returns:
        Chirag M. Pathak
    """

    case_name = extract_case_name(full_text)

    if not case_name:
        return None

    match = re.split(
        r"\s+\b(?:vs\.?|v\.|versus)\b\s+",
        case_name,
        maxsplit=1,
        flags=re.IGNORECASE
    )

    if len(match) == 2:
        petitioner = match[0].strip()

        # Remove common multi-party suffix
        petitioner = re.sub(
            r"\s*&\s*Ors\.?$",
            "",
            petitioner,
            flags=re.IGNORECASE
        )

        petitioner = clean_value(petitioner)

        return petitioner if petitioner else None

    return None

# ============================================================
# RESPONDENT CLEANING
# ============================================================

def clean_respondent_value(value):
    """
    Clean respondent metadata.
    """

    if not value:
        return None

    value = value.strip()

    # Remove Respondent / Respondents marker.
    value = re.sub(
        r"\s*(?:\.{2,}|…+|[.…]+)?\s*"
        r"Respondent(?:s)?\b.*$",
        "",
        value,
        flags=re.IGNORECASE
    )

    # Remove date suffix.
    value = re.sub(
        r"\s+on\s+"
        r"\d{1,2}\s+[A-Za-z]+,?\s+\d{4}.*$",
        "",
        value,
        flags=re.IGNORECASE
    )

    # Remove trailing punctuation.
    value = re.sub(
        r"[.…\s]+$",
        "",
        value
    )

    return clean_value(value)
# ============================================================
# RESPONDENT
# ============================================================

def extract_respondent(full_text):
    """
    Extract respondent from the case name.

    Example:
        Chirag M. Pathak vs Dollyben Kantilal Patel

    Returns:
        Dollyben Kantilal Patel
    """

    case_name = extract_case_name(full_text)

    if not case_name:
        return None

    match = re.split(
        r"\s+\b(?:vs\.?|v\.|versus)\b\s+",
        case_name,
        maxsplit=1,
        flags=re.IGNORECASE
    )

    if len(match) == 2:
        respondent = match[1].strip()

        # Remove common multi-party suffix
        respondent = re.sub(
            r"\s*&\s*Ors\.?$",
            "",
            respondent,
            flags=re.IGNORECASE
        )

        respondent = clean_value(respondent)

        return respondent if respondent else None

    return None
# ============================================================
# JUDGMENT DATE
# ============================================================

def extract_judgment_date(full_text):
    """
    Extract judgment date.
    """

    # --------------------------------------------------------
    # 1. Explicit DATE OF JUDGMENT
    # --------------------------------------------------------

    match = re.search(
        r"DATE\s+OF\s+JUDGMENT\s*:\s*"
        r"\n?\s*"
        r"(\d{1,2}/\d{1,2}/\d{4})",
        full_text,
        re.IGNORECASE
    )

    if match:

        day, month, year = (
            match.group(1).split("/")
        )

        months = [
            "January",
            "February",
            "March",
            "April",
            "May",
            "June",
            "July",
            "August",
            "September",
            "October",
            "November",
            "December"
        ]

        return (
            f"{int(day)} "
            f"{months[int(month) - 1]}, "
            f"{year}"
        )

    # --------------------------------------------------------
    # 2. Numeric date formats
    # --------------------------------------------------------

    match = re.search(
        r"DATE\s+OF\s+JUDGMENT\s*:\s*"
        r"\n?\s*"
        r"(\d{1,2})[-/]"
        r"(\d{1,2})[-/]"
        r"(\d{4})",
        full_text,
        re.IGNORECASE
    )

    if match:

        day = int(match.group(1))
        month = int(match.group(2))
        year = int(match.group(3))

        months = [
            "January",
            "February",
            "March",
            "April",
            "May",
            "June",
            "July",
            "August",
            "September",
            "October",
            "November",
            "December"
        ]

        if 1 <= month <= 12:

            return (
                f"{day} "
                f"{months[month - 1]}, "
                f"{year}"
            )

    # --------------------------------------------------------
    # 3. Case name date
    #
    # Example:
    # A.Kanthamani vs Nasreen Ahmed on 6 March, 2017
    # --------------------------------------------------------

    match = re.search(
        r"\bon\s+"
        r"(\d{1,2}\s+[A-Za-z]+,?\s+\d{4})",
        full_text,
        re.IGNORECASE
    )

    if match:

        return clean_value(
            match.group(1)
        )

    return None


# ============================================================
# JUDGES
# ============================================================

def extract_judges(full_text):
    """
    Extract judges from the Bench metadata.

    Handles:
        Bench: Judge One, Judge Two

    Also cleans PDF extraction artifacts such as:
        RE
        REPORTABLE
        J.
    """

    # ---------------------------------------------------------
    # 1. Look for Bench metadata
    # ---------------------------------------------------------
    match = re.search(
        r"\bBench\s*:\s*(.+)",
        full_text,
        re.IGNORECASE
    )

    if not match:
        return []

    bench_text = match.group(1).strip()

    # ---------------------------------------------------------
    # 2. Remove common PDF extraction artifacts
    # ---------------------------------------------------------
    bench_text = re.sub(
        r"\b(?:REPORTABLE|RE)\b.*$",
        "",
        bench_text,
        flags=re.IGNORECASE
    )

    bench_text = clean_value(bench_text)

    if not bench_text:
        return []

    # ---------------------------------------------------------
    # 3. Split judges by comma
    # ---------------------------------------------------------
    judges = []

    for judge in bench_text.split(","):
        judge = judge.strip()

        # Remove trailing judicial designations
        judge = re.sub(
            r",?\s*\bJ\.?\b$",
            "",
            judge,
            flags=re.IGNORECASE
        )

        judge = clean_value(judge)

        if judge:
            judges.append(judge)

    return judges


# ============================================================
# CITATIONS
# ============================================================

def extract_citations(full_text):
    """
    Extract equivalent citations without capturing
    Author / Bench / other metadata.
    """

    match = re.search(
        r"Equivalent citations?\s*:\s*"
        r"(.*?)(?=\b(?:Author|Bench|REPORTABLE|"
        r"IN\s+THE\s+SUPREME\s+COURT|JUDGMENT)\b)",
        full_text,
        re.IGNORECASE | re.DOTALL
    )

    if not match:
        return []

    citation_text = match.group(1)

    # Normalize whitespace.
    citation_text = re.sub(
        r"\s+",
        " ",
        citation_text
    ).strip()

    if not citation_text:
        return []

    citations = []

    # Usually citations are separated by commas.
    for citation in citation_text.split(","):

        citation = clean_value(
            citation
        )

        if not citation:
            continue

        if len(citation) > 300:
            continue

        if citation not in citations:
            citations.append(citation)

    return citations


# ============================================================
# COURT
# ============================================================

def extract_court(full_text, citations):
    """
    Determine the court.

    Prefer explicit Supreme Court information over
    generic High Court references.
    """

    text_upper = full_text.upper()

    # Strongest check first.
    if (
        "SUPREME COURT OF INDIA" in text_upper
        or "SUPREME COURT" in text_upper
    ):
        return "Supreme Court of India"

    # Check citations.
    for citation in citations:

        citation_upper = citation.upper()

        if "SUPREME COURT" in citation_upper:
            return "Supreme Court of India"

        if " AIR " in f" {citation_upper} ":
            pass

    if "HIGH COURT" in text_upper:
        return "High Court"

    if "DISTRICT COURT" in text_upper:
        return "District Court"

    if "SESSIONS COURT" in text_upper:
        return "Sessions Court"

    return None


# ============================================================
# CASE NUMBER
# ============================================================

def extract_case_number(full_text):
    """
    Extract the official case / appeal number.
    """

    text = clean_section_text(
        full_text
    )

    if not text:
        return None

    patterns = [

        r"""
        \b
        (?:CRIMINAL|CIVIL|CIVIL\s+APPEAL|CRIMINAL\s+APPEAL)
        \s+
        (?:APPEAL\s+)?
        No(?:\.|s)?
        \s*
        \(?s?\)?
        \s*
        [A-Za-z0-9./()\-]+
        (?:\s*-\s*[A-Za-z0-9./()\-]+)?
        \s*
        (?:OF|/)
        \s*
        \d{4}
        """,

        r"""
        \b
        CIVIL\s+APPEAL
        \s+
        Nos?
        (?:\.|s)?
        \s*
        [A-Za-z0-9./()\-]+
        (?:\s*-\s*[A-Za-z0-9./()\-]+)?
        \s+
        OF
        \s+
        \d{4}
        """,

        r"""
        \b
        APPEAL
        \s*
        \([^)]*\)
        \s*
        [A-Za-z0-9./()\-]+
        \s+
        OF
        \s+
        \d{4}
        """,

        r"""
        \b
        TRANSFER\s+CASE
        \s*
        \([^)]*\)
        \s*
        [A-Za-z0-9./()\-]+
        \s+
        OF
        \s+
        \d{4}
        """,

        r"""
        \b
        WRIT\s+PETITION
        \s+
        No(?:\.|s)?
        \s*
        [A-Za-z0-9./()\-]+
        \s+
        OF
        \s+
        \d{4}
        """,

        r"""
        \b
        SPECIAL\s+LEAVE\s+PETITION
        \s*
        \([^)]*\)
        \s*
        No(?:\.|s)?
        \s*
        [A-Za-z0-9./()\-]+
        """
    ]

    for pattern in patterns:

        match = re.search(
            pattern,
            text,
            re.IGNORECASE |
            re.VERBOSE
        )

        if match:

            result = clean_value(
                match.group(0)
            )

            if result:
                return result

    return None


# ============================================================
# ACT / LEGAL TOPICS
# ============================================================

def extract_legal_topics(full_text):
    """
    Extract ACT section only when an actual ACT metadata
    heading exists.

    Does not treat ordinary occurrences of the word 'act'
    inside the judgment as an ACT section.
    """

    match = re.search(
        r"(?m)^\s*ACT\s*:\s*"
        r"(.*?)(?="
        r"^\s*HEADNOTE\s*:?"
        r"|^\s*JUDGMENT\s*:?"
        r")",
        full_text,
        re.IGNORECASE | re.DOTALL
    )

    if not match:
        return []

    act_text = clean_section_text(
        match.group(1)
    )

    if not act_text:
        return []

    return [act_text]


# ============================================================
# FULL JUDGMENT
# ============================================================

def extract_judgment(full_text):
    """
    Extract the main JUDGMENT section.

    Supports:
        JUDGMENT:
        JUDGMENT
    """

    match = re.search(
        r"\bJUDGMENT\s*:?\s*"
        r"(.*)",
        full_text,
        re.IGNORECASE | re.DOTALL
    )

    if not match:
        return None

    judgment = clean_section_text(
        match.group(1)
    )

    return judgment


# ============================================================
# VERDICT / DECISION
# ============================================================

def extract_verdict(full_text):
    """
    Extract the final decision/disposition of the judgment.
    """

    judgment = extract_judgment(
        full_text
    )

    if not judgment:
        return None

    tail = judgment[-8000:]

    patterns = [

        r"[^.]{0,500}"
        r"\bappeal(?:s)?\b"
        r"[^.]{0,300}"
        r"\b(?:is|are|stands|stand)\s+"
        r"(?:dismissed|allowed|rejected)\b"
        r"[^.]*\.",

        r"[^.]{0,500}"
        r"\bpetition(?:s)?\b"
        r"[^.]{0,300}"
        r"\b(?:is|are|stands|stand)\s+"
        r"(?:dismissed|allowed|rejected)\b"
        r"[^.]*\.",

        r"[^.]{0,500}"
        r"\bapplication(?:s)?\b"
        r"[^.]{0,300}"
        r"\b(?:is|are|stands|stand)\s+"
        r"(?:dismissed|allowed|rejected)\b"
        r"[^.]*\.",

        r"[^.]{0,300}"
        r"\bappeal(?:s)?\b"
        r"[^.]{0,200}"
        r"\b(?:fails|succeeds)\b"
        r"[^.]*\.",

        r"\baccordingly\b[^.]{0,700}\.",

        r"\btherefore\b[^.]{0,700}\."
    ]

    candidates = []

    for pattern in patterns:

        matches = re.finditer(
            pattern,
            tail,
            re.IGNORECASE | re.DOTALL
        )

        for match in matches:

            text = clean_section_text(
                match.group(0)
            )

            if text:
                candidates.append(
                    text
                )

    if not candidates:
        return None

    return candidates[-1]


# ============================================================
# COMPLETE METADATA
# ============================================================

def extract_metadata(pages):
    """
    Extract judgment metadata.
    """

    full_text = get_full_text(
        pages
    )

    citations = extract_citations(
        full_text
    )

    return {

        "case_name": extract_case_name(
            full_text
        ),

        "petitioner": extract_petitioner(
            full_text
        ),

        "respondent": extract_respondent(
            full_text
        ),

        "judges": extract_judges(
            full_text
        ),

        "court": extract_court(
            full_text,
            citations
        ),

        "judgment_date": extract_judgment_date(
            full_text
        ),

        "citations": citations,

        "case_number": extract_case_number(
            full_text
        ),

        "legal_topics": extract_legal_topics(
            full_text
        )
    }

def extract_headnote(full_text):
    """
    Extract HEADNOTE section.

    Supports:
        HEADNOTE:
        HEADNOTE
    """

    match = re.search(
        r"\bHEADNOTE\s*:?\s*"
        r"(.*?)(?=\bJUDGMENT\s*:?\s*)",
        full_text,
        re.IGNORECASE | re.DOTALL
    )

    if not match:
        return None

    return clean_section_text(
        match.group(1)
    )
# ============================================================
# COMPLETE DOCUMENT
# ============================================================

def extract_document_sections(pages):
    """
    Extract important document sections.
    """

    full_text = get_full_text(
        pages
    )

    return {

        "acts": extract_legal_topics(
            full_text
        ),

        "headnote": extract_headnote(
            full_text
        ),

        "judgment": extract_judgment(
            full_text
        ),

        "verdict": extract_verdict(
            full_text
        )
    }


# ============================================================
# TEXT CLEANING HELPERS
# ============================================================

def clean_section_text(text):
    """
    Clean extracted section text.
    """

    if not text:
        return None

    text = re.sub(
        r"\s+",
        " ",
        text
    )

    text = text.strip()

    return text or None


def clean_value(value):
    """
    Clean metadata value.
    """

    if not value:
        return None

    value = re.sub(
        r"\s+",
        " ",
        value
    )

    value = value.strip()

    # Remove common trailing legal punctuation.
    value = value.rstrip(
        " .,:;-–—…"
    )

    # Remove accidental repeated punctuation.
    value = re.sub(
        r"\.{2,}$",
        "",
        value
    )

    value = value.rstrip(
        " .,:;-–—…"
    )

    return value or None
# ============================================================
# MAIN FUNCTION - DIRECT DOCUMENT SERVICE TEST
# ============================================================

# ============================================================
# MAIN FUNCTION - PROCESS ALL PDF FILES
# ============================================================

import json


def main():
    """
    Process all PDF files from data/raw and save
    processed JSON files into data/processed_v2.
    """

    print("\n" + "=" * 80)
    print("LEGAL MIND AI - BATCH DOCUMENT PROCESSING")
    print("=" * 80)

    # --------------------------------------------------------
    # FOLDERS
    # --------------------------------------------------------

    raw_folder = Path("data/raw")
    processed_folder = Path("data/processed_v2")

    # Create processed_v2 folder if it does not exist
    processed_folder.mkdir(
        parents=True,
        exist_ok=True
    )

    # --------------------------------------------------------
    # CHECK RAW FOLDER
    # --------------------------------------------------------

    if not raw_folder.exists():
        print("\nERROR: Raw folder not found:")
        print(raw_folder)
        return

    # --------------------------------------------------------
    # FIND ALL PDF FILES
    # --------------------------------------------------------

    pdf_files = list(raw_folder.glob("*.pdf")) + \
                list(raw_folder.glob("*.PDF"))

    # Remove duplicate paths
    pdf_files = list(
        {pdf.resolve(): pdf for pdf in pdf_files}.values()
    )

    pdf_files.sort()

    total_files = len(pdf_files)

    print(f"\nRaw folder:")
    print(raw_folder)

    print(f"\nPDF files found: {total_files}")

    if total_files == 0:
        print("\nNo PDF files found.")
        return

    # --------------------------------------------------------
    # PROCESSING COUNTERS
    # --------------------------------------------------------

    successful = 0
    failed = 0

    failed_files = []

    # --------------------------------------------------------
    # PROCESS EVERY PDF
    # --------------------------------------------------------

    for index, pdf_path in enumerate(pdf_files, start=1):

        json_filename = pdf_path.stem + ".json"
        json_path = processed_folder / json_filename

        print("\n" + "-" * 80)
        print(f"PROCESSING [{index}/{total_files}]")
        print(f"PDF: {pdf_path.name}")

        try:

            # ------------------------------------------------
            # STEP 1: Extract PDF text
            # ------------------------------------------------

            pages = extract_text_from_pdf(
                pdf_path
            )

            if not pages:
                raise ValueError(
                    "No text extracted from PDF"
                )

            # ------------------------------------------------
            # STEP 2: Extract metadata
            # ------------------------------------------------

            metadata = extract_metadata(
                pages
            )

            # ------------------------------------------------
            # STEP 3: Extract document sections
            # ------------------------------------------------

            sections = extract_document_sections(
                pages
            )

            # ------------------------------------------------
            # STEP 4: Create JSON structure
            # ------------------------------------------------

            document_data = {

                "filename": pdf_path.name,

                "document_id": pdf_path.stem,

                "case_name": metadata.get(
                    "case_name"
                ),

                "petitioner": metadata.get(
                    "petitioner"
                ),

                "respondent": metadata.get(
                    "respondent"
                ),

                "judges": metadata.get(
                    "judges",
                    []
                ),

                "court": metadata.get(
                    "court"
                ),

                "judgment_date": metadata.get(
                    "judgment_date"
                ),

                "case_number": metadata.get(
                    "case_number"
                ),

                "citations": metadata.get(
                    "citations",
                    []
                ),

                "legal_topics": metadata.get(
                    "legal_topics",
                    []
                ),

                "acts": sections.get(
                    "acts"
                ),

                "headnote": sections.get(
                    "headnote"
                ),

                "judgment": sections.get(
                    "judgment"
                ),

                "verdict": sections.get(
                    "verdict"
                )
            }

            # ------------------------------------------------
            # STEP 5: Save JSON
            # ------------------------------------------------

            with open(
                json_path,
                "w",
                encoding="utf-8"
            ) as json_file:

                json.dump(
                    document_data,
                    json_file,
                    ensure_ascii=False,
                    indent=4
                )

            successful += 1

            print("STATUS: SUCCESS")
            print(f"JSON: {json_path.name}")

        except Exception as e:

            failed += 1

            failed_files.append({
                "file": pdf_path.name,
                "error": str(e)
            })

            print("STATUS: FAILED")
            print(f"ERROR: {e}")

    # ========================================================
    # FINAL SUMMARY
    # ========================================================

    print("\n")
    print("=" * 80)
    print("BATCH PROCESSING COMPLETE")
    print("=" * 80)

    print(f"\nTotal PDFs : {total_files}")
    print(f"Successful : {successful}")
    print(f"Failed     : {failed}")

    # --------------------------------------------------------
    # Save failed files log
    # --------------------------------------------------------

    if failed_files:

        error_log = processed_folder / "processing_errors.json"

        with open(
            error_log,
            "w",
            encoding="utf-8"
        ) as file:

            json.dump(
                failed_files,
                file,
                ensure_ascii=False,
                indent=4
            )

        print("\nError log saved to:")
        print(error_log)

    print("\n" + "=" * 80)


# ============================================================
# RUN MAIN
# ============================================================

if __name__ == "__main__":
    main()