"use client";
import * as React from "react";
import { DashboardSummary } from "@/components/dashboard/DashboardSummary";
import { SentimentTrendChart } from "@/components/dashboard/SentimentTrendChart";
import { BurnoutLineChart } from "@/components/dashboard/BurnoutLineChart";
import { HeatmapMatrix } from "@/components/dashboard/HeatmapMatrix";
import { ChannelMetricsTable } from "@/components/dashboard/ChannelMetricsTable";
import { TimeRange } from "@/types/dashboard";
import { getDashboardKpi, getTrend, getChannelMetrics } from "@/mocks/dashboard";
import { TimeRangeSelector } from "@/components/dashboard/TimeRangeSelector";

export default function DashboardPage() {
  // In the future, lift this state to a store/context if needed across pages
  const [range, setRange] = React.useState<TimeRange>("week");
  const kpi = getDashboardKpi();
  const trend = getTrend(range);
  const channelMetrics = getChannelMetrics();
  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-semibold tracking-tight">Dashboard</h1>
        <TimeRangeSelector value={range} onChange={setRange} />
      </div>
      <DashboardSummary kpi={kpi} />
      <SentimentTrendChart data={trend} />
      <BurnoutLineChart range={range} />
      <HeatmapMatrix range={range} />
      <ChannelMetricsTable data={channelMetrics} />
    </div>
  );
}


