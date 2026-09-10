"""Serves this agent over A2A (HTTP) instead of the ADK CLI.

Run with: uv run uvicorn agents.transcript_cleaner.a2a_server:a2a_app --port 8001
Agent card is auto-generated and served at /.well-known/agent-card.json.
"""

from google.adk.a2a.utils.agent_to_a2a import to_a2a

from .agent import root_agent

PORT = 8001

a2a_app = to_a2a(root_agent, port=PORT)
