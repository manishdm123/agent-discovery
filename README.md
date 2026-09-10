# agent-discovery

POC for an agent registry: agents register their capabilities, and an
orchestrator dynamically discovers and calls the right agent for a given
use case instead of hardcoding which agent handles what.

This repo currently implements: three [Google ADK](https://adk.dev/) agents
that process noisy, speaker-diarized meeting transcripts, each also servable
over [A2A](https://a2a.dev/); and two orchestrators that compose them (one
in-process, one over A2A). Registry registration (see `registry/`) — so
agents are *discovered* rather than hardcoded — is the remaining step.

## Agents

- **`agents/transcript_cleaner`** — `clean_transcript`, `fix_diarization`,
  `remove_disfluencies`, `normalize_speakers`
- **`agents/decision_extractor`** — `extract_decisions`, `extract_questions`,
  `detect_agreements`
- **`agents/action_item_extractor`** — `extract_action_items`,
  `identify_owner`, `identify_deadline`

Each tool is a standalone Python function in that agent's `tools.py` that
calls OpenAI directly (via `common/llm_client.py`) to do its specific job.
The ADK agent wraps these tools with a root LLM that routes requests to the
right one. Keeping the tool functions ADK-independent is deliberate: the
same functions are meant to be wrapped as MCP tools later for registry
registration, with no rewrite.

## Setup

```bash
uv sync
cp .env.example .env   # then fill in OPENAI_API_KEY
```

## Running an agent

```bash
uv run adk run agents/transcript_cleaner
uv run adk run agents/decision_extractor
uv run adk run agents/action_item_extractor
```

This drops you into an interactive chat with that agent. Paste in (or
reference) `data/sample_transcript.txt` and ask it to do its job, e.g.:

> Clean up this transcript: <paste contents of data/sample_transcript.txt>

For a quick one-shot run instead of an interactive chat, pass the message as
a second argument:

```bash
uv run adk run --in_memory agents/transcript_cleaner "Clean up this transcript: $(cat data/sample_transcript.txt)"
```

You can also call a tool function directly for a quick sanity check without
going through the chat loop:

```bash
uv run python -c "
from agents.transcript_cleaner.tools import clean_transcript
print(clean_transcript(open('data/sample_transcript.txt').read()))
"
```

## Orchestrators

`orchestrator/local_orchestrator` and `orchestrator/a2a_orchestrator` each
compose all three agents into one — see `orchestrator/README.md` for how
they differ and how to run each (the A2A one needs the three agents' A2A
servers running first, see below).

## Running an agent over A2A

Each agent can also be served over HTTP via [A2A](https://a2a.dev/) instead
of the ADK CLI, using `google.adk.a2a.utils.agent_to_a2a.to_a2a` (see each
agent's `a2a_server.py`):

```bash
uv run uvicorn agents.transcript_cleaner.a2a_server:a2a_app --port 8001
uv run uvicorn agents.decision_extractor.a2a_server:a2a_app --port 8002
uv run uvicorn agents.action_item_extractor.a2a_server:a2a_app --port 8003
```

Each serves its auto-generated agent card at `/.well-known/agent-card.json`,
e.g. `curl http://localhost:8001/.well-known/agent-card.json`.

## Logging

Every tool call and LLM request is logged (`common/logging_config.py`) in
`<time> - <loglevel> - <filename> - <message>` format, printed straight to
the console. Level is controlled by `LOG_LEVEL` in `.env` (default `INFO`).
This works the same whether you're running standalone or via `adk run` —
logging attaches its own console handler rather than relying on
`logging.basicConfig()`, which would otherwise get silently ignored since
`adk` configures the root logger first.

`adk run` additionally writes everything (its own logs plus ours, since ours
still propagate up) to a per-run log file — path printed at startup
(`Log setup complete: ...`), also reachable via `tail -F` on the
`agent.latest.log` pointer in the same directory.
