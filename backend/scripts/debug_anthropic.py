from __future__ import annotations

import asyncio
import json
import os
from typing import Any

# Minimal, direct harness to exercise AnthropicService without FastAPI/uvicorn

from app.core.config import get_settings
from app.models.pydantic_types import SlackMessage
from app.services.anthropic_service import AnthropicService


def _print_heading(title: str) -> None:
    print("\n" + "=" * 80)
    print(title)
    print("=" * 80)


async def _run(messages: list[SlackMessage]) -> dict[str, Any]:
    svc = AnthropicService()
    out: dict[str, Any] = {}

    # Show whether API key is configured (masked)
    settings = get_settings()
    key = settings.anthropic_api_key or ""
    out["anthropic_key_present"] = bool(key)
    out["model"] = settings.anthropic_default_model
    out["max_tokens"] = settings.anthropic_max_tokens
    out["temperature"] = settings.anthropic_default_temperature

    try:
        result = await svc.analyze_slack_messages(messages)
        out["ok"] = True
        out["result"] = json.loads(result.model_dump_json())
    except Exception as exc:  # noqa: BLE001 (debug harness)
        out["ok"] = False
        out["error_type"] = type(exc).__name__
        out["error"] = str(exc)
    return out


def main() -> None:
    _print_heading("Anthropic Debug Harness")
    print(f"CWD: {os.getcwd()}")
    print(f"ENV LOG_LEVEL={os.getenv('LOG_LEVEL')} DEBUG_ANTHROPIC={os.getenv('DEBUG_ANTHROPIC')}\n")

    # Sample messages; adjust as needed
    sample_messages = [
        SlackMessage(id="m1", userId="U01", text="I am stressed about deadlines", ts="123"),
        SlackMessage(id="m2", userId="U02", text="The release went great!", ts="124"),
    ]

    data = asyncio.run(_run(sample_messages))
    _print_heading("Result")
    print(json.dumps(data, indent=2))


if __name__ == "__main__":
    main()


