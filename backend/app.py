import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent))

import streamlit as st
from src.llm_service import process_user_input
from src.database import init_db, save_interaction, get_recent_interactions

init_db()


def parse_response(raw_text: str) -> dict:
    data = {
        "type": "",
        "simple_explanation": "",
        "what_is_expected": "",
        "example_answer": "",
        "safety_note": "",
    }

    current_key = None

    for line in raw_text.splitlines():
        line = line.strip()
        if not line:
            continue

        lower = line.lower()

        if lower.startswith("type:"):
            data["type"] = line.split(":", 1)[1].strip()
            current_key = "type"
        elif lower.startswith("simple explanation:"):
            data["simple_explanation"] = line.split(":", 1)[1].strip()
            current_key = "simple_explanation"
        elif lower.startswith("what is expected:"):
            data["what_is_expected"] = line.split(":", 1)[1].strip()
            current_key = "what_is_expected"
        elif lower.startswith("example answer:"):
            data["example_answer"] = line.split(":", 1)[1].strip()
            current_key = "example_answer"
        elif lower.startswith("safety note:"):
            data["safety_note"] = line.split(":", 1)[1].strip()
            current_key = "safety_note"
        elif current_key:
            data[current_key] += " " + line

    return data


def render_parsed_response(parsed: dict):
    if parsed["type"]:
        st.markdown(f"**Type:** `{parsed['type']}`")

    if parsed["simple_explanation"]:
        st.markdown("### Simple explanation")
        st.write(parsed["simple_explanation"])

    if parsed["what_is_expected"]:
        st.markdown("### What is expected")
        st.write(parsed["what_is_expected"])

    if parsed["example_answer"]:
        st.markdown("### Example answer")
        st.info(parsed["example_answer"])

    if parsed["safety_note"]:
        st.markdown("### Safety note")
        st.warning(parsed["safety_note"])


st.set_page_config(page_title="Refugee Assistant Switzerland", page_icon="💬")
st.title("Refugee Assistant Switzerland")
st.caption("Guidance only — not legal advice")
st.caption("Privacy-first: do not share unnecessary personal details. If location is relevant, canton is enough.")

user_input = st.text_area(
    "Paste a form question or ask a simple question",
    placeholder=(
        "Examples:\n"
        "- Provide proof of residence\n"
        "- What does legal status mean?\n"
        "- Is canton information enough?"
    ),
    height=160,
)

if "last_result" not in st.session_state:
    st.session_state.last_result = None

if "last_input" not in st.session_state:
    st.session_state.last_input = ""

if st.button("Get Guidance", use_container_width=True):
    if user_input.strip():
        with st.spinner("Understanding your question..."):
            result = process_user_input(user_input)
            save_interaction(user_input, result)
            st.session_state.last_result = result
            st.session_state.last_input = user_input
    else:
        st.warning("Please enter a question first.")

if st.session_state.last_result:
    st.subheader("Latest result")
    st.markdown(f"**Question:** {st.session_state.last_input}")
    parsed_latest = parse_response(st.session_state.last_result)
    render_parsed_response(parsed_latest)

with st.expander("Recent interactions"):
    history = get_recent_interactions()

    if history:
        for index, (user_q, response, created_at) in enumerate(history, start=1):
            parsed_history = parse_response(response)

            with st.expander(f"{index}. {created_at} — {user_q[:60]}"):
                st.markdown(f"**Question:** {user_q}")
                render_parsed_response(parsed_history)
    else:
        st.caption("No saved interactions yet.")