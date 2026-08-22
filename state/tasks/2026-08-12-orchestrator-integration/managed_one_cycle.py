#!/usr/bin/env python3
"""Deterministic coordinator with a hard two-review ceiling."""

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
    review_profile: str = "standard",
    precreated_evidence: bool = False,
) -> dict[str, Any]:
    expected_attempts = 1 if review_profile == "light" else 2
    if review_profile not in {"light", "standard"} or max_attempts != expected_attempts:
        raise CycleError("review profile and attempt budget are inconsistent")
    root = root.resolve()
    if root.exists():
        contents = list(root.iterdir())
        if (not precreated_evidence or len(contents) != 1
                or contents[0].name != "RUN_EVIDENCE.jsonl"
                or contents[0].is_symlink() or not contents[0].is_file()):
            raise CycleError("cycle root already exists")
    else:
        if precreated_evidence:
            raise CycleError("precreated evidence root is missing")
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
            premature_targeted_closure = attempt == 1 and rule_id == "R15_NEED_FULL_REVIEW"
            targeted_closure = (attempt == 2 and rule_id == "R15_NEED_FULL_REVIEW"
                                and verdict.get("outcome") == "REWORK"
                                and verdict.get("closure_verified") is True)
            if premature_targeted_closure:
                outcome = "ESCALATED"
            elif targeted_closure:
                # R15 proves the policy registry has no open blocker/major and
                # requested only the legacy third full review. The two-pass
                # profile deliberately admits that state without another loop.
                outcome = "ACCEPTED"
            elif verdict.get("outcome") != outcome:
                outcome = "ESCALATED"
            trusted_rework = (rule_id in RULE_OUTCOMES and RULE_OUTCOMES[rule_id] == "REWORK"
                              and verdict.get("outcome") == "REWORK")
            history.append({"attempt": attempt, "implementation": implementation, "review": verdict,
                            "outcome": outcome,
                            "trusted_rework": trusted_rework,
                            **({"acceptance_basis": "targeted_closure_ceiling"} if targeted_closure else {})})
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
        "schema_version": "1.1.0",
        "status": final,
        "review_profile": review_profile,
        "review_ceiling": expected_attempts,
        "attempts_used": len(history),
        "terminal_reason": (
            "accepted" if final == "ACCEPTED" else "interrupted" if final == "INTERRUPTED"
            else "review_ceiling_exhausted"
            if (final == "ESCALATED" and len(history) == max_attempts
                and history[-1].get("review") and history[-1].get("outcome") == "ESCALATED"
                and history[-1].get("trusted_rework") is True)
            else "policy_or_runtime_escalation"
        ),
        "follow_up_required": bool(
            final == "ESCALATED" and len(history) == max_attempts
            and history[-1].get("review") and history[-1].get("outcome") == "ESCALATED"
            and history[-1].get("trusted_rework") is True
        ),
        "history": history,
    }
    _write(root / "cycle-result.json", result)
    return result
