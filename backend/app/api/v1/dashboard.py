from fastapi import APIRouter, Query
from typing import Literal
from datetime import datetime, timedelta

from app.models.pydantic_types import (
    TimeRange,
    SentimentPoint,
    ChannelMetric,
    KPI,
    BurnoutPoint,
    HeatmapMatrix,
)
from app.services.dashboard_service import DashboardService

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


@router.get("/trend", response_model=list[SentimentPoint])
async def get_trend(time_range: TimeRange = Query("week", alias="range")) -> list[SentimentPoint]:
    svc = DashboardService()
    return await svc.compute_trend(time_range=time_range)


@router.get("/channels", response_model=list[ChannelMetric])
async def get_channel_metrics(time_range: TimeRange = Query("week", alias="range")) -> list[ChannelMetric]:
    svc = DashboardService()
    return await svc.compute_channel_metrics(time_range=time_range)


@router.get("/kpi", response_model=KPI)
async def get_dashboard_kpi(time_range: TimeRange = Query("week", alias="range")) -> KPI:
    svc = DashboardService()
    return await svc.compute_kpi(time_range=time_range)


@router.get("/burnout-series")
async def get_burnout_series(
    time_range: TimeRange = Query("week", alias="range"),
    group: Literal["team", "person"] = Query("team"),
) -> dict[str, object]:
    svc = DashboardService()
    return await svc.compute_burnout_series(time_range=time_range, group=group)


@router.get("/heatmap", response_model=HeatmapMatrix)
async def get_heatmap(
    grouping: Literal["channels", "teams", "people"] = Query("channels"),
    metric: Literal["sentiment", "messages", "threads"] = Query("sentiment"),
    time_range: TimeRange = Query("week", alias="range"),
) -> HeatmapMatrix:
    svc = DashboardService()
    return await svc.compute_heatmap(grouping=grouping, metric=metric, time_range=time_range)
