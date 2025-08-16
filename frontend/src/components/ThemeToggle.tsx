"use client";
import * as React from "react";

export function ThemeToggle() {
  const [isDark, setIsDark] = React.useState(false);

  React.useEffect(() => {
    if (typeof document === "undefined") return;
    const prefersDark = window.matchMedia("(prefers-color-scheme: dark)").matches;
    const root = document.documentElement;
    const initialDark = root.classList.contains("dark") || prefersDark;
    root.classList.toggle("dark", initialDark);
    setIsDark(initialDark);
  }, []);

  function toggle() {
    if (typeof document === "undefined") return;
    const root = document.documentElement;
    const next = !isDark;
    root.classList.toggle("dark", next);
    setIsDark(next);
  }

  return (
    <button
      type="button"
      onClick={toggle}
      className="inline-flex items-center justify-center rounded-md border border-black/10 dark:border-white/10 px-2 py-1 text-xs text-foreground hover:bg-black/5 dark:hover:bg-white/10"
      aria-label="Toggle theme"
    >
      {isDark ? "Dark" : "Light"}
    </button>
  );
}


