import os
from pathlib import Path
from typing import Any
from dotenv import load_dotenv
from openai import OpenAI

env_path = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(dotenv_path=env_path)

api_key = os.getenv("OPENAI_API_KEY")
use_mock = os.getenv("USE_MOCK_LLM", "true").lower() == "true"

client = OpenAI(api_key=api_key) if api_key else None


def _format_history(messages: list[dict[str, str]], max_messages: int = 8) -> str:
    trimmed = messages[-max_messages:]
    return "\n".join(f"{m['role'].upper()}: {m['content']}" for m in trimmed)


def _format_sources(sources: list[dict[str, Any]]) -> str:
    if not sources:
        return "No trusted sources found."

    blocks = []
    for idx, src in enumerate(sources, start=1):
        blocks.append(
            f"[Source {idx}]\n"
            f"Title: {src['title']}\n"
            f"URL: {src['url']}\n"
            f"Content: {src['content']}\n"
        )
    return "\n".join(blocks)


def _source_titles(sources: list[dict[str, Any]]) -> str:
    if not sources:
        return ""
    return ", ".join(src["title"] for src in sources[:2])


def _has_source_support(sources: list[dict[str, Any]], *terms: str) -> bool:
    joined = " ".join(
        f"{src.get('title', '')} {src.get('topic', '')} {src.get('content', '')}"
        for src in sources
    ).lower()
    return all(term.lower() in joined for term in terms)


def _mock_response(
    messages: list[dict[str, str]],
    resolved: dict[str, Any],
    sources: list[dict[str, Any]]
) -> str:
    intent = resolved["intent"]
    permit = resolved.get("effective_permit")
    source_permit = resolved.get("source_permit")
    target_permit = resolved.get("target_permit")
    source_hint = _source_titles(sources)

    if resolved["needs_clarification"]:
        return (
            f"Answer: {resolved['clarification_question']}\n\n"
            "Safety note: I want to avoid guessing so I can give you more accurate guidance."
        )

    # ---------- DEFINITIONS ----------
    if intent == "definition" and permit == "Permit F":
        answer = (
            "Permit F means provisional admission in Switzerland. "
            "This usually means the person cannot currently be removed from Switzerland. "
            "It is generally issued for 12 months and can be renewed by the canton."
        )
        note = (
            "This is general guidance only. Please confirm important details with an official source or support worker."
        )
        return f"Answer: {answer}\n\nSafety note: {note}"

    if intent == "definition" and permit == "Permit B":
        answer = (
            "Permit B usually means a residence permit in Switzerland. "
            "The exact meaning can depend on the person’s legal situation, so it is important to check the official source that matches the case."
        )
        note = (
            "This is general guidance only. Permit B can appear in different legal contexts."
        )
        return f"Answer: {answer}\n\nSafety note: {note}"

    if intent == "definition" and permit == "Permit C":
        answer = (
            "Permit C usually means a settlement permit in Switzerland. "
            "It is generally linked to longer-term residence and a right to stay that is not limited in time."
        )
        note = "This is general guidance only."
        return f"Answer: {answer}\n\nSafety note: {note}"

    if intent == "definition" and permit == "Permit S":
        answer = (
            "Permit S is a protection status used in Switzerland for people in need of protection. "
            "The exact rules depend on the official source and the person’s situation."
        )
        note = "This is general guidance only."
        return f"Answer: {answer}\n\nSafety note: {note}"

    if intent == "definition" and permit:
        answer = (
            f"{permit} is a permit category used in Switzerland. "
            "I can give first-step guidance, but the exact meaning depends on the official legal context."
        )
        note = "Please confirm the exact permit meaning with an official source."
        return f"Answer: {answer}\n\nSafety note: {note}"

    # ---------- WORK RIGHTS ----------
    if intent == "work_rights" and permit == "Permit F":
        answer = (
            "Yes, people with Permit F may work in Switzerland. "
            "Permit F is a provisional admission permit and is usually issued for 12 months with possible renewal."
        )
        note = (
            "Please confirm important details with an official source or support worker."
        )
        return f"Answer: {answer}\n\nSafety note: {note}"

    if intent == "work_rights" and permit == "Permit S":
        answer = (
            "People with Permit S may have work rights in Switzerland, but the exact administrative steps should be checked with an official source."
        )
        note = "Please confirm the current rules with an official migration source."
        return f"Answer: {answer}\n\nSafety note: {note}"

    if intent == "work_rights" and permit == "Permit B":
        answer = (
            "Work rights with Permit B can depend on the legal context of the permit. "
            "In many cases Permit B is a residence permit, but the exact work situation should be checked against the official source that matches the case."
        )
        note = "This is general guidance only."
        return f"Answer: {answer}\n\nSafety note: {note}"

    if intent == "work_rights" and permit:
        answer = (
            f"Your question is about work rights for {permit}. "
            "I can give first-step guidance, but the exact answer depends on the official source and the person’s legal situation."
        )
        note = "Please confirm this with an official source or support worker."
        return f"Answer: {answer}\n\nSafety note: {note}"

    # ---------- PERMIT TRANSITIONS ----------
    if intent == "permit_transition" and source_permit and target_permit:
        answer = (
            f"I understand that you are asking about moving from {source_permit} to {target_permit}. "
            "This is a more sensitive administrative question, and the answer depends on the person’s legal status and individual case."
        )
        if source_hint:
            answer += f" I found related official sources such as {source_hint}, but I would still avoid giving a precise yes-or-no answer here."
        note = (
            "Please confirm permit transition questions with an official migration source or support worker."
        )
        return f"Answer: {answer}\n\nSafety note: {note}"

    if intent == "permit_transition":
        answer = (
            "Changing from one permit to another depends on the person’s legal and administrative situation. "
            "I would need the exact permit types to guide you more safely."
        )
        note = "Please confirm permit changes with an official migration source."
        return f"Answer: {answer}\n\nSafety note: {note}"

    # ---------- ASYLUM SEEKER INFO ----------
    if intent == "asylum_seeker_info":
        answer = (
            "An asylum seeker in Switzerland usually needs clear information about the asylum procedure, accommodation, documents, and administrative steps. "
            "I can help explain official information in simple language when trusted sources are available."
        )
        note = "This is general guidance only."
        return f"Answer: {answer}\n\nSafety note: {note}"

    # ---------- DOCUMENTS ----------
    if intent == "documents" and permit:
        answer = (
            f"The documents relevant to {permit} depend on the exact process or question. "
            "A good next step is to check the official source linked to that permit or ask a support worker for help with the specific form."
        )
        note = "This is general guidance only."
        return f"Answer: {answer}\n\nSafety note: {note}"

    # ---------- RESIDENCE / CANTON ----------
    if intent == "residence" and permit:
        answer = (
            f"For questions about residence and {permit}, canton-level information is usually enough for first-step guidance. "
            "You do not need to share a full home address unless an official form clearly requires it."
        )
        note = "Do not share unnecessary personal details."
        return f"Answer: {answer}\n\nSafety note: {note}"

    # ---------- GENERAL FALLBACK ----------
    answer = (
        "I can help with official form questions and simple administrative guidance in Switzerland. "
        "You can ask about permit meanings, work rights, asylum procedure basics, or what a form question is asking."
    )
    note = "This is general guidance only."
    return f"Answer: {answer}\n\nSafety note: {note}"


