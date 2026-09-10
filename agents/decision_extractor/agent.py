from google.adk.agents import Agent
from google.adk.models.lite_llm import LiteLlm

from common.llm_client import get_model_name

from . import tools

root_agent = Agent(
    name="decision_extractor",
    model=LiteLlm(model=f"openai/{get_model_name()}"),
    description=(
        "Extracts decisions, open questions, and agreements from a meeting "
        "transcript."
    ),
    instruction=(
        "You help pull structured insight out of meeting transcripts. Use "
        "extract_decisions for decisions that were made, extract_questions for "
        "questions raised (answered or not), and detect_agreements for moments "
        "where multiple speakers explicitly agreed on something. Call whichever "
        "tool(s) match what the user asked for, and present the results clearly."
    ),
    tools=[
        tools.extract_decisions,
        tools.extract_questions,
        tools.detect_agreements,
    ],
)
