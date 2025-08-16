"use client";
import type { SentimentPoint, TimeRange } from "@/types/dashboard";
import { LineChart, Line, XAxis, YAxis, Tooltip, ResponsiveContainer } from "recharts";
import { Lightbulb } from "lucide-react";

export function SentimentTrendChart({ data, range = "week" as TimeRange }: { data: SentimentPoint[]; range?: TimeRange }) {
  const last = data[data.length - 1]?.avgSentiment ?? 0;
  const prev = data.length > 1 ? data[data.length - 2]?.avgSentiment ?? last : last;
  const delta = last - prev;
  const hintDown = delta < 0 && last < 0;
  const hintUp = delta > 0 && last > 0;
  const hint = hintDown
    ? "Recent dip below neutral suggests fatigue. Acknowledge recent stressors and invite feedback in retro."
    : hintUp
    ? "Upward momentum. Reinforce what worked this week (recognize contributors, share wins)."
    : "Stable sentiment. Maintain cadence and keep communication clear around priorities.";

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
      <div className="mt-3 rounded-md bg-black/5 dark:bg-white/5 p-3 text-xs text-foreground/80 flex items-start gap-2">
        <Lightbulb className="h-4 w-4 mt-0.5" />
        <div>{hint}</div>
      </div>
    </div>
  );
}


