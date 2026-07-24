#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from typing import Any

from openclaw_shared_memory.config import Settings
from openclaw_shared_memory.repository import MemoryRepository


APPROVED_IDS = [
    "19309b52-9d04-47cb-83c8-fba1024522f4",
    "31ea008d-0ce1-4032-a499-2a75e34f6de6",
    "bf8b3331-7957-4e17-84e7-d9cf062b0c7c",
]


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Promote the approved Phase 5 candidate IDs")
    parser.add_argument("ids", nargs="*", default=APPROVED_IDS)
    parser.add_argument("--apply", action="store_true")
    parser.add_argument("--actor", default="openclaw-main")
    parser.add_argument(
        "--reason",
        default="Approved Phase 5 manual promotion of imported shared-memory candidates",
    )
    return parser


def assert_exact_approved_ids(ids: list[str]) -> None:
    if ids != APPROVED_IDS:
        raise ValueError("this pilot may promote only the exact approved candidate IDs in order")


def summarize_record(item: dict[str, Any]) -> dict[str, Any]:
    record = item["record"]
    return {
        "id": str(record["id"]),
        "title": record["title"],
        "status": record["status"],
        "privacy_class": record["privacy_class"],
        "scope": record["scope"],
        "source": record["source"],
        "confidence": float(record["confidence"]),
        "audit_events": [row["event_type"] for row in item["audit"]],
    }


def main() -> int:
    args = build_parser().parse_args()
    ids = list(args.ids)
    assert_exact_approved_ids(ids)

    repo = MemoryRepository(Settings.from_env())
    before = [repo.get_with_audit(record_id, privacy_classes={"project"}) for record_id in ids]
    for item in before:
        record = item["record"]
        if record["status"] != "candidate":
            raise ValueError(f"record {record['id']} is not candidate: {record['status']}")
        if record["privacy_class"] != "project":
            raise ValueError(f"record {record['id']} privacy changed: {record['privacy_class']}")

    if not args.apply:
        print(json.dumps([summarize_record(item) for item in before], ensure_ascii=False, indent=2))
        print(f"PHASE5_CANDIDATE_PROMOTION_DRY_RUN_OK count={len(before)}")
        return 0

    promoted = []
    for item in before:
        record = item["record"]
        row = repo.promote_to_shared(
            record_id=str(record["id"]),
            actor=args.actor,
            reason=args.reason,
            privacy_class=record["privacy_class"],
            scope=record["scope"],
            source=record["source"],
            confidence=float(record["confidence"]),
        )
        promoted.append(
            {
                "id": str(row["id"]),
                "title": row["title"],
                "status": row["status"],
                "privacy_class": row["privacy_class"],
            }
        )

    after = [summarize_record(repo.get_with_audit(record_id, privacy_classes={"project"})) for record_id in ids]
    print(json.dumps({"promoted": promoted, "after": after}, ensure_ascii=False, indent=2))
    print(f"PHASE5_CANDIDATE_PROMOTION_APPLY_OK count={len(promoted)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
