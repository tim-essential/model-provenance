from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class TrainingState:
    """The version-varying realised values of an Artifact required to
    evaluate or continue training.

    Contains model parameters/weights, optimizer state, scheduler position,
    step/token/epoch counters, RNG state, and other auxiliary accumulators
    or buffers.
    """

    content: dict[str, Any]
