from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.logging import configure_logging
from app.api.v1.health import router as health_router
from app.api.v1.dashboard import router as dashboard_router
from app.api.v1.insights import router as insights_router
from app.api.v1.slack import router as slack_router
from app.api.v1.metrics import router as metrics_router

# Initialize logger
configure_logging()

app = FastAPI(title="Employee Pulse API", version="0.1.0")

# Allow frontend dev origin
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For MVP; tighten later
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def on_startup() -> None:
    # Placeholder: initialize Prisma client when DB is used
    # from prisma import Prisma
    # app.state.db = Prisma()
    # await app.state.db.connect()
    return None


@app.on_event("shutdown")
async def on_shutdown() -> None:
    # Placeholder: close Prisma client
    # db = getattr(app.state, "db", None)
    # if db is not None:
    #     await db.disconnect()
    return None


# Mount API routers
app.include_router(health_router, prefix="/api/v1")
app.include_router(dashboard_router, prefix="/api/v1")
app.include_router(insights_router, prefix="/api/v1")
app.include_router(slack_router, prefix="/api/v1")
app.include_router(metrics_router, prefix="/api/v1")
