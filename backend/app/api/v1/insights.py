from fastapi import APIRouter, Query

from app.models.pydantic_types import Insight, TimeRange, LLMAnalyzeMessagesRequest, LLMAnalysisSummary
from app.services.anthropic_service import AnthropicService
from app.services.insights_service import InsightsService

router = APIRouter(prefix="/insights", tags=["insights"])


@router.get("/teams", response_model=list[Insight])
async def get_team_insights(time_range: TimeRange = Query("week", alias="range"), limit: int = Query(5, ge=1, le=10)) -> list[Insight]:
    svc = InsightsService()
    insights = await svc.generate_team_insights(time_range=time_range, limit=limit)
    # Ensure we never return more than requested
    return insights[:limit]


@router.post("/analyze", response_model=LLMAnalysisSummary)
async def analyze_messages(payload: LLMAnalyzeMessagesRequest) -> LLMAnalysisSummary:
    service = AnthropicService()
    return await service.analyze_slack_messages(payload.messages)
