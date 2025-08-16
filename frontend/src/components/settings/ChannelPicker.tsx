"use client";
import * as React from "react";
import type { SlackChannel } from "@/types/slack";
import { Button } from "@/components/ui/button";
import { X, Plus, Trash2 } from "lucide-react";

interface Props {
  value: SlackChannel[];
  suggestions: SlackChannel[];
  onAddByName: (name: string) => void;
  onAddMany: (channels: SlackChannel[]) => void;
  onRemove: (id: string) => void;
  onClear: () => void;
}

export function ChannelPicker({ value, suggestions, onAddByName, onAddMany, onRemove, onClear }: Props) {
  const [input, setInput] = React.useState("");
  // Show suggestions by default; user can hide
  const [open, setOpen] = React.useState(true);

  function submit(e: React.FormEvent) {
    e.preventDefault();
    onAddByName(input);
    setInput("");
  }

  return (
    <div className="space-y-4">
      {/* Tracked channels at the top */}
      <div className="flex items-center justify-between">
        <p className="text-sm font-medium">Tracked Channels</p>
        {value.length > 0 && (
          <button
            type="button"
            onClick={onClear}
            className="inline-flex items-center gap-1 rounded-md border border-black/10 dark:border-white/10 px-2 py-1 text-xs hover:bg-black/5 dark:hover:bg-white/10"
          >
            <Trash2 className="h-3 w-3" /> Clear all
          </button>
        )}
      </div>

      {value.length === 0 ? (
        <p className="text-sm text-foreground/60">No channels selected.</p>
      ) : (
        <ul className="flex flex-wrap gap-2">
          {value.map((ch) => (
            <li
              key={ch.id}
              className="inline-flex items-center gap-1 rounded-full border border-black/10 dark:border-white/10 px-2 py-1 text-sm"
            >
              <span>#{ch.name}</span>
              <button
                type="button"
                onClick={() => onRemove(ch.id)}
                className="rounded-full p-1 hover:bg-black/5 dark:hover:bg-white/10"
                aria-label={`Remove ${ch.name}`}
                title={`Remove ${ch.name}`}
              >
                <X className="h-3 w-3" />
              </button>
            </li>
          ))}
        </ul>
      )}

      {/* Manual add input */}
      <form onSubmit={submit} className="flex gap-2">
        <input
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="#channel-name"
          className="flex-1 rounded-md border border-black/10 dark:border-white/10 bg-transparent px-3 py-2 text-sm outline-none focus:ring-2 focus:ring-foreground/20"
        />
        <Button type="submit" size="md" className="shrink-0">
          <Plus className="mr-1 h-4 w-4" /> Add
        </Button>
      </form>

      {/* Suggestions list */}
      <div>
        <button
          type="button"
          onClick={() => setOpen((v) => !v)}
          className="text-xs text-foreground/70 hover:underline"
        >
          {open ? "Hide suggestions" : "Show suggestions"}
        </button>
        {open && (
          <div className="mt-2 grid grid-cols-2 gap-2 md:grid-cols-3">
            {suggestions.map((s) => (
              <button
                key={s.id}
                type="button"
                onClick={() => onAddMany([s])}
                className="rounded-md border border-black/10 dark:border-white/10 px-3 py-2 text-left text-sm hover:bg-black/5 dark:hover:bg-white/10"
              >
                #{s.name}
              </button>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}


