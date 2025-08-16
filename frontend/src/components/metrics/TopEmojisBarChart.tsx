"use client";
import * as React from "react";
import { ResponsiveContainer, BarChart, Bar, XAxis, YAxis, Tooltip } from "recharts";

interface EmojiStat {
  emoji: string; // display emoji or alias
  count: number;
}

const MOCK: EmojiStat[] = [
  { emoji: "👍", count: 120 },
  { emoji: "🎉", count: 95 },
  { emoji: "🙏", count: 70 },
  { emoji: "❤️", count: 64 },
  { emoji: "🔥", count: 58 },
  { emoji: "✅", count: 52 },
  { emoji: "😅", count: 41 },
  { emoji: "💡", count: 36 },
  { emoji: "🤝", count: 33 },
  { emoji: "🧠", count: 27 },
];

export function TopEmojisBarChart({ items = MOCK }: { items?: EmojiStat[] }) {
  const data = items.map((e) => ({ name: e.emoji, value: e.count }));
  return (
    <div className="rounded-lg border border-black/10 dark:border-white/10 p-4">
      <h2 className="mb-3 text-sm font-medium">Top Emojis</h2>
      <div className="h-64 w-full">
        <ResponsiveContainer width="100%" height="100%">
          <BarChart data={data} margin={{ left: 8, right: 8 }}>
            <XAxis dataKey="name" tick={{ fontSize: 14 }} interval={0} />
            <YAxis />
            <Tooltip cursor={false} />
            <Bar dataKey="value" fill="#22c55e" radius={[4, 4, 0, 0]} />
          </BarChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}


