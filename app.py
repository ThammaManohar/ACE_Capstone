import streamlit as st

from src.agent import answer_question, summarize_document
from src.ingest import load_docs_cache
from src.vectorstore import count

st.set_page_config(page_title="Legal Document Assistant", layout="wide")
st.title("⚖️ Legal Document Assistant (Agentic RAG POC)")

docs = load_docs_cache()
indexed_count = count()

with st.sidebar:
    st.header("Corpus")
    st.write(f"Indexed chunks: **{indexed_count}**")
    if indexed_count == 0:
        st.warning("Run `python scripts/build_index.py` first to build the index.")

    st.header("Sample document")
    doc_options = ["-- paste your own text below --"] + [d["doc_id"] for d in docs]
    selected = st.selectbox("Pick an indexed document", doc_options)

selected_doc = None
if selected != doc_options[0]:
    selected_doc = next(d for d in docs if d["doc_id"] == selected)

st.subheader("Summarize a document")
default_text = selected_doc["text"] if selected_doc else ""
text_input = st.text_area("Document text", value=default_text, height=200)

if st.button("Summarize", type="primary"):
    if not text_input.strip():
        st.error("Provide some document text first.")
    else:
        with st.spinner("Summarizing..."):
            summary = summarize_document(text_input)
        st.success("Summary")
        st.write(summary)
        if selected_doc and selected_doc.get("reference_summary"):
            with st.expander("Reference summary (from dataset)"):
                st.write(selected_doc["reference_summary"])

st.divider()
st.subheader("Ask a question about the indexed corpus")
question = st.text_input("Your question")

if st.button("Ask"):
    if not question.strip():
        st.error("Type a question first.")
    elif indexed_count == 0:
        st.error("No documents indexed yet. Run scripts/build_index.py first.")
    else:
        with st.spinner("Retrieving context and generating answer..."):
            answer_text, hits = answer_question(question)
        st.success("Answer")
        st.write(answer_text)
        with st.expander("Retrieved context"):
            for h in hits:
                st.markdown(f"**{h['doc_id']}** (distance: {h['distance']:.4f})")
                st.text(h["text"][:500])
                st.markdown("---")
