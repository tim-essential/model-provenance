from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class RunView:
    run_id: str
    name: str
    starting_artifact_id: str
    artifact_ids: list[str] = field(default_factory=list)
    derivation_ids: list[str] = field(default_factory=list)
