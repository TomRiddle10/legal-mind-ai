"""
Flask API for verdict retrieval (Legal Mind AI).

Endpoints:
    GET /api/search?q=...&court=...&year_from=...&year_to=...&page=1&page_size=10
    GET /api/verdict/<id>
    GET /api/courts

Run:
    python3 -m app.retrieval.api
"""
import re
from flask import Flask, request, jsonify
from flask_cors import CORS

from app.core.db import get_connection
from app.core.config import RETRIEVAL_HOST, RETRIEVAL_PORT, DEFAULT_PAGE_SIZE, MAX_PAGE_SIZE

app = Flask(__name__)
CORS(app)


def fts_escape(q: str) -> str:
    """Wrap a raw user query as an FTS5 prefix-AND expression (forgiving of
    punctuation like 'vs.' or 'A.K.' that would otherwise break FTS syntax)."""
    terms = re.findall(r"[A-Za-z0-9]+", q.strip())
    if not terms:
        return ""
    return " AND ".join(f"{t}*" for t in terms)


@app.route("/api/search")
def search():
    q = request.args.get("q", "").strip()
    court = request.args.get("court", "").strip()
    year_from = request.args.get("year_from", type=int)
    year_to = request.args.get("year_to", type=int)
    page = max(1, request.args.get("page", default=1, type=int))
    page_size = min(MAX_PAGE_SIZE, request.args.get("page_size", default=DEFAULT_PAGE_SIZE, type=int))
    offset = (page - 1) * page_size

    conn = get_connection()
    cur = conn.cursor()

    where_clauses = []
    params = []
    base_from = "FROM judgments j"

    if q:
        base_from = "FROM judgments_fts f JOIN judgments j ON j.id = f.rowid"
        where_clauses.append("judgments_fts MATCH ?")
        params.append(fts_escape(q))

    if court:
        where_clauses.append("j.court = ?")
        params.append(court)
    if year_from:
        where_clauses.append("CAST(substr(j.date_of_judgment, -4) AS INTEGER) >= ?")
        params.append(year_from)
    if year_to:
        where_clauses.append("CAST(substr(j.date_of_judgment, -4) AS INTEGER) <= ?")
        params.append(year_to)

    where_sql = f"WHERE {' AND '.join(where_clauses)}" if where_clauses else ""

    total = cur.execute(f"SELECT COUNT(*) as cnt {base_from} {where_sql}", params).fetchone()["cnt"]

    rows = cur.execute(
        f"""SELECT j.id, j.title, j.court, j.citations, j.petitioner, j.respondent,
                   j.date_of_judgment, j.is_partial
            {base_from} {where_sql}
            ORDER BY j.id
            LIMIT ? OFFSET ?""",
        params + [page_size, offset],
    ).fetchall()
    conn.close()

    return jsonify({
        "query": q, "total": total, "page": page, "page_size": page_size,
        "results": [dict(r) for r in rows],
    })


@app.route("/api/verdict/<int:verdict_id>")
def get_verdict(verdict_id):
    conn = get_connection()
    row = conn.execute("SELECT * FROM judgments WHERE id = ?", (verdict_id,)).fetchone()
    conn.close()
    if not row:
        return jsonify({"error": "not found"}), 404
    return jsonify(dict(row))


@app.route("/api/courts")
def get_courts():
    conn = get_connection()
    rows = conn.execute("SELECT DISTINCT court FROM judgments WHERE court IS NOT NULL ORDER BY court").fetchall()
    conn.close()
    return jsonify([r["court"] for r in rows])


if __name__ == "__main__":
    app.run(host=RETRIEVAL_HOST, port=RETRIEVAL_PORT, debug=True)
