"use client";
import * as React from "react";
import type { ColumnDef } from "@tanstack/react-table";
import { useReactTable, getCoreRowModel, flexRender } from "@tanstack/react-table";
import type { ChannelMetric } from "@/types/dashboard";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { Lightbulb } from "lucide-react";

const columns: ColumnDef<ChannelMetric>[] = [
  {
    accessorKey: "name",
    header: "Channel",
    cell: ({ row }) => <span>#{row.getValue("name")}</span>,
  },
  {
    accessorKey: "avgSentiment",
    header: "Avg Sentiment",
    cell: ({ row }) => <span>{Number(row.getValue("avgSentiment")).toFixed(2)}</span>,
  },
  { accessorKey: "messages", header: "Messages" },
  { accessorKey: "threads", header: "Threads" },
  {
    accessorKey: "lastActivity",
    header: "Last Activity",
    cell: ({ row }) => new Date(row.getValue<string>("lastActivity")).toLocaleDateString(),
  },
  { accessorKey: "risk", header: "Risk" },
];

export function ChannelMetricsTable({ data }: { data: ChannelMetric[] }) {
  const table = useReactTable({ data, columns, getCoreRowModel: getCoreRowModel() });

  return (
    <div className="rounded-lg border border-black/10 dark:border-white/10 p-4">
      <h2 className="mb-4 text-sm font-medium">Channel Metrics</h2>
      <Table>
        <TableHeader>
          {table.getHeaderGroups().map((hg) => (
            <TableRow key={hg.id}>
              {hg.headers.map((header) => (
                <TableHead key={header.id}>
                  {header.isPlaceholder ? null : flexRender(header.column.columnDef.header, header.getContext())}
                </TableHead>
              ))}
            </TableRow>
          ))}
        </TableHeader>
        <TableBody>
          {table.getRowModel().rows?.length ? (
            table.getRowModel().rows.map((row) => (
              <TableRow key={row.id}>
                {row.getVisibleCells().map((cell) => (
                  <TableCell key={cell.id}>{flexRender(cell.column.columnDef.cell, cell.getContext())}</TableCell>
                ))}
              </TableRow>
            ))
          ) : (
            <TableRow>
              <TableCell colSpan={columns.length} className="h-24 text-center">
                No results.
              </TableCell>
            </TableRow>
          )}
        </TableBody>
      </Table>
      <div className="mt-3 rounded-md bg-black/5 dark:bg-white/5 p-3 text-xs text-foreground/80 flex items-start gap-2">
        <Lightbulb className="h-4 w-4 mt-0.5" />
        <div>
          Channels with low sentiment and high thread counts may indicate misalignment. Try a brief sync when threads exceed ~20 replies.
        </div>
      </div>
    </div>
  );
}


