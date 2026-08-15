# mattpocock/skills Adaptation

## Goal

Create OpenClaw Skill Workshop proposals that adapt the useful engineering workflows from `mattpocock/skills` without installing the repository wholesale.

## Checklist

- [x] Verify current upstream reference.
- [x] Inspect local skill boundaries.
- [x] Create `debugging-feedback-loop` proposal.
- [x] Create/update workflow proposal for review/ticket/domain-modeling patterns.
- [x] Verify proposals are pending and summarize IDs.
- [x] Apply `agent-workflow-v2` update after explicit approval.
- [ ] Apply `debugging-feedback-loop` proposal only after separate explicit approval.

## Notes

- Do not manually write pending skill proposal lifecycle files.
- Do not apply proposals without explicit approval.
- Upstream checked: `mattpocock/skills` HEAD `ed37663cc5fbef691ddfecd080dff42f7e7e350d`.
- Local boundary: no existing debug/code-review skill; `agent-workflow-v2` is live and must be updated through Skill Workshop only.
- Created pending clean proposal: `debugging-feedback-loop-20260728-74757679c8`.
- Created pending clean update proposal: `agent-workflow-v2-20260728-e5caa32aae`.
- Applied `agent-workflow-v2-20260728-e5caa32aae` after Stanislav's explicit "Примени" approval on 2026-07-28 08:37 MSK.
- Initial apply copied proposal text into the live skill, so a corrective Skill Workshop update was created and applied: `agent-workflow-v2-20260728-6b35940606`.
- Verified live `skills/agent-workflow-v2/SKILL.md` is again the full workflow and now contains `Debugging Default`, `Two-Axis Review`, `Task Slicing Default`, `Domain Vocabulary Default`, plus the original approval/security/memory gates.
- `debugging-feedback-loop-20260728-74757679c8` remains pending.
