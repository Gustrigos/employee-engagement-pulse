import logging
import sys


def configure_logging() -> None:
    handler = logging.StreamHandler(sys.stdout)
    formatter = logging.Formatter(
        fmt="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    handler.setFormatter(formatter)

    root = logging.getLogger()
    root.setLevel(logging.INFO)
    # Opt-in to debug logs for metrics/slack via env var
    import os
    if os.getenv("DEBUG_METRICS", "").lower() in ("1", "true", "yes"):  # pragma: no cover
        logging.getLogger("app.services.metrics_service").setLevel(logging.DEBUG)
        logging.getLogger("app.services.slack_service").setLevel(logging.DEBUG)
    if not root.handlers:
        root.addHandler(handler)
