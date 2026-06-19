// Relative by default: the backend now serves this frontend itself (same origin),
// both locally and on Hugging Face Spaces. Override window.API_BASE before this
// script loads only if you're running the frontend from a separate static server.
const API_BASE = window.API_BASE || "";

function getSessionId() {
  let id = localStorage.getItem("lda_session_id");
  if (!id) {
    id = crypto.randomUUID();
    localStorage.setItem("lda_session_id", id);
  }
  return id;
}

function setHidden(el, hidden) {
  el.hidden = hidden;
}

function stripMarkdown(text) {
  return text
    .replace(/\*\*(.*?)\*\*/g, "$1")
    .replace(/(?<!\w)\*(.*?)\*(?!\w)/g, "$1")
    .replace(/^#{1,6}\s+/gm, "");
}

// --- Tabs ---
const tabs = document.querySelectorAll(".tab");
const panels = document.querySelectorAll(".tab-panel");

tabs.forEach((tab) => {
  tab.addEventListener("click", () => {
    tabs.forEach((t) => {
      t.classList.toggle("is-active", t === tab);
      t.setAttribute("aria-selected", t === tab ? "true" : "false");
    });
    panels.forEach((p) => {
      p.classList.toggle("is-active", p.dataset.panel === tab.dataset.tab);
    });
  });
});

// --- Ask flow ---
const questionInput = document.getElementById("question-input");
const askButton = document.getElementById("ask-button");
const askStatus = document.getElementById("ask-status");
const answerPanel = document.getElementById("answer-panel");
const answerText = document.getElementById("answer-text");
const sourcesBlock = document.getElementById("sources-block");
const sourcesList = document.getElementById("sources-list");
const scopePill = document.getElementById("scope-pill");

async function refreshScopePill() {
  const uploadedName = localStorage.getItem("lda_uploaded_name");
  if (uploadedName) {
    scopePill.textContent = `Including your uploaded document: ${uploadedName}`;
    setHidden(scopePill, false);
  }
}
refreshScopePill();

async function askQuestion() {
  const question = questionInput.value.trim();
  setHidden(askStatus, true);
  setHidden(answerPanel, true);
  setHidden(sourcesBlock, true);

  if (!question) {
    askStatus.textContent = "Type a question first.";
    askStatus.classList.add("error-line");
    setHidden(askStatus, false);
    return;
  }
  askStatus.classList.remove("error-line");

  askButton.disabled = true;
  askStatus.textContent = "Searching the indexed documents...";
  setHidden(askStatus, false);

  const SOURCES_MARKER = "\x00SOURCES\x00";

  try {
    const form = new FormData();
    form.append("question", question);
    form.append("session_id", getSessionId());

    const res = await fetch(`${API_BASE}/api/ask/stream`, { method: "POST", body: form });
    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      throw new Error(err.detail || "Something went wrong while asking.");
    }

    const reader = res.body.getReader();
    const decoder = new TextDecoder();
    let buffer = "";
    let revealedAnswer = false;

    while (true) {
      const { done, value } = await reader.read();
      if (done) break;
      buffer += decoder.decode(value, { stream: true });

      const markerIndex = buffer.indexOf(SOURCES_MARKER);
      const visibleText = markerIndex === -1 ? buffer : buffer.slice(0, markerIndex);

      if (visibleText && !revealedAnswer) {
        setHidden(askStatus, true);
        setHidden(answerPanel, false);
        revealedAnswer = true;
      }
      answerText.textContent = stripMarkdown(visibleText);

      if (markerIndex !== -1) {
        const sourcesJson = buffer.slice(markerIndex + SOURCES_MARKER.length);
        try {
          const sources = JSON.parse(sourcesJson);
          if (sources.length) {
            sourcesList.innerHTML = "";
            sources.forEach((s, i) => {
              const item = document.createElement("div");
              item.className = "source-item";
              item.innerHTML = `<div class="citation-mark">§${i + 1}</div><div><div class="label">${s.label}</div><div class="snippet">${s.snippet}…</div></div>`;
              sourcesList.appendChild(item);
            });
            setHidden(sourcesBlock, false);
          }
        } catch {
          // marker arrived but JSON not fully buffered yet; next chunk will complete it
        }
      }
    }
  } catch (e) {
    askStatus.textContent = e.message;
    askStatus.classList.add("error-line");
    setHidden(askStatus, false);
  } finally {
    askButton.disabled = false;
  }
}

askButton.addEventListener("click", askQuestion);
questionInput.addEventListener("keydown", (e) => {
  if (e.key === "Enter") askQuestion();
});

// --- Upload flow ---
const fileInput = document.getElementById("file-input");
const fileNameEl = document.getElementById("file-name");
const summarizeButton = document.getElementById("summarize-button");
const uploadStatus = document.getElementById("upload-status");
const uploadError = document.getElementById("upload-error");
const summaryPanel = document.getElementById("summary-panel");
const summaryText = document.getElementById("summary-text");
const uploadSuccess = document.getElementById("upload-success");

let selectedFile = null;

fileInput.addEventListener("change", () => {
  selectedFile = fileInput.files[0] || null;
  setHidden(summaryPanel, true);
  setHidden(uploadSuccess, true);
  setHidden(uploadError, true);
  setHidden(uploadStatus, true);

  if (selectedFile) {
    fileNameEl.textContent = selectedFile.name;
    setHidden(fileNameEl, false);
    summarizeButton.disabled = false;
  } else {
    setHidden(fileNameEl, true);
    summarizeButton.disabled = true;
  }
});

summarizeButton.addEventListener("click", async () => {
  if (!selectedFile) return;

  setHidden(uploadError, true);
  setHidden(uploadSuccess, true);
  setHidden(summaryPanel, true);
  summarizeButton.disabled = true;
  uploadStatus.textContent = "Reading the document...";
  setHidden(uploadStatus, false);

  try {
    const form = new FormData();
    form.append("file", selectedFile);
    form.append("session_id", getSessionId());

    const res = await fetch(`${API_BASE}/api/upload`, { method: "POST", body: form });
    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      throw new Error(err.detail || "Something went wrong while processing the file.");
    }
    const data = await res.json();
    setHidden(uploadStatus, true);

    if (!data.relevant) {
      uploadStatus.textContent =
        "This doesn't appear to be a legal document, so it hasn't been summarized or added to your session.";
      setHidden(uploadStatus, false);
    } else {
      summaryText.textContent = stripMarkdown(data.summary);
      setHidden(summaryPanel, false);

      localStorage.setItem("lda_uploaded_name", data.filename);
      refreshScopePill();

      uploadSuccess.textContent =
        "This document has been added to your session. Switch to the Ask tab to ask follow-up questions about it.";
      setHidden(uploadSuccess, false);
    }
  } catch (e) {
    uploadStatus.textContent = "";
    setHidden(uploadStatus, true);
    uploadError.textContent = e.message;
    setHidden(uploadError, false);
  } finally {
    summarizeButton.disabled = false;
  }
});

// --- Status check ---
fetch(`${API_BASE}/api/status`)
  .then((r) => r.json())
  .then((data) => {
    if (!data.indexed_chunks) {
      askStatus.textContent =
        "The document index has not been built yet. Run scripts/build_index.py first.";
      askStatus.classList.add("error-line");
      setHidden(askStatus, false);
      askButton.disabled = true;
    }
  })
  .catch(() => {
    askStatus.textContent = "Could not reach the backend. Is it running?";
    askStatus.classList.add("error-line");
    setHidden(askStatus, false);
  });
