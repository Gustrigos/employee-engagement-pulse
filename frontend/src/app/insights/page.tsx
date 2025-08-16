"use client";
import * as React from "react";
import { TimeRangeSelector } from "@/components/dashboard/TimeRangeSelector";
import { InsightCard } from "@/components/insights/InsightCard";
import { getTeamInsights } from "@/mocks/insights";
import type { TimeRange } from "@/types/dashboard";

export default function InsightsPage() {
  const [range, setRange] = React.useState<TimeRange>("week");
  const all = React.useMemo(() => getTeamInsights(range), [range]);
  const top = React.useMemo(() => {
    return [...all]
      .sort((a, b) => {
        const sevRank = { High: 3, Medium: 2, Low: 1 } as const;
        if (sevRank[b.severity] !== sevRank[a.severity]) return sevRank[b.severity] - sevRank[a.severity];
        return b.confidence - a.confidence;
      })
      .slice(0, 3);
  }, [all]);

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-semibold tracking-tight">Insights</h1>
        <TimeRangeSelector value={range} onChange={setRange} />
      </div>
      <div className="grid grid-cols-1 gap-4">
        {top.map((insight) => (
          <InsightCard key={insight.id} insight={insight} />
        ))}
      </div>
    </div>
  );
}


