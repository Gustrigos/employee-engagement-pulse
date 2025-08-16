"use client";
import * as React from "react";
import type { EntityTotalMetric, MetricKey } from "@/types/metrics";
import { ResponsiveContainer, BarChart, Bar, XAxis, YAxis, Tooltip } from "recharts";

export function EntityBarChart({ items, metric }: { items: EntityTotalMetric[]; metric: MetricKey }) {
  const data = items.map((i) => ({ name: i.name, value: i[metric] as number }));
  const label: Record<MetricKey, string> = {
    messages: "Messages",
    threads: "Threads",
    responses: "Responses",
    emojis: "Emojis",
  };
  return (
    <div className="rounded-lg border border-black/10 dark:border-white/10 p-4">
      <h2 className="mb-3 text-sm font-medium">{label[metric]}</h2>
      <div className="h-64 w-full">
        <ResponsiveContainer width="100%" height="100%">
          <BarChart data={data} margin={{ left: 8, right: 8 }}>
            <XAxis dataKey="name" tick={{ fontSize: 12 }} interval={0} angle={-15} textAnchor="end" height={50} />
            <YAxis />
            <Tooltip cursor={false} />
            <Bar dataKey="value" fill="#3b82f6" radius={[4, 4, 0, 0]} />
          </BarChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}


