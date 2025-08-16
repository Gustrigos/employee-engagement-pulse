"use client";
import * as React from "react";
import type { SlackChannel } from "@/types/slack";
import { fetchChannels, fetchConnection, fetchOAuthUrl, fetchSelectedChannels, postSelectChannels, devRehydrateInstallation } from "@/lib/slack";

const CHANNELS_KEY = "trackedSlackChannels";
const CONNECTED_KEY = "slackConnected";
// Dev token persistence to survive backend restarts (development only)
const DEV_TOKEN_KEY = "slackAccessToken";
const DEV_TEAM_ID_KEY = "slackTeamId";
const DEV_TEAM_NAME_KEY = "slackTeamName";
const DEV_BOT_USER_ID_KEY = "slackBotUserId";

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

  // Bootstrap from backend; in development try to rehydrate server with saved token
  React.useEffect(() => {
    let aborted = false;
    (async () => {
      const hydrateFromServer = async () => {
        const [available, selected] = await Promise.all([
          fetchChannels().catch(() => []),
          fetchSelectedChannels().catch(() => ({ channels: [] })),
        ]);
        if (aborted) return;
        setSuggestions(available);
        if (selected.channels?.length) setChannels(selected.channels);
      };

      try {
        const conn = await fetchConnection();
        if (aborted) return;
        setIsConnected(conn.isConnected);
        if (conn.isConnected) {
          await hydrateFromServer();
          return;
        }
      } catch { /* ignore */ }

      // Not connected: in development, try rehydrate API with saved token
      try {
        if (typeof window !== "undefined" && process.env.NODE_ENV === "development") {
          const token = window.localStorage.getItem(DEV_TOKEN_KEY);
          const teamId = window.localStorage.getItem(DEV_TEAM_ID_KEY);
          const teamName = window.localStorage.getItem(DEV_TEAM_NAME_KEY) || undefined;
          const botUserId = window.localStorage.getItem(DEV_BOT_USER_ID_KEY) || undefined;
          if (token && teamId) {
            const conn2 = await devRehydrateInstallation({ accessToken: token, teamId, teamName, botUserId: botUserId || undefined });
            if (!aborted && conn2.isConnected) {
              setIsConnected(true);
              await hydrateFromServer();
              return;
            }
          }
        }
      } catch { /* ignore */ }

      // Do not fetch suggestions while disconnected
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
  async function disconnect() {
    // For now just clear local and inform backend selection cleared
    setIsConnected(false);
    setChannels([]);
    try { await postSelectChannels([]); } catch { /* ignore */ }
    // Clear persisted state
    if (typeof window !== "undefined") {
      try {
        window.localStorage.removeItem(CONNECTED_KEY);
        window.localStorage.removeItem(CHANNELS_KEY);
        window.localStorage.removeItem(DEV_TOKEN_KEY);
        window.localStorage.removeItem(DEV_TEAM_ID_KEY);
        window.localStorage.removeItem(DEV_TEAM_NAME_KEY);
        window.localStorage.removeItem(DEV_BOT_USER_ID_KEY);
      } catch { /* ignore */ }
    }
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


