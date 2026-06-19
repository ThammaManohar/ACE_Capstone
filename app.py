import streamlit as st

from src.agent import answer_question, summarize_document
from src.llm import is_legal_document
from src.uploads import chunks_for_upload, extract_text
from src.vectorstore import count, new_session_collection, upsert_chunks

st.set_page_config(
    page_title="Legal Document Assistant",
    layout="centered",
    initial_sidebar_state="collapsed",
)

CUSTOM_CSS = """
<style>
:root {
  --bg: oklch(1.000 0.000 0);
  --surface: oklch(0.970 0.004 230);
  --border: oklch(0.880 0.006 230);
  --ink: oklch(0.200 0.010 230);
  --muted: oklch(0.480 0.012 230);
  --primary: oklch(0.450 0.086 230);
  --primary-ink: oklch(1.000 0.000 0);
  --accent: oklch(0.550 0.130 70);
  --danger: oklch(0.470 0.150 25);
  --focus-ring: oklch(0.450 0.086 230 / 0.45);
}

@import url('https://fonts.googleapis.com/css2?family=Source+Serif+4:wght@500;600&family=Inter:wght@400;500;600&display=swap');

html, body, [class*="css"] { font-family: 'Inter', sans-serif; color: var(--ink); }
h1, h2, h3 { font-family: 'Source Serif 4', serif; font-weight: 600; letter-spacing: -0.01em; }

#MainMenu, footer, header[data-testid="stHeader"] { visibility: hidden; height: 0; }

.block-container { max-width: 760px; padding-top: 2.5rem; }

.app-header { margin-bottom: 2.2rem; }
.app-header h1 { font-size: 1.75rem; margin-bottom: 0.2rem; }
.app-header p { color: var(--muted); font-size: 0.95rem; margin: 0; }

.stTabs [data-baseweb="tab-list"] { gap: 1.5rem; border-bottom: 1px solid var(--border); }
.stTabs [data-baseweb="tab"] {
  font-family: 'Inter', sans-serif; font-weight: 500; font-size: 0.95rem;
  color: var(--muted); padding: 0.5rem 0;
}
.stTabs [aria-selected="true"] { color: var(--primary) !important; }

.stTextInput input, .stTextArea textarea {
  border-radius: 8px; border: 1px solid var(--border); font-family: 'Inter', sans-serif;
}
.stTextInput input:focus, .stTextArea textarea:focus {
  box-shadow: 0 0 0 2px var(--focus-ring); border-color: var(--primary);
}

.stButton button {
  border-radius: 8px; font-weight: 500; border: 1px solid var(--primary);
  background: var(--primary); color: var(--primary-ink); box-shadow: none;
}
.stButton button:hover { opacity: 0.92; }
.stButton button:focus-visible { box-shadow: 0 0 0 2px var(--focus-ring); }

.answer-panel {
  background: var(--surface); border: 1px solid var(--border); border-radius: 8px;
  padding: 1.25rem 1.4rem; margin-top: 1rem;
  animation: fade-in 180ms ease-out;
}
@media (prefers-reduced-motion: reduce) { .answer-panel { animation: none; } }
@keyframes fade-in { from { opacity: 0; transform: translateY(4px); } to { opacity: 1; transform: translateY(0); } }

.answer-panel h4 { font-family: 'Inter', sans-serif; font-weight: 600; font-size: 0.85rem;
  color: var(--muted); text-transform: none; margin: 0 0 0.5rem 0; }
.answer-panel p { line-height: 1.6; margin: 0; }

.scope-pill {
  display: inline-block; background: var(--surface); border: 1px solid var(--border);
  color: var(--muted); border-radius: 999px; padding: 0.3rem 0.8rem; font-size: 0.85rem;
}

.source-item { padding: 0.6rem 0; border-bottom: 1px solid var(--border); }
.source-item:last-child { border-bottom: none; }
.source-item .label { font-weight: 500; font-size: 0.85rem; color: var(--ink); }
.source-item .snippet { color: var(--muted); font-size: 0.85rem; margin-top: 0.2rem; line-height: 1.5; }

.status-line { color: var(--muted); font-size: 0.9rem; margin-top: 0.6rem; }
.error-line { color: var(--danger); font-size: 0.9rem; margin-top: 0.6rem; }
</style>
"""
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

