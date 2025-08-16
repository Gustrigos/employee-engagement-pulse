"use client";
import * as React from "react";
import { DashboardSummary } from "@/components/dashboard/DashboardSummary";
import { SentimentTrendChart } from "@/components/dashboard/SentimentTrendChart";
import { BurnoutLineChart } from "@/components/dashboard/BurnoutLineChart";
import { HeatmapMatrix } from "@/components/dashboard/HeatmapMatrix";
import { ChannelMetricsTable } from "@/components/dashboard/ChannelMetricsTable";
import { TimeRange } from "@/types/dashboard";
import { fetchDashboardKpi, fetchDashboardChannels, fetchDashboardTrend } from "@/lib/metrics";
import { TimeRangeSelector } from "@/components/dashboard/TimeRangeSelector";
import { useSlackChannels } from "@/hooks/settings/useSlackChannels";

export default function DashboardPage() {
  // In the future, lift this state to a store/context if needed across pages
  const [range, setRange] = React.useState<TimeRange>("week");
  const { channels: selectedChannels } = useSlackChannels({ eagerSuggestions: false });
  const [kpi, setKpi] = React.useState<{ avgSentiment: number; burnoutRiskCount: number; monitoredChannels: number } | null>(null);
  const [trend, setTrend] = React.useState<{ date: string; label: string; avgSentiment: number; messageCount: number }[]>([]);
  const [channelMetrics, setChannelMetrics] = React.useState<{ id: string; name: string; avgSentiment: number; messages: number; threads: number; lastActivity: string; risk: "Low" | "Medium" | "High" }[]>([]);

  React.useEffect(() => {
    let aborted = false;
    (async () => {
      const ids = selectedChannels.map((c) => c.id);
      if (ids.length === 0) {
        if (!aborted) {
          setKpi({ avgSentiment: 0, burnoutRiskCount: 0, monitoredChannels: 0 });
          setTrend([]);
          setChannelMetrics([]);
        }
        return;
      }
      // Kick off requests independently so faster ones render first
      fetchDashboardKpi({ range, channelIds: ids })
        .then((k) => { if (!aborted) setKpi(k); })
        .catch(() => { if (!aborted) setKpi({ avgSentiment: 0, burnoutRiskCount: 0, monitoredChannels: 0 }); });
      fetchDashboardChannels({ range, channelIds: ids })
        .then((c) => { if (!aborted) setChannelMetrics(c); })
        .catch(() => { if (!aborted) setChannelMetrics([]); });
      fetchDashboardTrend({ range, channelIds: ids })
        .then((t) => { if (!aborted) setTrend(t); })
        .catch(() => { if (!aborted) setTrend([]); });
    })();
    return () => { aborted = true; };
  }, [range, selectedChannels]);
  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-semibold tracking-tight">Dashboard</h1>
        <TimeRangeSelector value={range} onChange={setRange} />
      </div>
      {kpi ? <DashboardSummary kpi={kpi} /> : <div className="rounded-lg border border-black/10 dark:border-white/10 p-4 text-sm text-foreground/60">Loading KPI…</div>}
      {selectedChannels.length > 0 && (
        <div className="text-sm text-foreground/70">Selected channels: {selectedChannels.map((c) => `#${c.name || c.id}`).join(", ")}</div>
      )}
      {trend.length > 0 ? <SentimentTrendChart data={trend} /> : <div className="rounded-lg border border-black/10 dark:border-white/10 p-4 text-sm text-foreground/60">Loading trend…</div>}
      <BurnoutLineChart range={range} />
      <HeatmapMatrix range={range} />
      {channelMetrics.length > 0 ? <ChannelMetricsTable data={channelMetrics} /> : <div className="rounded-lg border border-black/10 dark:border-white/10 p-4 text-sm text-foreground/60">Loading channels…</div>}
    </div>
  );
}


