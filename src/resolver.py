import re
from typing import Any

PERMIT_PATTERN = re.compile(r"\bpermit\s+([a-z])\b", re.IGNORECASE)

TOPIC_KEYWORDS = {
    "work": ["work", "job", "employment", "arbeiten", "travail", "emploi"],
    "integration": ["integration", "language", "course", "fide", "sprache", "langue"],
    "healthcare": ["health", "doctor", "medical", "hospital", "kranken", "santé"],
    "education": ["school", "children", "education", "schule", "école", "enfant"],
    "family": ["family", "reunification", "spouse", "children", "famille", "familien"],
    "appeal": ["appeal", "rejected", "negative", "recours", "beschwerde"],
    "asylum": ["asylum", "asyl", "asile", "procedure", "interview"],
    "naturalization": ["citizenship", "naturalization", "passport", "einbürgerung", "naturalisation"],
}


def _extract_permits(text: str) -> list[str]:
    matches = PERMIT_PATTERN.findall(text)
    seen = []
    for m in matches:
        permit = f"Permit {m.upper()}"
        if permit not in seen:
            seen.append(permit)
    return seen


def _detect_topics(text: str) -> list[str]:
    lower = text.lower()
    return [topic for topic, keywords in TOPIC_KEYWORDS.items() if any(kw in lower for kw in keywords)]


def _build_search_query(
    user_input: str,
    permits: list[str],
    topics: list[str],
    state: dict[str, Any],
) -> str:
    parts = []

    effective_permit = permits[0] if permits else state.get("current_permit")
    if effective_permit:
        parts.append(effective_permit)

    parts.extend(topics[:2])

    if not parts:
        return user_input.strip()

    return " ".join(parts) + " Switzerland"


def resolve_user_query(user_input: str, state: dict[str, Any]) -> dict[str, Any]:
    permits = _extract_permits(user_input)
    topics = _detect_topics(user_input)

    effective_permit = permits[0] if permits else state.get("current_permit")
    standalone_query = _build_search_query(user_input, permits, topics, state)

    return {
        "raw_input": user_input,
        "standalone_query": standalone_query,
        "mentioned_permits": permits,
        "effective_permit": effective_permit,
        "topics": topics,
    }
