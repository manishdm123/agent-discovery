"""Tool functions for the TranscriptCleaner agent.

Each function is a standalone capability: it takes raw transcript text and
returns cleaned transcript text. No shared state, no ADK dependency, so these
can later be wrapped as MCP tools unchanged.
"""

from common.llm_client import call_llm
from common.logging_config import get_logger

logger = get_logger(__name__)

_BASE_RULES = (
    "You clean up noisy, auto-generated speaker-diarized meeting transcripts. "
    "Preserve the original meaning and speaker turns. Do not summarize or omit content. "
    "Return only the cleaned transcript text, with no commentary or preamble."
)


def clean_transcript(transcript: str) -> str:
    """Fully clean a noisy diarized transcript in one pass.

    Fixes speaker-turn misattribution, removes disfluencies (filler words,
    false starts, stutters), and normalizes speaker labels consistently.

    Args:
        transcript: The raw, noisy diarized transcript text.

    Returns:
        The cleaned transcript text.
    """
    system_prompt = (
        f"{_BASE_RULES}\n\n"
        "Do all of the following:\n"
        "1. Fix diarization: merge turns that were incorrectly split across the same "
        "speaker, and reassign lines that were attributed to the wrong speaker when "
        "context makes the correct speaker obvious.\n"
        "2. Remove disfluencies: strip filler words (um, uh, like, you know), false "
        "starts, and stutters, without changing the substance of what was said.\n"
        "3. Normalize speaker labels: use consistent labels throughout "
        "(e.g. 'Speaker 1', 'Speaker 2', or resolved names if the transcript makes them "
        "clear)."
    )
    logger.info("clean_transcript called input_chars=%d", len(transcript))
    result = call_llm(system_prompt, transcript)
    logger.info("clean_transcript done output_chars=%d", len(result))
    return result


def fix_diarization(transcript: str) -> str:
    """Fix speaker-turn misattribution and incorrectly split turns.

    Args:
        transcript: The raw, noisy diarized transcript text.

    Returns:
        The transcript with corrected speaker turns.
    """
    system_prompt = (
        f"{_BASE_RULES}\n\n"
        "Only fix diarization errors: merge turns that were incorrectly split across "
        "the same speaker, and reassign lines that were attributed to the wrong "
        "speaker when context makes the correct speaker obvious. Do not remove "
        "disfluencies or otherwise rewrite the wording."
    )
    logger.info("fix_diarization called input_chars=%d", len(transcript))
    result = call_llm(system_prompt, transcript)
    logger.info("fix_diarization done output_chars=%d", len(result))
    return result


def remove_disfluencies(transcript: str) -> str:
    """Strip filler words, false starts, and stutters from a transcript.

    Args:
        transcript: The raw, noisy diarized transcript text.

    Returns:
        The transcript with disfluencies removed.
    """
    system_prompt = (
        f"{_BASE_RULES}\n\n"
        "Only remove disfluencies: filler words (um, uh, like, you know), false "
        "starts, and stutters. Do not change speaker attribution or wording beyond "
        "removing these disfluencies."
    )
    logger.info("remove_disfluencies called input_chars=%d", len(transcript))
    result = call_llm(system_prompt, transcript)
    logger.info("remove_disfluencies done output_chars=%d", len(result))
    return result


def normalize_speakers(transcript: str) -> str:
    """Normalize speaker labels to be consistent throughout the transcript.

    Args:
        transcript: The raw, noisy diarized transcript text.

    Returns:
        The transcript with consistent speaker labels.
    """
    system_prompt = (
        f"{_BASE_RULES}\n\n"
        "Only normalize speaker labels: make them consistent throughout "
        "(e.g. 'Speaker 1', 'Speaker 2', or resolved names if the transcript makes "
        "them clear). Do not change wording, disfluencies, or speaker turn "
        "boundaries."
    )
    logger.info("normalize_speakers called input_chars=%d", len(transcript))
    result = call_llm(system_prompt, transcript)
    logger.info("normalize_speakers done output_chars=%d", len(result))
    return result
