import type { TimeRange } from "@/types/dashboard";
import type { EntityTotalMetric, Perspective } from "@/types/metrics";
import { mockChannels, mockUsers } from "@/mocks/slack";
import { getChannelMetrics } from "@/mocks/dashboard";

const TEAMS = ["Eng", "Design", "Support", "Product"] as const;
const USER_TO_TEAM: Record<string, (typeof TEAMS)[number]> = {
  U01: "Eng",
  U02: "Eng",
  U03: "Design",
};

function scaleForRange(range: TimeRange): number {
  if (range === "week") return 1;
  if (range === "month") return 4;
  if (range === "quarter") return 12;
  return 48; // year
}

export function getEntityTotals(range: TimeRange, perspective: Perspective): EntityTotalMetric[] {
  const scale = scaleForRange(range);

  if (perspective === "channel") {
    const base = getChannelMetrics();
    return base.map((c, idx) => ({
      id: c.id,
      name: `#${c.name}`,
      messages: Math.round((c.messages / 10) * scale),
      threads: Math.round((c.threads / 2) * (1 + (idx % 3) * 0.2)),
      responses: Math.round((c.threads * 3) * (1 + (idx % 2) * 0.3)),
      emojis: Math.round((c.messages * 0.4) * (1 + (idx % 4) * 0.15)),
    }));
  }

  if (perspective === "employee") {
    // fabricate counts per user from mock channels/threads
    const counts: Record<string, number> = {};
    mockChannels.forEach((ch, idx) => {
      ch.threads?.forEach((th) => {
        th.messages.forEach((m) => {
          counts[m.userId] = (counts[m.userId] || 0) + 1 + (idx % 3);
        });
      });
    });
    return mockUsers.map((u, idx) => ({
      id: u.id,
      name: u.displayName,
      messages: (counts[u.id] || 5) * scale,
      threads: Math.round((counts[u.id] || 3) * 0.6),
      responses: Math.round(((counts[u.id] || 3) * 1.8) * (1 + (idx % 2) * 0.25)),
      emojis: Math.round(((counts[u.id] || 3) * 2.4) * (1 + (idx % 3) * 0.2)),
    }));
  }

  // team
  const teamCounts: Record<string, number> = {};
  mockUsers.forEach((u, idx) => {
    const team = USER_TO_TEAM[u.id] || TEAMS[idx % TEAMS.length];
    teamCounts[team] = (teamCounts[team] || 0) + 10 + idx * 3;
  });
  return TEAMS.map((t, idx) => ({
    id: `team-${t.toLowerCase()}`,
    name: t,
    messages: (teamCounts[t] || 8) * scale,
    threads: Math.round(((teamCounts[t] || 6) * 0.7) * (1 + (idx % 2) * 0.25)),
    responses: Math.round(((teamCounts[t] || 6) * 2) * (1 + (idx % 3) * 0.2)),
    emojis: Math.round(((teamCounts[t] || 6) * 2.6) * (1 + (idx % 4) * 0.15)),
  }));
}


