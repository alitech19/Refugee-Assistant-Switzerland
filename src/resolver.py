import re
from typing import Any

PERMIT_PATTERN = re.compile(r"\bpermit\s+([a-z])\b", re.IGNORECASE)


def extract_permits(text: str) -> list[str]:
    matches = PERMIT_PATTERN.findall(text)
    seen = []
    for m in matches:
        permit = f"Permit {m.upper()}"
        if permit not in seen:
            seen.append(permit)
    return seen


def detect_intent(text: str) -> str:
    lower = text.lower().strip()

    if any(x in lower for x in ["can i work", "can work", "work", "job", "employment"]):
        return "work_rights"

    if any(x in lower for x in ["change to", "switch to", "move to", "submit to have", "apply for permit", "change permit"]):
        return "permit_transition"

    if "what about permit" in lower:
        return "definition"

    if any(x in lower for x in ["what does", "what is", "mean", "means"]):
        return "definition"

    if "asylum seeker" in lower:
        return "asylum_seeker_info"

    if any(x in lower for x in ["document", "documents", "paper", "papers"]):
        return "documents"

    if any(x in lower for x in ["canton", "residence", "address", "live"]):
        return "residence"

    return "general_admin"


def is_short_followup(text: str) -> bool:
    return len(text.strip().split()) <= 6


def build_standalone_query(
    user_input: str,
    intent: str,
    source_permit: str | None,
    target_permit: str | None,
    effective_permit: str | None,
    state: dict[str, Any]
) -> str:
    raw = user_input.strip()

    if intent == "definition":
        if effective_permit:
            return f"What does {effective_permit} mean in Switzerland?"
        return raw

    if intent == "work_rights":
        if effective_permit:
            return f"Can a person with {effective_permit} work in Switzerland?"
        return raw

    if intent == "permit_transition":
        if source_permit and target_permit:
            return f"Can a person move from {source_permit} to {target_permit} in Switzerland?"
        if target_permit and state.get("current_permit"):
            return f"Can a person move from {state['current_permit']} to {target_permit} in Switzerland?"
        return raw

    if intent == "documents":
        if effective_permit:
            return f"What documents are relevant for a person with {effective_permit} in Switzerland?"
        return raw

    if intent == "residence":
        if effective_permit:
            return f"What residence or canton information is relevant for a person with {effective_permit} in Switzerland?"
        return raw

    if intent == "asylum_seeker_info":
        return "What official information is relevant for an asylum seeker in Switzerland?"

    if is_short_followup(raw) and state.get("last_resolved_query"):
        return state["last_resolved_query"]

    return raw


def resolve_user_query(user_input: str, state: dict[str, Any]) -> dict[str, Any]:
    permits = extract_permits(user_input)
    intent = detect_intent(user_input)

    current_permit = state.get("current_permit")
    previous_permit = state.get("previous_permit")

    source_permit = None
    target_permit = None
    effective_permit = None

    # Two permits explicitly mentioned in one message
    if len(permits) >= 2:
        source_permit = permits[0]
        target_permit = permits[1]
        effective_permit = target_permit

    # One permit explicitly mentioned
    elif len(permits) == 1:
        if intent == "permit_transition" and current_permit and permits[0] != current_permit:
            source_permit = current_permit
            target_permit = permits[0]
            effective_permit = permits[0]
        else:
            effective_permit = permits[0]

    # No explicit permit in the message
    else:
        if intent == "work_rights":
            effective_permit = current_permit

        elif intent == "definition":
            effective_permit = current_permit

        elif intent == "permit_transition":
            # Example: "Can I change to it?"
            source_permit = previous_permit
            target_permit = current_permit
            effective_permit = current_permit

    standalone_query = build_standalone_query(
        user_input=user_input,
        intent=intent,
        source_permit=source_permit,
        target_permit=target_permit,
        effective_permit=effective_permit,
        state=state,
    )

    needs_clarification = False
    clarification_question = None

    if intent in {"definition", "work_rights"} and not effective_permit:
        needs_clarification = True
        clarification_question = "Do you mean Permit F, Permit B, Permit C, Permit S, or another permit?"

    if intent == "permit_transition" and not target_permit:
        needs_clarification = True
        clarification_question = "Which permit are you asking about changing to?"

    return {
        "raw_input": user_input,
        "intent": intent,
        "source_permit": source_permit,
        "target_permit": target_permit,
        "effective_permit": effective_permit,
        "standalone_query": standalone_query,
        "needs_clarification": needs_clarification,
        "clarification_question": clarification_question,
    }