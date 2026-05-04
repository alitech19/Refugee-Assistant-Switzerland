import sys
import os
import io
import re
import threading
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent))

# Load env vars before any heavy imports so transformers picks them up
from dotenv import load_dotenv
load_dotenv(Path(__file__).resolve().parent.parent / ".env")

import openai
import streamlit as st
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


init_db()
seed_sources_from_json()
delete_old_conversations()

# Auto-fetch news once per day in the background
def _auto_fetch_news():
    try:
        from datetime import date
        last = get_last_fetch_time()
        if last == date.today().isoformat():
            return  # Already fetched today
        import importlib.util
        ROOT = Path(__file__).resolve().parent.parent
        spec = importlib.util.spec_from_file_location("fetch_news", ROOT / "scripts" / "fetch_news.py")
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        mod.fetch_all()
    except Exception:
        pass

threading.Thread(target=_auto_fetch_news, daemon=True).start()

_TRIVIAL_WORDS = {
    "hello", "hi", "hey", "greetings", "good morning", "good afternoon", "good evening",
    "thanks", "thank you", "thank", "merci", "danke", "grazie", "gracias",
    "ok", "okay", "sure", "yes", "no", "great", "good", "nice", "cool",
    "bye", "goodbye", "see you", "ciao",
    "سلام", "مرحبا", "شكرا", "اوكي",
}


# gTTS language codes (None = not supported by gTTS → falls back to English)
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


def _strip_md(text: str) -> str:
    """Remove markdown so TTS reads as natural speech."""
    text = re.sub(r'\*\*(.+?)\*\*', r'\1', text)
    text = re.sub(r'\*(.+?)\*',     r'\1', text)
    text = re.sub(r'#+\s*',          '',    text)
    text = re.sub(r'\[([^\]]+)\]\([^\)]+\)', r'\1', text)
    text = re.sub(r'`[^`]+`',        '',    text)
    text = re.sub(r'[⚠✓✗─━|]+',    '',    text)
    return text.strip()


def _tts_button(text: str, lang: str, key: str) -> None:
    """Render a 🔊 Listen button. Generates audio server-side via gTTS on click."""
    audio_key = f"tts_audio_{key}"
    lang_code = _GTTS_LANG.get(lang) or "en"

    if st.button("🔊 Listen", key=f"btn_{key}"):
        try:
            from gtts import gTTS
            clean = _strip_md(text)[:2500]
            tts = gTTS(text=clean, lang=lang_code, slow=False)
            buf = io.BytesIO()
            tts.write_to_fp(buf)
            buf.seek(0)
            st.session_state[audio_key] = buf.read()
        except Exception:
            st.session_state[audio_key] = None

    if st.session_state.get(audio_key):
        st.audio(st.session_state[audio_key], format="audio/mp3")


def _is_trivial(text: str) -> bool:
    """Return True for greetings/acknowledgements that need no source retrieval."""
    stripped = text.strip().lower()
    if stripped in _TRIVIAL_WORDS:
        return True
    # Very short messages with no question mark and no question words
    if len(stripped) <= 15 and "?" not in stripped:
        question_words = {"what", "how", "can", "when", "where", "who", "why", "which", "is", "are", "do"}
        if not any(w in stripped.split() for w in question_words):
            return True
    return False

st.set_page_config(
    page_title="AmanCH",
    page_icon="🇨🇭",
    layout="centered",
)

