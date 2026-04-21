import streamlit as st
from src.llm_service import explain_question
from src.database import init_db, save_interaction

init_db()

st.set_page_config(page_title="Refugee Assistant Switzerland")
st.title("Refugee Assistant Switzerland")
st.caption("Guidance only — not legal advice")

user_input = st.text_area("Paste a form question or ask a simple question")

if st.button("Explain"):
    if user_input.strip():
        with st.spinner("Thinking..."):
            result = explain_question(user_input)
            save_interaction(user_input, result)
        st.subheader("Result")
        st.write(result)
    else:
        st.warning("Please enter a question first.")
