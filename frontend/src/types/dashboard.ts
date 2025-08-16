export interface SentimentPoint {
  date: string; // e.g., 2025-08-16
  label: string; // e.g., Mon
  avgSentiment: number; // -1..1
  messageCount: number;
}

export type RiskLevel = "Low" | "Medium" | "High";

export interface ChannelMetric {
  id: string;
  name: string;
  avgSentiment: number;
  messages: number;
  threads: number;
  lastActivity: string; // ISO date
  risk: RiskLevel;
}

export interface KPI {
  avgSentiment: number;
  burnoutRiskCount: number;
  monitoredChannels: number;
}

export type TimeRange = "week" | "month" | "quarter" | "year";

export interface BurnoutPoint {
  label: string;
  value: number; // warnings count
}


