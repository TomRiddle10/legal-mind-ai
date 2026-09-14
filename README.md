# Legal Mind AI

**Legal Mind AI** is an AI-powered legal judgment retrieval and analysis system designed to help users search, read, summarize, and ask questions about Indian court judgments.

The system combines **semantic search, PostgreSQL, pgvector, SentenceTransformers, CrossEncoder reranking, Retrieval-Augmented Generation (RAG), Ollama, and Llama 3.1 8B** to provide locally processed AI-powered legal research capabilities.

The project is designed to run locally and does **not require OpenAI APIs**.

> **Disclaimer:** Legal Mind AI is an educational and research project. AI-generated responses should not be considered professional legal advice. Important legal information should always be verified against the original judgment and authoritative legal sources.

---

# 1. Project Objective

The main objective of Legal Mind AI is to make Indian legal judgments easier to search and understand.

Traditional legal research can require users to manually search through large numbers of judgments and read lengthy documents.

Legal Mind AI attempts to simplify this process by providing:

- Natural-language judgment search
- Semantic/vector search
- Relevance-based reranking
- Judgment-specific question answering
- AI-generated judgment summaries
- General legal chatbot functionality
- Local LLM-based responses
- Retrieval-Augmented Generation

The overall objective is:

```text
Large Collection of Legal Judgments
              ↓
        Intelligent Search
              ↓
      Relevant Judgments
              ↓
       Relevant Context
              ↓
          Local LLM
              ↓
     Understandable Answer
```

---

# 2. Main Features

## 2.1 Judgment Search

Users can search the judgment database using natural-language queries.

Example:

```text
Find judgments related to bail under money laundering cases.
```

The system converts the query into an embedding and searches the stored judgment/chunk embeddings.

---

## 2.2 Semantic Search

Legal Mind AI uses semantic/vector search rather than depending only on exact keyword matching.

The search process is:

```text
User Query
     ↓
SentenceTransformer
     ↓
Query Embedding
     ↓
PostgreSQL + pgvector
     ↓
Candidate Results
```

This allows the system to find conceptually related legal text even when the exact words used in the query are different.

---

## 2.3 CrossEncoder Reranking

After vector search retrieves candidate results, a CrossEncoder evaluates the relevance of the query and candidate text together.

```text
User Query
     +
Candidate Chunk
     ↓
CrossEncoder
     ↓
Relevance Score
```

The candidates are then sorted according to their reranking score.

This creates a two-stage retrieval system:

```text
Vector Search
      ↓
Candidate Retrieval
      ↓
CrossEncoder
      ↓
Final Ranking
```

---

# 3. Judgment-Specific RAG

One of the important features of Legal Mind AI is the ability to ask questions about a specific judgment.

For example:

```text
What was the final decision of the court?
```

or:

```text
What arguments were made by the petitioner?
```

The system does not search the entire database for these questions.

Instead, it retrieves information only from the selected judgment.

### Workflow

```text
Selected Judgment
        ↓
User Question
        ↓
Judgment-Specific Retrieval
        ↓
Vector Similarity Search
        ↓
CrossEncoder Reranking
        ↓
Relevant Chunks
        ↓
Neighboring Context
        ↓
RAG Context
        ↓
Llama 3.1 8B
        ↓
Answer
```

This helps keep the answer grounded in the selected judgment.

---

# 4. AI Judgment Summary

The system can generate an AI summary of a selected judgment.

The summary is structured around sections such as:

```text
OVERVIEW

KEY FACTS

LEGAL ISSUES

PARTIES' ARGUMENTS

COURT'S REASONING

FINAL DECISION

KEY TAKEAWAYS
```

The summary generation workflow is:

```text
Selected Judgment
       ↓
Retrieve Judgment Context
       ↓
Build Context
       ↓
Summary Prompt
       ↓
Llama 3.1 8B
       ↓
AI Summary
```

---

# 5. General Legal Chatbot

Legal Mind AI also provides a general chatbot mode.

