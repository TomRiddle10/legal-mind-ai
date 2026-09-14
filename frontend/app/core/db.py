"""
Shared SQLite connection + schema for Legal Mind AI.
Both the retrieval module and (later) the chatbot module read/write through
this single place, so the schema only lives in one file.
"""
import sqlite3
from app.core.config import DB_PATH

SCHEMA = """
CREATE TABLE IF NOT EXISTS judgments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    file_path TEXT UNIQUE,
    source_doc_id TEXT,
    title TEXT,
    court TEXT,
    citations TEXT,
    author_judge TEXT,
    bench_judges TEXT,   -- JSON array as text
    petitioner TEXT,
    respondent TEXT,
    date_of_judgment TEXT,
    full_text TEXT,
    num_chars INTEGER,
    is_partial INTEGER
);

CREATE VIRTUAL TABLE IF NOT EXISTS judgments_fts USING fts5(
    title, citations, petitioner, respondent, full_text,
    content='judgments', content_rowid='id'
);

CREATE TRIGGER IF NOT EXISTS judgments_ai AFTER INSERT ON judgments BEGIN
    INSERT INTO judgments_fts(rowid, title, citations, petitioner, respondent, full_text)
    VALUES (new.id, new.title, new.citations, new.petitioner, new.respondent, new.full_text);
END;
"""


def get_connection() -> sqlite3.Connection:
    """Open a connection to the shared Legal Mind AI database, ensuring the
    schema exists. Call this from any module instead of opening sqlite3
    directly, so schema changes only need to happen here."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.executescript(SCHEMA)
    return conn