st.markdown("""
<style>
/* ── Page ────────────────────────────────────── */
.stApp {
    background-color: #F7F6F3;
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', system-ui, sans-serif;
    -webkit-font-smoothing: antialiased;
}

/* ── Topbar: red line + white header ─────────── */
[data-testid="stHeader"] {
    background-color: #ffffff !important;
    border-bottom: 3px solid #D52B1E !important;
    box-shadow: 0 2px 10px rgba(0,0,0,0.07) !important;
}

/* ── Sidebar ──────────────────────────────────── */
[data-testid="stSidebar"] {
    background-color: #EEECEA !important;
    border-right: 1px solid rgba(0,0,0,0.07) !important;
}

/* ── Secondary buttons ───────────────────────── */
[data-testid="baseButton-secondary"] {
    background-color: #ffffff !important;
    color: #D52B1E !important;
    border: 1.5px solid #E8E6E3 !important;
    border-radius: 10px !important;
    font-weight: 500 !important;
    font-size: 0.875rem !important;
    letter-spacing: 0.01em !important;
    box-shadow: 0 1px 3px rgba(0,0,0,0.07) !important;
    transition: all 0.15s ease !important;
}
[data-testid="baseButton-secondary"]:hover {
    background-color: #D52B1E !important;
    color: #ffffff !important;
    border-color: #D52B1E !important;
    box-shadow: 0 4px 12px rgba(213,43,30,0.28) !important;
    transform: translateY(-1px) !important;
}
[data-testid="baseButton-secondary"]:focus {
    box-shadow: 0 0 0 3px rgba(213,43,30,0.18) !important;
}

/* ── Primary buttons: selected permit pill ────── */
[data-testid="baseButton-primary"] {
    background: linear-gradient(135deg, #D52B1E 0%, #B8221A 100%) !important;
    color: #ffffff !important;
    border: none !important;
    border-radius: 10px !important;
    font-weight: 700 !important;
    letter-spacing: 0.02em !important;
    box-shadow: 0 3px 10px rgba(213,43,30,0.38) !important;
    transition: all 0.15s ease !important;
}
[data-testid="baseButton-primary"]:hover {
    background: linear-gradient(135deg, #B8221A 0%, #9E1D16 100%) !important;
    box-shadow: 0 5px 14px rgba(213,43,30,0.45) !important;
    transform: translateY(-1px) !important;
}

/* ── Chat messages ───────────────────────────── */
[data-testid="stChatMessage"] {
    background: #ffffff;
    border-radius: 14px;
    padding: 1rem 1.25rem !important;
    margin-bottom: 0.75rem;
    box-shadow: 0 2px 8px rgba(0,0,0,0.05), 0 0 0 1px rgba(0,0,0,0.04);
    transition: box-shadow 0.2s ease;
}
[data-testid="stChatMessage"]:has(img[alt="assistant"]) {
    border-left: 3px solid #D52B1E;
    border-radius: 0 14px 14px 0;
}
[data-testid="stChatMessage"]:has(img[alt="user"]) {
    background: #FEF6F6;
    border-radius: 14px 0 14px 14px;
}

/* ── Expander as card ────────────────────────── */
[data-testid="stExpander"] {
    background: #ffffff !important;
    border: 1px solid rgba(0,0,0,0.07) !important;
    border-radius: 12px !important;
    box-shadow: 0 1px 5px rgba(0,0,0,0.05) !important;
    overflow: hidden;
}

/* ── Info/alert box ──────────────────────────── */
[data-testid="stAlert"] {
    border-radius: 12px !important;
    border-left-width: 4px !important;
    border-left-color: #D52B1E !important;
    background-color: #FEF6F6 !important;
}

/* ── Selectbox ───────────────────────────────── */
[data-testid="stSelectbox"] > div > div {
    background: #ffffff !important;
    border-radius: 10px !important;
    border-color: rgba(0,0,0,0.13) !important;
    box-shadow: 0 1px 3px rgba(0,0,0,0.06) !important;
}

/* ── RTL support ─────────────────────────────── */
.stMarkdown p, .stMarkdown li, .stMarkdown span {
    direction: auto;
    unicode-bidi: plaintext;
    text-align: start;
}
[data-testid="stChatMessageContent"] p,
[data-testid="stChatMessageContent"] li {
    direction: auto;
    unicode-bidi: plaintext;
    text-align: start;
}

/* ── Mobile responsive ───────────────────────── */
@media (max-width: 640px) {
    section[data-testid="stMain"] .stHorizontalBlock {
        flex-wrap: wrap;
    }
    section[data-testid="stMain"] .stHorizontalBlock > div[data-testid="stColumn"] {
        min-width: 48% !important;
        flex: 1 1 48% !important;
    }
    [data-testid="baseButton-secondary"],
    [data-testid="baseButton-primary"] {
        padding: 0.6rem 0.4rem !important;
        font-size: 0.82rem !important;
        min-height: 48px !important;
    }
    .block-container {
        padding-left: 0.75rem !important;
        padding-right: 0.75rem !important;
    }
    audio { width: 100% !important; }
}
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div style="background:#D52B1E;border-radius:12px;padding:0.75rem 1.25rem;
            display:inline-flex;align-items:center;gap:0.9rem;margin-bottom:0.5rem;">
  <div style="background:#ffffff;border-radius:5px;width:38px;height:38px;
              display:flex;align-items:center;justify-content:center;flex-shrink:0;">
    <svg width="22" height="22" viewBox="0 0 22 22">
      <rect x="9" y="1" width="4" height="20" fill="#D52B1E"/>
      <rect x="1" y="9" width="20" height="4" fill="#D52B1E"/>
    </svg>
  </div>
  <div>
    <div style="color:#ffffff;font-size:1.45rem;font-weight:700;
                line-height:1.15;letter-spacing:-0.01em;">AmanCH</div>
    <div style="color:rgba(255,255,255,0.88);font-size:0.78rem;
                font-weight:400;margin-top:2px;letter-spacing:0.01em;">
      Refugee Assistant Switzerland
    </div>
  </div>
</div>
""", unsafe_allow_html=True)

