import os
import sys

# Add project root to Python path for imports like `from app.main import app`
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PROJECT_ROOT not in sys.path:
	sys.path.insert(0, PROJECT_ROOT)