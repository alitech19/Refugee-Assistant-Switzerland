# Triage Log — AmanCH

A record of every significant technical problem encountered during development, how it was diagnosed, and how it was resolved.

---

## Issue #1 — Groq API Rate Limit Exceeded

**Symptom:**
The first real-world message received from a user triggered a `RateLimitError` from the Groq API — the AI response was aborted and the app crashed with a Python traceback.

**Root Cause:**
Token overconsumption per request:
- Full conversation history (all previous messages) was being sent to the LLM every turn
- The system prompt included a large PERMIT DETAILS section (~400–500 tokens) listing every permit type's rules
- Up to 3 sources × 600 characters each were injected into every prompt

**Solution:**
Four changes applied together:
1. Capped conversation history to the last 6 messages (`messages[:-1][-6:]`)
2. Removed the PERMIT DETAILS section from the system prompt — the LLM already knows Swiss asylum law from training
3. Reduced source retrieval from 3 to 2 results per query
4. Reduced source content limit from 600 to 400 characters per source

**Result:** Token usage per request dropped by approximately 40–50%.

---

## Issue #2 — Slow First Answer (5–10 Second Delay)

**Symptom:**
The first question a user asked always took noticeably longer than all subsequent questions — sometimes 5–10 seconds before any response began.

**Root Cause:**
The semantic search model (`paraphrase-multilingual-MiniLM-L12-v2`) is loaded lazily — only when the first search is triggered. Loading a ~120 MB sentence-transformer model from disk takes several seconds.

**Solution:**
Added a background thread that starts at app startup and calls `_ensure_embeddings()` while the user is reading the welcome screen:

```python
def _warm_embeddings():
    try:
        from backend.database import _ensure_embeddings
        _ensure_embeddings()
    except Exception:
        pass

threading.Thread(target=_warm_embeddings, daemon=True).start()
```

**Result:** By the time the user types their first question, the model is already loaded in memory. First-answer latency dropped to the same speed as all subsequent answers.

---

## Issue #3 — `AttributeError: st.session_state has no attribute "selected_permit"`

**Symptom:**
The entire UI crashed on startup with an `AttributeError`. The app was completely unusable.

**Root Cause:**
The permit pill buttons (N · F · B · C · S · ?) were added near the top of `app.py` and read `st.session_state.selected_permit` to determine which pill to highlight. However, the session state initialization block (which sets `selected_permit = None`) appeared further down the file. Streamlit executes the script top-to-bottom on every rerun, so the pills read the key before it was ever set.

**Solution:**
Changed the pill rendering to use `.get()` instead of direct attribute access:

```python
# Before (crashes if key not yet initialized)
is_selected = st.session_state.selected_permit == code

# After (safe — returns None if key does not exist)
is_selected = st.session_state.get("selected_permit") == code
```

**Result:** App loads correctly on every startup and rerun.

---

## Issue #4 — "Last Checked" Date Never Updated

**Symptom:**
The sidebar showed "Last checked: 2026-04-30" even after manually running the news fetcher. The date would only change when a new article was actually inserted — not when a fetch was attempted.

**Root Cause:**
`get_last_fetch_time()` was reading `MAX(created_at)` from the `auto_news` table. This only changes when a new article row is inserted. On days where no new articles exist (no new news published), the date was never updated even though the fetch ran successfully.

**Solution:**
Added a dedicated `settings` table (key-value store) to the database and a `record_fetch_time()` function that writes the current timestamp every time a fetch attempt completes — regardless of whether new articles were found:

```python
def record_fetch_time() -> None:
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    cursor.execute(
        "INSERT OR REPLACE INTO settings (key, value) VALUES ('last_news_fetch', ?)",
        (now,),
    )
```

**Result:** The sidebar now accurately shows the time of the last fetch attempt, not the last new article.

---

## Issue #5 — API Errors Showed Python Tracebacks to Users

**Symptom:**
When the Groq API was temporarily unavailable or rate-limited, the app displayed a raw Python traceback — confusing and alarming for a refugee user who sees technical error output.

**Root Cause:**
The `process_chat_turn()` call was not wrapped in a try/except block, so unhandled `openai.RateLimitError` and `openai.APIConnectionError` exceptions propagated to the Streamlit UI.

**Solution:**
Wrapped the LLM call in a specific exception handler for each error type, with a user-friendly message and fallback links:

```python
except openai.RateLimitError:
    assistant_text = (
        "⚠️ The AI service is temporarily at capacity. Please wait a minute and try again.\n\n"
        "For urgent help: [OSAR](https://www.osar.ch) · [SEM](https://www.sem.admin.ch)"
    )
except (openai.APIConnectionError, openai.APIStatusError):
    assistant_text = (
        "⚠️ Could not reach the AI service right now. Please check your internet connection."
    )
```

**Result:** Users see a calm, helpful message with fallback links instead of a crash.

---

## Issue #6 — All Imports Broke After Project Restructuring

**Symptom:**
After reorganising the project (moving `src/` → `backend/`, moving `backend/app.py` → `frontend/app.py`), the app failed to start with `ModuleNotFoundError: No module named 'src'`.

**Root Cause:**
Every file in the project used `from src.X import Y` (e.g. `from src.database import init_db`). After moving all `src/` modules into `backend/`, Python could no longer find the `src` package.

**Affected files:**
- `frontend/app.py` — 4 import blocks
- `backend/database.py` — 3 internal `from src.embeddings` imports (inside functions)
- `backend/llm_service.py` — 1 import
- `scripts/fetch_news.py` — 2 imports

**Solution:**
Systematically updated every `from src.X import Y` to `from backend.X import Y` across all files. Also verified that `sys.path.append(project_root)` in `frontend/app.py` correctly points to the project root from the new file location (`Path(__file__).resolve().parent.parent` works identically from `frontend/` as it did from `backend/`).

**Result:** All imports resolved correctly. App starts and runs normally.

---

## Issue #7 — LLM Inventing Swiss Government URLs

**Symptom:**
During testing, the LLM occasionally generated plausible-looking but incorrect Swiss government URLs (e.g. wrong cantonal subdomain paths, changed page slugs). A user following a broken link to a government site could be seriously misled.

**Root Cause:**
Large language models learn URL patterns from training data but cannot know which specific URLs are currently valid. Swiss government URLs frequently change structure between updates.

**Solution:**
Implemented a `_sanitize_urls()` post-processing function that runs on every LLM response before it reaches the user. It:
1. Parses all markdown links and bare URLs in the response
2. Checks each against a whitelist of approved domains (all 26 cantonal `.ch` domains, `sem.admin.ch`, `osar.ch`, etc.) and the URLs from retrieved sources
3. Replaces any non-approved URL with `*(please verify at sem.admin.ch or osar.ch)*`

The system prompt also contains an explicit rule forbidding URL invention, with examples of what to say instead.

**Result:** The LLM cannot surface a broken or invented link to the user.

---

*Issues are listed in the order they were discovered and resolved during development.*
