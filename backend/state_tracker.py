from typing import Any


def build_initial_state() -> dict[str, Any]:
    return {
        "current_permit": None,
    }


def update_state(state: dict[str, Any], resolved: dict[str, Any]) -> dict[str, Any]:
    new_state = state.copy()

    effective_permit = resolved.get("effective_permit")
    if effective_permit:
        new_state["current_permit"] = effective_permit

    return new_state
