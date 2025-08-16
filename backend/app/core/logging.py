import logging
import sys


def setup_logging(level: int = logging.INFO) -> None:
	root = logging.getLogger()
	if root.handlers:
		return
	handler = logging.StreamHandler(sys.stdout)
	formatter = logging.Formatter(
		"%(asctime)s | %(levelname)s | %(name)s | %(message)s",
	)
	handler.setFormatter(formatter)
	root.addHandler(handler)
	root.setLevel(level)