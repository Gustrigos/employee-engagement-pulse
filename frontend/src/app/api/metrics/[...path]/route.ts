import { NextRequest } from "next/server";

const BACKEND_BASE = (process.env.NEXT_PUBLIC_API_BASE_URL || "http://127.0.0.1:8000").replace(/\/$/, "");

async function proxy(req: NextRequest, path: string[]) {
  const upstreamUrl = new URL(`${BACKEND_BASE}/api/v1/metrics/${path.join("/")}`);
  const search = req.nextUrl.search;
  if (search) upstreamUrl.search = search;

  const init: RequestInit = {
    method: req.method,
    headers: {
      ...(req.headers.get("content-type") ? { "content-type": req.headers.get("content-type") as string } : {}),
    },
    cache: "no-store",
  };

  if (req.method !== "GET" && req.method !== "HEAD") {
    const body = await req.arrayBuffer();
    (init as RequestInit).body = body as unknown as BodyInit;
  }

  const res = await fetch(upstreamUrl, init);
  const text = await res.text();
  return new Response(text, {
    status: res.status,
    headers: {
      "content-type": res.headers.get("content-type") || "application/json",
    },
  });
}

export async function GET(req: NextRequest, ctx: { params: Promise<{ path: string[] }> }) {
  const { path } = await ctx.params;
  return proxy(req, path);
}

export async function POST(req: NextRequest, ctx: { params: Promise<{ path: string[] }> }) {
  const { path } = await ctx.params;
  return proxy(req, path);
}

export async function PUT(req: NextRequest, ctx: { params: Promise<{ path: string[] }> }) {
  const { path } = await ctx.params;
  return proxy(req, path);
}

export async function DELETE(req: NextRequest, ctx: { params: Promise<{ path: string[] }> }) {
  const { path } = await ctx.params;
  return proxy(req, path);
}


