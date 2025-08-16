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


class SlackOAuthUrl(BaseModel):
    url: str
    state: str


class SlackOAuthCallbackResult(BaseModel):
    ok: bool
    teamId: Optional[str] = None
    teamName: Optional[str] = None
    botUserId: Optional[str] = None
    error: Optional[str] = None
    returnTo: Optional[str] = None
    # Development-only convenience: expose token so frontend can persist locally
    # Never set in production.
    devAccessToken: Optional[str] = None


class SlackOAuthExchangeRequest(BaseModel):
    code: str
    state: str
    # Must match the redirect_uri used in the initial Slack authorize request
    redirectUri: Optional[str] = None


class SlackDevRehydrateRequest(BaseModel):
    # Development-only: allows frontend to rehydrate the in-memory installation
    # on API restart using a saved token.
    accessToken: str
    teamId: str
    teamName: Optional[str] = None
    botUserId: Optional[str] = None


class SlackSelectChannelsRequest(BaseModel):
    channelIds: list[str] = Field(default_factory=list)


class SlackSelectedChannels(BaseModel):
    channels: list[SlackChannel]


class SlackMessagesResponse(BaseModel):
    channelId: str
    messages: list[SlackMessage]


# ===== Basic Metrics (for Metrics page) =====

Perspective = Literal["channel", "team", "employee"]


class EntityTotalMetric(BaseModel):
    id: str
    name: str
    messages: int
    threads: int
    responses: int
    emojis: int


class EmojiStat(BaseModel):
    emoji: str
    count: int


# ===== LLM / Anthropic structured outputs =====

class LLMMessageAnalysisItem(BaseModel):
    messageId: str
    sentiment: float = Field(description="Range -1.0 (very negative) to 1.0 (very positive)")
    burnoutRisk: Optional[RiskLevel] = None
    categories: Optional[list[str]] = None
    summary: Optional[str] = None


class LLMAnalysisSummary(BaseModel):
    overallSentiment: float
    burnoutRiskLevel: RiskLevel
    items: list[LLMMessageAnalysisItem] = Field(default_factory=list)


class LLMAnalyzeMessagesRequest(BaseModel):
    messages: list[SlackMessage]


# ===== Dashboard specific structured responses =====

class HeatmapMatrix(BaseModel):
    rows: list[str]
    cols: list[str]
    values: list[list[float]]


# ===== Insights structured outputs =====

class LLMInsightDraft(BaseModel):
    # All optional to make LLM parsing robust; service will normalize into Insight
    id: Optional[str] = None
    scope: Optional[InsightScope] = None
    team: Optional[str] = None
    channelId: Optional[str] = None
    title: Optional[str] = None
    summary: Optional[str] = None
    recommendation: Optional[str] = None
    severity: Optional[RiskLevel] = None
    category: Optional[InsightCategory] = None
    confidence: Optional[float] = None
    tags: Optional[list[str]] = None
    createdAt: Optional[str] = None
    metricContext: Optional[InsightMetricContext] = None
    range: Optional[TimeRange] = None


class LLMGeneratedInsights(BaseModel):
    insights: list[LLMInsightDraft] = Field(default_factory=list)