st.caption("⚠️ Guidance only — not legal advice. For important decisions, always consult an official source or legal aid organisation.")

st.markdown(
    '<p style="direction:ltr;text-align:center;color:#aaa;font-size:0.8rem;'
    'letter-spacing:0.04em;margin:0.25rem 0 0.75rem 0;">'
    'Welcome &nbsp;·&nbsp; Willkommen &nbsp;·&nbsp; Bienvenue &nbsp;·&nbsp;'
    ' أهلاً &nbsp;·&nbsp; Ласкаво просимо &nbsp;·&nbsp; Bienvenido'
    '</p>',
    unsafe_allow_html=True,
)

_PERMIT_LABELS = {
    "N": ("N", "Asylum seeker — procedure pending"),
    "F": ("F", "Provisionally admitted"),
    "B": ("B", "Recognised refugee"),
    "C": ("C", "Settlement permit"),
    "S": ("S", "Protection status (e.g. Ukraine)"),
    "?": ("?", "I don't know my permit type"),
}

lbl_col, *pill_cols = st.columns([2.2, 1, 1, 1, 1, 1, 1])
with lbl_col:
    st.markdown(
        '<div style="padding-top:0.45rem;font-size:0.82rem;color:#666;font-weight:500;">My permit:</div>',
        unsafe_allow_html=True,
    )
for col, (code, (label, tooltip)) in zip(pill_cols, _PERMIT_LABELS.items()):
    with col:
        is_selected = st.session_state.get("selected_permit") == code
        if st.button(
            label,
            key=f"pill_{code}",
            use_container_width=True,
            help=tooltip,
            type="primary" if is_selected else "secondary",
        ):
            st.session_state.selected_permit = None if is_selected else code
            st.rerun()

with st.expander("📋 Permit Quick Reference — N · F · B · C · S", expanded=False):
    st.markdown("""
| | **N** — Asylum seeker | **F** — Provisionally admitted | **B** — Recognised refugee | **C** — Settlement | **S** — Protection status |
|---|---|---|---|---|---|
| **Who** | Procedure pending | Temporarily admitted | Refugee status granted | Long-term resident | Displaced persons (e.g. Ukrainians) |
| **Work** | After 3 months + cantonal authorisation | After 3 months + cantonal authorisation | Freely, no authorisation needed | Freely | Cantonal notification only |
| **Duration** | Renewed every 12 months | Renewed annually | 1–2 years, renewable | Long-term (no annual renewal) | Reviewed regularly by government |
| **Family reunification** | Not permitted | After 3 years in CH | Yes (conditions apply) | Yes (conditions apply) | Limited |
| **Travel abroad** | Very restricted | Very restricted — get written permission first | Permitted | Permitted | Can travel to home country and return |
| **Canton of residence** | Assigned by SEM | Cannot change without permission | Any canton | Any canton | Any canton |
""")
    st.caption("⚠️ Rules can vary by canton and individual case. Always verify with your cantonal migration office or OSAR (osar.ch).")

