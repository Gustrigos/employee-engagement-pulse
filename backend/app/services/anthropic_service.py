from __future__ import annotations

import json
import logging
from typing import Any, Dict, Optional, Type, TypeVar

try:
	from anthropic import Anthropic, APIConnectionError, APIStatusError
except Exception:  # pragma: no cover - allow import without SDK installed
	Anthropic = None  # type: ignore[assignment]
	APIConnectionError = Exception  # type: ignore[assignment]
	APIStatusError = Exception  # type: ignore[assignment]

from pydantic import BaseModel, ValidationError

from app.core.config import settings

logger = logging.getLogger(__name__)

T = TypeVar("T", bound=BaseModel)


MODEL_ALIASES: dict[str, str] = {
	# Friendly aliases to concrete Anthropic model IDs
	"sonnet": "claude-3-5-sonnet-20240620",
	"opus": "claude-3-opus-20240229",
	"haiku": "claude-3-haiku-20240307",
}


class AnthropicServiceError(Exception):
	pass


def _get_client() -> Anthropic:  # type: ignore[name-defined]
	if not settings.anthropic_api_key:
		raise AnthropicServiceError("ANTHROPIC_API_KEY is not configured")
	if Anthropic is None:  # type: ignore[truthy-bool]
		raise AnthropicServiceError(
			"anthropic SDK is not installed. Add it to dependencies and install."
		)
	return Anthropic(api_key=settings.anthropic_api_key)  # type: ignore[operator]


def _resolve_model(model: Optional[str]) -> str:
	candidate = model or settings.anthropic_model
	return MODEL_ALIASES.get(candidate.lower(), candidate)


def call_llm_structured(
	prompt: str,
	response_model: Type[T],
	*,
	model: Optional[str] = None,
	max_tokens: Optional[int] = None,
	temperature: float = 0,
	system: Optional[str] = None,
) -> T:
	"""
	Call Anthropic Messages API and parse a JSON structured response into the given Pydantic model.

	- Uses response_format={"type":"json_object"} so the model returns a single JSON object.
	- Validates the response against the provided Pydantic model.
	- Supports friendly model aliases via MODEL_ALIASES (e.g., "sonnet", "opus", "haiku").
	"""
	client = _get_client()
	chosen_model = _resolve_model(model)
	chosen_max_tokens = max_tokens or settings.anthropic_max_tokens

	try:
		messages = [
			{"role": "user", "content": prompt},
		]

		resp = client.messages.create(
			model=chosen_model,
			max_tokens=chosen_max_tokens,
			messages=messages,
			temperature=temperature,
			response_format={"type": "json_object"},
			system=system,
		)
	except (APIConnectionError, APIStatusError) as e:  # type: ignore[misc]
		logger.exception("Anthropic API error: %s", e)
		raise AnthropicServiceError(str(e)) from e

	text_parts: list[str] = []
	for block in getattr(resp, "content", []) or []:
		if getattr(block, "type", None) == "text":
			text_parts.append(getattr(block, "text", ""))

	if not text_parts:
		raise AnthropicServiceError("Empty response from model")

	raw_text = "\n".join(part for part in text_parts if part)

	try:
		data: Dict[str, Any] = json.loads(raw_text)
	except json.JSONDecodeError as e:
		logger.error("Failed to parse JSON from model output: %s", raw_text)
		raise AnthropicServiceError("Model did not return valid JSON") from e

	try:
		return response_model.model_validate(data)
	except ValidationError as e:
		logger.error("Response validation failed: %s", e)
		raise AnthropicServiceError("Response did not match expected schema") from e