The user can ask legal questions that are not necessarily associated with one selected judgment.

The general chatbot is separate from judgment-specific RAG.

The application therefore supports two main modes:

```text
┌─────────────────────────────┐
│       Legal Mind AI         │
├─────────────────────────────┤
│                             │
│  Judgment Retrieval         │
│           OR                │
│  General Legal Chatbot      │
│                             │
└─────────────────────────────┘
```

---

# 6. Technology Stack

## Frontend

- React
- Material UI
- React Router
- Vite
- JavaScript
- HTML/CSS

## Backend

- Python
- Flask
- REST APIs

## Database

- PostgreSQL
- pgvector

## NLP / AI

- SentenceTransformers
- CrossEncoder
- Retrieval-Augmented Generation
- Ollama
- Llama 3.1 8B

## Browser Storage

- localStorage

---

# 7. System Architecture

```text
                         USER
                           │
                           ▼
                  ┌─────────────────┐
                  │ React Frontend  │
                  │ Material UI     │
                  └────────┬────────┘
                           │
                           │ REST API
                           ▼
                  ┌─────────────────┐
                  │ Flask Backend   │
                  └────────┬────────┘
                           │
            ┌──────────────┼──────────────┐
            │              │              │
            ▼              ▼              ▼
       Search Service   Judgment RAG   LLM Service
            │              │              │
            │              │              ▼
            │              │          Ollama
            │              │              │
            │              │              ▼
            │              │        Llama 3.1 8B
            │              │
            └───────┬──────┘
                    ▼
           PostgreSQL + pgvector
```

---

# 8. Complete Project Flow

```text
                         USER
                           │
                           ▼
                  React Frontend
                           │
                           ▼
                   Flask REST API
                           │
                           ▼
                 PostgreSQL Database
                           │
                           ▼
                  Vector Retrieval
                           │
                           ▼
                  CrossEncoder
                   Reranking
                           │
                           ▼
                  Relevant Context
                           │
                           ▼
                         RAG
                           │
                           ▼
                       Ollama
                           │
                           ▼
                    Llama 3.1 8B
                           │
                           ▼
                     AI Response
```

---

# 9. Project Structure

The current project is organized approximately as follows:

```text
legal-mind-ai/
│
├── backend/
│   │
│   ├── app.py
│   │
│   ├── data/
│   │   ├── raw/
│   │   ├── processed/
│   │   └── processed_v2/
│   │
│   ├── processing/
│   │
│   ├── routes/
│   │   ├── __init__.py
│   │   ├── chat_routes.py
│   │   └── judgment_routes.py
│   │
│   └── services/
│       ├── __init__.py
│       ├── check_processed_data.py
│       ├── chunk_documents.py
│       ├── context_builder.py
│       ├── database.py
│       ├── document_service.py
│       ├── embed_chunks.py
│       ├── generate_embeddings.py
│       ├── import_to_postgres.py
│       ├── ingest_judgments.py
│       ├── judgment_rag.py
│       ├── judgment_retrieval.py
│       ├── judgment_to_json.py
│       ├── llm.py
│       ├── rag.py
│       ├── search.py
│       └── search_service.py
│
├── frontend/
│   ├── public/
│   ├── src/
│   ├── package.json
│   ├── package-lock.json
│   └── vite.config.js
│
├── .env.example
├── .gitignore
├── package.json
├── package-lock.json
├── requirements.txt
└── README.md
```

---

# 10. Backend Components

## `app.py`

Main Flask application entry point.

It initializes the backend and registers the API routes.

---

## `routes/chat_routes.py`

Handles general chatbot functionality.

---

## `routes/judgment_routes.py`

Handles judgment-related APIs including:

- Judgment search
- Getting a judgment
- Asking questions about a judgment
- Generating judgment summaries

---

## `services/database.py`

Handles the PostgreSQL database connection.

---

## `services/search.py`

Contains search-related functionality including:

