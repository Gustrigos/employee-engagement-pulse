import type { SlackChannel, SlackThread, SlackUser } from "@/types/slack";

export const mockUsers: SlackUser[] = [
  { id: "U01", username: "alice", displayName: "Alice" },
  { id: "U02", username: "bob", displayName: "Bob" },
  { id: "U03", username: "carol", displayName: "Carol" },
];

const sampleThread: SlackThread = {
  id: "T01",
  rootMessageId: "M01",
  lastActivityTs: String(Math.floor(Date.now() / 1000)),
  messages: [
    {
      id: "M01",
      userId: "U01",
      text: "Shipping the release this week. Feeling good!",
      ts: String(Math.floor(Date.now() / 1000) - 86400),
      sentiment: 0.7,
    },
    {
      id: "M02",
      userId: "U02",
      text: "Let’s keep an eye on burnout and PTO coverage.",
      ts: String(Math.floor(Date.now() / 1000) - 86000),
      sentiment: 0.1,
    },
  ],
};

export const mockChannels: SlackChannel[] = [
  {
    id: "C-general",
    name: "general",
    memberUserIds: ["U01", "U02", "U03"],
    threads: [sampleThread],
  },
  {
    id: "C-eng",
    name: "eng-announcements",
    memberUserIds: ["U01", "U02"],
    threads: [sampleThread],
  },
  {
    id: "C-random",
    name: "random",
    memberUserIds: ["U03"],
    threads: [sampleThread],
  },
];


