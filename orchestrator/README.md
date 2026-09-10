# Orchestrators

Two orchestrators exist, each composing the same three agents from `agents/`
a different way — steps toward the north star of registry-driven discovery,
each one removing one layer of hardcoding.

## `local_orchestrator/` (done)

In-process: imports the three agents' `root_agent` objects directly and adds
them as `sub_agents` with `mode="single_turn"`, which makes ADK auto-expose
each one as an inline tool (call in, get a result back, orchestrator stays in
control — not a full conversational hand-off). No network involved.

```bash
uv run adk run --in_memory orchestrator/local_orchestrator "Do a complete process of transcript: $(cat data/sample_transcript.txt)"
```

## `a2a_orchestrator/` (done)

Same behavior, but each agent is called over HTTP via A2A instead of being
imported directly. Uses `RemoteA2aAgent` pointed at each agent's `/.well-known/
agent-card.json`, wrapped explicitly in `AgentTool` (since `RemoteA2aAgent`
doesn't support `single_turn` mode the way a local sub-agent does — only
`task` mode or a full `transfer_to_agent` hand-off).

Requires the three agents' A2A servers running first:

```bash
uv run uvicorn agents.transcript_cleaner.a2a_server:a2a_app --port 8001
uv run uvicorn agents.decision_extractor.a2a_server:a2a_app --port 8002
uv run uvicorn agents.action_item_extractor.a2a_server:a2a_app --port 8003
```

Then:

```bash
uv run adk run --in_memory orchestrator/a2a_orchestrator "Process this transcript fully: $(cat data/sample_transcript.txt)"
```

Agent URLs (`localhost:8001/8002/8003`) are hardcoded in
`a2a_orchestrator/agent.py` for now.

## Next step (not yet implemented): registry-driven orchestrator

Both orchestrators above hardcode which agents exist and how to reach them
(a Python import in one case, a `localhost` URL in the other). The remaining
step is to remove that hardcoding: register each agent's A2A card with
`mcp-gateway-registry` (`POST /api/agents/register`), then have the
orchestrator resolve agents at runtime via `POST /api/agents/discover/semantic`
instead of a fixed list — see `registry/README.md`.
