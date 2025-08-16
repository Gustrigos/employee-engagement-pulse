"use client";
import * as React from "react";
import type { SlackChannel } from "@/types/slack";
import { mockChannels } from "@/mocks/slack";

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
  const [isConnected, setIsConnected] = React.useState<boolean>(() =>
    readLocalStorage(CONNECTED_KEY, false)
  );
  const [channels, setChannels] = React.useState<SlackChannel[]>(() =>
    readLocalStorage(CHANNELS_KEY, [])
  );

  React.useEffect(() => {
    writeLocalStorage(CONNECTED_KEY, isConnected);
  }, [isConnected]);

  React.useEffect(() => {
    writeLocalStorage(CHANNELS_KEY, channels);
  }, [channels]);

  function connect() {
    setIsConnected(true);
  }
  function disconnect() {
    setIsConnected(false);
  }

  function addChannelByName(name: string) {
    const trimmed = name.trim().replace(/^#/, "");
    if (!trimmed) return;
    const id = `C-${slugify(trimmed)}`;
    if (channels.some((c) => c.id === id)) return;
    setChannels((prev) => [{ id, name: trimmed }, ...prev]);
  }

  function addChannels(newOnes: SlackChannel[]) {
    const existing = new Set(channels.map((c) => c.id));
    const merged = [...newOnes.filter((c) => !existing.has(c.id)), ...channels];
    setChannels(merged);
  }

  function removeChannel(id: string) {
    setChannels((prev) => prev.filter((c) => c.id !== id));
  }

  function clearChannels() {
    setChannels([]);
  }

  const suggestions = mockChannels;

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


