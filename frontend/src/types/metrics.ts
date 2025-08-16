import type { TimeRange } from "@/types/dashboard";

export type Perspective = "channel" | "team" | "employee";

export interface EntityTotalMetric {
  id: string;
  name: string;
  messages: number;
  threads: number;
  responses: number; // total replies (approx)
  emojis: number; // total reactions
}

export interface MetricsState {
  range: TimeRange;
  perspective: Perspective;
}

export type MetricKey = "messages" | "threads" | "responses" | "emojis";


