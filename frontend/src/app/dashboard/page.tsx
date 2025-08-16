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

export default function DashboardPage() {
  // In the future, lift this state to a store/context if needed across pages
  const [range, setRange] = React.useState<TimeRange>("week");
  const [kpi, setKpi] = React.useState<{ avgSentiment: number; burnoutRiskCount: number; monitoredChannels: number } | null>(null);
  const [trend, setTrend] = React.useState<{ date: string; label: string; avgSentiment: number; messageCount: number }[]>([]);
  const [channelMetrics, setChannelMetrics] = React.useState<{ id: string; name: string; avgSentiment: number; messages: number; threads: number; lastActivity: string; risk: "Low" | "Medium" | "High" }[]>([]);

  React.useEffect(() => {
    let aborted = false;
    (async () => {
      try {
        const [kpiRes, trendRes, channelsRes] = await Promise.all([
          fetchDashboardKpi({ range }),
          fetchDashboardTrend({ range }),
          fetchDashboardChannels({ range }),
        ]);
        if (aborted) return;
        setKpi(kpiRes);
        setTrend(trendRes);
        setChannelMetrics(channelsRes);
      } catch {
        if (!aborted) {
          setKpi({ avgSentiment: 0, burnoutRiskCount: 0, monitoredChannels: 0 });
          setTrend([]);
          setChannelMetrics([]);
        }
      }
    })();
    return () => { aborted = true; };
  }, [range]);
  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-semibold tracking-tight">Dashboard</h1>
        <TimeRangeSelector value={range} onChange={setRange} />
      </div>
      {kpi && <DashboardSummary kpi={kpi} />}
      <SentimentTrendChart data={trend} />
      <BurnoutLineChart range={range} />
      <HeatmapMatrix range={range} />
      <ChannelMetricsTable data={channelMetrics} />
    </div>
  );
}


