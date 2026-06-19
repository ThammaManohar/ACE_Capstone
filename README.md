# Legal Document Assistant (Agentic AI) — POC

A minimal agentic RAG assistant that summarizes legal documents and answers questions
over the [ninadn/indian-legal](https://huggingface.co/datasets/ninadn/indian-legal) dataset.

- Embeddings: `sentence-transformers/all-MiniLM-L6-v2` (local, free)
- Vector store: ChromaDB (local, file-based)
- Generation: Gemini/Gemma via Google AI Studio's free API

## Setup

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

4. Run the app:
   ```bash
   streamlit run app.py
   ```

## Usage

- **Summarize**: pick a sample document from the sidebar (or paste your own text) and click "Summarize".
- **Ask**: type a question about the indexed corpus and click "Ask" — the agent retrieves relevant
  chunks via similarity search and answers using only that retrieved context, with the retrieved
  chunks shown for transparency.

## Notes

- This is a proof-of-concept: routing between "summarize" and "answer" tools is keyword-based,
  not LLM-based, to keep it simple and fast.
- The free Gemini API tier has request-per-minute limits; `src/llm.py` retries with backoff on
  transient errors.
