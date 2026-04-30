import os
from datetime import date
from pathlib import Path
from typing import Any
from openai import OpenAI
from dotenv import load_dotenv
from src.prompts import SYSTEM_PROMPT

env_path = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(dotenv_path=env_path)

api_key = os.getenv("GROQ_API_KEY")
client = OpenAI(
    api_key=api_key,
    base_url="https://api.groq.com/openai/v1",
) if api_key else None

MODEL = "llama-3.3-70b-versatile"


def _format_sources(sources: list[dict[str, Any]]) -> str:
    if not sources:
        return ""
    blocks = []
    for idx, src in enumerate(sources, start=1):
        blocks.append(
            f"[Source {idx}: {src['title']}]\n"
            f"URL: {src['url']}\n"
            f"{src['content']}"
        )
    return "\n\n".join(blocks)


def process_chat_turn(
    messages: list[dict[str, Any]],
    sources: list[dict[str, Any]],
    canton: str | None = None,
) -> str:
    if not client:
        raise ValueError(
            "GROQ_API_KEY is not set. Please add it to your .env file."
        )

    sources_text = _format_sources(sources)

    today = date.today().strftime("%B %d, %Y")
    canton_note = (
        f"\nUSER'S CANTON: {canton}. "
        "When answering questions about local offices, integration programmes, "
        "language courses, or canton-specific procedures, prioritise information "
        f"relevant to {canton}. Always mention the cantonal migration office "
        "if it is relevant to the question."
        if canton else ""
    )
    system_with_date = (
        f"{SYSTEM_PROMPT}\n\n"
        f"TODAY'S DATE: {today}. "
        f"Always use this date when the user asks what day or date it is."
        f"{canton_note}"
    )

    api_messages = [{"role": "system", "content": system_with_date}]

    for msg in messages[:-1]:
        api_messages.append({"role": msg["role"], "content": msg["content"]})

    last_content = messages[-1]["content"]
    if sources_text:
        last_content = (
            f"{last_content}\n\n"
            f"---\n"
            f"Relevant official sources:\n{sources_text}"
        )
    api_messages.append({"role": "user", "content": last_content})

    response = client.chat.completions.create(
        model=MODEL,
        messages=api_messages,
    )
    return response.choices[0].message.content
