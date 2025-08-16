from __future__ import annotations

import json
from typing import Any, Optional, Type, TypeVar
import logging

import httpx

from app.core.config import get_settings
from app.models.pydantic_types import (
    LLMAnalysisSummary,
    LLMMessageAnalysisItem,
    RiskLevel,
    SlackMessage,
)


TModel = TypeVar("TModel")


class AnthropicService:
    """Lightweight client wrapper around Anthropic Messages API.

    - Supports model selection per-call (defaults come from settings)
    - Encourages structured outputs by asking the model to return JSON only
    - Validates responses using Pydantic models (caller supplies the schema model)

    For development without an API key, returns a simple heuristic result
    for the "analyze_slack_messages" method so the app can function in demo mode.
    """

    def __init__(self) -> None:
        self.settings = get_settings()

    async def _http(self) -> httpx.AsyncClient:
        headers = {
            "anthropic-version": "2023-06-01",
        }
        if self.settings.anthropic_api_key:
            headers["x-api-key"] = self.settings.anthropic_api_key
        return httpx.AsyncClient(base_url="https://api.anthropic.com", timeout=60, headers=headers)

    @staticmethod
    def _extract_text_from_response(data: dict[str, Any]) -> str:
        """Extracts the model text from Anthropic's Messages API response structure."""
        content = data.get("content")
        if isinstance(content, list) and content:
            first = content[0] or {}
            if isinstance(first, dict):
                return str(first.get("text", ""))
        # Some SDKs flatten to "text"
        return str(data.get("text", ""))

    @staticmethod
    def _coerce_json(text: str) -> Any:
        """Try to parse JSON; if it fails, attempt to extract the largest JSON object substring."""
        text = (text or "").strip()
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            # Try to find a JSON object within the text
            start = text.find("{")
            end = text.rfind("}")
            if start != -1 and end != -1 and end > start:
                candidate = text[start : end + 1]
                try:
                    return json.loads(candidate)
                except json.JSONDecodeError:
                    pass
            # Try array form as fallback
            start = text.find("[")
            end = text.rfind("]")
            if start != -1 and end != -1 and end > start:
                candidate = text[start : end + 1]
                return json.loads(candidate)
            raise

    async def generate_structured(
        self,
        *,
        prompt: str,
        schema_model: Type[TModel],
        model: Optional[str] = None,
        temperature: Optional[float] = None,
        system: Optional[str] = None,
        max_tokens: Optional[int] = None,
    ) -> TModel:
        """Call Anthropic and return JSON parsed into the provided Pydantic model type.

        Parameters
        - prompt: The user prompt/instructions
        - schema_model: Pydantic model class for validating the structured output
        - model, temperature, system, max_tokens: optional overrides
        """

        selected_model = model or self.settings.anthropic_default_model
        selected_temp = (
            self.settings.anthropic_default_temperature
            if temperature is None
            else float(temperature)
        )
        selected_max_tokens = max_tokens or self.settings.anthropic_max_tokens

        # Strong JSON-only instruction to increase parse reliability
        json_instruction = (
            "Return ONLY valid JSON that strictly matches the provided JSON schema. "
            "Do not include any extra commentary, code fences, or explanations."
        )
        if system:
            system_text = f"{system}\n\n{json_instruction}"
        else:
            system_text = json_instruction

        schema = schema_model.model_json_schema()
        user_text = (
            "You must produce output that validates against this JSON schema.\n"\
            f"JSON Schema: {json.dumps(schema)}\n\n"\
            f"Task: {prompt}"
        )

        # If no API key, provide explicit guidance
        if not self.settings.anthropic_api_key:
            raise RuntimeError(
                "Anthropic API key is not configured. Set ANTHROPIC_API_KEY in the backend environment."
            )

        payload = {
            "model": selected_model,
            "max_tokens": int(selected_max_tokens),
            "temperature": float(selected_temp),
            "system": system_text,
            "messages": [
                {"role": "user", "content": [{"type": "text", "text": user_text}]}
            ],
        }

        logging.getLogger(__name__).debug(
            "anthropic: request model=%s temp=%s max_tokens=%s",
            selected_model,
            selected_temp,
            selected_max_tokens,
        )
        async with await self._http() as http:
            resp = await http.post("/v1/messages", json=payload)
            logging.getLogger(__name__).debug("anthropic: status=%s", resp.status_code)
            resp.raise_for_status()
            data = resp.json()
        logging.getLogger(__name__).debug("anthropic: raw response keys=%s", list(data.keys()))

        text = self._extract_text_from_response(data)
        parsed = self._coerce_json(text)
        # Validate using the provided Pydantic model class
        return schema_model.model_validate(parsed)  # type: ignore[return-value]

    # ===== Convenience domain method for Slack messages =====
    async def analyze_slack_messages(
        self,
        messages: list[SlackMessage],
        *,
        model: Optional[str] = None,
        temperature: Optional[float] = None,
    ) -> LLMAnalysisSummary:
        """Analyze Slack messages for sentiment and burnout risk using the LLM.

        Falls back to a simple heuristic if Anthropic is not configured.
        """

        logging.getLogger(__name__).info("anthropic: analyzing %d messages", len(messages))
        if not self.settings.anthropic_api_key:
            logging.getLogger(__name__).warning("anthropic: API key not configured; using heuristic analysis")
            return self._heuristic_analyze(messages)

        # Trim the number of messages to keep prompts short
        trimmed: list[SlackMessage] = messages[-100:]
        serializable: list[dict[str, Any]] = [
            {"id": m.id, "userId": m.userId, "text": m.text, "ts": m.ts} for m in trimmed
        ]

        # High-level guidance embedded in system prompt. The concrete task is in the user message.
        system = (
            "Be precise and consistent. "
            "Use a wide range of sentiment values (not just -1/0/1). "
            "Classify burnout risk as High only for strong, repeated stress signals."
        )

        logging.getLogger(__name__).debug(
            "anthropic: invoking structured analysis for %d messages", len(serializable)
        )
        try:
            result = await self.generate_structured(
                prompt=f"Messages: {json.dumps(serializable)}",
                schema_model=LLMAnalysisSummary,
                model=model,
                temperature=temperature,
                system=system,
            )
        except Exception as exc:
            logging.getLogger(__name__).exception("anthropic: structured call failed, using heuristic: %s", exc)
            return self._heuristic_analyze(messages)
        logging.getLogger(__name__).info(
            "anthropic: analysis overall_sentiment=%.3f burnout=%s items=%d",
            result.overallSentiment,
            result.burnoutRiskLevel,
            len(result.items),
        )
        return result

    # ===== Heuristic fallback =====
    @staticmethod
    def _heuristic_analyze(messages: list[SlackMessage]) -> LLMAnalysisSummary:
        positive_words = {
            "great",
            "good",
            "excellent",
            "awesome",
            "thanks",
            "thank you",
            "love",
            "nice",
            "well done",
            "amazing",
            "happy",
            "win",
            "ship",
        }
        negative_words = {
            "bad",
            "terrible",
            "awful",
            "hate",
            "stuck",
            "blocked",
            "broken",
            "late",
            "fail",
            "risky",
            "stress",
            "stressful",
            "overworked",
            "burnout",
            "exhausted",
            "tired",
            "anxious",
            "deadline",
        }

        def score_sentiment(text: str) -> float:
            t = text.lower()
            pos = sum(1 for w in positive_words if w in t)
            neg = sum(1 for w in negative_words if w in t)
            raw = pos - neg
            if raw == 0:
                return 0.0
            # squash into [-1, 1]
            return max(-1.0, min(1.0, raw / 5.0))

        def burnout_level(text: str) -> RiskLevel:
            t = text.lower()
            high_markers = ["burnout", "overworked", "exhausted"]
            medium_markers = ["stress", "deadline", "late", "tired", "anxious"]
            if any(m in t for m in high_markers):
                return "High"
            if any(m in t for m in medium_markers):
                return "Medium"
            return "Low"

        items: list[LLMMessageAnalysisItem] = []
        sentiments: list[float] = []
        for m in messages[-100:]:
            s = score_sentiment(m.text or "")
            sentiments.append(s)
            items.append(
                LLMMessageAnalysisItem(
                    messageId=m.id,
                    sentiment=s,
                    burnoutRisk=burnout_level(m.text or ""),
                    categories=None,
                    summary=None,
                )
            )
        overall = 0.0 if not sentiments else sum(sentiments) / max(1, len(sentiments))
        overall_level: RiskLevel
        if overall <= -0.4:
            overall_level = "High"
        elif overall <= -0.1:
            overall_level = "Medium"
        else:
            overall_level = "Low"
        return LLMAnalysisSummary(
            overallSentiment=overall,
            burnoutRiskLevel=overall_level,
            items=items,
        )


