"use client";
import * as React from "react";
import type { TimeRange } from "@/types/dashboard";
import type { Perspective, EntityTotalMetric, MetricKey } from "@/types/metrics";
import { fetchEntityTotals, fetchTopEmojis, type EmojiStat } from "@/lib/metrics";

export function useMetrics(initial: { range?: TimeRange; perspective?: Perspective; metric?: MetricKey } = {}) {
  const [range, setRange] = React.useState<TimeRange>(initial.range || "week");
  const [perspective, setPerspective] = React.useState<Perspective>(initial.perspective || "employee");
  const [metric, setMetric] = React.useState<MetricKey>(initial.metric || "messages");

  const [items, setItems] = React.useState<EntityTotalMetric[]>([]);
  const [emojis, setEmojis] = React.useState<EmojiStat[]>([]);

  React.useEffect(() => {
    let aborted = false;
    (async () => {
      try {
        const [totals, topEmoji] = await Promise.all([
          fetchEntityTotals({ perspective, range }),
          fetchTopEmojis({ range, limit: 10 }),
        ]);
        if (aborted) return;
        setItems(totals);
        setEmojis(topEmoji);
      } catch {
        if (!aborted) {
          setItems([]);
          setEmojis([]);
        }
      }
    })();
    return () => { aborted = true; };
  }, [range, perspective]);

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
    emojis,
    top,
  } as const;
}


