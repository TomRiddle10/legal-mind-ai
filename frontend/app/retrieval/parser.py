"""
Parser for Indian Kanoon-style court judgment PDFs (the format used by most
Kaggle Indian court judgment dumps: title -> Equivalent citations -> Author ->
Bench -> PETITIONER/RESPONDENT -> DATE OF JUDGMENT -> ACT -> HEADNOTE -> JUDGMENT body).

Usage:
    from judgment_parser import parse_judgment_pdf
    record = parse_judgment_pdf("path/to/file.pdf")
"""
import re
import subprocess


def pdf_to_text(pdf_path: str) -> str:
    """Extract text with layout preserved using pdftotext (poppler-utils)."""
    result = subprocess.run(
        ["pdftotext", "-layout", pdf_path, "-"],
        capture_output=True, text=True, check=True
    )
    return result.stdout


def _clean(s: str) -> str:
    return re.sub(r"\s+", " ", s).strip() if s else s


def guess_court(text_head: str, citations: str) -> str:
    """Heuristic court classification from citation strings / header text."""
    blob = (text_head + " " + (citations or "")).upper()
    if "SUPREME COURT" in blob or re.search(r"\bAIR \d{4} SC\b", blob) or " SCR " in blob:
        return "Supreme Court"
    if "HIGH COURT" in blob or re.search(r"\bHC\b", blob):
        return "High Court"
    if "DISTRICT COURT" in blob or "SESSIONS COURT" in blob or "TRIBUNAL" in blob:
        return "Lower Court / Tribunal"
    return "Unknown"


def parse_judgment_pdf(pdf_path: str) -> dict:
    text = pdf_to_text(pdf_path)

    # Header block = everything before ACT:/HEADNOTE:/JUDGMENT: (whichever comes first)
    split_match = re.search(r"\n\s*(ACT:|HEADNOTE:|JUDGMENT:)", text)
    header = text[:split_match.start()] if split_match else text[:3000]
    body = text[split_match.start():] if split_match else ""

    title_match = re.match(r"\s*(.+?)\n", text)
    title = _clean(title_match.group(1)) if title_match else None

    citations_match = re.search(r"Equivalent citations:\s*(.+?)(?:\n\s*\n|\nAuthor:|\nBench:)", header, re.S)
    citations = _clean(citations_match.group(1)) if citations_match else None

    author_match = re.search(r"Author:\s*(.+)", header)
    author = _clean(author_match.group(1)) if author_match else None

    petitioner_match = re.search(r"PETITIONER:\s*\n\s*(.+?)\n", header)
    petitioner = _clean(petitioner_match.group(1)) if petitioner_match else None

    respondent_match = re.search(r"RESPONDENT:\s*\n\s*(.+?)\n", header)
    respondent = _clean(respondent_match.group(1)) if respondent_match else None

    date_match = re.search(r"DATE OF JUDGMENT:\s*\n\s*(.+?)\n", header)
    date_of_judgment = _clean(date_match.group(1)) if date_match else None

    bench_match = re.search(r"\bBENCH:\s*\n((?:\s*.+\n)+?)(?:\s*CITATION:|\s*ACT:)", header)
    bench_judges = []
    if bench_match:
        seen = set()
        for l in bench_match.group(1).splitlines():
            cl = _clean(l)
            if cl and cl.upper() != "BENCH:" and cl not in seen:
                seen.add(cl)
                bench_judges.append(cl)

    doc_id_match = re.search(r"indiankanoon\.org/doc/(\d+)", text)
    doc_id = doc_id_match.group(1) if doc_id_match else None

    court = guess_court(header, citations or "")

    # --- Fallbacks: many files are missing explicit PETITIONER/RESPONDENT/DATE
    # fields, but the title consistently follows "X vs Y ... on DATE" -- use it
    # to backfill whatever the structured fields didn't catch.
    if title:
        title_match2 = re.match(
            r"^(.*?)\s+[Vv]s\.?\s+(.*?)(?:\s*:\s*\.\.\.)?\s+on\s+(.+)$", title
        )
        if title_match2:
            if not petitioner:
                petitioner = _clean(title_match2.group(1))
            if not respondent:
                respondent = _clean(title_match2.group(2))
            if not date_of_judgment:
                date_of_judgment = _clean(title_match2.group(3))

    is_partial = not all([petitioner, respondent, date_of_judgment, bench_judges])

    return {
        "source_doc_id": doc_id,
        "title": title,
        "court": court,
        "citations": citations,
        "author_judge": author,
        "bench_judges": bench_judges,
        "petitioner": petitioner,
        "respondent": respondent,
        "date_of_judgment": date_of_judgment,
        "full_text": text.strip(),
        "body_text": body.strip(),
        "num_chars": len(text),
        "is_partial": is_partial,  # True if any key field is still missing after fallbacks
    }


if __name__ == "__main__":
    import sys
    import json
    record = parse_judgment_pdf(sys.argv[1])
    preview = {k: (v[:300] if isinstance(v, str) else v) for k, v in record.items() if k not in ("full_text", "body_text")}
    print(json.dumps(preview, indent=2, ensure_ascii=False))
