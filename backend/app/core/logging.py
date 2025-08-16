import os

def configure_logging() -> None:
	level = os.getenv("LOG_LEVEL", "INFO").upper()
	dictConfig = __import__("logging").config.dictConfig  # type: ignore[attr-defined]
	dictConfig(
		{
			"version": 1,
			"disable_existing_loggers": False,
			"formatters": {
				"default": {
					"format": "%(asctime)s | %(levelname)s | %(name)s | %(message)s",
					"datefmt": "%Y-%m-%d %H:%M:%S",
				}
			},
			"handlers": {
				"console": {
					"class": "logging.StreamHandler",
					"formatter": "default",
					"stream": "ext://sys.stdout",
				}
			},
			"loggers": {
				"uvicorn": {"handlers": ["console"], "level": level},
				"uvicorn.error": {"handlers": ["console"], "level": level, "propagate": True},
				"uvicorn.access": {"handlers": ["console"], "level": level, "propagate": False},
				"app": {"handlers": ["console"], "level": level, "propagate": False},
			},
			"root": {"handlers": ["console"], "level": level},
		}
	)

	# Optional per-module debug overrides via env flags
	if os.getenv("DEBUG_METRICS", "").lower() in ("1", "true", "yes"):  # pragma: no cover
		__import__("logging").getLogger("app.services.metrics_service").setLevel("DEBUG")
		__import__("logging").getLogger("app.services.slack_service").setLevel("DEBUG")
	if os.getenv("DEBUG_ANTHROPIC", "").lower() in ("1", "true", "yes"):  # pragma: no cover
		__import__("logging").getLogger("app.services.anthropic_service").setLevel("DEBUG")
	if os.getenv("DEBUG_DASHBOARD", "").lower() in ("1", "true", "yes"):  # pragma: no cover
		__import__("logging").getLogger("app.services.dashboard_service").setLevel("DEBUG")
		__import__("logging").getLogger("app.api.v1.dashboard").setLevel("DEBUG")
