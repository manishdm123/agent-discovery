from google.adk.agents import Agent
from google.adk.models.lite_llm import LiteLlm

from common.llm_client import get_model_name

from . import tools

root_agent = Agent(
    name="transcript_cleaner",
    model=LiteLlm(model=f"openai/{get_model_name()}"),
    description=(
        "Cleans noisy, speaker-diarized meeting transcripts: fixes diarization "
        "errors, removes disfluencies, and normalizes speaker labels."
    ),
    instruction=(
        "You help clean up noisy diarized meeting transcripts. "
        "If the user just wants the transcript cleaned up in general, call "
        "clean_transcript. If they ask for a specific fix (diarization, "
        "disfluencies, or speaker labels only), call the matching tool instead. "
        "Always return the tool's output transcript text, not a summary of it."
    ),
    tools=[
        tools.clean_transcript,
        tools.fix_diarization,
        tools.remove_disfluencies,
        tools.normalize_speakers,
    ],
)
