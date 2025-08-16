from __future__ import annotations

from typing import Iterable, List, Dict, Tuple
from datetime import datetime, timezone, timedelta

from app.models.pydantic_types import (
    SlackChannel,
    SlackThread,
    SlackMessage,
    ChannelMetric,
    KPI,
    SentimentPoint,
    BurnoutPoint,
    RiskLevel,
    TimeRange,
    EntityTotalMetric,
    Perspective,
    HeatmapMatrix,
)


def _parse_ts_to_iso(ts_str: str) -> str:
    try:
        # Slack ts is epoch seconds as string
        sec = int(float(ts_str))
        dt = datetime.fromtimestamp(sec, tz=timezone.utc)
        return dt.isoformat()
    except Exception:
        return datetime.now(tz=timezone.utc).isoformat()


def _risk_from_sentiment(value: float) -> RiskLevel:
    if value < -0.2:
        return "High"
    if value < 0.2:
        return "Medium"
    return "Low"


# ----------------------------- Dashboard metrics -----------------------------

def compute_channel_metrics(channels: Iterable[SlackChannel]) -> List[ChannelMetric]:
    items: List[ChannelMetric] = []
    for ch in channels:
        threads: List[SlackThread] = ch.threads or []
        messages: List[SlackMessage] = [m for th in threads for m in th.messages]
        avg_sent = 0.0
        sent_vals = [m.sentiment for m in messages if m.sentiment is not None]
        if sent_vals:
            avg_sent = sum(sent_vals) / len(sent_vals)
        last_ts = None
        if threads:
            last_ts = max((int(float(th.lastActivityTs)) for th in threads), default=None)
        last_iso = _parse_ts_to_iso(str(last_ts)) if last_ts is not None else datetime.now(tz=timezone.utc).isoformat()
        items.append(
            ChannelMetric(
                id=ch.id,
                name=ch.name,
                avgSentiment=round(avg_sent, 2),
                messages=len(messages),
                threads=len(threads),
                lastActivity=last_iso,
                risk=_risk_from_sentiment(avg_sent),
            )
        )
    return items


def compute_kpi(channel_metrics: Iterable[ChannelMetric]) -> KPI:
    cms = list(channel_metrics)
    if not cms:
        return KPI(avgSentiment=0.0, burnoutRiskCount=0, monitoredChannels=0)
    avg = sum(c.avgSentiment for c in cms) / len(cms)
    burnout = sum(1 for c in cms if c.risk == "High")
    return KPI(avgSentiment=round(avg, 2), burnoutRiskCount=burnout, monitoredChannels=len(cms))


def compute_sentiment_trend(threads: Iterable[SlackThread], range: TimeRange = "week") -> List[SentimentPoint]:
    # Aggregate by day/week/month depending on range
    now = datetime.now(tz=timezone.utc)
    points: List[SentimentPoint] = []
    if range == "week":
        steps = 7
        delta = timedelta(days=1)
    elif range == "month":
        steps = 30
        delta = timedelta(days=1)
    elif range == "quarter":
        steps = 12
        delta = timedelta(days=7)
    else:
        steps = 12
        delta = timedelta(days=30)

    # Build buckets from oldest to newest
    bucket_bounds: List[Tuple[datetime, datetime]] = []
    start = now - delta * (steps - 1)
    for i in range(steps):
        b_start = start + i * delta
        b_end = b_start + delta
        bucket_bounds.append((b_start, b_end))

    # Flatten messages with datetime
    messages: List[SlackMessage] = [m for th in threads for m in th.messages]
    msg_with_dt: List[Tuple[datetime, SlackMessage]] = []
    for m in messages:
        try:
            dt = datetime.fromtimestamp(int(float(m.ts)), tz=timezone.utc)
        except Exception:
            dt = now
        msg_with_dt.append((dt, m))

    # Aggregate per bucket
    for b_start, b_end in bucket_bounds:
        bucket_msgs = [m for (dt, m) in msg_with_dt if b_start <= dt < b_end]
        avg = 0.0
        count = len(bucket_msgs)
        sents = [m.sentiment for m in bucket_msgs if m.sentiment is not None]
        if sents:
            avg = sum(s for s in sents if s is not None) / len(sents)
        label = (
            b_start.strftime("%a")
            if range in ("week", "month")
            else b_start.strftime("%b")
        )
        points.append(
            SentimentPoint(
                date=b_start.date().isoformat(),
                label=label if range == "week" else (str(b_start.day) if range == "month" else b_start.strftime("%b")),
                avgSentiment=round(avg, 2),
                messageCount=count,
            )
        )
    return points


# ------------------------------- Metrics totals -------------------------------

