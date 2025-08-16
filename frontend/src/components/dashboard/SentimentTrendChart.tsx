"use client";
import type { SentimentPoint, TimeRange } from "@/types/dashboard";
import { LineChart, Line, XAxis, YAxis, Tooltip, ResponsiveContainer } from "recharts";

export function SentimentTrendChart({ data, range = "week" as TimeRange }: { data: SentimentPoint[]; range?: TimeRange }) {
  return (
    <div className="rounded-lg border border-black/10 dark:border-white/10 p-4">
      <h2 className="mb-4 text-sm font-medium">Weekly Sentiment Trend</h2>
      <div className="h-64 w-full">
        <ResponsiveContainer width="100%" height="100%">
          <LineChart data={data} margin={{ left: 8, right: 8 }}>
            <XAxis dataKey="label" />
            <YAxis domain={[-1, 1]} tickFormatter={(v) => v.toFixed(1)} />
            <Tooltip formatter={(v: number) => v.toFixed(2)} cursor={false} />
            <Line type="monotone" dataKey="avgSentiment" stroke="#16a34a" strokeWidth={2} dot={false} />
          </LineChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}