- Query embedding
- Vector retrieval
- CrossEncoder reranking
- Result processing

---

## `services/judgment_rag.py`

Handles judgment-specific RAG.

It retrieves chunks only from the selected judgment.

---

## `services/llm.py`

Handles communication with the local Ollama LLM.

Current model:

```text
llama3.1:8b
```

Ollama endpoint:

```text
http://localhost:11434/api/generate
```

---

## `services/chunk_documents.py`

Splits long judgments into smaller chunks.

---

## `services/generate_embeddings.py`

Generates embeddings for the judgment data.

---

## `services/embed_chunks.py`

Handles embedding generation/storage for document chunks.

---

## `services/import_to_postgres.py`

Handles importing processed data into PostgreSQL.

---

# 11. Database

Legal Mind AI uses:

```text
PostgreSQL
```

with:

```text
pgvector
```

for vector similarity search.

---

# 12. Main Database Tables

## `documents_v2`

Stores judgment/document-level information.

Important fields include:

```text
id
document_id
filename
case_name
petitioner
respondent
judges
court
judgment_date
case_number
citations
legal_topics
acts
headnote
judgment
verdict
created_at
```

---

## `document_chunks`

Stores chunks extracted from judgments.

Important information includes:

```text
id
document_id
chunk_index
chunk_text
embedding
```

The `document_id` connects chunks to their original judgment.

---

# 13. Why Chunking Is Required

Legal judgments can be very large.

Sending an entire judgment to an LLM for every question is inefficient.

Therefore, the judgment is divided into smaller chunks.

Example:

```text
Complete Judgment
       │
       ├── Chunk 0
       ├── Chunk 1
       ├── Chunk 2
       ├── Chunk 3
       ├── ...
       └── Chunk N
```

Relevant chunks can then be retrieved instead of processing the complete database every time.

---

# 14. Embedding Process

The system converts legal text into numerical vectors.

```text
Legal Text
    ↓
SentenceTransformer
    ↓
Embedding Vector
    ↓
PostgreSQL + pgvector
```

A user query is converted into an embedding in the same way.

The query vector is then compared with stored vectors.

---

# 15. Why pgvector Is Used

`pgvector` allows PostgreSQL to store and search vector embeddings.

Instead of maintaining a separate vector database, the project keeps document information and embeddings in PostgreSQL.

Conceptually:

```text
Query Embedding
       ↓
PostgreSQL + pgvector
       ↓
Similarity Search
       ↓
Relevant Chunks
```

---

# 16. Why CrossEncoder Is Used

Vector search provides an efficient first-stage retrieval system.

However, the initial ranking may not always perfectly represent semantic relevance.

A CrossEncoder performs a second-stage relevance evaluation.

```text
Query
 +
Candidate Text
      ↓
CrossEncoder
      ↓
Relevance Score
```

The candidates are then sorted by relevance.

---

# 17. Why RAG Is Used

A Large Language Model should be provided with relevant source information before generating a response.

RAG stands for:

```text
Retrieval-Augmented Generation
```

The process is:

```text
Question
   ↓
Retrieve relevant information
   ↓
Create context
   ↓
Send context + question to LLM
   ↓
Generate response
```

This helps ground responses in retrieved legal content.

---

# 18. Why Ollama Is Used

The project uses Ollama to run the LLM locally.

Benefits include:

- Local LLM execution
- No OpenAI API dependency
- No OpenAI API key required
- Local processing of retrieved context
- Easy experimentation with different local models

Current model:

```text
Llama 3.1 8B
```

---

# 19. Data and GitHub

Large judgment datasets are intentionally **not included in the GitHub repository**.

The following folders are excluded using `.gitignore`:

```text
backend/data/raw/
backend/data/processed/
backend/data/processed_v2/
```

This prevents large raw and generated datasets from being pushed to GitHub.

When setting up the project on another laptop, the required data must be transferred separately.

---

# 20. Requirements for Another Laptop

To reproduce the project on another laptop, install:

