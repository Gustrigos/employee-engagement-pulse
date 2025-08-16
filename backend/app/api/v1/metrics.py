from typing import Optional
from fastapi import APIRouter, Query

from app.models.pydantic_types import (
    EntityTotalMetric,
    EmojiStat,
    TimeRange,
    Perspective,
)
from app.services.metrics_service import MetricsService


router = APIRouter(prefix="/metrics", tags=["metrics"])


@router.get("/entity-totals", response_model=list[EntityTotalMetric])
async def entity_totals(
    perspective: Perspective = Query("channel"),
    time_range: TimeRange = Query("week", alias="range"),
    channel_ids: Optional[str] = Query(None, description="Comma-separated channel IDs to include"),
) -> list[EntityTotalMetric]:
    service = MetricsService()
    selected_channels = None
    if channel_ids:
        selected_channels = [c.strip() for c in channel_ids.split(",") if c.strip()]
    return await service.compute_entity_totals(time_range=time_range, perspective=perspective, channel_ids=selected_channels)


@router.get("/top-emojis", response_model=list[EmojiStat])
async def top_emojis(
    time_range: TimeRange = Query("week", alias="range"),
    limit: int = Query(10, ge=1, le=50),
    channel_ids: Optional[str] = Query(None),
) -> list[EmojiStat]:
    service = MetricsService()
    selected_channels = None
    if channel_ids:
        selected_channels = [c.strip() for c in channel_ids.split(",") if c.strip()]
    return await service.compute_top_emojis(time_range=time_range, limit=limit, channel_ids=selected_channels)