def process_chat_turn(
    messages: list[dict[str, str]],
    resolved: dict[str, Any],
    sources: list[dict[str, Any]]
) -> str:
    if use_mock:
        return _mock_response(messages, resolved, sources)

    if not api_key:
        raise ValueError("OPENAI_API_KEY not found.")

    history_text = _format_history(messages)
    sources_text = _format_sources(sources)

    response = client.responses.create(
        model="gpt-4.1-mini",
        input=[
            {
                "role": "system",
                "content": (
                    "You are a refugee support assistant for Switzerland. "
                    "Answer naturally in simple English, like a helpful chat assistant. "
                    "Do not use headings like Type, What is expected, or Example answer. "
                    "Do not give legal advice. "
                    "Do not ask for a full home address. "
                    "If location is relevant, mention canton only. "
                    "Prefer the trusted sources provided. "
                    "If the user is asking about work rights, answer the permission question directly first if the sources support it, for example 'Yes' or 'No' and then explain briefly. "
                    "If the question is sensitive or the sources are not enough, say clearly that you are giving only general guidance. "
                    "Return your reply in this exact format:\n"
                    "Answer: ...\n"
                    "Safety note: ..."
                ),
            },
            {
                "role": "user",
                "content": (
                    f"Conversation history:\n{history_text}\n\n"
                    f"Resolved user intent: {resolved['intent']}\n"
                    f"Source permit: {resolved['source_permit']}\n"
                    f"Target permit: {resolved['target_permit']}\n"
                    f"Effective permit: {resolved['effective_permit']}\n"
                    f"Standalone query: {resolved['standalone_query']}\n\n"
                    f"Trusted source snippets:\n{sources_text}\n\n"
                    "Respond to the latest user message only, but use the resolved context to stay precise."
                ),
            },
        ],
    )

    return response.output_text