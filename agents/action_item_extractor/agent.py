from google.adk.agents import Agent
from google.adk.models.lite_llm import LiteLlm

from . import tools

root_agent = Agent(
    name="action_item_extractor",
    model=LiteLlm(model="openai/gpt-4o-mini"),
    description=(
        "Extracts action items from a meeting transcript, along with their "
        "owner and deadline."
    ),
    instruction=(
        "You help pull action items out of meeting transcripts. Call "
        "extract_action_items to get the full list with owner/deadline filled in "
        "where inferable. If an item is missing an owner or deadline and the user "
        "asks you to dig further, call identify_owner or identify_deadline with "
        "that specific item plus the transcript to try to resolve it."
    ),
    tools=[
        tools.extract_action_items,
        tools.identify_owner,
        tools.identify_deadline,
    ],
)
