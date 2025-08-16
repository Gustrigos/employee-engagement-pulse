import type { RiskLevel, TimeRange } from "@/types/dashboard";

export type InsightScope = "team" | "channel" | "company";

export type InsightCategory =
  | "burnout"
  | "engagement"
  | "communication"
  | "recognition"
  | "workload"
  | "sentiment";

export interface InsightMetricContext {
  avgSentimentDelta?: number; // change vs previous range
  messageVolumeDelta?: number; // change vs previous range
}

export interface Insight {
  id: string;
  scope: InsightScope; // for now, primarily "team"
  team?: string; // required when scope === "team"
  channelId?: string; // optional when scope === "channel"
  title: string;
  summary: string; // natural language summary of the pattern
  recommendation: string; // natural language, actionable suggestion
  severity: RiskLevel; // Low | Medium | High
  category: InsightCategory;
  confidence: number; // 0..1
  tags: string[];
  createdAt: string; // ISO date
  metricContext?: InsightMetricContext;
  range: TimeRange;
}

export interface InsightFilters {
  range: TimeRange;
  teams?: string[];
  severities?: RiskLevel[];
}


