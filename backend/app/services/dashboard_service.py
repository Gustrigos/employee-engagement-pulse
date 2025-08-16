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

    async def _fetch_recent_messages(self, *, channel_ids: Optional[list[str]] = None, oldest: Optional[str] = None, latest: Optional[str] = None) -> dict[str, list[SlackMessage]]:
        channels = channel_ids
        if not channels:
            selected = await self.slack.get_selected_channels()
            if selected.channels:
                channels = [c.id for c in selected.channels]
            else:
                # If not connected to Slack, fall back to demo channels; otherwise avoid fan-out
                if getattr(self.slack, "is_connected", lambda: False)():
                    channels = []
                else:
                    channels = [c.id for c in (await self.slack.list_channels())]
        results: dict[str, list[SlackMessage]] = {}
        for cid in channels:
            resp = await self.slack.get_channel_messages(channel_id=cid, oldest=oldest, latest=latest, limit=200)
            results[cid] = resp.messages
        return results

    async def compute_kpi(self, *, time_range: TimeRange, channel_ids: Optional[list[str]] = None) -> KPI:
        oldest = self._oldest_ts_for_range(time_range)
        logging.getLogger(__name__).info("dashboard: computing KPI for range=%s oldest=%s", time_range, oldest)
        by_channel = await self._fetch_recent_messages(channel_ids=channel_ids, oldest=oldest)
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
        burnout = len([lvl for lvl in channel_levels if lvl in ("Medium", "High")])  # type: ignore[comparison-overlap]
        return KPI(avgSentiment=round(avg, 2), burnoutRiskCount=burnout, monitoredChannels=len(by_channel))

    async def compute_channel_metrics(self, *, time_range: TimeRange, channel_ids: Optional[list[str]] = None) -> list[ChannelMetric]:
        oldest = self._oldest_ts_for_range(time_range)
        logging.getLogger(__name__).info("dashboard: computing channel metrics range=%s oldest=%s", time_range, oldest)
        by_channel = await self._fetch_recent_messages(channel_ids=channel_ids, oldest=oldest)
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

    async def compute_trend(self, *, time_range: TimeRange, channel_ids: Optional[list[str]] = None) -> list[SentimentPoint]:
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
            latest = str(int(end.timestamp()))
            by_channel = await self._fetch_recent_messages(channel_ids=channel_ids, oldest=oldest, latest=latest)
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

    async def compute_burnout_series(self, *, time_range: TimeRange, group: Literal["channels", "team", "person"] = "channels", channel_ids: Optional[list[str]] = None) -> dict[str, object]:
        # Channels-as-teams: show risk over time per selected channel
        steps = 7 if time_range == "week" else 30 if time_range == "month" else 12
        step_days = 1 if time_range in ("week", "month") else (7 if time_range == "quarter" else 30)
        selected = await self.slack.get_selected_channels()
        if channel_ids:
            # Filter to provided ids intersecting with selected list
            id_set = set(channel_ids)
            channels = [c for c in selected.channels if c.id in id_set] if selected.channels else []
        else:
            channels = selected.channels or []
        # If not connected, use demo channels
        if not channels:
            channels = await self.slack.list_channels()

        # Map id->name for labels
        name_map = {c.id: (c.name or c.id) for c in channels}
        series: dict[str, list[BurnoutPoint]] = {name_map[c.id]: [] for c in channels}

        now = datetime.utcnow()
        for i in range(steps - 1, -1, -1):
            start = now - timedelta(days=(i + 1) * step_days)
            end = now - timedelta(days=i * step_days)
            oldest = str(int(start.timestamp()))
            latest = str(int(end.timestamp()))
            label = (
                end.strftime("%a")
                if time_range == "week"
                else str(end.day)
                if time_range == "month"
                else end.strftime("%b")
            )
            for c in channels:
                msgs = (await self.slack.get_channel_messages(channel_id=c.id, oldest=oldest, latest=latest, limit=200)).messages
                if msgs:
                    try:
                        analysis = await self.anthropic.analyze_slack_messages(msgs)
                        lvl = analysis.burnoutRiskLevel
                        val = 2 if lvl == "High" else (1 if lvl == "Medium" else 0)
                    except Exception as exc:  # pragma: no cover
                        logging.getLogger(__name__).error("dashboard: anthropic error in burnout series for channel=%s: %s", c.id, exc)
                        val = 0
                else:
                    val = 0
                series[name_map[c.id]].append(BurnoutPoint(label=label, value=val))
        label = "Channels" if group in ("channels", "team") else "People"
        return {"label": label, "series": series}

    async def compute_heatmap(self, *, grouping: Literal["channels", "teams", "people"], metric: Literal["sentiment", "messages", "threads"], time_range: TimeRange, channel_ids: Optional[list[str]] = None) -> HeatmapMatrix:
        # Determine entities
        selected = await self.slack.get_selected_channels()
        channels = selected.channels or []
        if not channels:
            channels = await self.slack.list_channels()
        if channel_ids:
            channel_id_set = set(channel_ids)
            channels = [c for c in channels if c.id in channel_id_set]

        # Group mapping
        if grouping in ("channels", "teams"):
            # Treat teams as channels
            rows = [c.name for c in channels]
            # id mapping not currently needed
        else:
            # People: derive from selected channels' users
            users = await self.slack.list_users()
            # Default to all non-bot users; will filter per bucket
            rows = [u.displayName or u.username or u.id for u in users]
            user_id_map = { (u.displayName or u.username or u.id): u.id for u in users }

        # Build bucket boundaries and labels similar to trend
        step_days = 1 if time_range in ("week", "month") else (7 if time_range == "quarter" else 30)
        steps = 7 if time_range == "week" else 30 if time_range == "month" else 12
        now = datetime.utcnow()
        buckets: list[tuple[str, str, str]] = []  # (label, oldest, latest)
        for i in range(steps - 1, -1, -1):
            start = now - timedelta(days=(i + 1) * step_days)
            end = now - timedelta(days=i * step_days)
            label = (
                end.strftime("%a") if time_range == "week" else (str(end.day) if time_range == "month" else end.strftime("%b"))
            )
            buckets.append((label, str(int(start.timestamp())), str(int(end.timestamp()))))
        cols = [b[0] for b in buckets]

        # Initialize values matrix
        values: list[list[float]] = []

        if grouping in ("channels", "teams"):
            for c in channels:
                row_vals: list[float] = []
                for _, oldest, latest in buckets:
                    msgs = (await self.slack.get_channel_messages(channel_id=c.id, oldest=oldest, latest=latest, limit=200)).messages
                    if metric == "sentiment":
                        if msgs:
                            try:
                                analysis = await self.anthropic.analyze_slack_messages(msgs)
                                row_vals.append(float(analysis.overallSentiment))
                            except Exception:  # pragma: no cover
                                row_vals.append(0.0)
                        else:
                            row_vals.append(0.0)
                    elif metric == "messages":
                        row_vals.append(float(len(msgs)))
                    else:  # threads
                        row_vals.append(float(max(0, len(msgs) // 5)))
                values.append(row_vals)
            rows = [c.name for c in channels]
        else:
            # People metrics: compute counts per user per bucket; for sentiment, use a simple heuristic
            positive_words = {"great","good","excellent","awesome","thanks","thank you","love","nice","well done","amazing","happy","win","ship"}
            negative_words = {"bad","terrible","awful","hate","stuck","blocked","broken","late","fail","risky","stress","stressful","overworked","burnout","exhausted","tired","anxious","deadline"}

            def score_sent(text: str) -> float:
                t = text.lower()
                pos = sum(1 for w in positive_words if w in t)
                neg = sum(1 for w in negative_words if w in t)
                raw = pos - neg
                if raw == 0:
                    return 0.0
                return max(-1.0, min(1.0, raw / 5.0))

            # determine top users by total messages across the window to limit heatmap size
            aggregate_counts: dict[str, int] = {}
            # Single broad window for ranking
            wide_msgs = []
            oldest_all = self._oldest_ts_for_range(time_range)
            for c in channels:
                wide_msgs.extend((await self.slack.get_channel_messages(channel_id=c.id, oldest=oldest_all, limit=200)).messages)
            for m in wide_msgs:
                uid = m.userId or "unknown"
                aggregate_counts[uid] = aggregate_counts.get(uid, 0) + 1
            # Map to names
            user_name_map = {v: k for k, v in user_id_map.items()} if 'user_id_map' in locals() else {}
            top_users = sorted(aggregate_counts.items(), key=lambda kv: kv[1], reverse=True)[:8]
            rows = [user_name_map.get(uid, uid) for uid, _ in top_users]
            target_user_ids = [uid for uid, _ in top_users]

            for uid in target_user_ids:
                row_vals: list[float] = []
                for _, oldest, latest in buckets:
                    # gather user messages across selected channels in this window
                    msgs: list[SlackMessage] = []
                    for c in channels:
                        m = (await self.slack.get_channel_messages(channel_id=c.id, oldest=oldest, latest=latest, limit=200)).messages
                        msgs.extend([x for x in m if (x.userId or "") == uid])
                    if metric == "messages":
                        row_vals.append(float(len(msgs)))
                    elif metric == "threads":
                        row_vals.append(float(max(0, int(len(msgs) * 0.2))))
                    else:  # sentiment heuristic per user
                        if msgs:
                            s = sum(score_sent(x.text or "") for x in msgs) / max(1, len(msgs))
                            row_vals.append(float(s))
                        else:
                            row_vals.append(0.0)
                values.append(row_vals)

        return HeatmapMatrix(rows=rows, cols=cols, values=values)


