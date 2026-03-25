from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class ExecutionRecord:
    """The realised execution context of a Derivation.

    Contains information needed to reproduce the Update as actually
    executed: software versions, code revision, hardware/runtime
    environment, seed material, distributed topology, precision mode,
    compiler flags, wall-clock timestamps, and any runtime-resolved
    settings.
    """

    content: dict[str, Any]
