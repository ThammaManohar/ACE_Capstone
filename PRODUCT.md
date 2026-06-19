# Product

## Register

product

## Users
Non-technical, ordinary people looking up or making sense of Indian legal documents and case law — not lawyers, not developers. They may be researching a case, trying to understand a judgment they were sent, or asking general questions about legal precedent. They have no patience for ML-demo aesthetics (raw distance scores, "RAG POC" labels, debug-looking panels) and no tolerance for jargon.

## Product Purpose
A legal document assistant that answers questions over an indexed corpus of Indian legal case documents, and lets a user upload their own document (PDF/.txt) to get it summarized and folded into their session's Q&A context. Success = the user trusts the answer enough to act on it, understands when something is out of scope ("not in context") without confusion, and never sees an ML/engineering artifact (similarity scores, stack traces, raw chunk dumps) in the primary flow.

## Brand Personality
Professional, calm, precise. No emojis, no playful copy, no chat-bubble bot persona. It should read as a dedicated legal research tool, not a chatbot skin or a SaaS dashboard demo. Confidence comes from clarity and restraint, not from flourish.

## Anti-references
- Generic ChatGPT-style chat UI (bubble avatars, "AI is typing..." playfulness, bot personality)
- Raw ML-demo aesthetics: visible similarity/distance scores, "POC" labeling, debug panels, default Streamlit widget chrome
- Emoji-decorated headings or buttons
- Generic SaaS dashboard tropes (gradient hero text, icon-grid feature cards, eyebrows over every section)

## Design Principles
1. **Calm authority over flash.** Every visual choice should make the tool feel more credible, never more decorative.
2. **No leaking internals.** Retrieval mechanics (chunks, distances, "ephemeral session corpus") stay invisible; the user only sees documents, summaries, answers, and clear scope boundaries.
3. **Say "out of scope" plainly.** When something isn't in context, the UI states that directly and calmly — no apologetic chatbot tone, no hedging.
4. **One primary action per screen.** Q&A is the main act; upload-and-summarize is a clearly secondary, self-contained flow that doesn't compete with it visually.
5. **Built for someone who has never used a RAG tool.** No technical vocabulary (corpus, embedding, chunk, RAG) anywhere in the visible UI copy.

## Accessibility & Inclusion
Standard WCAG AA: body text ≥4.5:1 contrast, visible focus states on all interactive elements, no color-only status indicators (pair with text/icon), respects `prefers-reduced-motion`.
