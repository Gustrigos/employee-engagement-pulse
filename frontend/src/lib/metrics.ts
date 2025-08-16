import type { EntityTotalMetric } from "@/types/metrics";

// When running the frontend over HTTPS locally, use the Next.js API proxy to avoid mixed-content issues
const API_BASE = (typeof window !== "undefined" && window.location.protocol === "https:")
  ? "" // same-origin Next.js route
  : (process.env.NEXT_PUBLIC_API_BASE_URL || "http://127.0.0.1:8000").replace(/\/$/, "");
const METRICS_PREFIX = API_BASE ? "/api/v1/metrics" : "/api/metrics";

async function getJson<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(`${API_BASE}${path}`, {
    headers: { "Content-Type": "application/json" },
    cache: "no-store",
    ...init,
  });
  if (!res.ok) {
    throw new Error(`Request failed: ${res.status}`);
  }
  return (await res.json()) as T;
}

export async function fetchEntityTotals(params: { perspective?: "channel" | "team" | "employee"; range?: "week" | "month" | "quarter" | "year"; channelIds?: string[] }) {
  const p = new URLSearchParams();
  if (params.perspective) p.set("perspective", params.perspective);
  if (params.range) p.set("range", params.range);
  if (params.channelIds?.length) p.set("channel_ids", params.channelIds.join(","));
  const qs = p.toString();
  const suffix = qs ? `?${qs}` : "";
  return getJson<EntityTotalMetric[]>(`${METRICS_PREFIX}/entity-totals${suffix}`);
}

export interface EmojiStat { emoji: string; count: number }

export async function fetchTopEmojis(params: { range?: "week" | "month" | "quarter" | "year"; limit?: number; channelIds?: string[] }) {
  const p = new URLSearchParams();
  if (params.range) p.set("range", params.range);
  if (typeof params.limit === "number") p.set("limit", String(params.limit));
  if (params.channelIds?.length) p.set("channel_ids", params.channelIds.join(","));
  const qs = p.toString();
  const suffix = qs ? `?${qs}` : "";
  return getJson<EmojiStat[]>(`${METRICS_PREFIX}/top-emojis${suffix}`);
}


