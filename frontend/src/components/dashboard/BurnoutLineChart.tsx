"use client";
import * as React from "react";
import { ResponsiveContainer, LineChart, Line, XAxis, YAxis, Tooltip } from "recharts";
import type { TimeRange } from "@/types/dashboard";
import { getBurnoutSeries } from "@/mocks/dashboard";
import { useSlackChannels } from "@/hooks/settings/useSlackChannels";
import { fetchDashboardBurnoutSeries } from "@/lib/metrics";
import { Lightbulb } from "lucide-react";

type Group = "team" | "person";

export function BurnoutLineChart({ range }: { range: TimeRange }) {
  const [group, setGroup] = React.useState<Group>("team");
  const { channels: selectedChannels } = useSlackChannels({ eagerSuggestions: false });
  const [series, setSeries] = React.useState<Record<string, { label: string; value: number }[]>>({});

  React.useEffect(() => {
    let aborted = false;
    (async () => {
      const ids = selectedChannels.map((c) => c.id);
      if (ids.length === 0) { setSeries({}); return; }
      // Backend provides channels-as-teams burnout series now
      const resp = await fetchDashboardBurnoutSeries({ range, channelIds: ids });
      if (aborted) return;
      setSeries(resp.series);
    })();
    return () => { aborted = true; };
  }, [range, selectedChannels]);

  const keys = Object.keys(series);
  const colors = ["#ef4444", "#f59e0b", "#22c55e", "#3b82f6", "#a855f7", "#06b6d4"]; // light palette

  // Build data array where each entry is { label, [entityName]: value }
  type Row = { label: string } & Record<string, number>;
  const data: Row[] = (series[keys[0]] || []).map((pt, idx) => {
    const row: Record<string, number | string> = { label: pt.label };
    keys.forEach((k) => (row[k] = series[k][idx]?.value ?? 0));
    return row as Row;
  });

  return (
    <div className="rounded-lg border border-black/10 dark:border-white/10 p-4">
      <div className="mb-3 flex items-center justify-between">
        <h2 className="text-sm font-medium">Burnout Warnings</h2>
        <div className="flex items-center gap-2">
          <label htmlFor="burnout-group" className="text-xs text-foreground/70">
            Group by
          </label>
          <select
            id="burnout-group"
            value={group}
            onChange={(e) => setGroup(e.target.value as Group)}
            className="rounded-md border border-black/10 dark:border-white/10 bg-transparent px-2 py-1 text-xs"
          >
            <option value="team">Team</option>
            <option value="person">Person</option>
          </select>
        </div>
      </div>
      <div className="h-64 w-full">
        <ResponsiveContainer width="100%" height="100%">
          <LineChart data={data} margin={{ left: 8, right: 8 }}>
            <XAxis dataKey="label" />
            <YAxis allowDecimals={false} />
            <Tooltip cursor={false} />
            {keys.map((k, idx) => (
              <Line key={k} type="monotone" dataKey={k} stroke={colors[idx % colors.length]} strokeWidth={2} dot={false} />
            ))}
          </LineChart>
        </ResponsiveContainer>
      </div>
      <div className="mt-3 rounded-md bg-black/5 dark:bg-white/5 p-3 text-xs text-foreground/80 flex items-start gap-2">
        <Lightbulb className="h-4 w-4 mt-0.5" />
        <div>
          Spikes clustered after hours can indicate overload. Rebalance workload and encourage using office hours threads to reduce late pings.
        </div>
      </div>
    </div>
  );
}