def compute_entity_totals_from_channels(
    channels: Iterable[SlackChannel],
    perspective: Perspective = "channel",
    range: TimeRange = "week",
) -> List[EntityTotalMetric]:
    # The range can scale numbers, but real impl would filter time window. Here we use simple scaling similar to frontend mock.
    def scale_for_range(r: TimeRange) -> int:
        return 1 if r == "week" else 4 if r == "month" else 12 if r == "quarter" else 48

    scale = scale_for_range(range)
    channels_list = list(channels)

    if perspective == "channel":
        out: List[EntityTotalMetric] = []
        for idx, ch in enumerate(channels_list):
            threads = ch.threads or []
            messages = [m for th in threads for m in th.messages]
            responses = sum(max(0, len(th.messages) - 1) for th in threads)  # replies under root
            emojis = sum(len(m.reactions or []) for m in messages)
            out.append(
                EntityTotalMetric(
                    id=ch.id,
                    name=f"#{ch.name}",
                    messages=len(messages) * scale,
                    threads=len(threads),
                    responses=responses,
                    emojis=emojis,
                )
            )
        return out

    # Build user index and team mapping placeholder (could come from DB/config)
    user_display: Dict[str, str] = {}
    for ch in channels_list:
        for th in ch.threads or []:
            for m in th.messages:
                user_display[m.userId] = user_display.get(m.userId, m.userId)

    if perspective == "employee":
        counts: Dict[str, int] = {}
        responses: Dict[str, int] = {}
        emojis: Dict[str, int] = {}
        for ch in channels_list:
            for th in ch.threads or []:
                for i, m in enumerate(th.messages):
                    counts[m.userId] = counts.get(m.userId, 0) + 1
                    if i > 0:
                        responses[m.userId] = responses.get(m.userId, 0) + 1
                    emojis[m.userId] = emojis.get(m.userId, 0) + len(m.reactions or [])
        # approximate threads per user as number of roots authored
        threads_by_user: Dict[str, int] = {}
        for ch in channels_list:
            for th in ch.threads or []:
                if th.messages:
                    root = th.messages[0]
                    threads_by_user[root.userId] = threads_by_user.get(root.userId, 0) + 1
        return [
            EntityTotalMetric(
                id=user_id,
                name=user_display.get(user_id, user_id),
                messages=(counts.get(user_id, 0) * scale),
                threads=threads_by_user.get(user_id, 0),
                responses=responses.get(user_id, 0),
                emojis=emojis.get(user_id, 0),
            )
            for user_id in sorted(user_display.keys())
        ]

    # team perspective (placeholder grouping by first char of userId)
    team_of_user = lambda uid: {
        "U0": "Eng",
        "U1": "Eng",
        "U2": "Design",
        "U3": "Support",
    }.get(uid[:2], "Product")

    team_counts: Dict[str, int] = {}
    team_threads: Dict[str, int] = {}
    team_responses: Dict[str, int] = {}
    team_emojis: Dict[str, int] = {}
    for ch in channels_list:
        for th in ch.threads or []:
            if th.messages:
                root = th.messages[0]
                team = team_of_user(root.userId)
                team_threads[team] = team_threads.get(team, 0) + 1
            for i, m in enumerate(th.messages):
                team = team_of_user(m.userId)
                team_counts[team] = team_counts.get(team, 0) + 1
                if i > 0:
                    team_responses[team] = team_responses.get(team, 0) + 1
                team_emojis[team] = team_emojis.get(team, 0) + len(m.reactions or [])

    teams = sorted(team_counts.keys())
    return [
        EntityTotalMetric(
            id=f"team-{t.lower()}",
            name=t,
            messages=team_counts.get(t, 0) * scale,
            threads=team_threads.get(t, 0),
            responses=team_responses.get(t, 0),
            emojis=team_emojis.get(t, 0),
        )
        for t in teams
    ]


# ------------------------------- Heatmap matrix ------------------------------

def compute_heatmap_matrix(
    grouping: str,
    metric: str,
    range: TimeRange = "week",
) -> HeatmapMatrix:
    # This is a placeholder that mirrors the frontend mock ranges and labels
    def month_abbr(d: datetime) -> str:
        return d.strftime("%b")

    if grouping == "channels":
        rows = ["general", "eng-announcements", "random", "product", "support"]
    elif grouping == "teams":
        rows = ["Eng", "Design", "Support", "Product"]
    else:
        rows = ["Alice", "Bob", "Carol", "Diego", "Eve"]

    if range == "week":
        cols = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
    elif range == "month":
        cols = ["1–7", "8–14", "15–21", "22–28", "29–31"]
    elif range == "quarter":
        now = datetime.now(tz=timezone.utc)
        cols = [month_abbr(now - timedelta(weeks=8)), month_abbr(now - timedelta(weeks=4)), month_abbr(now)]
    else:
        now = datetime.now(tz=timezone.utc)
        cols = [month_abbr(now - timedelta(weeks=4 * i)) for i in range(11, -1, -1)]

    values: List[List[float]] = []
    for ri in range(len(rows)):
        row_vals: List[float] = []
        for ci in range(len(cols)):
            seed = (ri + 1) * (ci + 2) * 137
            if metric == "sentiment":
                row_vals.append((((seed % 1000) / 1000) * 2 - 1) * 0.9)
            else:
                row_vals.append((seed % 100) / 100)
        values.append(row_vals)

    return HeatmapMatrix(rows=rows, cols=cols, values=values)