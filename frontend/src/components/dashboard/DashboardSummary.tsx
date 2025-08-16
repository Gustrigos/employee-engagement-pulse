import type { KPI } from "@/types/dashboard";

export function DashboardSummary({ kpi }: { kpi: KPI }) {
  return (
    <div className="grid grid-cols-1 gap-4 md:grid-cols-2 lg:grid-cols-3">
      <div className="rounded-lg border border-black/10 dark:border-white/10 p-4">
        <h2 className="text-sm font-medium">This Week’s Sentiment</h2>
        <p className="mt-2 text-3xl font-semibold">
          {kpi.avgSentiment.toFixed(2)}
        </p>
        <p className="text-xs text-foreground/60">Avg score across channels</p>
      </div>
      <div className="rounded-lg border border-black/10 dark:border-white/10 p-4">
        <h2 className="text-sm font-medium">Burnout Risk</h2>
        <p className="mt-2 text-3xl font-semibold">{kpi.burnoutRiskCount}</p>
        <p className="text-xs text-foreground/60">Auto-detected warnings</p>
      </div>
      <div className="rounded-lg border border-black/10 dark:border-white/10 p-4">
        <h2 className="text-sm font-medium">Monitored Channels</h2>
        <p className="mt-2 text-3xl font-semibold">{kpi.monitoredChannels}</p>
        <p className="text-xs text-foreground/60">Configured in Settings</p>
      </div>
    </div>
  );
}


