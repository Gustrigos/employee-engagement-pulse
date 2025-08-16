"use client";
import * as React from "react";
import { InsightsFilters } from "@/components/insights/InsightsFilters";
import { InsightsList } from "@/components/insights/InsightsList";
import { useInsights } from "@/hooks/useInsights";

export default function InsightsPage() {
  const {
    range,
    setRange,
    allTeams,
    selectedTeams,
    toggleTeam,
    selectedSeverities,
    toggleSeverity,
    clearFilters,
    insights,
  } = useInsights("week");

  const top = React.useMemo(() => {
    const sevRank = { High: 3, Medium: 2, Low: 1 } as const;
    return [...insights]
      .sort((a, b) => {
        if (sevRank[b.severity] !== sevRank[a.severity]) return sevRank[b.severity] - sevRank[a.severity];
        return b.confidence - a.confidence;
      })
      .slice(0, 5);
  }, [insights]);

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-semibold tracking-tight">Insights</h1>
      </div>
      <InsightsFilters
        range={range}
        onRangeChange={setRange}
        teams={allTeams}
        selectedTeams={selectedTeams}
        toggleTeam={toggleTeam}
        selectedSeverities={selectedSeverities}
        toggleSeverity={toggleSeverity}
        clearFilters={clearFilters}
      />
      <InsightsList items={top} />
    </div>
  );
}


