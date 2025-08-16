from __future__ import annotations

from typing import List
from app.models.pydantic_types import SlackChannel, SlackUser, SlackConnection, SlackThread, SlackMessage


class SlackService:
    async def get_connection(self) -> SlackConnection:
        return SlackConnection(teamId="T123", teamName="Demo Team", isConnected=False)

    async def list_channels(self) -> List[SlackChannel]:
        sample_thread = SlackThread(
            id="T01",
            rootMessageId="M01",
            lastActivityTs=str(int(__import__("time").time())),
            messages=[
                SlackMessage(id="M01", userId="U01", text="Welcome to Employee Pulse!", ts=str(int(__import__("time").time()) - 86400), sentiment=0.6),
                SlackMessage(id="M02", userId="U02", text="Let's keep an eye on burnout and PTO coverage.", ts=str(int(__import__("time").time()) - 86000), sentiment=0.1),
            ],
        )
        return [
            SlackChannel(id="C-general", name="general", memberUserIds=["U01", "U02", "U03"], threads=[sample_thread]),
            SlackChannel(id="C-eng", name="eng-announcements", memberUserIds=["U01", "U02"], threads=[sample_thread]),
            SlackChannel(id="C-random", name="random", memberUserIds=["U03"], threads=[sample_thread]),
        ]

    async def list_users(self) -> List[SlackUser]:
        return [
            SlackUser(id="U01", username="alice", displayName="Alice"),
            SlackUser(id="U02", username="bob", displayName="Bob"),
            SlackUser(id="U03", username="carol", displayName="Carol"),
        ]