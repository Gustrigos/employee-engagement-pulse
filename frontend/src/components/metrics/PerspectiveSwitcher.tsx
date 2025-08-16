"use client";
import * as React from "react";
import type { Perspective } from "@/types/metrics";

export function PerspectiveSwitcher({ value, onChange }: { value: Perspective; onChange: (v: Perspective) => void }) {
  const options: Perspective[] = ["channel", "team", "employee"];
  const label: Record<Perspective, string> = { channel: "Channel", team: "Team", employee: "Employee" };
  return (
    <div className="inline-flex items-center gap-1 rounded-md border border-black/10 dark:border-white/10 p-1 text-xs">
      {options.map((opt) => (
        <button
          key={opt}
          type="button"
          onClick={() => onChange(opt)}
          className={`rounded px-2 py-1 ${value === opt ? "bg-black/5 dark:bg-white/10" : "hover:bg-black/5 dark:hover:bg-white/10"}`}
        >
          {label[opt]}
        </button>
      ))}
    </div>
  );
}


