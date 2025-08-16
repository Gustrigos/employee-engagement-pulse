"use client";
import * as React from "react";
import type { TimeRange, RiskLevel } from "@/types/dashboard";
import { TimeRangeSelector } from "@/components/dashboard/TimeRangeSelector";
import { Button } from "@/components/ui/button";

interface Props {
  range: TimeRange;
  onRangeChange: (v: TimeRange) => void;
  teams: string[];
  selectedTeams: string[];
  toggleTeam: (team: string) => void;
  selectedSeverities: RiskLevel[];
  toggleSeverity: (sev: RiskLevel) => void;
  clearFilters: () => void;
}

const SEVERITIES: RiskLevel[] = ["High", "Medium", "Low"];

export function InsightsFilters({
  range,
  onRangeChange,
  teams,
  selectedTeams,
  toggleTeam,
  selectedSeverities,
  toggleSeverity,
  clearFilters,
}: Props) {
  return (
    <div className="flex flex-wrap items-center gap-3">
      <TimeRangeSelector value={range} onChange={onRangeChange} />
      <div className="h-5 w-px bg-black/10 dark:bg-white/10" />
      <div className="flex items-center gap-2 text-xs">
        <span className="text-foreground/60">Teams:</span>
        {teams.map((t) => {
          const active = selectedTeams.includes(t);
          return (
            <button
              key={t}
              type="button"
              onClick={() => toggleTeam(t)}
              className={`rounded border px-2 py-1 ${
                active
                  ? "border-black/20 bg-black/5 dark:border-white/20 dark:bg-white/10"
                  : "border-transparent hover:bg-black/5 dark:hover:bg-white/10"
              }`}
            >
              {t}
            </button>
          );
        })}
      </div>
      <div className="h-5 w-px bg-black/10 dark:bg-white/10" />
      <div className="flex items-center gap-2 text-xs">
        <span className="text-foreground/60">Severity:</span>
        {SEVERITIES.map((s) => {
          const active = selectedSeverities.includes(s);
          return (
            <button
              key={s}
              type="button"
              onClick={() => toggleSeverity(s)}
              className={`rounded border px-2 py-1 ${
                active
                  ? "border-black/20 bg-black/5 dark:border-white/20 dark:bg-white/10"
                  : "border-transparent hover:bg-black/5 dark:hover:bg-white/10"
              }`}
            >
              {s}
            </button>
          );
        })}
      </div>
      <div className="h-5 w-px bg-black/10 dark:bg-white/10" />
      <Button size="sm" variant="secondary" onClick={clearFilters}>
        Clear filters
      </Button>
    </div>
  );
}


