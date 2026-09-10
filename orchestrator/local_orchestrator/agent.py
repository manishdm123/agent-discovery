"""In-process orchestrator: composes the three transcript-processing agents
as single-turn tools of one root LLM. Given a request, it calls whichever
agent(s) match, then presents the combined result.

This is the pre-registry milestone: agents are imported directly by module
path. `orchestrator/a2a_orchestrator` swaps these for RemoteA2aAgent
instances talking to the same agents over HTTP; a later registry milestone
replaces the hardcoded imports/URLs with dynamic discovery.
"""

from google.adk.agents import Agent
from google.adk.models.lite_llm import LiteLlm

from common.llm_client import get_model_name
from agents.transcript_cleaner.agent import root_agent as transcript_cleaner
from agents.decision_extractor.agent import root_agent as decision_extractor
from agents.action_item_extractor.agent import root_agent as action_item_extractor

# `single_turn` mode makes ADK auto-expose each sub-agent as an inline tool of
# this orchestrator (call in, get a result back, orchestrator stays in
# control) instead of a full conversational hand-off.
transcript_cleaner.mode = "single_turn"
decision_extractor.mode = "single_turn"
action_item_extractor.mode = "single_turn"

root_agent = Agent(
    name="local_orchestrator",
    model=LiteLlm(model=f"openai/{get_model_name()}"),
    description=(
        "Routes noisy-transcript processing requests to whichever specialist "
        "agent(s) can handle them: transcript_cleaner, decision_extractor, "
        "action_item_extractor."
    ),
    instruction=(
        "You have three specialist agents available as tools:\n"
        "- transcript_cleaner: cleans noisy diarized transcripts (fixes "
        "diarization, removes disfluencies, normalizes speaker labels).\n"
        "- decision_extractor: extracts decisions, questions, and agreements "
        "from a transcript.\n"
        "- action_item_extractor: extracts action items with owner and "
        "deadline from a transcript.\n"
        "Call whichever agent(s) match what the user is asking for, passing "
        "them the transcript text. If the user wants full processing, call "
        "transcript_cleaner first, then pass its cleaned output to the other "
        "two. Present the combined results clearly."
    ),
    sub_agents=[transcript_cleaner, decision_extractor, action_item_extractor],
)
