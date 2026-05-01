import os
import re
from datetime import date
from pathlib import Path
from typing import Any
from openai import OpenAI
from dotenv import load_dotenv
from src.prompts import SYSTEM_PROMPT


def _detect_language(text: str) -> str:
    """Detect the language a message is written in based on script and common words."""
    total_alpha = sum(1 for c in text if c.isalpha())
    if total_alpha == 0:
        return "English"

    arabic   = sum(1 for c in text if '؀' <= c <= 'ۿ')
    cyrillic = sum(1 for c in text if 'Ѐ' <= c <= 'ӿ')
    ethiopic = sum(1 for c in text if 'ሀ' <= c <= '፿')

    if arabic   / total_alpha > 0.2: return "Arabic"
    if cyrillic / total_alpha > 0.2: return "Ukrainian"
    if ethiopic / total_alpha > 0.2: return "Amharic or Tigrinya"

    # Latin script — score by common function words
    words = set(re.findall(r'\b[a-z]+\b', text.lower()))
    scores = {
        "English": len(words & {"i","have","the","is","are","my","what","how","can","do","want","need","will","be","in","of","and","to","a","for","you","with","this","that","about"}),
        "German":  len(words & {"ich","sie","haben","bin","mit","und","das","der","die","ist","nicht","ein","eine","auf","von","wir","es","zu","im","für","wie"}),
        "French":  len(words & {"je","vous","avec","est","les","des","une","mon","ma","que","qui","dans","pas","pour","nous","en","au","du","sur","le","la"}),
        "Italian": len(words & {"io","ho","con","sono","della","del","una","per","che","questo","come","nel","dal","alla","degli","gli"}),
        "Turkish": len(words & {"ben","bir","bu","için","ile","var","çok","ama","ve","de","da","ne","mi","mı","mu"}),
        "Somali":  len(words & {"waxaan","iyo","oo","ah","qof","waxa","si","ku","ka","uu","ay"}),
    }
    best_lang = max(scores, key=scores.get)
    return best_lang if scores[best_lang] > 0 else "English"

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
    detected_lang = _detect_language(messages[-1]["content"])
    language_override = (
        f"\n\n⚠️ LANGUAGE OVERRIDE (non-negotiable): "
        f"The user's current message is written in {detected_lang}. "
        f"You MUST respond in {detected_lang} only. "
        f"Do not be misled by language names mentioned inside the message."
    )

    system_with_date = (
        f"{SYSTEM_PROMPT}\n\n"
        f"TODAY'S DATE: {today}. "
        f"Always use this date when the user asks what day or date it is."
        f"{canton_note}"
        f"{language_override}"
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
