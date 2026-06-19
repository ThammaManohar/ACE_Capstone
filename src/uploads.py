from io import BytesIO

from pypdf import PdfReader

from src.ingest import chunk_text


def extract_text(uploaded_file) -> str:
    """uploaded_file: a Streamlit UploadedFile (has .name and read())."""
    name = uploaded_file.name.lower()
    data = uploaded_file.getvalue()

    if name.endswith(".pdf"):
        reader = PdfReader(BytesIO(data))
        pages = [page.extract_text() or "" for page in reader.pages]
        return "\n".join(pages).strip()

    if name.endswith(".txt"):
        return data.decode("utf-8", errors="ignore").strip()

    raise ValueError("Unsupported file type. Please upload a PDF or .txt file.")


def chunks_for_upload(doc_id: str, text: str):
    return [
        {"doc_id": doc_id, "chunk_id": f"{doc_id}_chunk_{idx}", "text": piece}
        for idx, piece in enumerate(chunk_text(text))
    ]
