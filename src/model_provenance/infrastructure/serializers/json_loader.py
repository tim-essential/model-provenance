from __future__ import annotations

import json
from pathlib import Path


def load_provenance_file(path: str | Path) -> dict:
    p = Path(path)
    with p.open(encoding="utf-8") as f:
        return json.load(f)
