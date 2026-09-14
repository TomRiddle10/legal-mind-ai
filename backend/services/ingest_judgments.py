"""
ingest_judgments.py

Reads processed judgment JSON files (raw pages format, like your
processed_v2/*.json), splits each into structural sections (headnote,
act, judgment, order, per-judge opinions), and inserts everything into
Postgres.

USAGE:
    export DATABASE_URL="postgresql://user:password@localhost:5432/legal_mind"
    python ingest_judgments.py /path/to/backend/data/processed_v2

Requires:
    pip install psycopg2-binary python-dateutil
"""

import json
import os
import re
import sys
from datetime import datetime

import psycopg2
from psycopg2.extras import execute_values

from services.database import get_connection

# ------------------------------------------------------------------
# 1. Parsing: raw pages -> structured sections
# ------------------------------------------------------------------

# Markers that typically start a new named section in Indian Kanoon judgments
SECTION_MARKERS = [
    ("headnote", r"^\s*HEADNOTE\s*:?\s*$"),
    ("act", r"^\s*ACT\s*:?\s*$"),
    ("judgment", r"^\s*JUDGMENT\s*:?\s*$"),
    ("order", r"^\s*ORDER\s*:?\s*$"),
]

# Matches lines like "A.M. Ahmadi, J." or "CHANDRACHUD, J.-" that signal
# a new judge's opinion starting (common in multi-opinion judgments)
JUDGE_OPINION_RE = re.compile(
    r"^\s*([A-Z][A-Za-z\.\s]{2,40}),?\s*J\.\s*[-–—]?\s*$"
)


def join_pages(pages):
    """Concatenate page texts in order, preserving page breaks as markers."""
    return "\n".join(p.get("text", "") for p in sorted(pages, key=lambda p: p["page"]))


def split_into_sections(full_text):
    """
    Best-effort structural split. Returns a list of dicts:
    {section_type, author_judge, section_order, section_text}

    Falls back to a single 'full_text' section if no markers are found,
    so nothing is ever silently dropped.
    """
    lines = full_text.split("\n")
    sections = []
    current_type = None
    current_judge = None
    current_lines = []
    order = 0

    def flush():
        nonlocal current_lines, order
        text = "\n".join(current_lines).strip()
        if text:
            sections.append({
                "section_type": current_type or "full_text",
                "author_judge": current_judge,
                "section_order": order,
                "section_text": text,
            })
            order += 1
        current_lines = []

    for line in lines:
        stripped = line.strip()

        matched_marker = None
        for sec_type, pattern in SECTION_MARKERS:
            if re.match(pattern, stripped, re.IGNORECASE):
                matched_marker = sec_type
                break

        if matched_marker:
            flush()
            current_type = matched_marker
            current_judge = None
            continue

        judge_match = JUDGE_OPINION_RE.match(stripped)
        if judge_match and current_type in ("judgment", "order", None):
            flush()
            current_type = "opinion"
            current_judge = judge_match.group(1).strip()
            continue

        current_lines.append(line)

    flush()

    if not sections:
        sections.append({
            "section_type": "full_text",
            "author_judge": None,
            "section_order": 0,
            "section_text": full_text.strip(),
        })

    return sections


NOISE_PATTERNS = [
    r"^NON.?REPORTAB",
    r"^IN THE .*COURT",
    r"JURISDICTION$",
    r"^CIVIL APPEAL",
    r"^CRIMINAL APPEAL",
    r"^C\.A\.",
    r"^SLP",
    r"^WRIT PETITION",
    r"^W\.P\.",
    r"^J\s?U\s?D\s?G\s?M\s?E\s?N\s?T\s?$",
    r"^ORDER\s?$",
    r"^Date\s*:",
    r"^\d+\.\s",          # numbered paragraph, e.g. "1. These civil appeals..."
    r"^\(Arising out",
    r"^WITH$",
]

JUDGE_NAME_RE = re.compile(r"^[A-Za-z\.\s,]+$")


def classify_metadata_judges(raw_list, meta_petitioner, meta_respondent):
    """
    metadata.judges in the source JSON is unreliable — it can contain real
    judge names, party/appellant lines, case headers, and even full body
    paragraphs, all mixed into one array. This walks the array and sorts
    each item into judges / petitioner / respondent / discarded noise.
    """
    judges = []
    petitioner = meta_petitioner
    respondent = meta_respondent

    for raw in raw_list or []:
        item = raw.strip()
        if not item:
            continue

        if re.search(r"appellant", item, re.IGNORECASE):
            if not petitioner:
                petitioner = re.split(r"\.{2,}|\bappellant", item, flags=re.IGNORECASE)[0].strip(" .")
            continue

        if re.search(r"respondent", item, re.IGNORECASE):
            if not respondent:
                respondent = re.split(r"\.{2,}|\brespondent", item, flags=re.IGNORECASE)[0].strip(" .")
            continue

        if any(re.search(p, item, re.IGNORECASE) for p in NOISE_PATTERNS):
            continue

        if len(item) > 100:
            # long free text is a body paragraph, not a judge name — discard
            continue

        if JUDGE_NAME_RE.match(item):
            for name in item.split(","):
                name = name.strip().rstrip(".")
                if name and 2 < len(name) < 60:
                    judges.append(name)

    return judges, petitioner, respondent


