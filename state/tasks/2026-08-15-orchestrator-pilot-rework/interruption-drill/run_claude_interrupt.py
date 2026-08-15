#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
from pathlib import Path


WORKSPACE = Path("/home/stanislav/.openclaw/workspace/agents/main")
INTEGRATION = WORKSPACE / "state/tasks/2026-08-12-orchestrator-integration"
sys.path.insert(0, str(INTEGRATION))

import live_review_cycle


PROJECT = Path("/home/stanislav/projects/home-agent-factory")
PROMPT = WORKSPACE / "state/tasks/2026-08-15-orchestrator-pilot-rework/t02-targeted-replay/REVIEW_PROMPT.md"
OUTPUT = Path("/home/stanislav/agent-runs/orchestrator-worktrees/pilot-interrupt-claude-r1")


def main() -> int:
    result = live_review_cycle.run_cycle(
        PROJECT,
        PROMPT,
        OUTPUT / "unused-bundle.json",
        OUTPUT / "live-review",
        timeout_seconds=600,
    )
    print(json.dumps(result, sort_keys=True, separators=(",", ":")))
    return 130 if result.get("status") == "INTERRUPTED" else 1


if __name__ == "__main__":
    raise SystemExit(main())
