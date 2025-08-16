import Link from "next/link";
import { Gauge, Settings, Lightbulb, BarChart4 } from "lucide-react";

const navItems = [
  { href: "/dashboard", label: "Overview", icon: Gauge },
  { href: "/insights", label: "Insights", icon: Lightbulb },
  { href: "/metrics", label: "Metrics", icon: BarChart4 },
  { href: "/settings", label: "Settings", icon: Settings },
];

export function Sidebar() {
  return (
    <aside className="hidden md:block border-r border-black/10 dark:border-white/10 w-60 p-4">
      <nav className="flex flex-col gap-2">
        {navItems.map((item) => (
          <Link
            key={item.href}
            href={item.href}
            className="flex items-center gap-2 rounded-md px-3 py-2 text-sm hover:bg-black/5 dark:hover:bg-white/10"
          >
            <item.icon className="h-4 w-4" />
            <span>{item.label}</span>
          </Link>
        ))}
      </nav>
    </aside>
  );
}


