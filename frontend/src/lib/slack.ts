import type { SlackChannel, SlackConnection, SlackMessagesResponse, SlackUser } from "@/types/slack";

// When running the frontend over HTTPS locally, use the Next.js API proxy to avoid mixed-content issues
const API_BASE = (typeof window !== "undefined" && window.location.protocol === "https:")
  ? "" // same-origin Next.js route
  : (process.env.NEXT_PUBLIC_API_BASE_URL || "http://127.0.0.1:8000").replace(/\/$/, "");
const SLACK_PREFIX = API_BASE ? "/api/v1/slack" : "/api/slack";

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

export async function fetchConnection(): Promise<SlackConnection> {
  return getJson<SlackConnection>(`${SLACK_PREFIX}/connection`);
}

export async function fetchOAuthUrl(returnTo: string, redirectUri?: string): Promise<{ url: string; state: string }>{
  const p = new URLSearchParams();
  if (returnTo) p.set("return_to", returnTo);
  if (redirectUri) p.set("redirect_uri", redirectUri);
  const qs = p.toString();
  const suffix = qs ? `?${qs}` : "";
  return getJson<{ url: string; state: string }>(`${SLACK_PREFIX}/oauth/url${suffix}`);
}

export async function fetchChannels(): Promise<SlackChannel[]> {
  return getJson<SlackChannel[]>(`${SLACK_PREFIX}/channels`);
}

export async function postSelectChannels(channelIds: string[]): Promise<{ channels: SlackChannel[] }>{
  return getJson<{ channels: SlackChannel[] }>(`${SLACK_PREFIX}/channels/select`, {
    method: "POST",
    body: JSON.stringify({ channelIds }),
  });
}

export async function fetchSelectedChannels(): Promise<{ channels: SlackChannel[] }>{
  return getJson<{ channels: SlackChannel[] }>(`${SLACK_PREFIX}/channels/selected`);
}

export async function fetchUsers(): Promise<SlackUser[]>{
  return getJson<SlackUser[]>(`${SLACK_PREFIX}/users`);
}

export async function fetchChannelMessages(channelId: string, opts?: { oldest?: string; latest?: string; limit?: number }): Promise<SlackMessagesResponse>{
  const p = new URLSearchParams();
  if (opts?.oldest) p.set("oldest", opts.oldest);
  if (opts?.latest) p.set("latest", opts.latest);
  if (opts?.limit) p.set("limit", String(opts.limit));
  const qs = p.toString();
  const suffix = qs ? `?${qs}` : "";
  return getJson<SlackMessagesResponse>(`${SLACK_PREFIX}/channels/${encodeURIComponent(channelId)}/messages${suffix}`);
}


