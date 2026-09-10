"""Tool functions for the DecisionExtractor agent.

Each function takes transcript text and returns structured JSON extracted
from it. No shared state, no ADK dependency, so these can later be wrapped
as MCP tools unchanged.
"""

from common.llm_client import call_llm
from common.logging_config import get_logger

logger = get_logger(__name__)

_DECISIONS_SCHEMA = {
    "title": "decisions",
    "type": "object",
    "properties": {
        "decisions": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "decision": {"type": "string"},
                    "made_by": {"type": "string"},
                    "context": {"type": "string"},
                },
                "required": ["decision", "made_by", "context"],
                "additionalProperties": False,
            },
        }
    },
    "required": ["decisions"],
    "additionalProperties": False,
}

_QUESTIONS_SCHEMA = {
    "title": "questions",
    "type": "object",
    "properties": {
        "questions": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "question": {"type": "string"},
                    "asked_by": {"type": "string"},
                    "answered": {"type": "boolean"},
                },
                "required": ["question", "asked_by", "answered"],
                "additionalProperties": False,
            },
        }
    },
    "required": ["questions"],
    "additionalProperties": False,
}

_AGREEMENTS_SCHEMA = {
    "title": "agreements",
    "type": "object",
    "properties": {
        "agreements": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "agreement": {"type": "string"},
                    "parties": {
                        "type": "array",
                        "items": {"type": "string"},
                    },
                },
                "required": ["agreement", "parties"],
                "additionalProperties": False,
            },
        }
    },
    "required": ["agreements"],
    "additionalProperties": False,
}


def extract_decisions(transcript: str) -> list[dict]:
    """Extract decisions that were made during the conversation.

    Args:
        transcript: The meeting transcript text.

    Returns:
        A list of {decision, made_by, context} dicts.
    """
    system_prompt = (
        "You analyze meeting transcripts and extract concrete decisions that were "
        "made. A decision is a conclusion the group committed to, not an idea that "
        "was merely floated. 'made_by' is the speaker who made or confirmed the "
        "decision (or 'group' if it was a joint decision). 'context' is a brief "
        "note on why the decision was made. If no decisions were made, return an "
        "empty list."
    )
    logger.info("extract_decisions called input_chars=%d", len(transcript))
    result = call_llm(system_prompt, transcript, json_schema=_DECISIONS_SCHEMA)
    logger.info("extract_decisions done count=%d", len(result["decisions"]))
    return result["decisions"]


def extract_questions(transcript: str) -> list[dict]:
    """Extract questions that were raised during the conversation.

    Args:
        transcript: The meeting transcript text.

    Returns:
        A list of {question, asked_by, answered} dicts.
    """
    system_prompt = (
        "You analyze meeting transcripts and extract questions that were raised. "
        "'asked_by' is the speaker who asked. 'answered' is true if the transcript "
        "shows the question being answered before the conversation moves on, false "
        "if it was left open. If no questions were asked, return an empty list."
    )
    logger.info("extract_questions called input_chars=%d", len(transcript))
    result = call_llm(system_prompt, transcript, json_schema=_QUESTIONS_SCHEMA)
    logger.info("extract_questions done count=%d", len(result["questions"]))
    return result["questions"]


def detect_agreements(transcript: str) -> list[dict]:
    """Detect points where multiple speakers reached agreement or consensus.

    Args:
        transcript: The meeting transcript text.

    Returns:
        A list of {agreement, parties} dicts.
    """
    system_prompt = (
        "You analyze meeting transcripts and detect moments of agreement or "
        "consensus between two or more speakers (e.g. one proposes something and "
        "another explicitly agrees). 'parties' lists the speakers who agreed. This "
        "is distinct from a unilateral decision — only include cases where "
        "agreement between multiple people is explicit in the transcript. If none, "
        "return an empty list."
    )
    logger.info("detect_agreements called input_chars=%d", len(transcript))
    result = call_llm(system_prompt, transcript, json_schema=_AGREEMENTS_SCHEMA)
    logger.info("detect_agreements done count=%d", len(result["agreements"]))
    return result["agreements"]
