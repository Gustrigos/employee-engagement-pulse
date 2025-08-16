from __future__ import annotations

import time
import secrets
from dataclasses import dataclass, field
from typing import Dict, List, Optional
import logging
from urllib.parse import urlencode

import httpx

from app.core.config import get_settings
from app.models.pydantic_types import (
    SlackChannel,
    SlackConnection,
    SlackMessage,
    SlackMessagesResponse,
    SlackOAuthCallbackResult,
    SlackOAuthUrl,
    SlackSelectedChannels,
    SlackSelectChannelsRequest,
    SlackThread,
    SlackUser,
    SlackDevRehydrateRequest,
)


# In-memory store for demo/dev. Replace with DB persistence via Prisma when ready.
_OAUTH_STATE_STORE: Dict[str, float] = {}
# Optional mapping state -> return URL so we can redirect back to the frontend after OAuth
_OAUTH_STATE_RETURN_TO: Dict[str, str] = {}


@dataclass
class _Installation:
    team_id: str
    team_name: str
    access_token: str
    bot_user_id: Optional[str] = None
    selected_channel_ids: set[str] = field(default_factory=set)


_INSTALLATIONS_BY_TEAM: Dict[str, _Installation] = {}
_ACTIVE_TEAM_ID: Optional[str] = None


def _now_epoch() -> int:
    return int(time.time())


def _cleanup_states(ttl_seconds: int = 600) -> None:
    cutoff = _now_epoch() - ttl_seconds
    for key in list(_OAUTH_STATE_STORE.keys()):
        if _OAUTH_STATE_STORE[key] < cutoff:
            del _OAUTH_STATE_STORE[key]


