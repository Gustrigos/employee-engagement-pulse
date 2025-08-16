from pydantic import BaseModel, Field
from typing import Literal, Optional


RiskLevel = Literal["Low", "Medium", "High"]
TimeRange = Literal["week", "month", "quarter", "year"]


class SentimentPoint(BaseModel):
    date: str
    label: str
    avgSentiment: float
    messageCount: int


class ChannelMetric(BaseModel):
    id: str
    name: str
    avgSentiment: float
    messages: int
    threads: int
    lastActivity: str
    risk: RiskLevel


class KPI(BaseModel):
    avgSentiment: float
    burnoutRiskCount: int
    monitoredChannels: int


class BurnoutPoint(BaseModel):
    label: str
    value: int


InsightScope = Literal["team", "channel", "company"]
InsightCategory = Literal[
    "burnout",
    "engagement",
    "communication",
    "recognition",
    "workload",
    "sentiment",
]


class InsightMetricContext(BaseModel):
    avgSentimentDelta: Optional[float] = None
    messageVolumeDelta: Optional[float] = None


class Insight(BaseModel):
    id: str
    scope: InsightScope
    team: Optional[str] = None
    channelId: Optional[str] = None
    title: str
    summary: str
    recommendation: str
    severity: RiskLevel
    category: InsightCategory
    confidence: float
    tags: list[str]
    createdAt: str
    metricContext: Optional[InsightMetricContext] = None
    range: TimeRange


class InsightFilters(BaseModel):
    range: TimeRange
    teams: Optional[list[str]] = None
    severities: Optional[list[RiskLevel]] = None


class SlackReaction(BaseModel):
    name: str
    userIds: list[str]
    emoji: Optional[str] = None


class SlackMessage(BaseModel):
    id: str
    userId: str
    text: str
    ts: str
    reactions: Optional[list[SlackReaction]] = None
    sentiment: Optional[float] = None


class SlackThread(BaseModel):
    id: str
    rootMessageId: str
    messages: list[SlackMessage]
    lastActivityTs: str


class SlackChannel(BaseModel):
    id: str
    name: str
    isPrivate: Optional[bool] = None
    memberUserIds: Optional[list[str]] = None
    threads: Optional[list[SlackThread]] = None
    lastFetchedTs: Optional[str] = None


class SlackUser(BaseModel):
    id: str
    username: str
    displayName: str
    avatarUrl: Optional[str] = None
    isBot: Optional[bool] = None


class SlackConnection(BaseModel):
    teamId: str
    teamName: str
    isConnected: bool
    botUserId: Optional[str] = None