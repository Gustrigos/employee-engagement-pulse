from fastapi import APIRouter

from app.models.pydantic_types import SlackChannel, SlackUser, SlackConnection
from app.services.slack_service import SlackService

router = APIRouter(prefix="/slack", tags=["slack"])


@router.get("/connection", response_model=SlackConnection)
async def get_connection() -> SlackConnection:
    service = SlackService()
    return await service.get_connection()


@router.get("/channels", response_model=list[SlackChannel])
async def list_channels() -> list[SlackChannel]:
    service = SlackService()
    return await service.list_channels()


@router.get("/users", response_model=list[SlackUser])
async def list_users() -> list[SlackUser]:
    service = SlackService()
    return await service.list_users()