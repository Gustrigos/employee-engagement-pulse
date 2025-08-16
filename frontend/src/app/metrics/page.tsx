"use client";
import * as React from "react";
import { TimeRangeSelector } from "@/components/dashboard/TimeRangeSelector";
import { PerspectiveSwitcher } from "@/components/metrics/PerspectiveSwitcher";
import { EntityBarChart } from "@/components/metrics/EntityBarChart";
import { EntityTable } from "@/components/metrics/EntityTable";
import { useMetrics } from "@/hooks/useMetrics";
import { MetricKeySwitcher } from "@/components/metrics/MetricKeySwitcher";
import { TopEmojisBarChart } from "@/components/metrics/TopEmojisBarChart";
import { useSlackChannels } from "@/hooks/settings/useSlackChannels";

export default function MetricsPage() {
  const { range, setRange, perspective, setPerspective, metric, setMetric, items, top, emojis } = useMetrics({ perspective: "employee", metric: "messages" });
  const { channels } = useSlackChannels();

  return (
    <div className="space-y-6">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <h1 className="text-2xl font-semibold tracking-tight">Metrics</h1>
        <div className="flex items-center gap-3">
          <PerspectiveSwitcher value={perspective} onChange={setPerspective} />
          <MetricKeySwitcher value={metric} onChange={setMetric} />
          <TimeRangeSelector value={range} onChange={setRange} />
        </div>
      </div>
      {channels.length > 0 ? (
        <div className="flex flex-wrap items-center gap-2 text-sm text-foreground/80">
          <span className="font-medium">Tracking:</span>
          <div className="flex flex-wrap gap-2">
            {channels.map((c) => (
              <span key={c.id} className="rounded-full border border-black/10 dark:border-white/10 px-2 py-0.5 text-xs">#{c.name}</span>
            ))}
          </div>
        </div>
      ) : (
        <div className="text-sm text-foreground/60">No channels selected. Go to Settings to choose channels.</div>
      )}
      <EntityBarChart items={top.slice(0, 10)} metric={metric} />
      <TopEmojisBarChart items={emojis} />
      <EntityTable items={items} />
    </div>
  );
}


