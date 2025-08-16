"use client";
import * as React from "react";
import { TimeRangeSelector } from "@/components/dashboard/TimeRangeSelector";
import { PerspectiveSwitcher } from "@/components/metrics/PerspectiveSwitcher";
import { EntityBarChart } from "@/components/metrics/EntityBarChart";
import { EntityTable } from "@/components/metrics/EntityTable";
import { useMetrics } from "@/hooks/useMetrics";
import { MetricKeySwitcher } from "@/components/metrics/MetricKeySwitcher";
import { TopEmojisBarChart } from "@/components/metrics/TopEmojisBarChart";

export default function MetricsPage() {
  const { range, setRange, perspective, setPerspective, metric, setMetric, items, top } = useMetrics({ perspective: "employee", metric: "messages" });

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
      <EntityBarChart items={top.slice(0, 10)} metric={metric} />
      <TopEmojisBarChart />
      <EntityTable items={items} />
    </div>
  );
}


