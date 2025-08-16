from __future__ import annotations

from datetime import datetime, timedelta
from typing import Literal, Optional
import logging

from app.models.pydantic_types import (
    BurnoutPoint,
    ChannelMetric,
    HeatmapMatrix,
    KPI,
    RiskLevel,
    SentimentPoint,
    SlackMessage,
    TimeRange,
)
from app.services.slack_service import SlackService
from app.services.anthropic_service import AnthropicService


class DashboardService:
    def __init__(self) -> None:
        self.slack = SlackService()
        self.anthropic = AnthropicService()

    @staticmethod
    def _oldest_ts_for_range(time_range: TimeRange) -> str:
        now = int(datetime.utcnow().timestamp())
        days = 7 if time_range == "week" else 30 if time_range == "month" else 90 if time_range == "quarter" else 365
        return str(now - days * 24 * 60 * 60)

    async def _fetch_recent_messages(self, *, channel_ids: Optional[list[str]] = None, oldest: Optional[str] = None) -> dict[str, list[SlackMessage]]:
        channels = channel_ids
        if not channels:
            selected = await self.slack.get_selected_channels()
            if selected.channels:
                channels = [c.id for c in selected.channels]
            else:
                channels = [c.id for c in (await self.slack.list_channels())]
        results: dict[str, list[SlackMessage]] = {}
        for cid in channels:
            resp = await self.slack.get_channel_messages(channel_id=cid, oldest=oldest, limit=200)
            results[cid] = resp.messages
        return results

    async def compute_kpi(self, *, time_range: TimeRange) -> KPI:
        oldest = self._oldest_ts_for_range(time_range)
        logging.getLogger(__name__).info("dashboard: computing KPI for range=%s oldest=%s", time_range, oldest)
        by_channel = await self._fetch_recent_messages(oldest=oldest)
        logging.getLogger(__name__).debug("dashboard: fetched messages for %d channels", len(by_channel))
        # Aggregate sentiment via LLM per channel and overall
        channel_levels: list[RiskLevel] = []
        sentiments: list[float] = []
        for cid, msgs in by_channel.items():
            if not msgs:
                continue
            logging.getLogger(__name__).debug("dashboard: analyzing channel=%s messages=%d", cid, len(msgs))
            try:
                analysis = await self.anthropic.analyze_slack_messages(msgs)
                sentiments.append(analysis.overallSentiment)
                channel_levels.append(analysis.burnoutRiskLevel)
            except Exception as exc:  # pragma: no cover
                logging.getLogger(__name__).error("dashboard: anthropic error for channel=%s: %s", cid, exc)
        avg = 0.0 if not sentiments else sum(sentiments) / max(1, len(sentiments))
        burnout = len([lvl for lvl in channel_levels if lvl == "High"])  # type: ignore[comparison-overlap]
        return KPI(avgSentiment=round(avg, 2), burnoutRiskCount=burnout, monitoredChannels=len(by_channel))

    async def compute_channel_metrics(self, *, time_range: TimeRange) -> list[ChannelMetric]:
        oldest = self._oldest_ts_for_range(time_range)
        logging.getLogger(__name__).info("dashboard: computing channel metrics range=%s oldest=%s", time_range, oldest)
        by_channel = await self._fetch_recent_messages(oldest=oldest)
        # Need names
        channel_name_map = {c.id: c.name for c in (await self.slack.list_channels())}
        out: list[ChannelMetric] = []
        for cid, msgs in by_channel.items():
            name = channel_name_map.get(cid, cid)
            logging.getLogger(__name__).debug("dashboard: channel=%s name=%s messages=%d", cid, name, len(msgs))
            analysis = None
            if msgs:
                try:
                    analysis = await self.anthropic.analyze_slack_messages(msgs)
                except Exception as exc:  # pragma: no cover
                    logging.getLogger(__name__).error("dashboard: anthropic error for channel=%s: %s", cid, exc)
            avg_sent = analysis.overallSentiment if analysis else 0.0
            risk = analysis.burnoutRiskLevel if analysis else "Low"
            threads = max(0, len(msgs) // 5)
            last_ts = msgs[0].ts if msgs else str(int(datetime.utcnow().timestamp()))
            last_iso = datetime.utcfromtimestamp(int(float(last_ts))).isoformat()
            out.append(
                ChannelMetric(
                    id=cid,
                    name=name,
                    avgSentiment=round(avg_sent, 2),
                    messages=len(msgs),
                    threads=threads,
                    lastActivity=last_iso,
                    risk=risk,
                )
            )
        return out

    async def compute_trend(self, *, time_range: TimeRange) -> list[SentimentPoint]:
        # Build buckets by day/week/month and analyze per bucket
        step_days = 1 if time_range in ("week", "month") else (7 if time_range == "quarter" else 30)
        steps = 7 if time_range == "week" else 30 if time_range == "month" else 12
        points: list[SentimentPoint] = []
        now = datetime.utcnow()
        logging.getLogger(__name__).info(
            "dashboard: computing trend range=%s steps=%d step_days=%d",
            time_range,
            steps,
            step_days,
        )
        for i in range(steps - 1, -1, -1):
            start = now - timedelta(days=(i + 1) * step_days)
            end = now - timedelta(days=i * step_days)
            oldest = str(int(start.timestamp()))
            by_channel = await self._fetch_recent_messages(oldest=oldest)
            logging.getLogger(__name__).debug(
                "dashboard: trend bucket %d: oldest=%s channels=%d",
                i,
                oldest,
                len(by_channel),
            )
            # Flatten messages in window (Slack API call already filters oldest; we could also filter latest if provided)
            msgs = [m for msgs in by_channel.values() for m in msgs]
            logging.getLogger(__name__).debug(
                "dashboard: trend bucket %d message_count=%d", i, len(msgs)
            )
            if msgs:
                try:
                    analysis = await self.anthropic.analyze_slack_messages(msgs)
                    avg_s = analysis.overallSentiment
                    count = len(msgs)
                except Exception as exc:  # pragma: no cover
                    logging.getLogger(__name__).error(
                        "dashboard: anthropic error in trend bucket %d: %s", i, exc
                    )
                    avg_s = 0.0
                    count = len(msgs)
            else:
                avg_s = 0.0
                count = 0
            label = (
                end.strftime("%a")
                if time_range == "week"
                else str(end.day)
                if time_range == "month"
                else end.strftime("%b")
            )
            points.append(
                SentimentPoint(
                    date=end.strftime("%Y-%m-%d"),
                    label=label,
                    avgSentiment=round(avg_s, 2),
                    messageCount=count,
                )
            )
        return points

    async def compute_burnout_series(self, *, time_range: TimeRange, group: Literal["team", "person"]) -> dict[str, object]:
        # For MVP, reuse trend bucketization and sample warnings per group label as proxy
        # TODO: When users and teams are mapped, aggregate by real teams/people
        entities = ["Eng", "Design", "Support", "Product"] if group == "team" else ["Alice", "Bob", "Carol", "Diego", "Eve"]
        steps = 7 if time_range == "week" else 30 if time_range == "month" else 12
        step_days = 1 if time_range in ("week", "month") else (7 if time_range == "quarter" else 30)
        series: dict[str, list[BurnoutPoint]] = {}
        for idx, name in enumerate(entities):
            arr: list[BurnoutPoint] = []
            for i in range(steps - 1, -1, -1):
                end = datetime.utcnow() - timedelta(days=i * step_days)
                label = end.strftime("%a") if time_range == "week" else (str(end.day) if time_range == "month" else end.strftime("%b"))
                # Very rough proxy using idx/i to vary values 0..2
                arr.append(BurnoutPoint(label=label, value=((i + 1) * (idx + 2) * 97) % 3))
            series[name] = arr
        return {"label": "Teams" if group == "team" else "People", "series": series}

    async def compute_heatmap(self, *, grouping: Literal["channels", "teams", "people"], metric: Literal["sentiment", "messages", "threads"], time_range: TimeRange) -> HeatmapMatrix:
        # MVP: channels sentiment from LLM, teams/people placeholders similar to frontend mocks
        if grouping == "channels":
            channels = await self.slack.list_channels()
            rows = [c.name for c in channels][:8]
        elif grouping == "teams":
            rows = ["Eng", "Design", "Support", "Product"]
        else:
            rows = ["Alice", "Bob", "Carol", "Diego", "Eve"]

        # Build column labels as in frontend
        now = datetime.utcnow()
        if time_range == "week":
            cols = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
        elif time_range == "month":
            cols = ["1–7", "8–14", "15–21", "22–28", "29–31"]
        elif time_range == "quarter":
            cols = [(now - timedelta(weeks=w*4)).strftime("%b") for w in range(8, -1, -4)]  # 3 months
        else:
            cols = [(now.replace(day=1) - timedelta(days=30*i)).strftime("%b") for i in range(11, -1, -1)]

        # For MVP, fill values with basic placeholders; a later pass can compute real per-cell metrics
        values: list[list[float]] = []
        for ri, _ in enumerate(rows):
            row: list[float] = []
            for ci, _ in enumerate(cols):
                seed = (ri + 1) * (ci + 2) * 137
                if metric == "sentiment":
                    val = (((seed % 1000) / 1000) * 2 - 1) * 0.9
                else:
                    val = (seed % 100) / 100
                row.append(float(val))
            values.append(row)
        return HeatmapMatrix(rows=rows, cols=cols, values=values)