class SlackService:
    def __init__(self) -> None:
        self.settings = get_settings()

    async def _http(self) -> httpx.AsyncClient:
        return httpx.AsyncClient(base_url="https://slack.com/api", timeout=20)

    def _get_active_installation(self) -> Optional[_Installation]:
        if _ACTIVE_TEAM_ID is None:
            return None
        return _INSTALLATIONS_BY_TEAM.get(_ACTIVE_TEAM_ID)

    async def get_connection(self) -> SlackConnection:
        installation = self._get_active_installation()
        if not installation:
            return SlackConnection(teamId="", teamName="", isConnected=False)
        return SlackConnection(
            teamId=installation.team_id,
            teamName=installation.team_name,
            isConnected=True,
            botUserId=installation.bot_user_id,
        )

    async def get_oauth_url(self, return_to: Optional[str] = None, override_redirect_uri: Optional[str] = None) -> SlackOAuthUrl:
        client_id = self.settings.slack_client_id
        redirect_uri = override_redirect_uri or self.settings.slack_redirect_uri
        if not client_id or not redirect_uri:
            # Generate a placeholder state even if misconfigured to avoid None issues
            state = secrets.token_urlsafe(24)
            _OAUTH_STATE_STORE[state] = _now_epoch()
            return SlackOAuthUrl(url="", state=state)

        _cleanup_states()
        state = secrets.token_urlsafe(24)
        _OAUTH_STATE_STORE[state] = _now_epoch()
        if return_to:
            _OAUTH_STATE_RETURN_TO[state] = return_to

        params = {
            "client_id": client_id,
            "scope": self.settings.slack_bot_scopes,
            "redirect_uri": redirect_uri,
            "state": state,
        }
        if self.settings.slack_user_scopes:
            params["user_scope"] = self.settings.slack_user_scopes
        url = f"https://slack.com/oauth/v2/authorize?{urlencode(params)}"
        return SlackOAuthUrl(url=url, state=state)

    async def handle_oauth_callback(self, code: str, state: str, override_redirect_uri: Optional[str] = None) -> SlackOAuthCallbackResult:
        expected_ts = _OAUTH_STATE_STORE.pop(state, None)
        if expected_ts is None or (_now_epoch() - expected_ts) > 600:
            return SlackOAuthCallbackResult(ok=False, error="invalid_state")
        return_to = _OAUTH_STATE_RETURN_TO.pop(state, None)

        client_id = self.settings.slack_client_id
        client_secret = self.settings.slack_client_secret
        redirect_uri = override_redirect_uri or self.settings.slack_redirect_uri
        if not client_id or not client_secret or not redirect_uri:
            return SlackOAuthCallbackResult(ok=False, error="server_not_configured")

        async with await self._http() as http:
            resp = await http.post(
                "/oauth.v2.access",
                data={
                    "client_id": client_id,
                    "client_secret": client_secret,
                    "code": code,
                    "redirect_uri": redirect_uri,
                },
                headers={"Content-Type": "application/x-www-form-urlencoded"},
            )
            data = resp.json()
        if not data.get("ok"):
            return SlackOAuthCallbackResult(ok=False, error=str(data.get("error", "unknown_error")))

        access_token: str = data.get("access_token", "")
        team = data.get("team", {}) or {}
        team_id: str = team.get("id", "")
        team_name: str = team.get("name", "")
        bot_user_id: Optional[str] = data.get("bot_user_id")

        if not access_token or not team_id:
            return SlackOAuthCallbackResult(ok=False, error="invalid_token_response")

        installation = _Installation(
            team_id=team_id,
            team_name=team_name or team_id,
            access_token=access_token,
            bot_user_id=bot_user_id,
        )
        _INSTALLATIONS_BY_TEAM[team_id] = installation
        global _ACTIVE_TEAM_ID
        _ACTIVE_TEAM_ID = team_id

        return SlackOAuthCallbackResult(
            ok=True,
            teamId=team_id,
            teamName=installation.team_name,
            botUserId=bot_user_id,
            returnTo=return_to,
            devAccessToken=access_token if (self.settings.environment == "development") else None,
        )

    async def dev_rehydrate_installation(self, payload: SlackDevRehydrateRequest) -> SlackConnection:
        """
        Development-only helper to rehydrate a Slack installation from a token
        stored on the client side. This is useful when the API process restarts
        and loses its in-memory token store during local development.
        """
        if self.settings.environment != "development":
            # Silently ignore in non-dev to avoid accidental token ingestion
            return SlackConnection(teamId="", teamName="", isConnected=False)

        team_id = payload.teamId
        installation = _Installation(
            team_id=team_id,
            team_name=(payload.teamName or team_id),
            access_token=payload.accessToken,
            bot_user_id=payload.botUserId,
        )
        _INSTALLATIONS_BY_TEAM[team_id] = installation
        global _ACTIVE_TEAM_ID
        _ACTIVE_TEAM_ID = team_id
        return SlackConnection(teamId=team_id, teamName=installation.team_name, isConnected=True, botUserId=installation.bot_user_id)

    async def list_channels(self) -> List[SlackChannel]:
        installation = self._get_active_installation()
        if not installation:
            # Fallback demo data when not connected
            sample_thread = SlackThread(
                id="T01",
                rootMessageId="M01",
                lastActivityTs=str(_now_epoch()),
                messages=[
                    SlackMessage(
                        id="M01",
                        userId="U01",
                        text="Welcome to Employee Pulse!",
                        ts=str(_now_epoch() - 86400),
                        sentiment=0.6,
                    ),
                    SlackMessage(
                        id="M02",
                        userId="U02",
                        text="Let's keep an eye on burnout and PTO coverage.",
                        ts=str(_now_epoch() - 86000),
                        sentiment=0.1,
                    ),
                ],
            )
            return [
                SlackChannel(id="C-general", name="general", memberUserIds=["U01", "U02", "U03"], threads=[sample_thread]),
                SlackChannel(id="C-eng", name="eng-announcements", memberUserIds=["U01", "U02"], threads=[sample_thread]),
                SlackChannel(id="C-random", name="random", memberUserIds=["U03"], threads=[sample_thread]),
            ]

        channels: list[SlackChannel] = []
        cursor: Optional[str] = None
        async with await self._http() as http:
            while True:
                params = {
                    "limit": 200,
                    "types": "public_channel,private_channel",
                }
                if cursor:
                    params["cursor"] = cursor
                resp = await http.get(
                    "/conversations.list",
                    params=params,
                    headers={"Authorization": f"Bearer {installation.access_token}"},
                )
                data = resp.json()
                if not data.get("ok"):
                    break
                for ch in data.get("channels", []) or []:
                    channels.append(
                        SlackChannel(
                            id=ch.get("id", ""),
                            name=ch.get("name", ""),
                            isPrivate=ch.get("is_private"),
                        )
                    )
                cursor = (data.get("response_metadata") or {}).get("next_cursor")
                if not cursor:
                    break
        return channels

    async def select_channels(self, payload: SlackSelectChannelsRequest) -> SlackSelectedChannels:
        installation = self._get_active_installation()
        selected: list[SlackChannel] = []
        if not installation:
            # Allow selection in demo mode without real Slack
            for cid in payload.channelIds:
                selected.append(SlackChannel(id=cid, name=cid))
            return SlackSelectedChannels(channels=selected)

        installation.selected_channel_ids = set(payload.channelIds)
        # Return rich channel info
        all_channels = await self.list_channels()
        selected_map = {c.id: c for c in all_channels}
        for cid in payload.channelIds:
            if cid in selected_map:
                selected.append(selected_map[cid])
        return SlackSelectedChannels(channels=selected)

    async def get_selected_channels(self) -> SlackSelectedChannels:
        installation = self._get_active_installation()
        if not installation or not installation.selected_channel_ids:
            return SlackSelectedChannels(channels=[])
        all_channels = await self.list_channels()
        selected = [c for c in all_channels if c.id in installation.selected_channel_ids]
        return SlackSelectedChannels(channels=selected)

    async def get_channel_messages(
        self, channel_id: str, oldest: Optional[str] = None, latest: Optional[str] = None, limit: int = 200
    ) -> SlackMessagesResponse:
        installation = self._get_active_installation()
        messages: list[SlackMessage] = []
        if not installation:
            logging.getLogger(__name__).warning(
                "slack: no active installation; returning empty message list for channel=%s",
                channel_id,
            )
            return SlackMessagesResponse(channelId=channel_id, messages=messages)

        params: dict[str, str | int] = {"channel": channel_id, "limit": limit}
        if oldest:
            params["oldest"] = oldest
        if latest:
            params["latest"] = latest

        async with await self._http() as http:
            resp = await http.get(
                "/conversations.history",
                params=params,
                headers={"Authorization": f"Bearer {installation.access_token}"},
            )
            data = resp.json()
        logging.getLogger(__name__).info(
            "slack: history channel=%s ok=%s count=%s",
            channel_id,
            data.get("ok"),
            len((data.get("messages") or [])),
        )
        if data.get("ok"):
            for m in data.get("messages", []) or []:
                # Skip non-user messages (e.g. channel_join) without text where appropriate
                msg_id = m.get("ts", "")
                user = m.get("user") or m.get("bot_id") or ""
                text = m.get("text", "")
                ts = m.get("ts", "")
                reactions = []
                reactions_raw = m.get("reactions")
                if isinstance(reactions_raw, list):
                    for r in reactions_raw:
                        name = (r or {}).get("name", "")
                        users = (r or {}).get("users") or []
                        if not isinstance(users, list):
                            users = []
                        reactions.append({"name": name, "userIds": [str(u) for u in users], "emoji": None})
                messages.append(
                    SlackMessage(
                        id=msg_id,
                        userId=str(user),
                        text=text or "",
                        ts=str(ts),
                        reactions=reactions or None,
                    )
                )
        return SlackMessagesResponse(channelId=channel_id, messages=messages)

    async def list_users(self) -> List[SlackUser]:
        installation = self._get_active_installation()
        if not installation:
            return [
                SlackUser(id="U01", username="alice", displayName="Alice"),
                SlackUser(id="U02", username="bob", displayName="Bob"),
                SlackUser(id="U03", username="carol", displayName="Carol"),
            ]

        users: list[SlackUser] = []
        cursor: Optional[str] = None
        async with await self._http() as http:
            while True:
                params = {"limit": 200}
                if cursor:
                    params["cursor"] = cursor
                resp = await http.get(
                    "/users.list",
                    params=params,
                    headers={"Authorization": f"Bearer {installation.access_token}"},
                )
                data = resp.json()
                if not data.get("ok"):
                    break
                for u in data.get("members", []) or []:
                    if u.get("deleted"):
                        continue
                    users.append(
                        SlackUser(
                            id=u.get("id", ""),
                            username=u.get("name", ""),
                            displayName=(u.get("profile", {}) or {}).get("real_name", ""),
                            avatarUrl=(u.get("profile", {}) or {}).get("image_48"),
                            isBot=u.get("is_bot"),
                        )
                    )
                cursor = (data.get("response_metadata") or {}).get("next_cursor")
                if not cursor:
                    break
        return users
