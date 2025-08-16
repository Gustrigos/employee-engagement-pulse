"use client";
import * as React from "react";
import type { TimeRange, RiskLevel } from "@/types/dashboard";
import type { Insight } from "@/types/insights";
import { getTeamInsights, getAvailableTeams } from "@/mocks/insights";

export function useInsights(initialRange: TimeRange = "week") {
  const [range, setRange] = React.useState<TimeRange>(initialRange);
  const [selectedTeams, setSelectedTeams] = React.useState<string[]>([]);
  const [selectedSeverities, setSelectedSeverities] = React.useState<RiskLevel[]>([]);
  const [dismissedIds, setDismissedIds] = React.useState<Set<string>>(new Set());

  const allTeams = React.useMemo(() => getAvailableTeams(), []);

  const raw = React.useMemo(() => getTeamInsights(range), [range]);

  const insights = React.useMemo(() => {
    return raw
      .filter((i) => !dismissedIds.has(i.id))
      .filter((i) => (selectedTeams.length ? (i.team ? selectedTeams.includes(i.team) : true) : true))
      .filter((i) => (selectedSeverities.length ? selectedSeverities.includes(i.severity) : true));
  }, [raw, dismissedIds, selectedTeams, selectedSeverities]);

  function toggleTeam(team: string) {
    setSelectedTeams((prev) =>
      prev.includes(team) ? prev.filter((t) => t !== team) : [...prev, team]
    );
  }

  function toggleSeverity(sev: RiskLevel) {
    setSelectedSeverities((prev) =>
      prev.includes(sev) ? prev.filter((s) => s !== sev) : [...prev, sev]
    );
  }

  function clearFilters() {
    setSelectedTeams([]);
    setSelectedSeverities([]);
  }

  function dismiss(id: string) {
    setDismissedIds((prev) => new Set([...prev, id]));
  }

  function clearDismissed() {
    setDismissedIds(new Set());
  }

  return {
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
    clearDismissed,
  } as const;
}


