from typing import Any


def build_initial_state() -> dict[str, Any]:
    return {
        "current_permit": None,
        "previous_permit": None,
        "current_topic": None,
        "last_resolved_query": None,
        "needs_clarification": False,
    }


def update_state(state: dict[str, Any], resolved: dict[str, Any]) -> dict[str, Any]:
    new_state = state.copy()

    effective_permit = resolved.get("effective_permit")
    target_permit = resolved.get("target_permit")
    intent = resolved.get("intent")
    standalone_query = resolved.get("standalone_query")

    # If user switched to a new permit topic, keep the previous one
    if effective_permit and effective_permit != new_state.get("current_permit"):
        if new_state.get("current_permit"):
            new_state["previous_permit"] = new_state["current_permit"]
        new_state["current_permit"] = effective_permit

    # For explicit transition questions, store both ends clearly
    if intent == "permit_transition":
        if resolved.get("source_permit"):
            new_state["previous_permit"] = resolved["source_permit"]
        if target_permit:
            new_state["current_permit"] = target_permit

    if intent:
        new_state["current_topic"] = intent

    if standalone_query:
        new_state["last_resolved_query"] = standalone_query

    new_state["needs_clarification"] = resolved.get("needs_clarification", False)

    return new_state