```text
Git
Python
Node.js
npm
PostgreSQL
pgvector
Ollama
```

The computer should have enough resources to run local embedding models, CrossEncoder reranking, PostgreSQL, and Llama 3.1 8B.

---

# 21. Setup on Another Laptop

This section explains how to reproduce the project from scratch.

---

## Step 1 — Install Git

Install Git on the new laptop.

Verify:

```powershell
git --version
```

---

# 22. Step 2 — Install Python

Install Python 3.x.

Verify:

```powershell
python --version
```

Also verify pip:

```powershell
pip --version
```

---

# 23. Step 3 — Install Node.js

Install Node.js.

Verify:

```powershell
node --version
```

and:

```powershell
npm --version
```

---

# 24. Step 4 — Install PostgreSQL

Install PostgreSQL.

Make sure the PostgreSQL server is running.

Verify that PostgreSQL is available using:

```powershell
psql --version
```

---

# 25. Step 5 — Install pgvector

The project requires the PostgreSQL `vector` extension.

After creating the database, enable it using:

```sql
CREATE EXTENSION IF NOT EXISTS vector;
```

---

# 26. Step 6 — Install Ollama

Install Ollama.

Verify:

```powershell
ollama --version
```

Download the required model:

```powershell
ollama pull llama3.1:8b
```

Verify:

```powershell
ollama list
```

The output should contain:

```text
llama3.1:8b
```

---

# 27. Step 7 — Clone the GitHub Repository

Clone the project:

```powershell
git clone <YOUR_GITHUB_REPOSITORY_URL>
```

Example:

```powershell
git clone https://github.com/YOUR_USERNAME/legal-mind-ai.git
```

Go into the project:

```powershell
cd legal-mind-ai
```

---

# 28. Step 8 — Create Backend Virtual Environment

Go to backend:

```powershell
cd backend
```

Create a virtual environment:

```powershell
python -m venv .venv
```

Activate it on Windows PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

You should see something similar to:

```text
(.venv)
```

at the beginning of the terminal prompt.

---

# 29. Step 9 — Install Backend Dependencies

Install Python dependencies:

```powershell
pip install -r requirements.txt
```

If `requirements.txt` is located at the project root instead, use:

```powershell
pip install -r ..\requirements.txt
```

---

# 30. Step 10 — Create PostgreSQL Database

Open PostgreSQL/psql.

Create the database:

```sql
CREATE DATABASE legal_mind_ai;
```

Connect to it and enable pgvector:

```sql
CREATE EXTENSION IF NOT EXISTS vector;
```

---

# 31. Step 11 — Configure Database Credentials

The backend requires PostgreSQL connection information.

Typical local configuration:

```text
Host: localhost
Port: 5432
Database: legal_mind_ai
Username: <your PostgreSQL username>
Password: <your PostgreSQL password>
```

Use the configuration expected by the current `database.py`.

Do not commit database passwords to GitHub.

Use `.env` when environment variables are configured for the project.

---

# 32. Step 12 — Copy the Judgment Dataset

The judgment dataset is not included in GitHub.

Copy the required data separately to:

```text
backend/data/
```

Expected folders:

```text
backend/
└── data/
    ├── raw/
    ├── processed/
    └── processed_v2/
```

For the current processed judgment setup, the processed files are stored under:

```text
backend/data/processed_v2/
```

The data should be transferred separately from the Git repository.

---

# 33. Step 13 — Process the Data

The project contains scripts for processing and preparing judgment data.

Important scripts include:

```text
judgment_to_json.py
ingest_judgments.py
chunk_documents.py
generate_embeddings.py
embed_chunks.py
import_to_postgres.py
check_processed_data.py
```

The general processing pipeline is:

```text
Raw Data
   ↓
Judgment Processing
   ↓
Processed JSON
   ↓
Chunking
   ↓
Embedding Generation
   ↓
PostgreSQL Import
   ↓
Vector Search Ready
```

The exact scripts/order should follow the current implementation and dataset state.

