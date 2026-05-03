import sys
import os
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent))

# Load env vars before any heavy imports so transformers picks them up
from dotenv import load_dotenv
load_dotenv(Path(__file__).resolve().parent.parent / ".env")

import streamlit as st
from src.database import (
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
from src.llm_service import process_chat_turn, transcribe_audio
from src.resolver import resolve_user_query
from src.state_tracker import build_initial_state, update_state


init_db()
seed_sources_from_json()
delete_old_conversations()

st.set_page_config(
    page_title="Refugee Assistant Switzerland",
    page_icon="🇨🇭",
    layout="centered",
)

# Auto-detect text direction so Arabic/Hebrew/Urdu render RTL, English LTR
st.markdown("""
<style>
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
</style>
""", unsafe_allow_html=True)

st.title("🇨🇭 Refugee Assistant Switzerland")
st.caption(
    "Ask questions in **any language** — I will answer in your language. "
    "This assistant covers all of Switzerland."
)
st.caption("⚠️ Guidance only — not legal advice. For important decisions, always consult an official source or legal aid organisation.")

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
            st.caption("No news loaded yet. Run the fetch script.")

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
        st.caption(f"🕐 Last updated: {last_fetch}")

    st.markdown("---")
    if st.button("Start new conversation", use_container_width=True):
        st.session_state.conversation_id = create_conversation()
        st.session_state.messages = []
        st.session_state.chat_state = build_initial_state()
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

            sources = search_sources(resolved["standalone_query"], limit=3, canton=canton)

            try:
                assistant_text = process_chat_turn(st.session_state.messages, sources, canton=canton)
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
        if sources:
            with st.expander("Official sources"):
                for src in sources:
                    st.markdown(f"**{src['title']}**")
                    pub = (src.get("published_at") or "")[:10]
                    if pub:
                        st.caption(f"Published: {pub}")
                    st.markdown(f"[Open source]({src['url']})")
                    st.markdown("---")
