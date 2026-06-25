"""Print every registered route. Run from the backend root:

    python -m scripts.inspect_routes
"""

import os
import sys

# Allow running as a plain script (`python scripts/inspect_routes.py`) by making
# the backend root importable.
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.main import app  # noqa: E402

for route in app.routes:
    print(f"Path: {route.path}, Name: {route.name}, Methods: {getattr(route, 'methods', 'N/A')}")
