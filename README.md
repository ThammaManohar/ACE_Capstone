---
title: Legal Document Assistant
emoji: ⚖️
colorFrom: gray
colorTo: blue
sdk: docker
app_port: 7860
---

# Legal Document Assistant

An agentic RAG assistant that answers questions over Indian case law and lets a user upload
their own legal document (PDF/.txt) for summarization and session-scoped follow-up questions.

- Embeddings: `sentence-transformers/all-MiniLM-L6-v2` (local, free)
- Vector store: ChromaDB (local, file-based)
- Generation: Gemini/Gemma via Google AI Studio's free API
- Backend: FastAPI ([backend/main.py](backend/main.py)), also serves the static frontend
- Frontend: plain HTML/CSS/JS ([frontend/](frontend/))

A legacy Streamlit version of the UI is still present at [app.py](app.py) for reference.

## Local setup

1. Create a virtual environment and install dependencies:
   ```bash
   python -m venv .venv
   .venv\Scripts\activate   # Windows
   pip install -r requirements.txt
   ```

2. Get a free API key at https://aistudio.google.com/apikey and copy it into `.env`:
   ```bash
   copy .env.example .env
   # then edit .env and paste your key as GEMINI_API_KEY=...
   ```

3. Build the vector index (downloads a subset of the dataset, embeds, and persists to `chroma_db/`):
   ```bash
   python scripts/build_index.py
   ```
   This indexes the first 300 documents by default. Override with `MAX_DOCS=1000` env var if desired.

4. Run the app (backend serves the frontend too — one server, one URL):
   ```bash
   uvicorn backend.main:app --port 8011
   ```
   Open http://localhost:8011

## Deploying publicly (free, no card required)

This repo ships a `Dockerfile` for [Hugging Face Spaces](https://huggingface.co/spaces):

1. Create a free Space at huggingface.co/new-space, SDK: **Docker**.
2. Push this repo to the Space's git remote (or link your GitHub repo in the Space settings).
3. In the Space's **Settings → Repository secrets**, add `GEMINI_API_KEY` with your key.
4. The Space builds the Docker image, runs `scripts/build_index.py` then starts the server —
   you get a permanent public URL.

Storage on the free tier is ephemeral, so the index rebuilds on every restart (a few minutes);
no persistent disk is required.

## Usage

- **Ask**: type a question about the indexed corpus — the agent retrieves relevant chunks via
  similarity search and answers using only that retrieved context, streaming the answer as it
  generates, with sources shown for transparency.
- **Upload a document**: upload a PDF/.txt, click Summarize. If it's recognized as a legal
  document, it's summarized and added to your session's search scope so you can ask follow-up
  questions about it specifically (in addition to the base indexed corpus).

## Notes

- The free Gemini API tier has request-per-minute limits; `src/llm.py` retries with backoff on
  transient errors.
- Session-uploaded documents are held in memory only (never written to disk) and are discarded
  when the server process restarts.
