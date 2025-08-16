from __future__ import annotations

from collections import defaultdict
import time
from typing import Iterable, Optional

from app.models.pydantic_types import (
    EmojiStat,
    EntityTotalMetric,
    Perspective,
    SlackMessage,
    TimeRange,
)
from app.services.slack_service import SlackService


class MetricsService:
    """Compute basic metrics from Slack data without heavy processing."""

    def __init__(self) -> None:
        self.slack = SlackService()

    async def _get_channel_ids(self, requested: Optional[list[str]] = None) -> list[str]:
        if requested:
            return requested
        selected = await self.slack.get_selected_channels()
        if selected.channels:
            return [c.id for c in selected.channels]
        # fallback to all channels
        channels = await self.slack.list_channels()
        return [c.id for c in channels]

    @staticmethod
    def _oldest_ts_for_range(time_range: TimeRange) -> Optional[str]:
        now = int(time.time())
        days = 7
        if time_range == "week":
            days = 7
        elif time_range == "month":
            days = 30
        elif time_range == "quarter":
            days = 90
        elif time_range == "year":
            days = 365
        oldest = now - days * 24 * 60 * 60
        return str(oldest)

    async def _fetch_messages_for_channels(self, channel_ids: Iterable[str], *, oldest: Optional[str] = None) -> dict[str, list[SlackMessage]]:
        # For MVP we fetch recent history once per channel
        results: dict[str, list[SlackMessage]] = {}
        for cid in channel_ids:
            try:
                resp = await self.slack.get_channel_messages(channel_id=cid, oldest=oldest, limit=200)
                # Basic debug info: how many messages we fetched per channel
                __import__("logging").getLogger(__name__).debug(
                    "metrics: fetched %d messages for channel %s (oldest=%s)",
                    len(resp.messages),
                    cid,
                    oldest,
                )
                results[cid] = resp.messages
            except Exception as exc:
                __import__("logging").getLogger(__name__).warning(
                    "metrics: error fetching messages for channel %s: %s", cid, exc
                )
                results[cid] = []
        return results

    @staticmethod
    def _count_threads(messages: list[SlackMessage]) -> int:
        # Minimal heuristic: treat messages that look like thread roots (have replies?) as threads
        # Slack conversations.history does not include reply_count unless requested; keep basic for now
        return max(0, len(messages) // 5)

    async def compute_entity_totals(
        self,
        *,
        time_range: TimeRange,
        perspective: Perspective,
        channel_ids: Optional[list[str]] = None,
    ) -> list[EntityTotalMetric]:
        # Range currently not used for filtering; could map to oldest ts later
        channels = await self._get_channel_ids(channel_ids)
        oldest = self._oldest_ts_for_range(time_range)
        by_channel = await self._fetch_messages_for_channels(channels, oldest=oldest)

        if perspective == "channel":
            items: list[EntityTotalMetric] = []
            # We need channel names; build a map
            channel_name_map = {c.id: c.name for c in (await self.slack.list_channels())}
            for cid, msgs in by_channel.items():
                name = channel_name_map.get(cid, cid)
                messages = len(msgs)
                threads = self._count_threads(msgs)
                responses = max(0, int(messages * 0.6))  # heuristic
                emojis = sum(len(r.userIds) for m in msgs for r in (m.reactions or []))
                items.append(
                    EntityTotalMetric(
                        id=cid,
                        name=f"#{name}",
                        messages=messages,
                        threads=threads,
                        responses=responses,
                        emojis=emojis,
                    )
                )
            return items

        if perspective == "employee":
            per_user_counts: dict[str, EntityTotalMetric] = {}
            # user display names map
            user_name_map = {u.id: (u.displayName or u.username or u.id) for u in (await self.slack.list_users())}
            for _, msgs in by_channel.items():
                for m in msgs:
                    uid = m.userId or "unknown"
                    if uid not in per_user_counts:
                        per_user_counts[uid] = EntityTotalMetric(
                            id=uid,
                            name=user_name_map.get(uid, uid),
                            messages=0,
                            threads=0,
                            responses=0,
                            emojis=0,
                        )
                    entry = per_user_counts[uid]
                    entry.messages += 1
                    entry.responses += 1  # simplistic: treat each message as a response opportunity
                    entry.emojis += sum(len(r.userIds) for r in (m.reactions or []))
            # approximate threads per user
            for entry in per_user_counts.values():
                entry.threads = max(0, int(entry.messages * 0.2))
            return list(per_user_counts.values())

        # perspective == "team"
        # Without org mapping, group by first letter of username as pseudo-team
        team_map: dict[str, EntityTotalMetric] = {}
        user_map = {u.id: (u.displayName or u.username or u.id) for u in (await self.slack.list_users())}
        pseudo_team_of: dict[str, str] = {uid: (name[:1].upper() if name else "X") for uid, name in user_map.items()}

        for _, msgs in by_channel.items():
            for m in msgs:
                team = pseudo_team_of.get(m.userId, "X")
                if team not in team_map:
                    team_map[team] = EntityTotalMetric(
                        id=f"team-{team}",
                        name=f"Team {team}",
                        messages=0,
                        threads=0,
                        responses=0,
                        emojis=0,
                    )
                entry = team_map[team]
                entry.messages += 1
                entry.responses += 1
                entry.emojis += sum(len(r.userIds) for r in (m.reactions or []))
        for entry in team_map.values():
            entry.threads = max(0, int(entry.messages * 0.2))
        return list(team_map.values())

    async def compute_top_emojis(
        self,
        *,
        time_range: TimeRange,
        limit: int = 10,
        channel_ids: Optional[list[str]] = None,
    ) -> list[EmojiStat]:
        channels = await self._get_channel_ids(channel_ids)
        oldest = self._oldest_ts_for_range(time_range)
        by_channel = await self._fetch_messages_for_channels(channels, oldest=oldest)
        counts: dict[str, int] = defaultdict(int)
        for _, msgs in by_channel.items():
            for m in msgs:
                for r in (m.reactions or []):
                    counts[r.name] += len(r.userIds)
        # Map Slack alias names to unicode where possible
        alias_map: dict[str, str] = {
            "tada": "🎉",
            "rocket": "🚀",
            "raised_hands": "🙌",
            "thumbsup": "👍",
            "+1": "👍",
            "white_check_mark": "✅",
            "heavy_check_mark": "✔️",
            "smile": "😄",
            "simple_smile": "🙂",
            "grinning": "😀",
            "joy": "😂",
            "laughing": "😆",
            "sweat_smile": "😅",
            "heart": "❤️",
            "fire": "🔥",
            "pray": "🙏",
            "clap": "👏",
            "eyes": "👀",
            "bulb": "💡",
            "handshake": "🤝",
            "brain": "🧠",
            "sparkles": "✨",
            "star": "⭐",
            "confetti_ball": "🎊",
            "100": "💯",
        }
        def to_unicode(name: str) -> str:
            return alias_map.get(name, name)

        top = sorted((EmojiStat(emoji=to_unicode(k), count=v) for k, v in counts.items()), key=lambda e: e.count, reverse=True)
        return top[:limit]


