# agent-discovery

POC for an agent registry: agents register their capabilities, and an
orchestrator dynamically discovers and calls the right agent for a given
use case instead of hardcoding which agent handles what.

This repo currently implements the first slice of that: three standalone
[Google ADK](https://adk.dev/) agents that process noisy, speaker-diarized
meeting transcripts. Registry registration and the orchestrator (see
`registry/` and `orchestrator/`) are follow-up work.

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

You can also call a tool function directly for a quick sanity check without
going through the chat loop:

```bash
uv run python -c "
from agents.transcript_cleaner.tools import clean_transcript
print(clean_transcript(open('data/sample_transcript.txt').read()))
"
```