---

# 34. Step 14 — Start Ollama

Make sure Ollama is running.

Verify the model:

```powershell
ollama list
```

If required:

```powershell
ollama pull llama3.1:8b
```

The backend communicates with:

```text
http://localhost:11434/api/generate
```

---

# 35. Step 15 — Start the Flask Backend

Open a terminal:

```powershell
cd legal-mind-ai\backend
```

Activate the environment:

```powershell
.\.venv\Scripts\Activate.ps1
```

Start the backend:

```powershell
python app.py
```

The backend will run on the host/port configured by the application.

A common development address is:

```text
http://localhost:5000
```

Use the address displayed by the Flask application if it is different.

---

# 36. Step 16 — Install Frontend Dependencies

Open another terminal.

Go to the frontend:

```powershell
cd legal-mind-ai\frontend
```

Install dependencies:

```powershell
npm install
```

This recreates the frontend dependencies using:

```text
package.json
package-lock.json
```

---

# 37. Step 17 — Start the Frontend

Run:

```powershell
npm run dev
```

Vite will display the local frontend address.

It will commonly look like:

```text
http://localhost:5173
```

Open that address in your browser.

---

# 38. Complete Startup Process

Every time you want to run the project locally:

### Terminal 1 — PostgreSQL

Make sure PostgreSQL is running.

---

### Terminal 2 — Ollama

Make sure Ollama is running and the model exists:

```powershell
ollama list
```

---

### Terminal 3 — Backend

```powershell
cd legal-mind-ai\backend
.\.venv\Scripts\Activate.ps1
python app.py
```

---

### Terminal 4 — Frontend

```powershell
cd legal-mind-ai\frontend
npm run dev
```

---

# 39. Complete Runtime Architecture

Once everything is running:

```text
                   Browser
                      │
                      ▼
              React Frontend
                      │
                      ▼
                Flask API
                      │
          ┌───────────┴───────────┐
          │                       │
          ▼                       ▼
 PostgreSQL + pgvector         Ollama
          │                       │
          ▼                       ▼
 Retrieval + Reranking      Llama 3.1 8B
          │                       │
          └──────────┬────────────┘
                     ▼
                 RAG Answer
```

---

# 40. API Endpoints

The judgment routes currently include:

## Search Judgments

```text
GET /api/judgments/search
```

---

## Get Judgment

```text
GET /api/judgments/<document_id>
```

---

## Ask About Judgment

```text
POST /api/judgments/<document_id>/ask
```

---

## Summarize Judgment

```text
POST /api/judgments/<document_id>/summarize
```

---

# 41. Judgment Search Workflow

When a user searches for a judgment:

```text
User enters query
       ↓
Frontend sends API request
       ↓
Flask receives query
       ↓
SentenceTransformer creates embedding
       ↓
PostgreSQL + pgvector searches candidates
       ↓
CrossEncoder reranks candidates
       ↓
Relevant judgments returned
       ↓
Frontend displays results
```

---

# 42. Judgment Question Workflow

When the user opens a judgment and asks a question:

```text
User Question
       ↓
Selected document_id
       ↓
Search chunks belonging to document_id
       ↓
Vector similarity
       ↓
CrossEncoder reranking
       ↓
Top relevant chunks
       ↓
Neighboring chunks added
       ↓
Context builder
       ↓
RAG prompt
       ↓
Llama 3.1 8B
       ↓
Answer
```

---

# 43. Judgment Summary Workflow

```text
Selected Judgment
       ↓
Retrieve judgment chunks
       ↓
Build judgment context
       ↓
Summary prompt
       ↓
Llama 3.1 8B
       ↓
Structured Summary
```

---

# 44. Frontend Chat Persistence

The frontend uses browser `localStorage` to preserve conversations.

General chatbot history uses:

```text
legalMindAI:generalChat
```

Judgment-specific chat uses:

```text
legalMindAI:judgmentChat:<documentId>
```

