from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class Settings:
    database_url: str
    reader_database_url: str
    writer_database_url: str
    promoter_database_url: str
    backup_database_url: str
    embedding_dim: int
    mirror_dir: Path
    backup_dir: Path
    default_scope: str
    readable_privacy_classes: frozenset[str]
    writable_privacy_classes: frozenset[str]
    mirror_privacy_classes: frozenset[str]
    promoter_actors: frozenset[str]

    @classmethod
    def from_env(cls) -> "Settings":
        database_url = os.environ.get(
            "OPENCLAW_MEMORY_DATABASE_URL",
            "postgresql://openclaw_memory:openclaw_memory_dev@127.0.0.1:55432/openclaw_memory",
        )
        readable_privacy_classes = _csv_set(
            os.environ.get("OPENCLAW_MEMORY_READABLE_PRIVACY_CLASSES", "project,shared_safe")
        )
        writable_privacy_classes = _csv_set(
            os.environ.get("OPENCLAW_MEMORY_WRITABLE_PRIVACY_CLASSES", "project,shared_safe")
        )
        mirror_privacy_classes = _csv_set(
            os.environ.get("OPENCLAW_MEMORY_MIRROR_PRIVACY_CLASSES", "shared_safe")
        )
        promoter_actors = _csv_set(
            os.environ.get("OPENCLAW_MEMORY_PROMOTER_ACTORS", "stanislav,openclaw-main")
        )
        return cls(
            database_url=database_url,
            reader_database_url=os.environ.get("OPENCLAW_MEMORY_READER_DATABASE_URL", database_url),
            writer_database_url=os.environ.get("OPENCLAW_MEMORY_WRITER_DATABASE_URL", database_url),
            promoter_database_url=os.environ.get("OPENCLAW_MEMORY_PROMOTER_DATABASE_URL", database_url),
            backup_database_url=os.environ.get("OPENCLAW_MEMORY_BACKUP_DATABASE_URL", database_url),
            embedding_dim=int(os.environ.get("OPENCLAW_MEMORY_EMBEDDING_DIM", "768")),
            mirror_dir=Path(os.environ.get("OPENCLAW_MEMORY_MIRROR_DIR", "./mirror")),
            backup_dir=Path(os.environ.get("OPENCLAW_MEMORY_BACKUP_DIR", "./backups")),
            default_scope=os.environ.get("OPENCLAW_MEMORY_DEFAULT_SCOPE", "openclaw"),
            readable_privacy_classes=frozenset(readable_privacy_classes),
            writable_privacy_classes=frozenset(writable_privacy_classes),
            mirror_privacy_classes=frozenset(mirror_privacy_classes),
            promoter_actors=frozenset(promoter_actors),
        )

    def database_url_for_role(self, role: str) -> str:
        if role == "reader":
            return self.reader_database_url
        if role == "writer":
            return self.writer_database_url
        if role == "promoter":
            return self.promoter_database_url
        if role == "backup":
            return self.backup_database_url
        if role == "admin":
            return self.database_url
        raise ValueError(f"Unsupported database role: {role}")


def _csv_set(value: str) -> set[str]:
    return {part.strip() for part in value.split(",") if part.strip()}
