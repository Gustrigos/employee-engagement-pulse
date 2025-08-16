"use client";
import * as React from "react";
import type { TimeRange } from "@/types/dashboard";
import type { Perspective, EntityTotalMetric, MetricKey } from "@/types/metrics";
import { getEntityTotals } from "@/mocks/metrics";

export function useMetrics(initial: { range?: TimeRange; perspective?: Perspective; metric?: MetricKey } = {}) {
  const [range, setRange] = React.useState<TimeRange>(initial.range || "week");
  const [perspective, setPerspective] = React.useState<Perspective>(initial.perspective || "employee");
  const [metric, setMetric] = React.useState<MetricKey>(initial.metric || "messages");

  const items: EntityTotalMetric[] = React.useMemo(() => getEntityTotals(range, perspective), [range, perspective]);
  const top = React.useMemo(() => {
    const m = metric;
    return [...items].sort((a, b) => (b[m] as number) - (a[m] as number));
  }, [items, metric]);

  return {
    range,
    setRange,
    perspective,
    setPerspective,
    metric,
    setMetric,
    items,
    top,
  } as const;
}


