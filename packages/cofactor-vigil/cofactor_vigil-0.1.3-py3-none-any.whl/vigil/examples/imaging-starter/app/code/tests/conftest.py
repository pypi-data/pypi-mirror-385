from __future__ import annotations

import sys
from pathlib import Path

# Ensure repository root is importable for app.* modules
ROOT = Path(__file__).resolve().parents[3]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
