"""
Central configuration for Legal Mind AI.
All modules (retrieval, chatbot) read settings from here instead of
hardcoding paths/values, so the project can move from local dev to
deployment without touching module code.
"""
import os
from pathlib import Path

# Project root = legal-mind-ai/
BASE_DIR = Path(__file__).resolve().parent.parent.parent

# --- Data ---
# Point this at your local copy of the full dataset when you ingest it.
RAW_PDF_DIR = os.environ.get("LMAI_RAW_PDF_DIR", str(BASE_DIR / "data" / "sample_pdfs"))
DB_PATH = os.environ.get("LMAI_DB_PATH", str(BASE_DIR / "data" / "legal_mind.db"))

# --- Retrieval API ---
RETRIEVAL_HOST = os.environ.get("LMAI_RETRIEVAL_HOST", "0.0.0.0")
RETRIEVAL_PORT = int(os.environ.get("LMAI_RETRIEVAL_PORT", 5000))

# --- Chatbot API (phase 2) ---
CHATBOT_HOST = os.environ.get("LMAI_CHATBOT_HOST", "0.0.0.0")
CHATBOT_PORT = int(os.environ.get("LMAI_CHATBOT_PORT", 5001))
ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY", "")  # set in .env, never commit it

# --- Search behavior ---
DEFAULT_PAGE_SIZE = 10
MAX_PAGE_SIZE = 50
