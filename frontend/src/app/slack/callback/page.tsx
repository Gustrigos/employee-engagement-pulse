"use client";
import * as React from "react";
import { useRouter, useSearchParams } from "next/navigation";

async function exchange(code: string, state: string, redirectUri: string) {
  const base = (process.env.NEXT_PUBLIC_API_BASE_URL || "http://127.0.0.1:8000").replace(/\/$/, "");
  const res = await fetch(`${base}/api/v1/slack/oauth/exchange`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ code, state, redirectUri }),
    cache: "no-store",
  });
  if (!res.ok) throw new Error("exchange failed");
  return (await res.json()) as { ok: boolean; returnTo?: string };
}

export default function SlackCallbackPage() {
  const params = useSearchParams();
  const router = useRouter();

  React.useEffect(() => {
    const code = params.get("code");
    const state = params.get("state");
    if (!code || !state) return;
    const redirectUri = typeof window !== "undefined" ? `${window.location.origin}/slack/callback` : "";
    (async () => {
      try {
        const result = await exchange(code, state, redirectUri);
        const target = result.returnTo || "/settings";
        router.replace(target);
      } catch {
        router.replace("/settings");
      }
    })();
  }, [params, router]);

  return (
    <div className="p-6">
      <p className="text-sm text-foreground/70">Completing Slack connection…</p>
    </div>
  );
}
