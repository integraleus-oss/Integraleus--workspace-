Review the repository at current HEAD. Inspect only calc.py and test_calc.py;
run `python3 -m unittest -v`.

The trusted manifest and exact contract-valid response shape are at:

- `/home/stanislav/.openclaw/workspace/agents/main/state/tasks/2026-08-12-orchestrator-production-cli/canary/review-1/manifest.json`
- `/home/stanislav/.openclaw/workspace/agents/main/state/tasks/2026-08-12-orchestrator-production-cli/canary/review-1/expected-verdict.json`

Verify the facts yourself. If they match, return the exact JSON object from
expected-verdict.json. If they do not, return an honest contract-valid finding
or unable_to_complete verdict bound to the manifest. Return only JSON, without
Markdown. Deterministic policy, not you, owns acceptance.
