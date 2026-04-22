import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent))

import streamlit as st
from src.database import (
    init_db,
    seed_sources_from_json,
    create_conversation,
    save_message,
    get_conversation_messages,
    search_sources,
)
from src.llm_service import process_chat_turn
from src.resolver import resolve_user_query
from src.state_tracker import build_initial_state, update_state


init_db()
seed_sources_from_json()

st.set_page_config(
    page_title="Refugee Assistant Switzerland",
    page_icon="🇨🇭",
    layout="centered",
)

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

# Sidebar
with st.sidebar:
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
- ❓ **General questions** — life and administration in Switzerland
""")

    st.markdown("---")
    st.markdown("**Useful contacts**")
    st.markdown("- [SEM (State Secretariat for Migration)](https://www.sem.admin.ch/en)")
    st.markdown("- [ch.ch — Official Swiss portal](https://www.ch.ch/en/)")
    st.markdown("- [OSAR — Swiss Refugee Council](https://www.osar.ch/en/)")

    st.markdown("---")
    if st.button("Start new conversation", use_container_width=True):
        st.session_state.conversation_id = create_conversation()
        st.session_state.messages = []
        st.session_state.chat_state = build_initial_state()
        st.rerun()

# Render chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        sources = message.get("sources", [])
        if sources:
            with st.expander("Official sources"):
                for src in sources:
                    st.markdown(f"**{src['title']}**")
                    st.markdown(f"[Open source]({src['url']})")
                    st.markdown("---")

# Chat input
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

            sources = search_sources(resolved["standalone_query"], limit=3)

            try:
                assistant_text = process_chat_turn(st.session_state.messages, sources)
            except ValueError as e:
                assistant_text = (
                    f"⚠️ Configuration error: {e}\n\n"
                    "Please add your `ANTHROPIC_API_KEY` to the `.env` file and restart the app."
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
                    st.markdown(f"[Open source]({src['url']})")
                    st.markdown("---")