# Session state
if "conversation_id" not in st.session_state:
    st.session_state.conversation_id = create_conversation()

if "messages" not in st.session_state:
    db_messages = get_conversation_messages(st.session_state.conversation_id)
    st.session_state.messages = [
        {"role": m["role"], "content": m["content"], "sources": []}
        for m in db_messages
    ]

if "chat_state" not in st.session_state:
    st.session_state.chat_state = build_initial_state()

if "voice_key" not in st.session_state:
    st.session_state.voice_key = 0

if "selected_permit" not in st.session_state:
    st.session_state.selected_permit = None

CANTONS = [
    "— Select your canton —",
    "Aargau (AG)", "Appenzell Ausserrhoden (AR)", "Appenzell Innerrhoden (AI)",
    "Basel-Landschaft (BL)", "Basel-Stadt (BS)", "Bern (BE)",
    "Fribourg (FR)", "Geneva (GE)", "Glarus (GL)", "Graubünden (GR)",
    "Jura (JU)", "Lucerne (LU)", "Neuchâtel (NE)", "Nidwalden (NW)",
    "Obwalden (OW)", "Schaffhausen (SH)", "Schwyz (SZ)", "Solothurn (SO)",
    "St. Gallen (SG)", "Thurgau (TG)", "Ticino (TI)", "Uri (UR)",
    "Valais (VS)", "Vaud (VD)", "Zug (ZG)", "Zurich (ZH)",
]

# Sidebar — lean and focused
with st.sidebar:
    st.markdown("## Your Canton")
    selected = st.selectbox(
        "Select your canton for local answers:",
        CANTONS,
        index=0,
        key="canton_selector",
    )
    canton = None if selected.startswith("—") else selected
    if canton:
        st.success(f"Showing answers tailored to **{canton}**")

    st.markdown("---")
    with st.expander("📰 Latest News", expanded=False):
        recent = get_recent_news(limit=3)
        if recent:
            for item in recent:
                title_display = item['title'][:70] + ('…' if len(item['title']) > 70 else '')
                st.markdown(f"**[{title_display}]({item['url']})**")
                st.caption(f"{item['source_name']} · {item['published_at']}")
                st.markdown("")
        else:
            st.caption("News is loading in the background — check back shortly.")

    st.markdown("---")
    st.markdown("## Emergency Contacts")
    st.error("🚨 Police: **117** · Ambulance: **144** · Emergency: **112**")
    st.markdown("""
- [OSAR — Free legal aid](https://www.osar.ch)
- [SEM — Migration authority](https://www.sem.admin.ch)
- [Swiss Red Cross](https://www.redcross.ch)
- [ch.ch — Swiss portal](https://www.ch.ch/en/)
""")

    st.markdown("---")
    st.caption("🔒 Conversations stored locally, processed via Groq AI. No data sold or shared.")
    news_count = count_auto_news()
    last_fetch = get_last_fetch_time()
    if news_count:
        st.caption(f"📡 {news_count} articles from SEM & OSAR")
    if last_fetch:
        st.caption(f"🕐 Last checked: {last_fetch}")

    st.markdown("---")
    if st.button("Start new conversation", use_container_width=True):
        st.session_state.conversation_id = create_conversation()
        st.session_state.messages = []
        st.session_state.chat_state = build_initial_state()
        st.session_state.selected_permit = None
        st.rerun()

