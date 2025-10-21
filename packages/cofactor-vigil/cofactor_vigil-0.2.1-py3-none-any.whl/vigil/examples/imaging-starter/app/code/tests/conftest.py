from __future__ import annotations

import sys
from pathlib import Path

from app.code.lib.paths import ensure_project_on_path

ROOT = Path(__file__).resolve().parents[3]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

ensure_project_on_path()
