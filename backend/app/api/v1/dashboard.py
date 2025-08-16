from fastapi import APIRouter, Query
from typing import Optional
from typing import Literal
from datetime import datetime, timedelta

from app.models.pydantic_types import (
    TimeRange,
    SentimentPoint,
    ChannelMetric,
    KPI,
    HeatmapMatrix,
)
from app.services.dashboard_service import DashboardService

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


@router.get("/trend", response_model=list[SentimentPoint])
async def get_trend(time_range: TimeRange = Query("week", alias="range"), channel_ids: Optional[str] = Query(None)) -> list[SentimentPoint]:
    svc = DashboardService()
    channel_list = [c.strip() for c in channel_ids.split(",") if c.strip()] if channel_ids else None
    return await svc.compute_trend(time_range=time_range, channel_ids=channel_list)


@router.get("/channels", response_model=list[ChannelMetric])
async def get_channel_metrics(time_range: TimeRange = Query("week", alias="range"), channel_ids: Optional[str] = Query(None)) -> list[ChannelMetric]:
    svc = DashboardService()
    channel_list = [c.strip() for c in channel_ids.split(",") if c.strip()] if channel_ids else None
    return await svc.compute_channel_metrics(time_range=time_range, channel_ids=channel_list)


@router.get("/kpi", response_model=KPI)
async def get_dashboard_kpi(time_range: TimeRange = Query("week", alias="range"), channel_ids: Optional[str] = Query(None)) -> KPI:
    svc = DashboardService()
    channel_list = [c.strip() for c in channel_ids.split(",") if c.strip()] if channel_ids else None
    return await svc.compute_kpi(time_range=time_range, channel_ids=channel_list)


@router.get("/burnout-series")
async def get_burnout_series(
    time_range: TimeRange = Query("week", alias="range"),
    group: Literal["channels", "team", "person"] = Query("channels"),
    channel_ids: Optional[str] = Query(None),
) -> dict[str, object]:
    svc = DashboardService()
    channel_list = [c.strip() for c in channel_ids.split(",") if c.strip()] if channel_ids else None
    return await svc.compute_burnout_series(time_range=time_range, group=group, channel_ids=channel_list)


@router.get("/heatmap", response_model=HeatmapMatrix)
async def get_heatmap(
    grouping: Literal["channels", "teams", "people"] = Query("channels"),
    metric: Literal["sentiment", "messages", "threads"] = Query("sentiment"),
    time_range: TimeRange = Query("week", alias="range"),
    channel_ids: Optional[str] = Query(None),
) -> HeatmapMatrix:
    svc = DashboardService()
    channel_list = [c.strip() for c in channel_ids.split(",") if c.strip()] if channel_ids else None
    return await svc.compute_heatmap(grouping=grouping, metric=metric, time_range=time_range, channel_ids=channel_list)
