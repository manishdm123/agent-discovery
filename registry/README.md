# Registry integration (not yet implemented)

This will hold the glue for registering the three agents in `agents/` with
[mcp-gateway-registry](https://github.com/agentic-community/mcp-gateway-registry)
so the orchestrator can discover them dynamically instead of hardcoding
endpoints.

Planned shape:
- A thin FastMCP server per agent (or one server exposing all three
  namespaced) that imports the existing `agents/*/tools.py` functions
  unchanged and exposes them as MCP tools. The tool logic already lives in
  plain, ADK-independent functions specifically so this wrapper stays thin.
- A registration script that calls the registry's `POST /api/servers/register`
  (or the equivalent CLI/UI flow) for each MCP server, with a description rich
  enough for the registry's semantic search / `intelligent_tool_finder` to
  match it correctly.
- Requires running the registry itself locally (docker compose — Keycloak,
  MongoDB, nginx gateway, registry API). Out of scope for this repo until
  that infra work is explicitly taken on.
