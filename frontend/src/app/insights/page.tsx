"use client";
import * as React from "react";
import { useInsights } from "@/hooks/useInsights";
import { InsightsFilters } from "@/components/insights/InsightsFilters";
import { InsightsList } from "@/components/insights/InsightsList";

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
    dismiss,
  } = useInsights("week");

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
      <InsightsList items={insights} onDismiss={dismiss} />
    </div>
  );
}


