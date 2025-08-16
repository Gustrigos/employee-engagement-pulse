import { NextRequest, NextResponse } from "next/server";

const BACKEND_BASE = (process.env.NEXT_PUBLIC_API_BASE_URL || "http://127.0.0.1:8000").replace(/\/$/, "");

export async function GET(req: NextRequest) {
  const url = new URL(req.url);
  const code = url.searchParams.get("code");
  const state = url.searchParams.get("state");
  if (!code || !state) {
    return NextResponse.redirect(new URL("/settings?slack_oauth=missing_params", url.origin));
  }
  const redirectUri = `${url.origin}${url.pathname}`;

  try {
    const resp = await fetch(`${BACKEND_BASE}/api/v1/slack/oauth/exchange`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ code, state, redirectUri }),
      cache: "no-store",
    });
    const data = await resp.json();
    const target = (data?.returnTo as string | undefined) || "/settings?slack_oauth=ok";
    return NextResponse.redirect(new URL(target, url.origin));
  } catch {
    return NextResponse.redirect(new URL("/settings?slack_oauth=error", url.origin));
  }
}