def parse_date(date_str):
    if not date_str:
        return None
    for fmt in ("%d/%m/%Y", "%Y-%m-%d", "%d-%m-%Y"):
        try:
            return datetime.strptime(date_str, fmt).date()
        except ValueError:
            continue
    return None


def parse_judgment_file(filepath):
    with open(filepath, "r", encoding="utf-8") as f:
        data = json.load(f)

    meta = data.get("metadata", {})
    full_text = join_pages(data.get("pages", []))
    sections = split_into_sections(full_text)

    verdict = data.get("sections", {}).get("verdict") if isinstance(data.get("sections"), dict) else None

    judges, petitioner, respondent = classify_metadata_judges(
        meta.get("judges", []), meta.get("petitioner"), meta.get("respondent")
    )

    case_name = meta.get("case_name")
    if (not petitioner or not respondent) and case_name and " vs " in case_name.lower():
        parts = re.split(r"\s+vs\.?\s+", case_name, flags=re.IGNORECASE, maxsplit=1)
        if len(parts) == 2:
            petitioner = petitioner or parts[0].strip()
            respondent = respondent or parts[1].strip()

    return {
        "judgment_id": data.get("id"),
        "case_name": case_name,
        "court": meta.get("court"),
        "judgment_date": parse_date(meta.get("judgment_date")),
        "case_number": meta.get("case_number"),
        "petitioner": petitioner,
        "respondent": respondent,
        "verdict": verdict,
        "source_file": data.get("filename"),
        "judges": judges,
        "citations": meta.get("citations", []) or [],
        "sections": sections,
    }


# ------------------------------------------------------------------
# 2. Insertion
# ------------------------------------------------------------------

def upsert_judgment(cur, rec):
    cur.execute(
        """
        INSERT INTO judgments (judgment_id, case_name, court, judgment_date,
                                case_number, petitioner, respondent, verdict, source_file)
        VALUES (%(judgment_id)s, %(case_name)s, %(court)s, %(judgment_date)s,
                %(case_number)s, %(petitioner)s, %(respondent)s, %(verdict)s, %(source_file)s)
        ON CONFLICT (judgment_id) DO UPDATE SET
            case_name = EXCLUDED.case_name,
            court = EXCLUDED.court,
            judgment_date = EXCLUDED.judgment_date,
            case_number = EXCLUDED.case_number,
            petitioner = EXCLUDED.petitioner,
            respondent = EXCLUDED.respondent,
            verdict = EXCLUDED.verdict,
            source_file = EXCLUDED.source_file;
        """,
        rec,
    )


def replace_sections(cur, judgment_id, sections):
    cur.execute("DELETE FROM judgment_sections WHERE judgment_id = %s", (judgment_id,))
    rows = [
        (judgment_id, s["section_type"], s["author_judge"], s["section_order"], s["section_text"])
        for s in sections
    ]
    execute_values(
        cur,
        """
        INSERT INTO judgment_sections (judgment_id, section_type, author_judge, section_order, section_text)
        VALUES %s
        """,
        rows,
    )


def upsert_judges(cur, judgment_id, judge_names):
    cur.execute("DELETE FROM judgment_judges WHERE judgment_id = %s", (judgment_id,))
    for name in judge_names:
        name = name.strip()
        if not name:
            continue
        cur.execute(
            "INSERT INTO judges (name) VALUES (%s) ON CONFLICT (name) DO NOTHING",
            (name,),
        )
        cur.execute("SELECT judge_id FROM judges WHERE name = %s", (name,))
        judge_id = cur.fetchone()[0]
        cur.execute(
            "INSERT INTO judgment_judges (judgment_id, judge_id) VALUES (%s, %s) "
            "ON CONFLICT DO NOTHING",
            (judgment_id, judge_id),
        )


def replace_citations(cur, judgment_id, citations):
    cur.execute("DELETE FROM citations WHERE judgment_id = %s", (judgment_id,))
    if citations:
        rows = [(judgment_id, c) for c in citations]
        execute_values(
            cur,
            "INSERT INTO citations (judgment_id, citation_text) VALUES %s",
            rows,
        )


def ingest_file(cur, filepath):
    rec = parse_judgment_file(filepath)
    if not rec["judgment_id"]:
        print(f"  SKIP (no id): {filepath}")
        return
    upsert_judgment(cur, rec)
    replace_sections(cur, rec["judgment_id"], rec["sections"])
    upsert_judges(cur, rec["judgment_id"], rec["judges"])
    replace_citations(cur, rec["judgment_id"], rec["citations"])
    print(f"  OK  {rec['judgment_id']}  ({len(rec['sections'])} sections)")


def main(folder):
    conn = get_connection()
    conn.autocommit = False
    cur = conn.cursor()

    json_files = [
        os.path.join(folder, f) for f in os.listdir(folder) if f.lower().endswith(".json")
    ]
    print(f"Found {len(json_files)} JSON files in {folder}")

    for path in json_files:
        try:
            ingest_file(cur, path)
            conn.commit()
        except Exception as e:
            conn.rollback()
            print(f"  ERROR in {path}: {e}")

    cur.close()
    conn.close()
    print("Done.")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python ingest_judgments.py <folder_with_json_files>")
        sys.exit(1)
    main(sys.argv[1])