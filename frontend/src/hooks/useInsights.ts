"use client";
import * as React from "react";
import type { TimeRange, RiskLevel } from "@/types/dashboard";
import type { Insight } from "@/types/insights";

export function useInsights(initialRange: TimeRange = "week") {
  const [range, setRange] = React.useState<TimeRange>(initialRange);
  const [selectedTeams, setSelectedTeams] = React.useState<string[]>([]);
  const [selectedSeverities, setSelectedSeverities] = React.useState<RiskLevel[]>([]);
  const [dismissedIds, setDismissedIds] = React.useState<Set<string>>(new Set());
  const [raw, setRaw] = React.useState<Insight[]>([]);

  // Fetch from backend API (proxied via Next app route)
  React.useEffect(() => {
    let aborted = false;
    async function load() {
      try {
        const res = await fetch(`/api/insights/teams?range=${range}&limit=5`, { cache: "no-store" });
        if (!res.ok) throw new Error(`Failed to load insights: ${res.status}`);
        const data: Insight[] = await res.json();
        if (!aborted) setRaw(Array.isArray(data) ? data : []);
      } catch {
        if (!aborted) setRaw([]);
      }
    }
    load();
    return () => {
      aborted = true;
    };
  }, [range]);

  const allTeams = React.useMemo(() => {
    const names = new Set<string>();
    for (const i of raw) if (i.team) names.add(i.team);
    return Array.from(names);
  }, [raw]);

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


