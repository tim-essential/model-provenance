from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class TrainingInputDescriptor:
    """The provenance description of the Training Input consumed by a
    Derivation.

    May include dataset identity, split/shard identity, sampling policy,
    mixture weights, filter/ordering/augmentation policy, exact sample ids
    or content hash for full reproducibility.
    """

    content: dict[str, Any]