# Render chat history
for msg_idx, message in enumerate(st.session_state.messages):
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        sources = message.get("sources", [])
        if sources:
            with st.expander("Official sources"):
                for src in sources:
                    st.markdown(f"**{src['title']}**")
                    pub = (src.get("published_at") or "")[:10]
                    if pub:
                        st.caption(f"Published: {pub}")
                    st.markdown(f"[Open source]({src['url']})")
                    st.markdown("---")

    if message["role"] == "assistant":
        # Detect language from the preceding user message for TTS
        tts_lang = "English"
        for i in range(msg_idx - 1, -1, -1):
            if st.session_state.messages[i]["role"] == "user":
                tts_lang = _detect_language(st.session_state.messages[i]["content"])
                break
        _tts_button(message["content"], tts_lang, f"hist_{msg_idx}")

        fb_key = f"fb_{msg_idx}"
        already_rated = st.session_state.get(fb_key)
        if already_rated:
            st.caption(f"{'👍' if already_rated == 1 else '👎'} Feedback recorded — thank you!")
        else:
            col1, col2, col3 = st.columns([1, 1, 8])
            with col1:
                if st.button("👍", key=f"up_{msg_idx}", help="This answer was helpful"):
                    prev_user = next(
                        (st.session_state.messages[i]["content"]
                         for i in range(msg_idx - 1, -1, -1)
                         if st.session_state.messages[i]["role"] == "user"),
                        "",
                    )
                    save_feedback(
                        st.session_state.conversation_id,
                        prev_user,
                        message["content"],
                        1,
                    )
                    st.session_state[fb_key] = 1
                    st.rerun()
            with col2:
                if st.button("👎", key=f"down_{msg_idx}", help="This answer was not helpful"):
                    prev_user = next(
                        (st.session_state.messages[i]["content"]
                         for i in range(msg_idx - 1, -1, -1)
                         if st.session_state.messages[i]["role"] == "user"),
                        "",
                    )
                    save_feedback(
                        st.session_state.conversation_id,
                        prev_user,
                        message["content"],
                        -1,
                    )
                    st.session_state[fb_key] = -1
                    st.rerun()

# Welcome screen — shown only when conversation is empty
if not st.session_state.messages:
    st.info(
        "**What I can help with:** Swiss asylum procedure · Permits (N, F, B, C, S) · "
        "Work rights · Language courses · Healthcare · Family reunification · Appeals · Housing\n\n"
        "**Languages:** I reply in your language — Arabic, Tigrinya, Somali, Dari, Ukrainian, "
        "Turkish, German, French, Italian, English, and more. Just write or speak naturally.\n\n"
        "**Important:** I give guidance only — not legal advice. For appeals, rejections, or "
        "urgent legal matters, always contact [OSAR](https://www.osar.ch) (free legal aid) or "
        "[SEM](https://www.sem.admin.ch) directly."
    )
    st.markdown("### What would you like to know today?")
    st.caption("Tap a topic or type your question below — I answer in your language.")
    st.markdown("")

    TOPICS = [
        ("🔖", "Permits",        "What types of permits exist in Switzerland and what does each one allow?"),
        ("📋", "Asylum",         "What are the steps of the Swiss asylum procedure?"),
        ("💼", "Work rights",    "Can I work in Switzerland and what do I need to do?"),
        ("🏥", "Healthcare",     "How do I access healthcare and get health insurance in Switzerland?"),
        ("🎓", "Integration",    "What language courses and integration programs are available for refugees?"),
        ("👨‍👩‍👧", "Family",         "How can I bring my family to Switzerland?"),
        ("⚖️", "Appeals",        "How do I appeal a rejected asylum decision?"),
        ("🏠", "Housing",        "What housing do asylum seekers receive in Switzerland?"),
    ]

    cols = st.columns(4)
    for i, (emoji, label, question) in enumerate(TOPICS):
        with cols[i % 4]:
            if st.button(f"{emoji} {label}", use_container_width=True, key=f"topic_{label}"):
                st.session_state.quick_prompt = question
                st.rerun()

    st.markdown("---")
    st.markdown("**Common questions:**")

    COMMON_Q = [
        "What do I do when I first arrive in Switzerland as a refugee?",
        "What is Permit F and can I work with it?",
        "How do I appeal a rejected asylum decision?",
        "How can I bring my family to Switzerland?",
        "What is Permit S for Ukrainians?",
        "What are the latest asylum updates in Switzerland?",
    ]

    cq_cols = st.columns(2)
    for i, q in enumerate(COMMON_Q):
        with cq_cols[i % 2]:
            if st.button(q, use_container_width=True, key=f"cq_{i}"):
                st.session_state.quick_prompt = q
                st.rerun()

    st.markdown("")

