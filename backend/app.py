import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent))

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
)
from src.llm_service import process_chat_turn
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

# Sidebar
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
    st.markdown("## Quick Questions")
    st.caption("Tap to get an instant answer:")
    QUICK_QUESTIONS = [
        "What is Permit F and can I work with it?",
        "How do I appeal a rejected asylum decision?",
        "How can I bring my family to Switzerland?",
        "What language courses are available for refugees?",
        "What are my rights as an asylum seeker with Permit N?",
        "What is Permit S for Ukrainians?",
        "What housing do asylum seekers receive?",
        "How do I get health insurance as a refugee?",
    ]
    for q in QUICK_QUESTIONS:
        if st.button(q, use_container_width=True, key=f"qq_{q[:30]}"):
            st.session_state.quick_prompt = q
            st.rerun()

    st.markdown("---")
    st.markdown("## What I can help with")
    st.markdown("""
- 🔖 **Permits** — N, F, B, C, S: what they mean and what they allow
- 📋 **Asylum procedure** — steps, timelines, hearings, decisions
- 💼 **Work rights** — by permit type, cantonal authorisation
- 🎓 **Integration** — language courses, FIDE test, social integration
- 🏥 **Healthcare** — access during and after the asylum procedure
- 🏫 **Education** — rights for children
- 👨‍👩‍👧 **Family reunification** — rules by permit type
- ⚖️ **Appeals** — what to do after a negative decision
- 🏛️ **Naturalization** — path to Swiss citizenship
- 🏠 **Housing** — accommodation rules during the procedure
""")

    st.markdown("---")
    st.markdown("## Emergency Contacts")
    st.error("🚨 Police: **117** · Ambulance: **144** · Emergency: **112**")
    st.markdown("""
- [OSAR — Free legal aid for asylum seekers](https://www.osar.ch)
- [SEM — Official migration authority](https://www.sem.admin.ch)
- [Swiss Red Cross](https://www.redcross.ch)
- [ch.ch — Official Swiss portal](https://www.ch.ch/en/)
""")

    st.markdown("---")
    st.caption("🔒 Your conversation is stored locally and processed via Groq AI. Groq does not use your data for training. No data is sold or shared with other parties.")
    st.markdown("---")
    news_count = count_auto_news()
    last_fetch = get_last_fetch_time()
    if news_count:
        st.caption(f"📡 {news_count} official news articles loaded from SEM & OSAR")
    if last_fetch:
        st.caption(f"🕐 News last updated: {last_fetch}")

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

# Chat input — check for quick question button first
user_prompt = st.session_state.get("quick_prompt")
if user_prompt:
    st.session_state.quick_prompt = None
else:
    user_prompt = st.chat_input(
        "Ask anything — asylum, permits, work, integration, healthcare… (any language)"
    )

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
