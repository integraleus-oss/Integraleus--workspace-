from __future__ import annotations

import pytest

from openclaw_shared_memory.models import MemoryDraft


def test_memory_draft_accepts_valid_record() -> None:
    draft = MemoryDraft(
        record_type="decision",
        title="Shared memory canon",
        body="Use Postgres as shared canon.",
        privacy_class="shared_safe",
        source="test",
        created_by="pytest",
    )

    draft.validate()


def test_memory_draft_rejects_unknown_privacy_class() -> None:
    draft = MemoryDraft(
        record_type="decision",
        title="Bad class",
        body="Example",
        privacy_class="public_internet",
        source="test",
        created_by="pytest",
    )

    with pytest.raises(ValueError):
        draft.validate()

