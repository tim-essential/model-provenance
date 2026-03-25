from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class TrainingInput:
    """The data consumed by an Update.  Intentionally general: may be a
    batch, microbatch sequence, replay sample, curriculum slice, full
    epoch shard, RL experience, or any bounded input used to compute
    one successor artifact.
    """

    content: dict[str, Any]


@dataclass(frozen=True)
class Batch(TrainingInput):
    """A Training Input consisting of a finite sample of training examples."""
