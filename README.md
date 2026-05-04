# AmanCH — Refugee Assistant Switzerland

> **Free, multilingual AI assistant helping refugees and asylum seekers understand Switzerland's asylum system — in their own language.**

AmanCH answers questions about permits, work rights, asylum procedures, healthcare, family reunification, and integration — grounded in 70+ verified Swiss official sources (SEM, OSAR, cantonal offices), never guessing.
https://refugee-assistant-switzerland-gndat6oqniq737kahzd3p9.streamlit.app/
---

## Features

- **15+ languages** — Arabic, Tigrinya, Somali, Dari, Ukrainian, Turkish, German, French, Italian, English, and more. Detects the language automatically and always responds in the same language.
- **Permit-aware answers** — Users select their permit type (N · F · B · C · S · ?) and every answer is tailored specifically to that permit.
- **Canton-specific information** — Select your canton and get answers about local migration offices, language courses, and integration programmes.
- **RAG pipeline** — Every answer is grounded in retrieved Swiss official sources. The LLM is never allowed to invent URLs or fabricate legal facts.
- **Voice input** — Ask questions by speaking in any language (Whisper via Groq).
- **Text-to-speech** — Responses can be read aloud in the user's language (gTTS).
- **Live news** — Automatically fetches the latest updates from SEM and OSAR RSS feeds daily.
- **30-day appeal reminder** — Proactively warns about the critical appeal deadline after a rejected decision.
- **Conversation history** — Full chat stored locally in SQLite; context preserved across turns.
- **No account needed** — Open the app, ask a question. That is all.

---

## Project Structure

```
AmanCH/
│
├── frontend/
│   └── app.py                  # Streamlit UI — the full web interface
│
├── backend/
│   ├── database.py             # SQLite layer: conversations, sources, news, feedback
│   ├── embeddings.py           # Sentence-transformer model for semantic search
│   ├── llm_service.py          # Groq API calls, language detection, URL sanitisation
│   ├── prompts.py              # System prompt for the AmanCH assistant
│   ├── resolver.py             # Query parsing: permit detection, topic detection, search query builder
│   └── state_tracker.py        # Conversation state (current permit across turns)
│
├── data/
│   ├── app.db                  # SQLite database (auto-created on first run)
│   └── official_sources.json   # 70+ curated Swiss official sources (SEM, OSAR, cantons)
│
├── scripts/
│   └── fetch_news.py           # Fetches SEM + OSAR RSS feeds, saves to auto_news table
│
├── .streamlit/
│   └── config.toml             # Streamlit config (file watcher disabled for performance)
│
├── .env                        # Your API key (not committed to git)
├── requirements.txt
└── generate_pitch_deck.py      # Generates the project pitch deck as a .pptx file
```

---

## Tech Stack

| Layer | Technology | Why |
|---|---|---|
| **Frontend** | Streamlit | Rapid Python-native web UI, no JavaScript needed |
| **LLM** | LLaMA 3.3-70b via Groq API | Fast inference, strong multilingual capability, OpenAI-compatible |
| **Speech-to-text** | Whisper large-v3 via Groq | 99-language transcription, same API key |
| **Text-to-speech** | gTTS (Google TTS) | Free, works for all major languages |
| **Semantic search** | `paraphrase-multilingual-MiniLM-L12-v2` | Compact multilingual embedding model, runs locally |
| **Database** | SQLite | Zero-config, serverless, stores knowledge base + conversations |
| **News feed** | feedparser + SEM/OSAR RSS | Keeps answers current without manual updates |
| **Env management** | python-dotenv | Keeps API key out of source code |

---

## Setup

### 1. Clone the repository

```bash
git clone https://github.com/your-username/Refugee-Assistant-Switzerland.git
cd Refugee-Assistant-Switzerland
```

### 2. Create a virtual environment

```bash
python -m venv .venv

# Windows
.venv\Scripts\activate

# macOS / Linux
source .venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Create your `.env` file

Create a file named `.env` in the project root:

```env
GROQ_API_KEY=your_groq_api_key_here
```

To get a free Groq API key:
1. Go to [console.groq.com](https://console.groq.com)
2. Sign up for a free account
3. Navigate to **API Keys** and create a new key
4. Paste it into your `.env` file

### 5. Run the app

```bash
streamlit run frontend/app.py
```

The app will open automatically in your browser at `http://localhost:8501`.

> On first launch, the embedding model (`paraphrase-multilingual-MiniLM-L12-v2`) is downloaded once (~120 MB) and cached locally. This is a one-time step.

---

## Environment Variables

