import re

from src import llm, vectorstore

QUESTION_PATTERN = re.compile(
    r"^(what|why|how|who|when|where|which|is|are|does|did|can|could|should)\b", re.IGNORECASE
)


def is_question(user_input: str) -> bool:
    text = user_input.strip()
    return text.endswith("?") or bool(QUESTION_PATTERN.match(text))


def summarize_document(text: str) -> str:
    """Tool: summarize raw document text."""
    return llm.summarize(text)


def answer_question(question: str, session_collection=None, top_k: int = 4):
    """Tool: RAG over the indexed corpus (plus an optional session collection).
    Returns (answer, retrieved_chunks)."""
    hits = vectorstore.query_merged(question, session_collection=session_collection, top_k=top_k)
    context = "\n\n---\n\n".join(h["text"] for h in hits)
    response = llm.answer(question, context)
    return response, hits


def answer_question_stream(question: str, session_collection=None, top_k: int = 4):
    """Same as answer_question, but returns (retrieved_chunks, token_generator) so the
    caller can show retrieved sources immediately while the answer streams in."""
    hits = vectorstore.query_merged(question, session_collection=session_collection, top_k=top_k)
    context = "\n\n---\n\n".join(h["text"] for h in hits)
    return hits, llm.stream_answer(question, context)


def route(user_input: str):
    """Decide which tool to call for a free-form input. Returns (tool_name, result)."""
    if user_input.lower().startswith("summarize:"):
        text = user_input.split(":", 1)[1].strip()
        return "summarize", summarize_document(text)

    if is_question(user_input):
        answer_text, hits = answer_question(user_input)
        return "answer", (answer_text, hits)

    # default: treat as a doc/text to summarize
    return "summarize", summarize_document(user_input)
