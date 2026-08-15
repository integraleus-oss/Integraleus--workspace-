#!/usr/bin/env python3
"""Deterministic bounded coordinator for at most one Codex rework."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Callable


class CycleError(RuntimeError):
    pass


RULE_OUTCOMES = {
    "R01_BINDING": "ESCALATED", "R02_REPLAY": "ESCALATED", "R03_STALE": "ESCALATED",
    "R04_INCOMPLETE": "ESCALATED", "R05_INFRA_RETRY": "FAILED_INFRA",
    "R06_INFRA_EXHAUSTED": "ESCALATED", "R07_UNKNOWN_FAILURE": "ESCALATED",
    "R08_REVIEW_CONTRACT": "ESCALATED", "R09_GATE_FAIL": "REWORK",
    "R10_GATE_FAIL_EXHAUSTED": "ESCALATED", "R11_OPEN_FINDINGS": "REWORK",
    "R12_FINDINGS_EXHAUSTED": "ESCALATED", "R13_EVIDENCE": "REWORK",
    "R14_EVIDENCE_EXHAUSTED": "ESCALATED", "R15_NEED_FULL_REVIEW": "REWORK",
    "R16_FULL_REVIEW_EXHAUSTED": "ESCALATED", "R17_ACCEPT": "ACCEPTED",
}


def _write(path: Path, value: Any) -> None:
    path.write_text(json.dumps(value, sort_keys=True, separators=(",", ":")) + "\n", encoding="utf-8")


def run_managed_cycle(
    root: Path,
    implement: Callable[[int, str | None, Path], dict[str, Any]],
    review: Callable[[int, Path], dict[str, Any]],
    *,
    max_attempts: int = 2,
) -> dict[str, Any]:
    if max_attempts != 2:
        raise CycleError("managed cycle permits exactly two attempts")
    root = root.resolve()
    if root.exists():
        raise CycleError("cycle root already exists")
    root.mkdir(parents=True)
    history: list[dict[str, Any]] = []
    rework_context: str | None = None
    final = "ESCALATED"
    try:
        for attempt in range(1, max_attempts + 1):
            attempt_dir = root / f"attempt-{attempt}"
            attempt_dir.mkdir()
            implementation = implement(attempt, rework_context, attempt_dir / "codex")
            if implementation.get("status") != "OK":
                final = ("INTERRUPTED" if implementation.get("status") == "INTERRUPTED"
                         else "FAILED_INFRA" if implementation.get("classification") == "KNOWN_INFRA"
                         else "ESCALATED")
                history.append({"attempt": attempt, "implementation": implementation, "review": None, "outcome": final})
                break
            verdict = review(attempt, attempt_dir / "claude")
            if verdict.get("status") == "INTERRUPTED":
                final = "INTERRUPTED"
                history.append({"attempt": attempt, "implementation": implementation,
                                "review": verdict, "outcome": final})
                break
            rule_id = verdict.get("rule_id") if verdict.get("document_type") == "local_orchestrator_run_result" else None
            outcome = RULE_OUTCOMES.get(rule_id, "ESCALATED")
            if verdict.get("outcome") != outcome:
                outcome = "ESCALATED"
            history.append({"attempt": attempt, "implementation": implementation, "review": verdict, "outcome": outcome})
            if outcome == "REWORK" and rule_id == "R15_NEED_FULL_REVIEW":
                final_dir = root / "review-only-final-full"
                final_dir.mkdir()
                final_verdict = review(max_attempts + 1, final_dir / "claude")
                if final_verdict.get("status") == "INTERRUPTED":
                    final = "INTERRUPTED"
                    history.append({"attempt": max_attempts + 1,
                                    "implementation": {"status": "SKIPPED_REVIEW_ONLY"},
                                    "review": final_verdict, "outcome": final})
                    break
                final_rule = (final_verdict.get("rule_id")
                              if final_verdict.get("document_type") == "local_orchestrator_run_result" else None)
                final_outcome = RULE_OUTCOMES.get(final_rule, "ESCALATED")
                if final_verdict.get("outcome") != final_outcome or final_outcome == "REWORK":
                    final_outcome = "ESCALATED"
                history.append({"attempt": max_attempts + 1, "implementation": {"status": "SKIPPED_REVIEW_ONLY"},
                                "review": final_verdict, "outcome": final_outcome})
                final = final_outcome
                break
            if outcome == "REWORK" and attempt < max_attempts:
                rework_context = verdict.get("rework_packet")
                if not isinstance(rework_context, str) or not rework_context.strip() or len(rework_context.encode()) > 8192:
                    final = "ESCALATED"
                    history[-1]["outcome"] = final
                    break
                continue
            final = "ESCALATED" if outcome == "REWORK" else outcome
            if outcome == "REWORK":
                history[-1]["outcome"] = final
            break
    except (KeyboardInterrupt, Exception) as exc:
        final = "INTERRUPTED" if isinstance(exc, KeyboardInterrupt) else "ESCALATED"
        history.append({"attempt": len(history) + 1, "implementation": None, "review": None, "outcome": final,
                        "error": {"type": type(exc).__name__, "message": str(exc)}})
    result = {
        "document_type": "managed_one_cycle_result",
        "schema_version": "1.0.0",
        "status": final,
        "attempts_used": len(history),
        "history": history,
    }
    _write(root / "cycle-result.json", result)
    return result
