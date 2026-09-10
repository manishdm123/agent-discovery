# Orchestrator (not yet implemented)

This will hold the use-case orchestrator: given a task (e.g. "process this
noisy transcript"), it queries the agent registry to dynamically discover
which registered agent(s)/tool(s) can handle each step, invokes them, and
returns the combined response — instead of hardcoding which agent to call.

Planned approach, built on top of `mcp-gateway-registry`:
1. Call the registry's `intelligent_tool_finder` MCP tool with a natural-language
   description of the needed capability (e.g. "clean up a noisy diarized meeting
   transcript") to resolve it to a specific registered tool/server.
2. Call the registry's `invoke_mcp_tool` to actually run it.
3. Repeat per pipeline step (clean -> extract decisions/questions/agreements ->
   extract action items), threading output from one step into the next.

Depends on the three agents in `agents/` being registered with the registry
first (see `registry/`).
