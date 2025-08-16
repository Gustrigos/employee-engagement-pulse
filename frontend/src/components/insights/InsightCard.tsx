"use client";
import * as React from "react";
import { Lightbulb, AlertTriangle, CheckCircle2, Tag } from "lucide-react";
import type { Insight } from "@/types/insights";
import { Button } from "@/components/ui/button";

interface Props {
  insight: Insight;
  onDismiss?: (id: string) => void;
}

function severityStyles(sev: Insight["severity"]) {
  if (sev === "High") return "bg-red-100 text-red-800 dark:bg-red-950/50 dark:text-red-300";
  if (sev === "Medium") return "bg-amber-100 text-amber-900 dark:bg-amber-950/50 dark:text-amber-300";
  return "bg-emerald-100 text-emerald-900 dark:bg-emerald-950/50 dark:text-emerald-300";
}

export function InsightCard({ insight, onDismiss }: Props) {
  const Icon = insight.severity === "High" ? AlertTriangle : Lightbulb;
  return (
    <div className="rounded-lg border border-black/10 dark:border-white/10 p-4">
      <div className="flex items-start gap-3">
        <div className="mt-0.5">
          <Icon className="h-5 w-5 text-foreground/80" />
        </div>
        <div className="flex-1">
          <div className="flex flex-wrap items-center gap-2">
            {insight.team ? (
              <span className="inline-flex items-center rounded-md bg-black/5 dark:bg-white/10 px-2 py-0.5 text-xs">
                Team: {insight.team}
              </span>
            ) : null}
            <span className={`inline-flex items-center rounded-md px-2 py-0.5 text-xs ${severityStyles(insight.severity)}`}>
              {insight.severity} priority
            </span>
            <span className="ml-auto text-xs text-foreground/60">
              {new Date(insight.createdAt).toLocaleString()}
            </span>
          </div>
          <h3 className="mt-2 text-sm font-semibold tracking-tight">{insight.title}</h3>
          <p className="mt-1 text-sm text-foreground/80">{insight.summary}</p>
          <div className="mt-3 rounded-md bg-black/5 dark:bg-white/5 p-3">
            <div className="flex items-center gap-2 text-xs font-medium">
              <CheckCircle2 className="h-4 w-4" />
              Recommended action
            </div>
            <p className="mt-1 text-sm text-foreground/80">{insight.recommendation}</p>
          </div>
          {insight.tags?.length ? (
            <div className="mt-3 flex flex-wrap items-center gap-2">
              {insight.tags.map((t) => (
                <span key={t} className="inline-flex items-center gap-1 rounded-md border border-black/10 dark:border-white/10 px-2 py-0.5 text-xs text-foreground/70">
                  <Tag className="h-3 w-3" /> {t}
                </span>
              ))}
            </div>
          ) : null}
        </div>
      </div>
      <div className="mt-4 flex items-center gap-2">
        <Button size="sm" variant="default" onClick={() => onDismiss?.(insight.id)}>
          Dismiss
        </Button>
        <Button size="sm" variant="secondary" onClick={() => onDismiss?.(insight.id)}>
          Mark as done
        </Button>
        <div className="ml-auto text-xs text-foreground/60">Confidence: {(insight.confidence * 100).toFixed(0)}%</div>
      </div>
    </div>
  );
}


