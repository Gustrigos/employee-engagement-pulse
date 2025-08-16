from typing import Optional
from fastapi import APIRouter, Query
from fastapi.responses import JSONResponse, RedirectResponse

from app.models.pydantic_types import (
    SlackChannel,
    SlackConnection,
    SlackMessagesResponse,
    SlackOAuthUrl,
    SlackOAuthExchangeRequest,
    SlackSelectedChannels,
    SlackSelectChannelsRequest,
    SlackUser,
    SlackDevRehydrateRequest,
)
from app.services.slack_service import SlackService

router = APIRouter(prefix="/slack", tags=["slack"])


@router.get("/connection", response_model=SlackConnection)
async def get_connection() -> SlackConnection:
    service = SlackService()
    return await service.get_connection()


@router.get("/oauth/url", response_model=SlackOAuthUrl)
async def get_oauth_url(return_to: Optional[str] = Query(None), redirect_uri: Optional[str] = Query(None)) -> SlackOAuthUrl:
    service = SlackService()
    return await service.get_oauth_url(return_to=return_to, override_redirect_uri=redirect_uri)


@router.get("/oauth/callback")
async def oauth_callback(code: str = Query(...), state: str = Query(...), redirect_uri: Optional[str] = Query(None)):
    service = SlackService()
    result = await service.handle_oauth_callback(code=code, state=state, override_redirect_uri=redirect_uri)
    # If we have a return URL and success, redirect user back to frontend
    if result.ok and result.returnTo:
        # append a simple flag to indicate success
        separator = "&" if ("?" in result.returnTo) else "?"
        target = f"{result.returnTo}{separator}slack_oauth=ok&teamId={result.teamId}"
        return RedirectResponse(url=target, status_code=302)
    # Otherwise return JSON payload
    return JSONResponse(content=result.model_dump())


@router.post("/oauth/exchange")
async def oauth_exchange(payload: SlackOAuthExchangeRequest):
    service = SlackService()
    result = await service.handle_oauth_callback(code=payload.code, state=payload.state, override_redirect_uri=payload.redirectUri)
    return JSONResponse(content=result.model_dump())


@router.post("/dev/rehydrate", response_model=SlackConnection)
async def dev_rehydrate(payload: SlackDevRehydrateRequest) -> SlackConnection:
    service = SlackService()
    return await service.dev_rehydrate_installation(payload)


@router.get("/channels", response_model=list[SlackChannel])
async def list_channels() -> list[SlackChannel]:
    service = SlackService()
    return await service.list_channels()


@router.post("/channels/select", response_model=SlackSelectedChannels)
async def select_channels(payload: SlackSelectChannelsRequest) -> SlackSelectedChannels:
    service = SlackService()
    return await service.select_channels(payload)


@router.get("/channels/selected", response_model=SlackSelectedChannels)
async def get_selected_channels() -> SlackSelectedChannels:
    service = SlackService()
    return await service.get_selected_channels()


@router.get("/channels/{channel_id}/messages", response_model=SlackMessagesResponse)
async def get_channel_messages(
    channel_id: str,
    oldest: Optional[str] = None,
    latest: Optional[str] = None,
    limit: int = 200,
) -> SlackMessagesResponse:
    service = SlackService()
    return await service.get_channel_messages(channel_id=channel_id, oldest=oldest, latest=latest, limit=limit)


@router.get("/users", response_model=list[SlackUser])
async def list_users() -> list[SlackUser]:
    service = SlackService()
    return await service.list_users()
