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


def parse_chat_response(raw_text: str) -> dict:
    data = {
        "answer": "",
        "safety_note": "",
    }

    current_key = None

    for line in raw_text.splitlines():
        line = line.strip()
        if not line:
            continue

        lower = line.lower()

        if lower.startswith("answer:"):
            data["answer"] = line.split(":", 1)[1].strip()
            current_key = "answer"
        elif lower.startswith("safety note:"):
            data["safety_note"] = line.split(":", 1)[1].strip()
            current_key = "safety_note"
        elif current_key:
            data[current_key] += " " + line

    return data


def render_assistant_response(message: dict) -> None:
    parsed = parse_chat_response(message["content"])

    if parsed["answer"]:
        st.write(parsed["answer"])

    if parsed["safety_note"]:
        st.caption(parsed["safety_note"])

    sources = message.get("sources", [])
    if sources:
        with st.expander("Sources"):
            for src in sources:
                st.markdown(f"**{src['title']}**")
                st.markdown(f"[Open source]({src['url']})")
                st.markdown("---")


# Initialize database and source seeding
init_db()
seed_sources_from_json()

st.set_page_config(page_title="Refugee Assistant Switzerland", page_icon="💬")
st.title("Refugee Assistant Switzerland")
st.caption("Guidance only — not legal advice")
st.caption(
    "Privacy-first: do not share unnecessary personal details. If location is relevant, canton is enough."
)

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
    st.subheader("Chat")

    if st.button("Start new conversation", use_container_width=True):
        st.session_state.conversation_id = create_conversation()
        st.session_state.messages = []
        st.session_state.chat_state = build_initial_state()
        st.rerun()

    st.markdown("### What this assistant helps with")
    st.markdown("- Official form questions")
    st.markdown("- Simple administrative guidance")
    st.markdown("- Canton-level location context only")

    # Optional debug section
    with st.expander("Debug state"):
        st.json(st.session_state.chat_state)

# Render chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        if message["role"] == "user":
            st.write(message["content"])
        else:
            render_assistant_response(message)

# Chat input
user_prompt = st.chat_input("Ask about a form question or simple administrative issue")

if user_prompt:
    user_message = {
        "role": "user",
        "content": user_prompt,
        "sources": [],
    }
    st.session_state.messages.append(user_message)
    save_message(st.session_state.conversation_id, "user", user_prompt)

    with st.chat_message("user"):
        st.write(user_prompt)

    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            # STEP 3: resolve using conversation state
            resolved = resolve_user_query(user_prompt, st.session_state.chat_state)

            # update state after resolution
            st.session_state.chat_state = update_state(
                st.session_state.chat_state,
                resolved
            )

            if resolved["needs_clarification"]:
                assistant_text = (
                    f"Answer: {resolved['clarification_question']}\n\n"
                    "Safety note: I want to avoid guessing and give you more accurate guidance."
                )
                sources = []
            else:
                # STEP 4: retrieve using standalone_query, not raw input
                sources = search_sources(resolved["standalone_query"], limit=2)

                assistant_text = process_chat_turn(
                    st.session_state.messages,
                    resolved,
                    sources,
                )

            assistant_message = {
                "role": "assistant",
                "content": assistant_text,
                "sources": sources,
            }

            st.session_state.messages.append(assistant_message)
            save_message(st.session_state.conversation_id, "assistant", assistant_text)

            render_assistant_response(assistant_message)