# Registry integration (not yet implemented)

This will hold the glue for registering the three A2A agents (`agents/*/a2a_server.py`)
with [mcp-gateway-registry](https://github.com/agentic-community/mcp-gateway-registry)
so `orchestrator/a2a_orchestrator` can discover them dynamically instead of
hardcoding `localhost:8001/8002/8003`.

Planned shape:
- A registration script that, for each agent, fetches its live agent card
  (`GET http://localhost:800X/.well-known/agent-card.json`) and posts it to
  the registry's `POST /api/agents/register`. No new agent-side code needed —
  `to_a2a()` already generates the card from the existing `root_agent`.
- Swap `orchestrator/a2a_orchestrator`'s hardcoded `RemoteA2aAgent` URLs for a
  runtime call to `POST /api/agents/discover/semantic` (natural-language
  query per capability needed), using whatever URL the registry returns.
- Requires running the registry itself locally (docker compose — Keycloak,
  MongoDB, nginx gateway, registry API). Auth mode (static API token vs.
  Keycloak client-credentials JWT) still to be decided. Out of scope for this
  repo until that infra work is explicitly taken on.
