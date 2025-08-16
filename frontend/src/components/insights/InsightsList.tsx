"use client";
import * as React from "react";
import type { Insight } from "@/types/insights";
import { InsightCard } from "@/components/insights/InsightCard";

interface Props {
  items: Insight[];
  onDismiss?: (id: string) => void;
}

export function InsightsList({ items, onDismiss }: Props) {
  if (!items.length) {
    return (
      <div className="rounded-md border border-black/10 dark:border-white/10 p-6 text-center text-sm text-foreground/70">
        No insights match your filters right now.
      </div>
    );
  }
  return (
    <div className="grid grid-cols-1 gap-4">
      {items.map((insight) => (
        <InsightCard key={insight.id} insight={insight} onDismiss={onDismiss} />
      ))}
    </div>
  );
}


