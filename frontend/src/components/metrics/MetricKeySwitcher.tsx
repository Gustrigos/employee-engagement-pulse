"use client";
import * as React from "react";
import type { MetricKey } from "@/types/metrics";

const OPTIONS: MetricKey[] = ["messages", "threads", "responses", "emojis"];
const LABEL: Record<MetricKey, string> = {
  messages: "Messages",
  threads: "Threads",
  responses: "Responses",
  emojis: "Emojis",
};

export function MetricKeySwitcher({ value, onChange }: { value: MetricKey; onChange: (v: MetricKey) => void }) {
  return (
    <div className="inline-flex items-center gap-1 rounded-md border border-black/10 dark:border-white/10 p-1 text-xs">
      {OPTIONS.map((opt) => (
        <button
          key={opt}
          type="button"
          onClick={() => onChange(opt)}
          className={`rounded px-2 py-1 ${value === opt ? "bg-black/5 dark:bg-white/10" : "hover:bg-black/5 dark:hover:bg-white/10"}`}
        >
          {LABEL[opt]}
        </button>
      ))}
    </div>
  );
}