st.markdown(
    """
    <div class="app-header">
      <h1>Legal Document Assistant</h1>
      <p>Ask a question about Indian case law, or upload a document of your own.</p>
    </div>
    """,
    unsafe_allow_html=True,
)

if "session_collection" not in st.session_state:
    st.session_state.session_collection = None
if "session_doc_name" not in st.session_state:
    st.session_state.session_doc_name = None

indexed_count = count()

ask_tab, upload_tab = st.tabs(["Ask", "Upload a document"])

with ask_tab:
    if indexed_count == 0:
        st.markdown(
            '<p class="error-line">The document index has not been built yet. '
            "Run scripts/build_index.py before asking questions.</p>",
            unsafe_allow_html=True,
        )

    if st.session_state.session_doc_name:
        st.markdown(
            f'<span class="scope-pill">Including your uploaded document: '
            f"{st.session_state.session_doc_name}</span>",
            unsafe_allow_html=True,
        )

    question = st.text_input("Your question", placeholder="e.g. What counts as valid consideration in a contract?")
    ask_clicked = st.button("Ask", disabled=indexed_count == 0)

    if ask_clicked:
        if not question.strip():
            st.markdown('<p class="error-line">Type a question first.</p>', unsafe_allow_html=True)
        else:
            with st.spinner("Searching the indexed documents..."):
                answer_text, hits = answer_question(
                    question, session_collection=st.session_state.session_collection
                )
            st.markdown(
                f'<div class="answer-panel"><h4>Answer</h4><p>{answer_text}</p></div>',
                unsafe_allow_html=True,
            )
            if hits:
                with st.expander("Sources"):
                    for h in hits:
                        label = (
                            "Your uploaded document"
                            if h["doc_id"] == "session_upload"
                            else f"Case document {h['doc_id'].replace('doc_', '#')}"
                        )
                        snippet = h["text"][:220].replace("\n", " ").strip()
                        st.markdown(
                            f'<div class="source-item"><div class="label">{label}</div>'
                            f'<div class="snippet">{snippet}…</div></div>',
                            unsafe_allow_html=True,
                        )

with upload_tab:
    st.write("Upload a legal document (PDF or .txt) to get a summary and ask follow-up questions about it.")
    uploaded_file = st.file_uploader("Document", type=["pdf", "txt"], label_visibility="collapsed")

    if uploaded_file is not None:
        summarize_clicked = st.button("Summarize")

        if summarize_clicked:
            try:
                text = extract_text(uploaded_file)
            except ValueError as e:
                st.markdown(f'<p class="error-line">{e}</p>', unsafe_allow_html=True)
                text = None

            if text is not None and not text.strip():
                st.markdown(
                    '<p class="error-line">No readable text was found in this file.</p>',
                    unsafe_allow_html=True,
                )
            elif text:
                with st.spinner("Reading the document..."):
                    relevant = is_legal_document(text)

                if not relevant:
                    st.markdown(
                        '<p class="status-line">This doesn\'t appear to be a legal document, '
                        "so it hasn't been summarized or added to your session.</p>",
                        unsafe_allow_html=True,
                    )
                else:
                    with st.spinner("Summarizing..."):
                        summary = summarize_document(text)

                    session_collection = new_session_collection()
                    chunks = chunks_for_upload("session_upload", text)
                    upsert_chunks(chunks, collection=session_collection)
                    st.session_state.session_collection = session_collection
                    st.session_state.session_doc_name = uploaded_file.name

                    st.markdown(
                        f'<div class="answer-panel"><h4>Summary</h4><p>{summary}</p></div>',
                        unsafe_allow_html=True,
                    )
                    st.markdown(
                        '<p class="status-line">This document has been added to your session. '
                        "Switch to the Ask tab to ask follow-up questions about it.</p>",
                        unsafe_allow_html=True,
                    )
