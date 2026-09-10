"""Tool functions for the ActionItemExtractor agent.

Each function takes transcript text (and, for the two resolver helpers, a
single action item) and returns structured JSON. No shared state, no ADK
dependency, so these can later be wrapped as MCP tools unchanged.
"""

from common.llm_client import call_llm

_ACTION_ITEMS_SCHEMA = {
    "title": "action_items",
    "type": "object",
    "properties": {
        "action_items": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "item": {"type": "string"},
                    "owner": {"type": ["string", "null"]},
                    "deadline": {"type": ["string", "null"]},
                },
                "required": ["item", "owner", "deadline"],
                "additionalProperties": False,
            },
        }
    },
    "required": ["action_items"],
    "additionalProperties": False,
}

_OWNER_SCHEMA = {
    "title": "owner",
    "type": "object",
    "properties": {"owner": {"type": ["string", "null"]}},
    "required": ["owner"],
    "additionalProperties": False,
}

_DEADLINE_SCHEMA = {
    "title": "deadline",
    "type": "object",
    "properties": {"deadline": {"type": ["string", "null"]}},
    "required": ["deadline"],
    "additionalProperties": False,
}


def extract_action_items(transcript: str) -> list[dict]:
    """Extract action items from the conversation, with owner and deadline.

    Args:
        transcript: The meeting transcript text.

    Returns:
        A list of {item, owner, deadline} dicts. `owner`/`deadline` are null
        when not inferable from the transcript alone.
    """
    system_prompt = (
        "You analyze meeting transcripts and extract concrete action items "
        "(tasks someone committed to doing). For each: 'item' is a concise "
        "description of the task, 'owner' is the person responsible if stated or "
        "clearly implied (otherwise null), and 'deadline' is the due date/time if "
        "stated or clearly implied (otherwise null). Do not guess an owner or "
        "deadline that isn't supported by the transcript. If there are no action "
        "items, return an empty list."
    )
    result = call_llm(system_prompt, transcript, json_schema=_ACTION_ITEMS_SCHEMA)
    return result["action_items"]


def identify_owner(action_item: str, transcript: str) -> str | None:
    """Resolve who owns a single action item, using the full transcript as context.

    Useful when `extract_action_items` couldn't infer an owner on its own.

    Args:
        action_item: The action item text to resolve an owner for.
        transcript: The full meeting transcript, for context.

    Returns:
        The owner's name, or None if it can't be determined.
    """
    system_prompt = (
        "You are given a meeting transcript and a single action item derived from "
        "it. Identify who is responsible for that action item, using the "
        "transcript as context. Return null if the transcript does not make the "
        "owner clear — do not guess."
    )
    user_content = f"Action item: {action_item}\n\nTranscript:\n{transcript}"
    result = call_llm(system_prompt, user_content, json_schema=_OWNER_SCHEMA)
    return result["owner"]


def identify_deadline(action_item: str, transcript: str) -> str | None:
    """Resolve the deadline for a single action item, using the full transcript as context.

    Useful when `extract_action_items` couldn't infer a deadline on its own.

    Args:
        action_item: The action item text to resolve a deadline for.
        transcript: The full meeting transcript, for context.

    Returns:
        The deadline as stated (e.g. a date or relative phrase), or None if it
        can't be determined.
    """
    system_prompt = (
        "You are given a meeting transcript and a single action item derived from "
        "it. Identify the deadline for that action item, using the transcript as "
        "context. Return null if the transcript does not state or clearly imply a "
        "deadline — do not guess."
    )
    user_content = f"Action item: {action_item}\n\nTranscript:\n{transcript}"
    result = call_llm(system_prompt, user_content, json_schema=_DEADLINE_SCHEMA)
    return result["deadline"]
