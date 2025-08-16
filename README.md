# Employee Pulse – Dev Setup

End-to-end setup for the FastAPI backend and Next.js frontend.

## Prerequisites
- Python 3.12
- Poetry
- Node.js 18+ and pnpm (or npm)
- Optional: PostgreSQL (planned for Prisma)

## Environment configuration

Create two `.env` files: one for backend, one for frontend.

### Backend `.env`
Required keys (no values shown here):
- `ANTHROPIC_API_KEY`
- `ANTHROPIC_DEFAULT_MODEL` (optional, default `claude-3-5-sonnet-20240620`)
- `ANTHROPIC_MAX_TOKENS` (optional)
- `ANTHROPIC_DEFAULT_TEMPERATURE` (optional)
- `ANTHROPIC_API_BASE` (optional; leave empty for official API)
- `SLACK_CLIENT_ID`
- `SLACK_CLIENT_SECRET`
- `SLACK_SIGNING_SECRET` (optional for webhooks, not required for OAuth in this MVP)
- `SLACK_REDIRECT_URI` (must match your Slack app config)
- `CORS_ALLOW_ORIGINS` (optional; defaults to `*` for dev)

Notes:
- Slack redirect URI should point to the backend OAuth callback, e.g. `http://localhost:8000/api/v1/slack/oauth/callback`.
- For local dev over HTTPS, you can pass `redirect_uri` when requesting the OAuth URL from the frontend to override.

### Frontend `.env.local`
Required public keys:
- `NEXT_PUBLIC_API_BASE_URL` – Base URL where the backend runs (e.g. `http://127.0.0.1:8000`). Used by client-side calls when not using the Next.js proxy.
- `NEXT_PUBLIC_SLACK_REDIRECT_URI` – Frontend URL that Slack should redirect back to, e.g. `http://localhost:3000/slack/callback`. This should align with your Slack app settings.

Notes:
- In development, the frontend proxies API routes under `/api/{dashboard,metrics,slack,insights}` to the backend to avoid CORS issues.

## Slack app setup (quick)
1. Create a Slack app in your workspace (from `api.slack.com/apps`).
2. Add bot scopes: `channels:read`, `groups:read`, `chat:write`, `users:read`, `emoji:read`, `channels:history`, `groups:history`.
3. Set OAuth redirect URL(s):
   - Backend: `http://localhost:8000/api/v1/slack/oauth/callback`
   - Frontend (optional for convenience flows): `http://localhost:3000/slack/callback`
4. Install the app to your workspace and keep the Bot User OAuth token (the backend handles OAuth and stores it in memory for dev).
5. Copy client ID/secret into the backend `.env`.

## Backend – install and run
```bash
cd backend
poetry env use 3.12
poetry install
poetry run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Quick validation:
- Health: `GET http://127.0.0.1:8000/api/v1/health`
- Slack connection: `GET http://127.0.0.1:8000/api/v1/slack/connection`
- Insights: `GET http://127.0.0.1:8000/api/v1/insights/teams?range=week`

## Frontend – install and run
```bash
cd frontend
pnpm install # or npm install
pnpm dev     # or npm run dev
```

Open `http://localhost:3000`.

## Development tips
- Select Slack channels in Settings → Slack to enable Dashboard/Metrics/Insights.
- Without a Slack installation, the backend returns demo channels and limited data; Anthropic insights still work if `ANTHROPIC_API_KEY` is set (fallback heuristics otherwise).
- Run tests:
  - Backend: `cd backend && poetry run pytest -q`
  - Frontend lint: `cd frontend && pnpm lint`


