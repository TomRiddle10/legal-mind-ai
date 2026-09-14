# Chatbot / Summarizer — Phase 2 (not built yet)

Will read verdict text via `app.core.db.get_connection()` (same DB as
retrieval — no duplicate data layer), chunk + embed it, and expose:
- `POST /api/summarize/<verdict_id>` — plain-language summary
- `POST /api/chat/<verdict_id>` — Q&A grounded in that verdict's text (RAG)

Planned as its own Flask app (`app/chatbot/api.py`, port from
`app.core.config.CHATBOT_PORT`) so it can run and scale independently of
the retrieval API, while sharing the same core config/DB layer.