This allows the conversation to remain available after a browser refresh.

---

# 45. Troubleshooting

## PostgreSQL Connection Error

Check:

```text
PostgreSQL is running
Database name is correct
Username is correct
Password is correct
Port is correct
pgvector is installed
```

Verify the database:

```text
legal_mind_ai
```

---

## pgvector Error

Make sure the extension exists:

```sql
CREATE EXTENSION IF NOT EXISTS vector;
```

---

## Ollama Error

Check:

```powershell
ollama --version
```

Then:

```powershell
ollama list
```

If the model is missing:

```powershell
ollama pull llama3.1:8b
```

---

## Python Module Not Found

Activate the virtual environment:

```powershell
.\.venv\Scripts\Activate.ps1
```

Then reinstall:

```powershell
pip install -r requirements.txt
```

---

## Frontend Module Error

Run:

```powershell
npm install
```

Then:

```powershell
npm run dev
```

---

## Search Returns No Results

Check:

1. PostgreSQL is running.
2. `legal_mind_ai` exists.
3. `documents_v2` contains data.
4. `document_chunks` contains data.
5. Embeddings exist.
6. pgvector is enabled.
7. SentenceTransformers is installed.

---

## Judgment Q&A Does Not Work

Check:

1. The selected `document_id` exists.
2. The judgment has chunks.
3. The chunks have embeddings.
4. The CrossEncoder loaded correctly.
5. Ollama is running.
6. `llama3.1:8b` exists.

---

# 46. GitHub Data Policy

The following are intentionally excluded from GitHub:

```text
backend/data/raw/
backend/data/processed/
backend/data/processed_v2/
```

Also excluded:

```text
.venv/
__pycache__/
*.pyc
node_modules/
.env
frontend/dist/
```

Before committing, check:

```powershell
git status
```

To see ignored files:

```powershell
git status --ignored
```

To verify a data file is ignored:

```powershell
git check-ignore -v backend/data/processed_v2/<file>.json
```

---

# 47. Development Workflow

The recommended development workflow is:

```text
1. Start PostgreSQL
        ↓
2. Start Ollama
        ↓
3. Activate backend environment
        ↓
4. Start Flask
        ↓
5. Start React/Vite
        ↓
6. Test frontend
        ↓
7. Test judgment search
        ↓
8. Test judgment viewer
        ↓
9. Test judgment Q&A
        ↓
10. Test summary
```

---

# 48. Why Legal Mind AI Uses Vector Search

Keyword search mainly depends on matching words.

Legal questions can use different words while discussing the same concept.

For example:

```text
Query:
"Can bail be granted in a money laundering case?"
```

could retrieve legal text discussing:

```text
"grant of bail under the Prevention of Money Laundering Act"
```

even if the exact wording differs.

This is possible because both texts are represented as semantic embeddings.

---

# 49. Why Legal Mind AI Uses RAG

Without retrieval, an LLM may not have access to the exact judgment required to answer a question.

RAG first retrieves relevant legal text.

```text
Question
   ↓
Retrieve Legal Context
   ↓
Build Prompt
   ↓
LLM
   ↓
Answer
```

This provides the model with relevant context before generation.

---

# 50. Why the Project Uses a Local LLM

The current project uses:

```text
Ollama
+
Llama 3.1 8B
```

instead of an external OpenAI API.

This provides:

- Local model execution
- No OpenAI API dependency
- No OpenAI API key requirement
- Local handling of retrieved context
- Ability to experiment with other Ollama models

---

# 51. Security Considerations

Do not commit:

```text
.env
database passwords
API keys
private credentials
large datasets
local model files
```

Always verify `.gitignore` before pushing the repository.

---

# 52. Current Limitations

Legal Mind AI is currently an educational/research prototype.

Possible limitations include:

- AI responses may contain errors.
- Retrieval quality depends on data quality.
- Missing metadata can affect search/filtering.
- Local LLM performance depends on hardware.
- Very long judgments require careful context management.
- Generated summaries should be verified against the original judgment.
- The system should not be treated as a substitute for professional legal advice.