# Voice input — always visible, works in any language
audio_input = st.audio_input(
    "🎤 Speak your question in any language",
    key=f"voice_{st.session_state.voice_key}",
)
if audio_input:
    with st.spinner("Transcribing your question..."):
        try:
            transcribed = transcribe_audio(audio_input)
            if transcribed:
                st.session_state.voice_key += 1
                st.session_state.quick_prompt = transcribed
                st.rerun()
        except Exception as e:
            st.warning(f"Voice input could not be processed: {e}")

# Chat input — always render so the text box is always visible
typed_input = st.chat_input(
    "Ask anything — asylum, permits, work, integration, healthcare… (any language)"
)

# Quick prompt from topic/question buttons takes priority over typed input
user_prompt = st.session_state.get("quick_prompt") or typed_input
if st.session_state.get("quick_prompt"):
    st.session_state.quick_prompt = None

if user_prompt:
    user_message = {"role": "user", "content": user_prompt, "sources": []}
    st.session_state.messages.append(user_message)
    save_message(st.session_state.conversation_id, "user", user_prompt)

    with st.chat_message("user"):
        st.markdown(user_prompt)

    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            resolved = resolve_user_query(user_prompt, st.session_state.chat_state)
            st.session_state.chat_state = update_state(st.session_state.chat_state, resolved)

            sources = (
                []
                if _is_trivial(user_prompt)
                else search_sources(resolved["standalone_query"], limit=2, canton=canton)
            )

            try:
                assistant_text = process_chat_turn(
                    st.session_state.messages,
                    sources,
                    canton=canton,
                    permit=st.session_state.get("selected_permit"),
                )
            except openai.RateLimitError:
                assistant_text = (
                    "⚠️ The AI service is temporarily at capacity. Please wait a minute and try again.\n\n"
                    "For urgent help while you wait:\n"
                    "- [OSAR — Free legal aid](https://www.osar.ch)\n"
                    "- [SEM — Migration authority](https://www.sem.admin.ch)\n"
                    "- [ch.ch — Swiss portal](https://www.ch.ch/en/)"
                )
                sources = []
            except (openai.APIConnectionError, openai.APIStatusError):
                assistant_text = (
                    "⚠️ Could not reach the AI service right now. Please check your internet connection and try again.\n\n"
                    "For urgent help: [OSAR](https://www.osar.ch) · [SEM](https://www.sem.admin.ch)"
                )
                sources = []
            except ValueError as e:
                assistant_text = (
                    f"⚠️ Configuration error: {e}\n\n"
                    "Please add your `GROQ_API_KEY` to the `.env` file and restart the app."
                )
                sources = []

        assistant_message = {
            "role": "assistant",
            "content": assistant_text,
            "sources": sources,
        }
        st.session_state.messages.append(assistant_message)
        save_message(st.session_state.conversation_id, "assistant", assistant_text)

        st.markdown(assistant_text)
        _tts_button(assistant_text, _detect_language(user_prompt), f"new_{st.session_state.conversation_id}")
        if sources:
            with st.expander("Official sources"):
                for src in sources:
                    st.markdown(f"**{src['title']}**")
                    pub = (src.get("published_at") or "")[:10]
                    if pub:
                        st.caption(f"Published: {pub}")
                    st.markdown(f"[Open source]({src['url']})")
                    st.markdown("---")
