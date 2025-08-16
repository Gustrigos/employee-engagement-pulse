"use client";
import * as React from "react";
import type { SlackChannel } from "@/types/slack";
import { fetchChannels, fetchConnection, fetchOAuthUrl, fetchSelectedChannels, postSelectChannels } from "@/lib/slack";

const CHANNELS_KEY = "trackedSlackChannels";
const CONNECTED_KEY = "slackConnected";

function readLocalStorage<T>(key: string, fallback: T): T {
  if (typeof window === "undefined") return fallback;
  try {
    const raw = window.localStorage.getItem(key);
    return raw ? (JSON.parse(raw) as T) : fallback;
  } catch {
    return fallback;
  }
}

function writeLocalStorage<T>(key: string, value: T) {
  if (typeof window === "undefined") return;
  try {
    window.localStorage.setItem(key, JSON.stringify(value));
  } catch {
    // ignore
  }
}

function slugify(name: string) {
  return name
    .toLowerCase()
    .replace(/[^a-z0-9-]+/g, "-")
    .replace(/^-+|-+$/g, "");
}

export function useSlackChannels() {
  const [isConnected, setIsConnected] = React.useState<boolean>(() => readLocalStorage(CONNECTED_KEY, false));
  const [channels, setChannels] = React.useState<SlackChannel[]>(() => readLocalStorage(CHANNELS_KEY, []));
  const [suggestions, setSuggestions] = React.useState<SlackChannel[]>([]);

  React.useEffect(() => { writeLocalStorage(CONNECTED_KEY, isConnected); }, [isConnected]);

  React.useEffect(() => { writeLocalStorage(CHANNELS_KEY, channels); }, [channels]);

  // Bootstrap from backend
  React.useEffect(() => {
    let aborted = false;
    (async () => {
      try {
        const conn = await fetchConnection();
        if (aborted) return;
        setIsConnected(conn.isConnected);
        const [available, selected] = await Promise.all([
          fetchChannels().catch(() => []),
          fetchSelectedChannels().catch(() => ({ channels: [] })),
        ]);
        if (aborted) return;
        setSuggestions(available);
        if (selected.channels?.length) setChannels(selected.channels);
      } catch { /* ignore */ }
    })();
    return () => { aborted = true; };
  }, []);

  async function connect() {
    try {
      const here = typeof window !== "undefined" ? window.location.href : "/settings";
      // Prefer explicit env to guarantee exact Slack redirect URI match
      const envRedirect = process.env.NEXT_PUBLIC_SLACK_REDIRECT_URI;
      const computed = typeof window !== "undefined" ? `${window.location.origin}/api/auth/callback/slack` : undefined;
      const frontendRedirect = (envRedirect && envRedirect.length > 0) ? envRedirect : computed;
      const { url } = await fetchOAuthUrl(here, frontendRedirect);
      if (url) {
        window.location.href = url;
      } else {
        if (typeof window !== "undefined") {
          window.alert("Slack is not configured on the server. Please set SLACK_CLIENT_ID and SLACK_REDIRECT_URI in the backend .env and restart the API.");
        }
      }
    } catch {
      if (typeof window !== "undefined") {
        window.alert("Could not initiate Slack OAuth. Check server logs and configuration.");
      }
    }
  }
  function disconnect() {
    // For now just clear local state; real revoke would be backend endpoint
    setIsConnected(false);
    setChannels([]);
  }

  function addChannelByName(name: string) {
    const trimmed = name.trim().replace(/^#/, "");
    if (!trimmed) return;
    const id = `C-${slugify(trimmed)}`;
    if (channels.some((c) => c.id === id)) return;
    setChannels((prev) => [{ id, name: trimmed }, ...prev]);
  }

  async function addChannels(newOnes: SlackChannel[]) {
    const existing = new Set(channels.map((c) => c.id));
    const merged = [...newOnes.filter((c) => !existing.has(c.id)), ...channels];
    setChannels(merged);
    try { await postSelectChannels(merged.map((c) => c.id)); } catch { /* ignore */ }
  }

  async function removeChannel(id: string) {
    const next = channels.filter((c) => c.id !== id);
    setChannels(next);
    try { await postSelectChannels(next.map((c) => c.id)); } catch { /* ignore */ }
  }

  async function clearChannels() {
    setChannels([]);
    try { await postSelectChannels([]); } catch { /* ignore */ }
  }

  return {
    isConnected,
    connect,
    disconnect,
    channels,
    addChannelByName,
    addChannels,
    removeChannel,
    clearChannels,
    suggestions,
  } as const;
}


