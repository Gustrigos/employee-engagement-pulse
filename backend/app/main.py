from fastapi import FastAPI

from app.core.config import settings
from app.core.logging import setup_logging

setup_logging()

app = FastAPI(title=settings.app_name)


@app.get("/api/v1/health")
def health() -> dict[str, str]:
	return {"status": "ok"}