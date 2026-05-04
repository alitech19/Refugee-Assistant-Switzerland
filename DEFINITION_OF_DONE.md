# Definition of Done — AmanCH MVP

Progress tracking for the Minimum Viable Product submission.

**Project:** AmanCH — Refugee Assistant Switzerland
**Submitted by:** Ali Sulaiman
**Programme:** PowerCoders
**GitHub:** https://github.com/alitech19/Refugee-Assistant-Switzerland

---

## Core Functionality

- [x] AI assistant answers questions about the Swiss asylum system
- [x] Answers are grounded in retrieved Swiss official sources — not hallucinated
- [x] Works in 15+ languages (auto-detected from the user's message)
- [x] No account, login, or installation required for the end user
- [x] Conversation history is preserved across turns within a session

---

## Permit & Location Awareness

- [x] User can select their permit type (N · F · B · C · S · ?)
- [x] Every LLM answer is tailored specifically to the selected permit type
- [x] User can select their canton from a dropdown
- [x] Answers prioritise canton-specific offices, language courses, and procedures

---

## Information Sources

- [x] 70+ curated Swiss official sources loaded into the knowledge base (SEM, OSAR, ch.ch, FIDE, all 26 cantonal migration offices)
- [x] Hybrid keyword + semantic search retrieves the most relevant sources per query
- [x] Daily automatic news fetch from SEM and OSAR RSS feeds
- [x] Embeddings stored in SQLite and recomputed only when source content changes
- [x] LLM is forbidden from inventing URLs — URL sanitiser strips any non-approved links

---

## User Experience

- [x] Voice input in any language (Whisper large-v3 via Groq — 99 languages)
- [x] Text-to-speech read-aloud in the user's language (gTTS)
- [x] Topic shortcut buttons on the welcome screen (Permits, Asylum, Work, Healthcare…)
- [x] Common question buttons for fast access to the most frequent queries
- [x] Permit Quick Reference table (expandable)
- [x] Thumbs up / thumbs down feedback on every AI response
- [x] "Start new conversation" button resets context cleanly
- [x] Mobile-responsive layout

---

## Safety & Reliability

- [x] Groq rate limit and connection errors handled with user-friendly fallback messages + links to OSAR and SEM
- [x] Proactive 30-day appeal deadline warning when relevant
- [x] Emergency contacts always visible in the sidebar (Police 117 · Ambulance 144)
- [x] Legal disclaimer displayed on every page ("Guidance only — not legal advice")
- [x] Conversations stored locally only — no data shared or sold

---

## Code Quality & Structure

- [x] Clean separation: `frontend/` (UI) · `backend/` (logic) · `data/` (sources) · `scripts/` (automation)
- [x] No hardcoded API keys — all secrets loaded from `.env`
- [x] Background thread warms the embedding model at startup (eliminates slow first answer)
- [x] Background thread auto-fetches news once per day without blocking the UI
- [x] Conversation history capped at 6 messages to control token usage

---

## Documentation

- [x] Professional README ("Founder's Manual") covering features, setup, architecture, and disclaimer
- [x] Triage Log documenting 7 technical hurdles encountered and resolved
- [x] Definition of Done (this document)
- [x] Inline comments for non-obvious code decisions

---

## Submission Deliverables

- [x] Working code on GitHub: https://github.com/alitech19/Refugee-Assistant-Switzerland
- [x] App runnable with a single command: `streamlit run frontend/app.py`
- [x] README explains what the tool does and how to run it
- [x] Triage Log documents independent problem-solving
- [x] Definition of Done with checked boxes (this document)

---

## Not in MVP — Planned for Next Version

- [ ] Admin dashboard for analysing user feedback (thumbs up/down data is collected, not yet visualised)
- [ ] Deployed to cloud (Streamlit Cloud / Hugging Face Spaces) for public access without local setup
- [ ] Canton data complete for all 26 cantons (16 cantons currently have migration office only; 10 have full integration + language course data)
- [ ] Conversation export / print functionality for users

---

**MVP Status: Complete ✅**
