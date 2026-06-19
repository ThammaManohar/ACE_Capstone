import time

from google import genai

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


def _generate(prompt: str, retries: int = 3) -> str:
    client = get_client()
    last_err = None
    for attempt in range(retries):
        try:
            response = client.models.generate_content(model=GEMINI_MODEL, contents=prompt)
            return (response.text or "").strip()
        except Exception as e:  # rate limit / transient errors
            last_err = e
            time.sleep(2 ** attempt)
    raise last_err


SUMMARY_PROMPT = """You are a legal assistant. Summarize the following legal document \
in plain, accurate language. Cover the case background, key arguments, and the outcome \
if present. Keep it under 200 words.

DOCUMENT:
{text}

SUMMARY:"""

QA_PROMPT = """You are a legal assistant answering questions using ONLY the provided \
context from legal documents. If the answer is not contained in the context, say \
"I could not find this in the indexed documents." Do not make up information.

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
    return _generate(SUMMARY_PROMPT.format(text=text[:12000]))


def answer(question: str, context: str) -> str:
    return _generate(QA_PROMPT.format(context=context[:12000], question=question))


def is_legal_document(text: str) -> bool:
    response = _generate(RELEVANCE_PROMPT.format(text=text[:6000]))
    return response.strip().upper().startswith("YES")
