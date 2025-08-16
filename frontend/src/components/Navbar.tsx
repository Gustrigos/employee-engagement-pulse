"use client";
import Link from "next/link";
import { Menu } from "lucide-react";
import { Button } from "@/components/ui/button";

export function Navbar() {
  return (
    <header className="sticky top-0 z-30 w-full border-b border-black/10 dark:border-white/10 bg-background/80 backdrop-blur-sm">
      <div className="mx-auto flex h-14 max-w-6xl items-center gap-3 px-4">
        <Button variant="ghost" size="icon" aria-label="Open menu">
          <Menu className="h-5 w-5" />
        </Button>
        <Link href="/" className="text-sm font-semibold tracking-tight">
          Employee Engagement Pulse
        </Link>
        <div className="ml-auto flex items-center gap-2">
          <Link
            href="/insights"
            className="text-sm text-foreground/80 hover:text-foreground"
          >
            Insights
          </Link>
          <Link
            href="/settings"
            className="text-sm text-foreground/80 hover:text-foreground"
          >
            Settings
          </Link>
        </div>
      </div>
    </header>
  );
}


