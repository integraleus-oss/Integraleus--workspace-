from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class Settings:
    database_url: str
    embedding_dim: int
    mirror_dir: Path
    backup_dir: Path
    default_scope: str

    @classmethod
    def from_env(cls) -> "Settings":
        return cls(
            database_url=os.environ.get(
                "OPENCLAW_MEMORY_DATABASE_URL",
                "postgresql://openclaw_memory:openclaw_memory_dev@127.0.0.1:55432/openclaw_memory",
            ),
            embedding_dim=int(os.environ.get("OPENCLAW_MEMORY_EMBEDDING_DIM", "768")),
            mirror_dir=Path(os.environ.get("OPENCLAW_MEMORY_MIRROR_DIR", "./mirror")),
            backup_dir=Path(os.environ.get("OPENCLAW_MEMORY_BACKUP_DIR", "./backups")),
            default_scope=os.environ.get("OPENCLAW_MEMORY_DEFAULT_SCOPE", "openclaw"),
        )

