"""Orchestrator that calls the three agents over A2A (HTTP) instead of
importing them directly in-process like orchestrator/local_orchestrator.

Pre-registry milestone: agent URLs are hardcoded here rather than resolved
via mcp-gateway-registry. A later step replaces these hardcoded URLs with a
registry lookup. Requires each agent's A2A server to be running first, e.g.:

    uv run uvicorn agents.transcript_cleaner.a2a_server:a2a_app --port 8001
    uv run uvicorn agents.decision_extractor.a2a_server:a2a_app --port 8002
    uv run uvicorn agents.action_item_extractor.a2a_server:a2a_app --port 8003
"""

from google.adk.agents import Agent
from google.adk.agents.remote_a2a_agent import RemoteA2aAgent
from google.adk.models.lite_llm import LiteLlm
from google.adk.tools.agent_tool import AgentTool

from common.llm_client import get_model_name

transcript_cleaner = RemoteA2aAgent(
    name="transcript_cleaner",
    agent_card="http://localhost:8001",
    description=(
        "Cleans noisy, speaker-diarized meeting transcripts: fixes diarization "
        "errors, removes disfluencies, and normalizes speaker labels."
    ),
)
decision_extractor = RemoteA2aAgent(
    name="decision_extractor",
    agent_card="http://localhost:8002",
    description=(
        "Extracts decisions, open questions, and agreements from a meeting "
        "transcript."
    ),
)
action_item_extractor = RemoteA2aAgent(
    name="action_item_extractor",
    agent_card="http://localhost:8003",
    description=(
        "Extracts action items from a meeting transcript, along with their "
        "owner and deadline."
    ),
)

# RemoteA2aAgent only supports mode="task" (multi-turn delegation protocol,
# requires the remote agent to signal completion via a finish_task tool) or
# None (full conversational transfer_to_agent hand-off) — unlike a local
# sub-agent it has no "single_turn" mode. To get the same "call it, get a
# result back, stay in control" behavior as the local orchestrator, each
# remote agent is wrapped explicitly as a tool here instead of relying on
# automatic sub_agents mode-wrapping.
root_agent = Agent(
    name="a2a_orchestrator",
    model=LiteLlm(model=f"openai/{get_model_name()}"),
    description=(
        "Routes noisy-transcript processing requests to whichever specialist "
        "A2A agent(s) can handle them: transcript_cleaner, decision_extractor, "
        "action_item_extractor."
    ),
    instruction=(
        "You have three specialist agents available as tools, each reached "
        "over A2A:\n"
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
    tools=[
        AgentTool(transcript_cleaner),
        AgentTool(decision_extractor),
        AgentTool(action_item_extractor),
    ],
)
