import type { KPI, SentimentPoint, ChannelMetric, RiskLevel, TimeRange, BurnoutPoint } from "@/types/dashboard";

function formatDate(date: Date): string {
  return date.toISOString().slice(0, 10);
}

function dayLabel(date: Date): string {
  return date.toLocaleDateString(undefined, { weekday: "short" });
}

export function getTrend(range: TimeRange = "week"): SentimentPoint[] {
  const out: SentimentPoint[] = [];
  const now = new Date();
  const steps = range === "week" ? 7 : range === "month" ? 30 : range === "quarter" ? 12 : 12; // month=30 days, quarter=12 weeks, year=12 months
  for (let i = steps - 1; i >= 0; i--) {
    const d = new Date(now);
    if (range === "week" || range === "month") {
      d.setDate(now.getDate() - i);
    } else {
      d.setDate(now.getDate() - i * (range === "quarter" ? 7 : 30));
    }
    const seed = (i * 9301 + 49297) % 233280;
    const sentiment = ((seed / 233280) * 2 - 1) * 0.8; // -0.8..0.8
    const messages = Math.floor(30 + (seed % 40));
    out.push({
      date: formatDate(d),
      label:
        range === "week"
          ? dayLabel(d)
          : range === "month"
          ? d.getDate().toString()
          : d.toLocaleDateString(undefined, { month: "short" }),
      avgSentiment: Number(sentiment.toFixed(2)),
      messageCount: messages,
    });
  }
  return out;
}

function riskFromSentiment(value: number): RiskLevel {
  if (value < -0.2) return "High";
  if (value < 0.2) return "Medium";
  return "Low";
}

export function getChannelMetrics(): ChannelMetric[] {
  const channels = [
    { id: "C-general", name: "general" },
    { id: "C-eng", name: "eng-announcements" },
    { id: "C-random", name: "random" },
    { id: "C-product", name: "product" },
    { id: "C-support", name: "support" },
    { id: "C-design", name: "design" },
  ];
  return channels.map((c, idx) => {
    const seed = (idx * 1103515245 + 12345) % 2147483647;
    const sentiment = (((seed % 1000) / 1000) * 2 - 1) * 0.9;
    const messages = 50 + (seed % 150);
    const threads = 5 + (seed % 20);
    const daysAgo = (seed % 14) + 1;
    const last = new Date();
    last.setDate(last.getDate() - daysAgo);
    return {
      id: c.id,
      name: c.name,
      avgSentiment: Number(sentiment.toFixed(2)),
      messages,
      threads,
      lastActivity: last.toISOString(),
      risk: riskFromSentiment(sentiment),
    } satisfies ChannelMetric;
  });
}

export function getDashboardKpi(): KPI {
  const channels = getChannelMetrics();
  const avg =
    channels.reduce((sum, c) => sum + c.avgSentiment, 0) /
    Math.max(1, channels.length);
  const burnout = channels.filter((c) => c.risk === "High").length;
  return {
    avgSentiment: Number(avg.toFixed(2)),
    burnoutRiskCount: burnout,
    monitoredChannels: channels.length,
  };
}

export function getBurnoutSeries(range: TimeRange = "week", group: "team" | "person" = "team"): { label: string; series: Record<string, BurnoutPoint[]> } {
  const entities = group === "team" ? ["Eng", "Design", "Support", "Product"] : ["Alice", "Bob", "Carol", "Diego", "Eve"];
  const steps = range === "week" ? 7 : range === "month" ? 30 : range === "quarter" ? 12 : 12;
  const labeler = (i: number, d: Date) =>
    range === "week" ? dayLabel(d) : range === "month" ? d.getDate().toString() : d.toLocaleDateString(undefined, { month: "short" });
  const result: Record<string, BurnoutPoint[]> = {};
  entities.forEach((name, idx) => {
    const arr: BurnoutPoint[] = [];
    for (let i = steps - 1; i >= 0; i--) {
      const d = new Date();
      if (range === "week" || range === "month") d.setDate(d.getDate() - i);
      else d.setDate(d.getDate() - i * (range === "quarter" ? 7 : 30));
      const seed = (i + 1) * (idx + 2) * 97;
      arr.push({ label: labeler(i, d), value: seed % 3 });
    }
    result[name] = arr;
  });
  return { label: group === "team" ? "Teams" : "People", series: result };
}

export function getHeatmapMatrix(
  grouping: "channels" | "teams" | "people",
  metric: "sentiment" | "messages" | "threads",
  range: TimeRange = "week"
) {
  const rows =
    grouping === "channels"
      ? ["general", "eng-announcements", "random", "product", "support"]
      : grouping === "teams"
      ? ["Eng", "Design", "Support", "Product"]
      : ["Alice", "Bob", "Carol", "Diego", "Eve"];

  function monthAbbr(d: Date) {
    return d.toLocaleDateString(undefined, { month: "short" });
  }

  let cols: string[] = [];
  if (range === "week") {
    cols = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"];
  } else if (range === "month") {
    cols = ["1–7", "8–14", "15–21", "22–28", "29–31"];
  } else if (range === "quarter") {
    // last 3 months including current
    const now = new Date();
    const months: string[] = [];
    for (let i = 2; i >= 0; i--) {
      const d = new Date(now);
      d.setMonth(now.getMonth() - i);
      months.push(monthAbbr(d));
    }
    cols = months;
  } else {
    // year: last 12 months including current
    const now = new Date();
    const months: string[] = [];
    for (let i = 11; i >= 0; i--) {
      const d = new Date(now);
      d.setMonth(now.getMonth() - i);
      months.push(monthAbbr(d));
    }
    cols = months;
  }

  const values = rows.map((_, ri) =>
    cols.map((_, ci) => {
      const seed = (ri + 1) * (ci + 2) * 137;
      if (metric === "sentiment") {
        return (((seed % 1000) / 1000) * 2 - 1) * 0.9; // -0.9..0.9
      }
      // scale 0..1 for messages/threads
      return (seed % 100) / 100;
    })
  );
  return { rows, cols, values };
}


