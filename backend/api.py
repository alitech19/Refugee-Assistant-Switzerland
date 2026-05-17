import sys
import io
import re
import base64
import threading
from pathlib import Path
from typing import Optional

sys.path.append(str(Path(__file__).resolve().parent.parent))

from dotenv import load_dotenv
load_dotenv(Path(__file__).resolve().parent.parent / ".env")

import openai
from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from backend.database import (
    init_db,
    seed_sources_from_json,
    delete_old_conversations,
    create_conversation,
    save_message,
    get_conversation_messages,
    search_sources,
    save_feedback,
    count_auto_news,
    get_last_fetch_time,
    get_recent_news,
)
from backend.llm_service import process_chat_turn, transcribe_audio, _detect_language
from backend.resolver import resolve_user_query
from backend.state_tracker import build_initial_state, update_state

# ── App ───────────────────────────────────────────────────
app = FastAPI(title="AmanCH API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:5173",
        "https://refugee-assistant-switzerland.vercel.app",
        "https://amanch.onrender.com",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Startup ───────────────────────────────────────────────
@app.on_event("startup")
def startup():
    init_db()
    seed_sources_from_json()
    delete_old_conversations()
    threading.Thread(target=_auto_fetch_news, daemon=True).start()


def _auto_fetch_news():
    try:
        from datetime import date
        last = get_last_fetch_time()
        if last == date.today().isoformat():
            return
        import importlib.util
        ROOT = Path(__file__).resolve().parent.parent
        spec = importlib.util.spec_from_file_location(
            "fetch_news", ROOT / "scripts" / "fetch_news.py"
        )
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        mod.fetch_all()
    except Exception:
        pass


# ── Helpers ───────────────────────────────────────────────
_TRIVIAL_WORDS = {
    "hello", "hi", "hey", "greetings", "good morning", "good afternoon",
    "good evening", "thanks", "thank you", "thank", "merci", "danke",
    "grazie", "gracias", "ok", "okay", "sure", "yes", "no", "great",
    "good", "nice", "cool", "bye", "goodbye", "see you", "ciao",
    "سلام", "مرحبا", "شكرا", "اوكي",
}

_GTTS_LANG: dict[str, str | None] = {
    "Arabic":              "ar",
    "German":              "de",
    "French":              "fr",
    "Italian":             "it",
    "Turkish":             "tr",
    "Ukrainian":           "uk",
    "English":             "en",
    "Amharic or Tigrinya": "am",
    "Dari or Farsi":       "fa",
    "Swahili":             "sw",
    "Somali":              None,
    "Pashto":              None,
    "Kurdish":             None,
}


def _is_trivial(text: str) -> bool:
    stripped = text.strip().lower()
    if stripped in _TRIVIAL_WORDS:
        return True
    if len(stripped) <= 15 and "?" not in stripped:
        question_words = {
            "what", "how", "can", "when", "where", "who", "why", "which", "is", "are", "do"
        }
        if not any(w in stripped.split() for w in question_words):
            return True
    return False


def _strip_md(text: str) -> str:
    text = re.sub(r'\*\*(.+?)\*\*', r'\1', text)
    text = re.sub(r'\*(.+?)\*',     r'\1', text)
    text = re.sub(r'#+\s*',          '',    text)
    text = re.sub(r'\[([^\]]+)\]\([^\)]+\)', r'\1', text)
    text = re.sub(r'`[^`]+`',        '',    text)
    text = re.sub(r'[⚠✓✗─━|]+',    '',    text)
    return text.strip()


# ── Request / Response models ─────────────────────────────
class ChatRequest(BaseModel):
    message: str
    conversation_id: int
    permit: Optional[str] = None
    canton: Optional[str] = None


class FeedbackRequest(BaseModel):
    conversation_id: int
    user_message: str
    assistant_message: str
    rating: int


class TTSRequest(BaseModel):
    text: str
    language: str = "English"


# ── Endpoints ─────────────────────────────────────────────

@app.get("/health")
def health():
    return {"status": "ok", "service": "AmanCH API"}


@app.post("/conversation")
def new_conversation():
    conversation_id = create_conversation()
    return {"conversation_id": conversation_id}


@app.get("/conversation/{conversation_id}/messages")
def get_messages(conversation_id: int):
    messages = get_conversation_messages(conversation_id)
    return {"messages": messages}


@app.post("/chat")
def chat(req: ChatRequest):
    # Build conversation state from current permit
    state = build_initial_state()
    if req.permit:
        state["current_permit"] = f"Permit {req.permit}"

    # Load full message history from DB for LLM context
    db_messages = get_conversation_messages(req.conversation_id)
    history = [{"role": m["role"], "content": m["content"]} for m in db_messages]

    # Save the user message
    save_message(req.conversation_id, "user", req.message)
    history.append({"role": "user", "content": req.message})

    # Resolve query — detect permit/topics, build search query
    resolved = resolve_user_query(req.message, state)
    state = update_state(state, resolved)

    # Source retrieval (skip for trivial messages)
    sources = (
        []
        if _is_trivial(req.message)
        else search_sources(resolved["standalone_query"], limit=8, canton=req.canton)
    )

    # LLM call
    try:
        assistant_text = process_chat_turn(
            history,
            sources,
            canton=req.canton,
            permit=req.permit,
        )
    except openai.RateLimitError:
        assistant_text = (
            "⚠️ The AI service is temporarily at capacity. Please wait a minute and try again.\n\n"
            "For urgent help: [OSAR](https://www.osar.ch) · [SEM](https://www.sem.admin.ch)"
        )
        sources = []
    except openai.AuthenticationError:
        assistant_text = (
            "⚠️ The API key is invalid or expired. Please update the GROQ_API_KEY and restart.\n\n"
            "For urgent help: [OSAR](https://www.osar.ch) · [SEM](https://www.sem.admin.ch)"
        )
        sources = []
    except openai.APIConnectionError:
        assistant_text = (
            "⚠️ Could not reach the AI service. Please check your internet connection.\n\n"
            "For urgent help: [OSAR](https://www.osar.ch) · [SEM](https://www.sem.admin.ch)"
        )
        sources = []
    except openai.APIStatusError as e:
        assistant_text = (
            f"⚠️ The AI service returned an error (status {e.status_code}). Please try again.\n\n"
            "For urgent help: [OSAR](https://www.osar.ch) · [SEM](https://www.sem.admin.ch)"
        )
        sources = []
    except ValueError as e:
        raise HTTPException(status_code=500, detail=str(e))

    # Save the assistant reply
    save_message(req.conversation_id, "assistant", assistant_text)

    # Detect language for TTS hint
    detected_lang = _detect_language(req.message)

    return {
        "reply": assistant_text,
        "sources": [
            {
                "title": s["title"],
                "url": s["url"],
                "topic": s.get("topic", ""),
                "published_at": (s.get("published_at") or "")[:10],
            }
            for s in sources
        ],
        "detected_language": detected_lang,
    }


@app.get("/news")
def news(limit: int = 3):
    items = get_recent_news(limit=limit)
    count = count_auto_news()
    last_fetch = get_last_fetch_time()
    return {
        "news": items,
        "total_articles": count,
        "last_fetch": last_fetch,
    }


@app.post("/feedback")
def feedback(req: FeedbackRequest):
    if req.rating not in (1, -1):
        raise HTTPException(status_code=400, detail="Rating must be 1 or -1")
    save_feedback(
        req.conversation_id,
        req.user_message,
        req.assistant_message,
        req.rating,
    )
    return {"ok": True}


@app.post("/transcribe")
async def transcribe(file: UploadFile = File(...)):
    try:
        audio_bytes = await file.read()
        audio_file = io.BytesIO(audio_bytes)
        audio_file.name = file.filename or "audio.wav"
        text = transcribe_audio(audio_file)
        if not text:
            raise HTTPException(status_code=422, detail="Could not transcribe audio")
        return {"text": text}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/tts")
def tts(req: TTSRequest):
    try:
        from gtts import gTTS
        lang_code = _GTTS_LANG.get(req.language) or "en"
        clean = _strip_md(req.text)[:2500]
        tts_obj = gTTS(text=clean, lang=lang_code, slow=False)
        buf = io.BytesIO()
        tts_obj.write_to_fp(buf)
        buf.seek(0)
        audio_b64 = base64.b64encode(buf.read()).decode("utf-8")
        return {"audio_base64": audio_b64, "format": "mp3"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
