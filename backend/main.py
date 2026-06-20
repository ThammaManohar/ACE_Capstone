import json
import threading
import uuid
from pathlib import Path

from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles

from src.agent import answer_question, answer_question_stream, summarize_document
from src.ingest import chunk_documents, load_documents, save_docs_cache
from src.llm import is_legal_document
from src.uploads import chunks_for_upload, extract_text
from src.vectorstore import count, new_session_collection, upsert_chunks

SOURCES_MARKER = "\x00SOURCES\x00"

app = FastAPI(title="Legal Document Assistant API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# session_id -> chroma ephemeral collection (in-memory, never persisted)
SESSIONS: dict[str, object] = {}

INDEX_STATUS = {"state": "pending"}  # pending -> building -> ready | failed


def _build_index_in_background():
    if count() > 0:
        INDEX_STATUS["state"] = "ready"
        return
    INDEX_STATUS["state"] = "building"
    try:
        docs = load_documents()
        save_docs_cache(docs)
        chunks = chunk_documents(docs)
        upsert_chunks(chunks)
        INDEX_STATUS["state"] = "ready"
    except Exception as e:
        INDEX_STATUS["state"] = "failed"
        INDEX_STATUS["error"] = str(e)


@app.on_event("startup")
def start_index_build():
    # Runs in a background thread so the server can bind to its port and pass
    # platform health checks immediately, instead of blocking startup on the
    # multi-minute dataset download + embedding step.
    threading.Thread(target=_build_index_in_background, daemon=True).start()


class UploadedFileLike:
    """Adapter so FastAPI's UploadFile fits src.uploads.extract_text's expected interface."""

    def __init__(self, name: str, data: bytes):
        self.name = name
        self._data = data

    def getvalue(self) -> bytes:
        return self._data


@app.get("/api/status")
def status():
    return {"indexed_chunks": count(), "index_state": INDEX_STATUS["state"]}


@app.post("/api/session")
def create_session():
    session_id = str(uuid.uuid4())
    return {"session_id": session_id}


@app.post("/api/ask")
def ask(question: str = Form(...), session_id: str | None = Form(None)):
    if not question.strip():
        raise HTTPException(400, "Question is required.")
    if count() == 0:
        raise HTTPException(503, "The document index has not been built yet.")

    session_collection = SESSIONS.get(session_id) if session_id else None
    answer_text, hits = answer_question(question, session_collection=session_collection)

    sources = [
        {
            "label": "Your uploaded document"
            if h["doc_id"] == "session_upload"
            else f"Case document {h['doc_id'].replace('doc_', '#')}",
            "snippet": h["text"][:220].strip(),
        }
        for h in hits
    ]
    return {"answer": answer_text, "sources": sources}


def _source_label(doc_id: str) -> str:
    return "Your uploaded document" if doc_id == "session_upload" else f"Case document {doc_id.replace('doc_', '#')}"


@app.post("/api/ask/stream")
def ask_stream(question: str = Form(...), session_id: str | None = Form(None)):
    if not question.strip():
        raise HTTPException(400, "Question is required.")
    if count() == 0:
        raise HTTPException(503, "The document index has not been built yet.")

    session_collection = SESSIONS.get(session_id) if session_id else None
    hits, token_stream = answer_question_stream(question, session_collection=session_collection)

    sources = [
        {"label": _source_label(h["doc_id"]), "snippet": h["text"][:220].strip()} for h in hits
    ]

    def generate():
        for token in token_stream:
            yield token
        yield SOURCES_MARKER + json.dumps(sources)

    return StreamingResponse(generate(), media_type="text/plain")


@app.post("/api/upload")
async def upload(file: UploadFile = File(...), session_id: str = Form(...)):
    name = file.filename or ""
    if not (name.lower().endswith(".pdf") or name.lower().endswith(".txt")):
        raise HTTPException(400, "Please upload a PDF or .txt file.")

    data = await file.read()
    try:
        text = extract_text(UploadedFileLike(name, data))
    except ValueError as e:
        raise HTTPException(400, str(e))

    if not text.strip():
        raise HTTPException(400, "No readable text was found in this file.")

    relevant = is_legal_document(text)
    if not relevant:
        return JSONResponse({"relevant": False})

    summary = summarize_document(text)

    session_collection = new_session_collection()
    chunks = chunks_for_upload("session_upload", text)
    upsert_chunks(chunks, collection=session_collection)
    SESSIONS[session_id] = session_collection

    return {"relevant": True, "summary": summary, "filename": name}


FRONTEND_DIR = Path(__file__).resolve().parent.parent / "frontend"
app.mount("/", StaticFiles(directory=str(FRONTEND_DIR), html=True), name="frontend")
