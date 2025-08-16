"use client";
import * as React from "react";
import type { TimeRange } from "@/types/dashboard";

interface Props {
  value: TimeRange;
  onChange: (v: TimeRange) => void;
}

export function TimeRangeSelector({ value, onChange }: Props) {
  return (
    <div className="inline-flex items-center gap-1 rounded-md border border-black/10 dark:border-white/10 p-1 text-xs">
      {([
        ["week", "Week"],
        ["month", "Month"],
        ["quarter", "Quarter"],
        ["year", "Year"],
      ] as [TimeRange, string][]).map(([key, label]) => (
        <button
          key={key}
          type="button"
          onClick={() => onChange(key)}
          className={`rounded px-2 py-1 ${value === key ? "bg-black/5 dark:bg-white/10" : "hover:bg-black/5 dark:hover:bg-white/10"}`}
        >
          {label}
        </button>
      ))}
    </div>
  );
}


