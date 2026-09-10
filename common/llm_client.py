"""Shared OpenAI helper used directly by every agent's tool functions.

Kept independent of the ADK runtime on purpose: these functions are also the
future MCP tool implementations, so they must not depend on anything ADK-specific.
"""

import json
import os

from dotenv import load_dotenv
from openai import OpenAI

from common.logging_config import get_logger

load_dotenv()

logger = get_logger(__name__)

_client: OpenAI | None = None


def _get_client() -> OpenAI:
    global _client
    if _client is None:
        _client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])
    return _client


def get_model_name() -> str:
    """The OpenAI model name to use, shared by tool calls and each agent's root LLM."""
    return os.environ.get("OPENAI_MODEL", "gpt-4o-mini")


def call_llm(
    system_prompt: str,
    user_content: str,
    json_schema: dict | None = None,
) -> str | dict:
    """Run a single chat completion.

    Returns plain text, or a parsed dict when `json_schema` is given (uses
    OpenAI structured outputs so the result always matches the schema).
    """
    client = _get_client()
    model = get_model_name()

    kwargs = {}
    if json_schema is not None:
        kwargs["response_format"] = {
            "type": "json_schema",
            "json_schema": {
                "name": json_schema.get("title", "response"),
                "schema": json_schema,
                "strict": True,
            },
        }

    logger.info(
        "Calling OpenAI model=%s json_schema=%s input_chars=%d",
        model,
        json_schema.get("title") if json_schema else None,
        len(user_content),
    )
    try:
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_content},
            ],
            **kwargs,
        )
    except Exception:
        logger.exception("OpenAI call failed model=%s", model)
        raise

    content = response.choices[0].message.content
    logger.debug("OpenAI response received output_chars=%d", len(content or ""))

    if json_schema is not None:
        return json.loads(content)
    return content