---

# 53. Future Enhancements

Possible future improvements include:

- Hybrid keyword + vector search
- Advanced legal filters
- Judgment comparison
- Citation/precedent explorer
- Legal citation graph
- Important-date timeline
- Source-linked answers
- Retrieval evaluation
- RAG evaluation metrics
- Hallucination detection
- Advanced judgment analysis
- Legal research workspace
- Improved grounding
- Production deployment

---

# 54. Future Advanced Judgment Analysis

A future version can extract:

```text
Case Overview
Parties
Important Dates
Legal Issues
Applicable Acts & Sections
Petitioner's Arguments
Respondent's Arguments
Court's Reasoning
Important Precedents
Final Decision
Key Takeaways
Supporting Sources
```

This would turn Legal Mind AI from a basic search/RAG application into a more advanced legal research assistant.

---

# 55. Complete New-Laptop Checklist

Before running the project on a new laptop:

```text
[ ] Git installed

[ ] Python installed

[ ] Node.js installed

[ ] npm installed

[ ] PostgreSQL installed

[ ] pgvector installed

[ ] Ollama installed

[ ] Repository cloned

[ ] Backend virtual environment created

[ ] Backend dependencies installed

[ ] PostgreSQL database created

[ ] vector extension enabled

[ ] Database configuration completed

[ ] Judgment dataset copied separately

[ ] Judgment data processed

[ ] Judgment data imported

[ ] Embeddings generated

[ ] Llama 3.1 8B downloaded

[ ] Flask backend running

[ ] React frontend running

[ ] Judgment search tested

[ ] Judgment viewer tested

[ ] Judgment Q&A tested

[ ] AI summary tested
```

---

# 56. Quick Start

For a machine where all required software is already installed:

```powershell
git clone <YOUR_GITHUB_REPOSITORY_URL>

cd legal-mind-ai
```

### Backend

```powershell
cd backend

python -m venv .venv

.\.venv\Scripts\Activate.ps1

pip install -r requirements.txt

python app.py
```

### Frontend

Open another terminal:

```powershell
cd legal-mind-ai\frontend

npm install

npm run dev
```

### Ollama

Make sure the model exists:

```powershell
ollama pull llama3.1:8b
```

Then open the frontend URL displayed by Vite.

---

# 57. Final Technology Summary

| Component | Technology |
|---|---|
| Frontend | React |
| UI | Material UI |
| Routing | React Router |
| Build Tool | Vite |
| Backend | Flask |
| Language | Python |
| Database | PostgreSQL |
| Vector Database | PostgreSQL + pgvector |
| Embeddings | SentenceTransformers |
| Reranking | CrossEncoder |
| Architecture | RAG |
| Local LLM Runtime | Ollama |
| LLM | Llama 3.1 8B |
| Browser Storage | localStorage |

---

# 58. Project Summary

Legal Mind AI combines modern information retrieval and generative AI techniques to create an intelligent legal judgment research system.

The complete pipeline is:

```text
Indian Court Judgments
          ↓
      Processing
          ↓
        Chunking
          ↓
      Embeddings
          ↓
 PostgreSQL + pgvector
          ↓
    Semantic Search
          ↓
 CrossEncoder Reranking
          ↓
   Relevant Context
          ↓
          RAG
          ↓
       Ollama
          ↓
    Llama 3.1 8B
          ↓
   AI Legal Response
```

The project provides a foundation for building more advanced legal research capabilities such as judgment comparison, precedent exploration, citation graphs, source-grounded answers, and automated legal judgment analysis.

---

# 59. License

Add the project's license here when a license is selected.

Third-party libraries, datasets, models, and legal judgment sources may have their own terms and licenses. Those terms should be reviewed and followed separately.

For Database:
https://drive.google.com/file/d/1gB6U2ObIFtSBz9On4NvEapY6ZgiSa86A/view?usp=drive_link
