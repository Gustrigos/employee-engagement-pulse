"use client";
import * as React from "react";
import { getHeatmapMatrix } from "@/mocks/dashboard";
import type { TimeRange } from "@/types/dashboard";
import { Lightbulb } from "lucide-react";

type Metric = "sentiment" | "messages" | "threads";
type Grouping = "channels" | "teams" | "people";

export function HeatmapMatrix({ range = "week" as TimeRange }: { range?: TimeRange }) {
  const [metric, setMetric] = React.useState<Metric>("sentiment");
  const [grouping, setGrouping] = React.useState<Grouping>("channels");
  const { rows, cols, values } = getHeatmapMatrix(grouping, metric, range);

  const cellSizePx = 14; // square size
  const gapPx = 6; // space between squares

  function strideForLabels(total: number) {
    if (total <= 6) return 1;
    if (total <= 16) return 2;
    if (total <= 26) return 4;
    return 8; // for 52 weeks
  }
  const labelStride = strideForLabels(cols.length);

  function colorFor(value: number) {
    if (metric === "sentiment") {
      // map -1..1 to light red -> light green
      const t = (value + 1) / 2;
      const r = Math.round(255 - t * 80);
      const g = Math.round(200 + t * 40);
      const b = Math.round(200 - t * 80);
      return `rgb(${r}, ${g}, ${b})`;
    }
    // messages/threads: scale 0..1 -> blue
    const t = Math.max(0, Math.min(1, value));
    const base = 230;
    const delta = Math.round(t * 80);
    return `rgb(${base - delta}, ${base - delta / 2}, 255)`;
  }

  return (
    <div className="rounded-lg border border-black/10 dark:border-white/10 p-4">
      <div className="mb-3 flex flex-wrap items-center gap-3 justify-between">
        <h2 className="text-sm font-medium">Health Heatmap</h2>
        <div className="flex items-center gap-2">
          <label className="text-xs text-foreground/70" htmlFor="hm-group">
            Group
          </label>
          <select
            id="hm-group"
            value={grouping}
            onChange={(e) => setGrouping(e.target.value as Grouping)}
            className="rounded-md border border-black/10 dark:border-white/10 bg-transparent px-2 py-1 text-xs"
          >
            <option value="channels">Channels</option>
            <option value="teams">Teams</option>
            <option value="people">People</option>
          </select>
          <label className="ml-3 text-xs text-foreground/70" htmlFor="hm-metric">
            Metric
          </label>
          <select
            id="hm-metric"
            value={metric}
            onChange={(e) => setMetric(e.target.value as Metric)}
            className="rounded-md border border-black/10 dark:border-white/10 bg-transparent px-2 py-1 text-xs"
          >
            <option value="sentiment">Sentiment</option>
            <option value="messages">Messages</option>
            <option value="threads">Threads</option>
          </select>
        </div>
      </div>

      <div className="overflow-x-auto w-full">
        <div className="min-w-max">
          <div className="flex gap-4">
            <div className="grid" style={{ gridTemplateRows: `24px repeat(${rows.length}, 16px)` }}>
              <div />
              {rows.map((r) => (
                <div key={r} className="text-xs text-foreground/70 leading-4">
                  {r}
                </div>
              ))}
            </div>
            <div
              className="grid p-2"
              style={{
                gridTemplateRows: `24px repeat(${rows.length}, ${cellSizePx}px)`,
                gridTemplateColumns: `repeat(${cols.length}, ${cellSizePx}px)`,
                columnGap: gapPx,
                rowGap: gapPx + 2,
              }}
            >
              {cols.map((c, ci) => (
                <div key={c} className="text-center text-[10px] text-foreground/70 leading-4">
                  {ci % labelStride === 0 ? c : ""}
                </div>
              ))}
              {rows.map((r, ri) =>
                cols.map((c, ci) => {
                  const v = values[ri][ci];
                  const bg = colorFor(v);
                  return (
                    <div
                      key={`${r}-${c}`}
                      className="rounded-[2px] border border-black/10 dark:border-white/10"
                      title={`${r} · ${c}: ${metric === "sentiment" ? v.toFixed(2) : Math.round(v * 100)}`}
                      style={{ background: bg, width: cellSizePx, height: cellSizePx }}
                    />
                  );
                })
              )}
            </div>
          </div>
        </div>
      </div>
      <div className="mt-3 rounded-md bg-black/5 dark:bg-white/5 p-3 text-xs text-foreground/80 flex items-start gap-2">
        <Lightbulb className="h-4 w-4 mt-0.5" />
        <div>
          Concentrated high activity in a few teams with lower sentiment suggests bottlenecks. Pair seniors with juniors and clarify owners to spread load.
        </div>
      </div>
    </div>
  );
}


