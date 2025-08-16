from fastapi import APIRouter, Query
from typing import Literal
from datetime import datetime, timedelta

from app.models.pydantic_types import (
    TimeRange,
    SentimentPoint,
    ChannelMetric,
    KPI,
    BurnoutPoint,
)

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


@router.get("/trend", response_model=list[SentimentPoint])
async def get_trend(time_range: TimeRange = Query("week", alias="range")) -> list[SentimentPoint]:
    now = datetime.utcnow()
    if time_range == "week":
        steps, step_days = 7, 1
    elif time_range == "month":
        steps, step_days = 30, 1
    elif time_range == "quarter":
        steps, step_days = 12, 7
    else:
        steps, step_days = 12, 30

    points: list[SentimentPoint] = []
    for i in range(steps - 1, -1, -1):
        d = now - timedelta(days=i * step_days)
        seed = (i * 9301 + 49297) % 233280
        sentiment = ((seed / 233280) * 2 - 1) * 0.8
        messages = int(30 + (seed % 40))
        label = (
            d.strftime("%a")
            if time_range == "week"
            else str(d.day)
            if time_range == "month"
            else d.strftime("%b")
        )
        points.append(
            SentimentPoint(
                date=d.strftime("%Y-%m-%d"),
                label=label,
                avgSentiment=round(sentiment, 2),
                messageCount=messages,
            )
        )
    return points


@router.get("/channels", response_model=list[ChannelMetric])
async def get_channel_metrics() -> list[ChannelMetric]:
    channels = [
        {"id": "C-general", "name": "general"},
        {"id": "C-eng", "name": "eng-announcements"},
        {"id": "C-random", "name": "random"},
        {"id": "C-product", "name": "product"},
        {"id": "C-support", "name": "support"},
        {"id": "C-design", "name": "design"},
    ]
    result: list[ChannelMetric] = []
    for idx, c in enumerate(channels):
        seed = (idx * 1103515245 + 12345) % 2147483647
        sentiment = (((seed % 1000) / 1000) * 2 - 1) * 0.9
        messages = 50 + (seed % 150)
        threads = 5 + (seed % 20)
        days_ago = (seed % 14) + 1
        last = datetime.utcnow() - timedelta(days=days_ago)
        risk = "High" if sentiment < -0.2 else "Medium" if sentiment < 0.2 else "Low"
        result.append(
            ChannelMetric(
                id=c["id"],
                name=c["name"],
                avgSentiment=round(sentiment, 2),
                messages=messages,
                threads=threads,
                lastActivity=last.isoformat(),
                risk=risk,  # type: ignore[arg-type]
            )
        )
    return result


@router.get("/kpi", response_model=KPI)
async def get_dashboard_kpi() -> KPI:
    channels = await get_channel_metrics()
    avg = sum(c.avgSentiment for c in channels) / max(1, len(channels))
    burnout = len([c for c in channels if c.risk == "High"])  # type: ignore[comparison-overlap]
    return KPI(avgSentiment=round(avg, 2), burnoutRiskCount=burnout, monitoredChannels=len(channels))


@router.get("/burnout-series")
async def get_burnout_series(
    time_range: TimeRange = Query("week", alias="range"),
    group: Literal["team", "person"] = Query("team"),
) -> dict[str, object]:
    entities = ["Eng", "Design", "Support", "Product"] if group == "team" else [
        "Alice",
        "Bob",
        "Carol",
        "Diego",
        "Eve",
    ]
    steps = 7 if time_range == "week" else 30 if time_range == "month" else 12
    step_days = 1 if time_range in ("week", "month") else (7 if time_range == "quarter" else 30)
    series: dict[str, list[BurnoutPoint]] = {}

    for idx, name in enumerate(entities):
        arr: list[BurnoutPoint] = []
        for i in range(steps - 1, -1, -1):
            d = datetime.utcnow() - timedelta(days=i * step_days)
            seed = (i + 1) * (idx + 2) * 97
            label = d.strftime("%a") if time_range == "week" else (str(d.day) if time_range == "month" else d.strftime("%b"))
            arr.append(BurnoutPoint(label=label, value=seed % 3))
        series[name] = arr

    return {"label": "Teams" if group == "team" else "People", "series": series}
