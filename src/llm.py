import json
import time

from google import genai
from google.genai import types

from src.config import GEMINI_API_KEY, GEMINI_MODEL

_client = None


def get_client():
    global _client
    if _client is None:
        if not GEMINI_API_KEY:
            raise RuntimeError(
                "GEMINI_API_KEY is not set. Copy .env.example to .env and add your "
                "free key from https://aistudio.google.com/apikey"
            )
        _client = genai.Client(api_key=GEMINI_API_KEY)
    return _client


def _generate(prompt: str, retries: int = 3, config=None) -> str:
    client = get_client()
    last_err = None
    for attempt in range(retries):
        try:
            response = client.models.generate_content(
                model=GEMINI_MODEL, contents=prompt, config=config
            )
            return (response.text or "").strip()
        except Exception as e:  # rate limit / transient errors
            last_err = e
            time.sleep(2 ** attempt)
    raise last_err


SUMMARY_PROMPT = """You are a legal assistant. Summarize the following legal document \
in plain, accurate language, in three parts: background, key arguments, and outcome \
(leave outcome empty if the document has no resolution yet). Plain sentences only, no \
markdown formatting. Keep each part to 2-4 sentences.

DOCUMENT:
{text}"""

SUMMARY_SCHEMA = {
    "type": "object",
    "properties": {
        "background": {"type": "string"},
        "key_arguments": {"type": "string"},
        "outcome": {"type": "string"},
    },
    "required": ["background", "key_arguments"],
}

QA_PROMPT = """You are a legal assistant answering questions using ONLY the provided \
context from legal documents. If the answer is not contained in the context, say \
"I could not find this in the indexed documents." Do not make up information. Answer in \
plain sentences with no markdown formatting (no asterisks, no bold, no headers).

CONTEXT:
{context}

QUESTION:
{question}

ANSWER:"""


RELEVANCE_PROMPT = """Decide if the following text is a legal document (e.g. a court \
judgment, legal filing, contract, statute, or similar). Answer with exactly one word: \
YES or NO.

TEXT:
{text}

ANSWER:"""


def summarize(text: str) -> str:
    """Returns a summary with guaranteed paragraph breaks between Background /
    Key arguments / Outcome — built from structured JSON output rather than
    hoping the model inserts literal newlines consistently."""
    config = types.GenerateContentConfig(
        response_mime_type="application/json", response_schema=SUMMARY_SCHEMA
    )
    raw = _generate(SUMMARY_PROMPT.format(text=text[:12000]), config=config)
    try:
        data = json.loads(raw)
    except (json.JSONDecodeError, TypeError):
        return raw

    parts = []
    if data.get("background"):
        parts.append(f"Background\n{data['background'].strip()}")
    if data.get("key_arguments"):
        parts.append(f"Key arguments\n{data['key_arguments'].strip()}")
    if data.get("outcome"):
        parts.append(f"Outcome\n{data['outcome'].strip()}")
    return "\n\n".join(parts)


def answer(question: str, context: str) -> str:
    return _generate(QA_PROMPT.format(context=context[:12000], question=question))


def stream_answer(question: str, context: str, retries: int = 2):
    """Yield answer text chunks as they're generated, instead of waiting for the full response.
    Falls back to the non-streaming call (with its own retry/backoff) if streaming itself
    fails to even start, which happens occasionally on the free tier."""
    client = get_client()
    prompt = QA_PROMPT.format(context=context[:12000], question=question)

    for attempt in range(retries):
        try:
            chunks = client.models.generate_content_stream(model=GEMINI_MODEL, contents=prompt)
            for chunk in chunks:
                if chunk.text:
                    yield chunk.text
            return
        except Exception:
            if attempt == retries - 1:
                break
            time.sleep(2 ** attempt)

    yield _generate(prompt)


def is_legal_document(text: str) -> bool:
    response = _generate(RELEVANCE_PROMPT.format(text=text[:6000]))
    return response.strip().upper().startswith("YES")