| Variable | Required | Description |
|---|---|---|
| `GROQ_API_KEY` | Yes | API key for Groq (LLM + Whisper transcription) |

---

## How It Works — RAG Pipeline

```
User question (any language)
        │
        ▼
  Query Resolver
  (permit detection, topic detection, search query builder)
        │
        ▼
  Source Search
  (hybrid keyword + semantic search across 70+ Swiss official sources + live news)
        │
        ▼
  LLM Call (LLaMA 3.3-70b via Groq)
  System prompt + retrieved sources + conversation history + permit/canton context
        │
        ▼
  URL Sanitiser
  (strips any invented URLs — only approved Swiss domains allowed)
        │
        ▼
  Answer shown in user's language
```

The assistant is explicitly forbidden from inventing URLs, extrapolating beyond sources, or giving personal legal advice. If it does not know, it says so and directs the user to SEM or OSAR.

---

## Knowledge Base

`data/official_sources.json` contains 70+ manually curated entries covering:

- Swiss Federal sources: SEM (State Secretariat for Migration), OSAR, ch.ch, FIDE, UNHCR
- All 26 cantonal migration offices with direct URLs
- Permit-specific pages for N, F, B, C, S permit types
- Integration programmes and language courses for major cantons
- Work authorisation, family reunification, healthcare, education, and appeals

Sources are loaded into SQLite on startup. Embeddings are computed lazily and cached in the database — they are only recomputed when source content changes.

---

## Scheduled News Fetch

The app fetches SEM and OSAR RSS feeds automatically once per day at startup. To also run it on a schedule independently (e.g. to keep the database fresh even when the app is not running), set up a Windows Task Scheduler job:

**Option A — Task Scheduler (GUI):**
1. Open **Task Scheduler** → Create Basic Task
2. Name: `AmanCH News Fetch`
3. Trigger: Daily at 07:00
4. Action: Start a program
   - Program: `.venv\Scripts\python.exe`
   - Arguments: `scripts\fetch_news.py`
   - Start in: `C:\path\to\Refugee-Assistant-Switzerland`
5. Finish → Enable

**Option B — Command Prompt (Administrator):**
```cmd
schtasks /create /tn "AmanCHNews" ^
  /tr "\"C:\path\to\.venv\Scripts\python.exe\" \"C:\path\to\scripts\fetch_news.py\"" ^
  /sc daily /st 07:00 /f
```

---

## Key Architecture Decisions

**Why keyword + semantic hybrid search, not pure vectors?**
Swiss asylum law is structured and domain-specific. A hybrid approach (keyword scoring for exact permit/canton matches + semantic embeddings for cross-language queries) gives better precision than either alone, while running entirely on CPU with a compact 120 MB model.

**Why Groq + LLaMA 3.3-70b?**
Fast inference (token/s far above OpenAI on equivalent models), strong multilingual capability, and an OpenAI-compatible API that makes swapping models trivial. The free tier covers normal usage.

**Why SQLite?**
Zero configuration, no server to manage, and a single file that holds the knowledge base, conversation history, feedback, news, and settings. Straightforward to back up or move.

**Why Streamlit?**
The entire UI is Python — no JavaScript, no separate frontend build step. This keeps the codebase small and the deployment simple for a single-user or small-group tool.

---

## Important Disclaimer

AmanCH provides **guidance only — not legal advice**.

For important decisions (asylum appeals, rejected applications, family reunification, work authorisation), users must always verify with:

- **SEM** — [sem.admin.ch](https://www.sem.admin.ch) — Federal migration authority
- **OSAR** — [osar.ch](https://www.osar.ch) — Free legal aid for asylum seekers
- **Their cantonal migration office** — For canton-specific rules and procedures

The 30-day appeal window after a rejected asylum decision is critical. Missing it forfeits the right to appeal.

---

## Supported Languages

Arabic · Tigrinya · Amharic · Somali · Dari · Farsi · Pashto · Kurdish · Ukrainian · Turkish · German · French · Italian · Swahili · English · and more

The language is detected automatically from the user's message. No selection required.

---

## Supported Permit Types

| Permit | Who it covers |
|---|---|
| **N** | Asylum seekers — procedure pending |
| **F** | Provisionally admitted persons |
| **B** | Recognised refugees (residence permit) |
| **C** | Settlement permit (long-term residents) |
| **S** | Protection status (e.g. Ukrainian displaced persons) |

---

## License

This project is open source. See [LICENSE](LICENSE) for details.

---

*Built during the PowerCoders programme — coding and IT training for refugees and asylum seekers in Switzerland. [powercoders.org](https://www.powercoders.org)*
