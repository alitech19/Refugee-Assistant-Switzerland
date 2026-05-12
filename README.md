# AmanCH — Refugee Assistant Switzerland

[![Live App](https://img.shields.io/badge/live%20app-Vercel-brightgreen?logo=vercel)](https://refugee-assistant-switzerland.vercel.app)
[![API](https://img.shields.io/badge/API-Render-blue?logo=render)](https://amanch.onrender.com/health)
[![License](https://img.shields.io/badge/license-MIT-yellow)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.11-blue?logo=python&logoColor=white)](https://www.python.org/)
[![React](https://img.shields.io/badge/react-18-61DAFB?logo=react&logoColor=black)](https://react.dev/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-009688?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![Powered by Groq](https://img.shields.io/badge/LLM-Groq%20%2F%20LLaMA%203.3-orange)](https://console.groq.com)

> **Free, multilingual AI assistant helping refugees and asylum seekers understand Switzerland's asylum system — in their own language.**
> *Aman = Peace · CH = Switzerland*

AmanCH answers questions about permits, work rights, asylum procedures, healthcare, family reunification, and integration — grounded in 70+ verified Swiss official sources (SEM, OSAR, cantonal offices). It never guesses, never invents URLs, and always responds in the user's own language.

---

## Live App

| Service | URL |
|---|---|
| **Web app (React)** | [refugee-assistant-switzerland.vercel.app](https://refugee-assistant-switzerland.vercel.app) |
| **API (FastAPI)** | [amanch.onrender.com](https://amanch.onrender.com) |
| **API health check** | [amanch.onrender.com/health](https://amanch.onrender.com/health) |

> **Note:** The API is hosted on Render's free tier. After 15 minutes of inactivity it sleeps — the first request after a sleep takes ~30 seconds to respond. Subsequent requests are fast.

---

## Features

- **Multilingual interface** — Switch the entire UI (menus, buttons, labels) to English, Arabic, Ukrainian, or Turkish via the language selector in the header. Arabic switches the layout to right-to-left (RTL) automatically.
- **15+ conversation languages** — Arabic, Tigrinya, Somali, Dari, Ukrainian, Turkish, German, French, Italian, English, and more. Language is detected automatically from each message; the assistant always replies in the same language as the user.
- **Permit-aware answers** — Select your permit type (N · F · B · C · S · ?) and every answer is tailored to that permit's specific rights and restrictions.
- **Canton-specific information** — Select your canton to get answers about local migration offices, language courses, and integration programmes.
- **RAG pipeline** — Every answer is grounded in retrieved Swiss official sources. The LLM is forbidden from inventing URLs or fabricating legal facts.
- **Clickable source links** — Sources cited in every answer are shown as clickable hyperlinks pointing to official Swiss websites.
- **Voice input** — Ask questions by speaking in any language (Whisper large-v3 via Groq).
- **Text-to-speech** — Responses can be read aloud in the user's language (gTTS).
- **Live news** — Automatically fetches the latest updates from SEM and OSAR RSS feeds daily. Total article count shown in the sidebar.
- **30-day appeal reminder** — Proactively warns about the critical appeal deadline after a rejected decision.
- **Conversation history** — Full chat stored in SQLite; context preserved across turns.
- **Feedback system** — Thumbs up / thumbs down on every reply, stored for quality improvement.
- **No account needed** — Open the app, ask a question. That is all.

---

## Project Structure

```
AmanCH/
│
├── frontend-react/                  # React + Vite web app (deployed on Vercel)
│   ├── src/
│   │   ├── App.jsx                  # Main app: state management, routing logic
│   │   ├── App.css                  # Full design system (CSS variables, layout, RTL overrides)
│   │   ├── api.js                   # Axios API client
│   │   ├── i18n.js                  # UI translations (EN/AR/UK/TR) + LANGUAGES export
│   │   └── components/
│   │       ├── Header.jsx           # Top bar with Swiss cross logo + language selector
│   │       ├── Sidebar.jsx          # Canton picker, latest news, emergency contacts
│   │       ├── PermitBar.jsx        # Permit type selector (N/F/B/C/S/?)
│   │       ├── WelcomeScreen.jsx    # Topic grid + quick question buttons
│   │       ├── MessageList.jsx      # Chat bubbles, TTS, feedback, sources
│   │       └── ChatInput.jsx        # Text input + voice recording
│   ├── .env                         # Production API URL (VITE_API_URL)
│   └── vite.config.js
│
├── backend/
│   ├── api.py                       # FastAPI app — all REST endpoints
│   ├── database.py                  # SQLite layer: conversations, sources, news, feedback
│   ├── embeddings.py                # Sentence-transformer model for semantic search
│   ├── llm_service.py               # Groq API calls, language detection, URL sanitisation
│   ├── prompts.py                   # System prompt for the AmanCH assistant
│   ├── resolver.py                  # Query parsing: permit/topic detection, search builder
│   └── state_tracker.py            # Conversation state (permit across turns)
│
├── data/
│   ├── app.db                       # SQLite database (auto-created on first run)
│   └── official_sources.json        # 70+ curated Swiss official sources
│
├── scripts/
│   └── fetch_news.py                # Fetches SEM + OSAR RSS feeds → auto_news table
│
├── tests/
│   └── test_search.py               # RAG search quality tests
├── tools/
│   ├── generate_pitch_deck.py       # Generates AmanCH_PitchDeck.pptx
│   └── generate_project_brief.py    # Generates AmanCH_ProjectBrief.docx
│
├── run_api.py                       # FastAPI entry point (reads $PORT env var)
├── render.yaml                      # Render deployment config
├── Dockerfile                       # FastAPI Docker image
├── docker-compose.yml               # Runs api (port 8000) + frontend (port 80)
└── requirements.txt
```

---

## Tech Stack

| Layer | Technology | Why |
|---|---|---|
| **Frontend** | React 18 + Vite | Component-based, fast build, ready for React Native mobile app |
| **Styling** | CSS variables (design tokens) | Consistent theme, easy to extend to mobile |
| **API client** | Axios | Clean async calls, easy error handling |
| **Markdown** | react-markdown + remark-gfm | Renders bot replies with clickable links |
| **Backend** | FastAPI + Uvicorn | Fast async Python REST API, auto-generated docs at `/docs` |
| **LLM** | LLaMA 3.3-70b via Groq API | Fast inference, strong multilingual capability |
| **Speech-to-text** | Whisper large-v3 via Groq | 99-language transcription, same API key |
| **Text-to-speech** | gTTS (Google TTS) | Free, works for all major languages |
| **Semantic search** | `paraphrase-multilingual-MiniLM-L12-v2` | Compact multilingual embedding model, runs locally |
| **Database** | SQLite | Zero-config, stores knowledge base + conversations + news |
| **News feed** | feedparser + SEM/OSAR RSS | Keeps answers current without manual updates |
| **Hosting — frontend** | Vercel | Auto-deploys from `main` branch, global CDN |
| **Hosting — backend** | Render | Python runtime, free tier, auto-deploy on push |

---

## API Endpoints

The FastAPI backend exposes these endpoints (interactive docs at `/docs`):

| Method | Path | Description |
|---|---|---|
| `GET` | `/health` | Health check |
| `POST` | `/conversation` | Start a new conversation → returns `conversation_id` |
| `GET` | `/conversation/{id}/messages` | Retrieve message history |
| `POST` | `/chat` | Send a message → returns AI reply + sources |
| `GET` | `/news` | Latest news articles + total indexed count |
| `POST` | `/feedback` | Submit thumbs up/down rating |
| `POST` | `/transcribe` | Upload audio → returns transcribed text |
| `POST` | `/tts` | Convert text to speech → returns base64 MP3 |

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
  (hybrid keyword + semantic search — 70+ Swiss official sources + live news)
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
  Answer in user's language + clickable source links
```

The assistant is explicitly forbidden from inventing URLs, extrapolating beyond sources, or giving personal legal advice. If it does not know, it says so and directs the user to SEM or OSAR.

---

## Local Development

### Prerequisites

- Node.js 18+ and npm
- Python 3.10+
- A free [Groq API key](https://console.groq.com)

### 1. Clone the repository

```bash
git clone https://github.com/alitech19/Refugee-Assistant-Switzerland.git
cd Refugee-Assistant-Switzerland
```

### 2. Backend setup

```bash
# Create virtual environment
python -m venv .venv

# Activate — Windows
.venv\Scripts\activate

# Activate — macOS / Linux
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Create .env file with your Groq API key
echo GROQ_API_KEY=your_key_here > .env

# Run the FastAPI server
python run_api.py
# → http://localhost:8000
# → Interactive docs: http://localhost:8000/docs
```

### 3. Frontend setup

```bash
cd frontend-react

# Install dependencies
npm install

# Create local env file pointing to local backend
echo VITE_API_URL=http://localhost:8000 > .env.local

# Start dev server
npm run dev
# → http://localhost:5173
```

> `.env.local` is gitignored and overrides `.env` in local development. The committed `.env` file points to the production Render API URL.

### 4. Run with Docker (alternative)

```bash
# Create your .env file first
echo GROQ_API_KEY=your_key_here > .env

# Build and run
docker compose up
```

Open [http://localhost:80](http://localhost:80) for the React app and [http://localhost:8000/docs](http://localhost:8000/docs) for the API.

---

## Deployment

### Backend — Render

The backend auto-deploys from `main` via `render.yaml`. To set up from scratch:

1. Connect the GitHub repo to Render
2. Render detects `render.yaml` automatically
3. Add `GROQ_API_KEY` as an environment variable in the Render dashboard
4. First deploy takes ~3–5 minutes (embedding model download)

### Frontend — Vercel

The React app auto-deploys from `main` via Vercel. To set up from scratch:

1. Import the GitHub repo in Vercel
2. Set **Framework Preset** to `Vite`
3. Set **Root Directory** to `frontend-react`
4. Add environment variable: `VITE_API_URL = https://amanch.onrender.com`
5. Deploy — Vercel rebuilds automatically on every push to `main`

---

## Environment Variables

| Variable | Where | Required | Description |
|---|---|---|---|
| `GROQ_API_KEY` | Backend `.env` / Render dashboard | Yes | Groq API key for LLM + Whisper |
| `VITE_API_URL` | `frontend-react/.env` / Vercel dashboard | Yes | URL of the FastAPI backend |

---

## Knowledge Base

`data/official_sources.json` contains 70+ manually curated entries covering:

- Swiss Federal sources: SEM, OSAR, ch.ch, FIDE, UNHCR
- All 26 cantonal migration offices with direct URLs
- Permit-specific pages for N, F, B, C, S permit types
- Integration programmes and language courses for major cantons
- Work authorisation, family reunification, healthcare, education, and appeals

Sources are loaded into SQLite on startup. Embeddings are computed lazily and cached — only recomputed when source content changes.

---

## Supported Languages

Arabic · Tigrinya · Amharic · Somali · Dari · Farsi · Pashto · Kurdish · Ukrainian · Turkish · German · French · Italian · Swahili · English · and more

Language is detected automatically from the user's message. No selection required.

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

## Important Disclaimer

AmanCH provides **guidance only — not legal advice**.

For important decisions (asylum appeals, rejected applications, family reunification, work authorisation), always verify with:

- **SEM** — [sem.admin.ch](https://www.sem.admin.ch) — Federal migration authority
- **OSAR** — [osar.ch](https://www.osar.ch) — Free legal aid for asylum seekers
- **Your cantonal migration office** — For canton-specific rules and procedures

The 30-day appeal window after a rejected asylum decision is critical. Missing it forfeits the right to appeal.

---

## Key Architecture Decisions

**Why React + FastAPI?**
The React + FastAPI architecture separates concerns cleanly, enables a proper REST API consumed by any client, and is the natural foundation for a future React Native iOS/Android app.

**Why keyword + semantic hybrid search?**
Swiss asylum law is structured and domain-specific. A hybrid approach (keyword scoring for exact permit/canton matches + semantic embeddings for cross-language queries) gives better precision than either alone, while running entirely on CPU with a compact 120 MB model.

**Why Groq + LLaMA 3.3-70b?**
Fast inference, strong multilingual capability, and an OpenAI-compatible API that makes swapping models trivial. The free tier covers normal usage.

**Why SQLite?**
Zero configuration, no server to manage, and a single file holding the knowledge base, conversation history, feedback, news, and settings. Straightforward to back up or move.

---

## License

This project is open source under the MIT License. See [LICENSE](LICENSE) for details.

---

*Built during the PowerCoders programme — coding and IT training for refugees and asylum seekers in Switzerland. [powercoders.org](https://www.powercoders.org)*
