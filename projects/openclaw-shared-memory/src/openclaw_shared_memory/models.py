from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


RECORD_TYPES = {
    "decision",
    "state",
    "fact",
    "preference",
    "task",
    "incident",
    "procedure",
}

PRIVACY_CLASSES = {
    "private_agent",
    "personal_stanislav",
    "project",
    "shared_safe",
    "external_forbidden",
}


@dataclass(frozen=True)
class MemoryDraft:
    record_type: str
    title: str
    body: str
    privacy_class: str
    source: str
    created_by: str
    scope: str = "openclaw"
    source_ref: str | None = None
    owner: str | None = None
    confidence: float = 0.7
    tags: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)

    def validate(self) -> None:
        if self.record_type not in RECORD_TYPES:
            raise ValueError(f"Unsupported record_type: {self.record_type}")
        if self.privacy_class not in PRIVACY_CLASSES:
            raise ValueError(f"Unsupported privacy_class: {self.privacy_class}")
        for name in ("title", "body", "source", "created_by", "scope"):
            if not str(getattr(self, name)).strip():
                raise ValueError(f"{name} must not be blank")
        if not 0 <= self.confidence <= 1:
            raise ValueError("confidence must be between 0 and 1")

