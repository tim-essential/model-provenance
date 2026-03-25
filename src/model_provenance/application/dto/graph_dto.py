from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class GraphNodeView:
    id: str
    label: str
    kind: str
    layer: int = 0
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class GraphEdgeView:
    source: str
    target: str
    label: str
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class GraphView:
    nodes: list[GraphNodeView]
    edges: list[GraphEdgeView]
