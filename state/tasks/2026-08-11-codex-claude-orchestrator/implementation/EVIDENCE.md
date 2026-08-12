# Reviewer Contract Rework Evidence

Date: 2026-08-11

## State Machine Targeted R2

Files changed in this pass:

- `orchestrator_policy.py`
- `STATE_MACHINE.md`
- `tests/test_orchestrator_policy.py`
- `EVIDENCE.md`

No completed reviewer-contract schema, validator, or tests were edited. No task
packet, review report, shared file, or file outside `implementation/` was
edited. No commit was made and danger mode was not used.

Implemented the remaining SM-07 fix by canonically sorting every finding
history on registry output, including records untouched by the current review.
Occurrence identity is documented and enforced as
`(review_id, occurrence_id)`: reuse across reviews appends a distinct entry,
while an existing pair is retained without overwrite.

Regression coverage proves that reversing two valid history entries on an
untouched `resolved_verified` record produces the same `ACCEPTED/R17_ACCEPT`
outcome, `input_digests`, `registry_digest_after`, `decision_digest`, and full
canonical decision bytes. Cross-review reuse of an `occurrence_id` produces a
valid engine-emitted registry, a repeated pair does not overwrite history, and
the emitted registry passes validation on the next invocation.

Focused policy tests:

```text
python3 -m unittest tests.test_orchestrator_policy
.........................................................
----------------------------------------------------------------------
Ran 57 tests in 0.041s

OK
```

All tests:

```text
python3 -m unittest discover
...............................................................................
----------------------------------------------------------------------
Ran 79 tests in 2.800s

OK
```

Policy schema self-check:

```text
python3 orchestrator_policy.py --check-schema
{"errors":[],"mode":"schema_self_check","schemas_valid":true}
```

Reviewer-contract schema self-check:

```text
python3 validate_review_verdict.py --check-schema
{"contract_valid":true,"errors":[],"failure_kind":null,"layers":{"schema":true,"semantic":null,"transport":true},"mode":"schema_self_check"}
```

Policy fixture check:

```text
python3 orchestrator_policy.py --check-fixtures fixtures/policy
```

Exit `0`: 2 valid fixtures matched their expected decisions and 2 invalid
fixtures were rejected (`passed: true`).

Compilation and whitespace checks:

```text
python3 -m py_compile orchestrator_policy.py tests/test_orchestrator_policy.py validate_review_verdict.py tests/test_review_verdict.py
git diff --check -- implementation
```

Both exited `0` with no output. The supplemental scan of all non-cache files
under `implementation/` also exited `0` with
`implementation whitespace check passed`.

Scoped status and latest commit observed after verification:

```text
?? implementation/
?? reviews/claude-state-machine-targeted-r1.md
f558763 fix: improve Spectech mobile layout and contact links
```

## Policy Engine Adversarial Rework R1

Files changed in this pass:

- `orchestrator_policy.py`
- `tests/test_orchestrator_policy.py`
- `EVIDENCE.md`

Completed reviewer-contract files were not modified:

- `review-verdict.schema.json`
- `validate_review_verdict.py`
- `tests/test_review_verdict.py`

No task packets, review reports, shared files, configuration, or files outside
`implementation/` were edited. No commit was made. No danger mode was used.

Implemented confirmed policy-engine findings from
`reviews/claude-state-machine-core-review.md`:

- SM-01: terminal replay now runs only after schema, binding, replay/stale, and
  payload-digest checks. Digest normalization is path-aware and no longer sorts
  opaque payload lists solely because a nested key is named `findings` or
  `required_evidence`.
- SM-02: duplicate `evidence_artifacts.req_id` fails closed before evidence
  evaluation; no last-wins artifact map can accept.
- SM-03: ledger finding registries are strictly validated and duplicate
  `finding_id` fails closed before merge.
- SM-04: terminal decisions are strictly validated, their digest is recomputed,
  and their full content must match a freshly derived current decision before
  replay. Forged digest, outcome, rule, directives, or budgets escalate.
- SM-05: unknown registry `status`, `effective_severity`, document type,
  malformed counts, bool counts, and malformed history fail closed.
- SM-06: malformed nested containers in scalar lists/maps return machine
  `ESCALATED` decisions instead of uncaught exceptions.
- SM-07: required-evidence failure reasons/directives are sorted by `req_id`,
  so semantically equivalent required-evidence permutations produce identical
  decision JSON and digest.
- Evidence rework now applies the no-progress policy consistently.

Regression coverage added:

- exact SM-01 through SM-07 repro shapes from the Claude report;
- terminal decision with forged digest/outcome/budgets;
- invalid ledger registry status, severity, count, history entry, document
  type, and bool count;
- duplicate registry and reviewer occurrence IDs/history entries;
- duplicate mandatory gate, required evidence, evidence artifact, and verified
  finding identifiers;
- opaque payload keys named `findings`/`required_evidence` do not trigger outer
  unordered-list canonicalization;
- public `decide()` is total for representative malformed dict/list/scalar
  containers.

Focused policy regression command:

```sh
cd state/tasks/2026-08-11-codex-claude-orchestrator/implementation
python3 -m unittest tests.test_orchestrator_policy
```

Result: exit `0`

```text
.......................................................
----------------------------------------------------------------------
Ran 55 tests in 0.041s

OK
```

Policy schema self-check:

```sh
python3 state/tasks/2026-08-11-codex-claude-orchestrator/implementation/orchestrator_policy.py --check-schema
```

Result: exit `0`

```json
{"errors":[],"mode":"schema_self_check","schemas_valid":true}
```

Reviewer contract schema self-check:

```sh
python3 state/tasks/2026-08-11-codex-claude-orchestrator/implementation/validate_review_verdict.py --check-schema
```

Result: exit `0`

```json
{"contract_valid":true,"errors":[],"failure_kind":null,"layers":{"schema":true,"semantic":null,"transport":true},"mode":"schema_self_check"}
```

All unit tests:

```sh
cd state/tasks/2026-08-11-codex-claude-orchestrator/implementation
python3 -m unittest discover
```

Result: exit `0`

```text
.............................................................................
----------------------------------------------------------------------
Ran 77 tests in 2.804s

OK
```

Policy fixture expectations:

```sh
python3 state/tasks/2026-08-11-codex-claude-orchestrator/implementation/orchestrator_policy.py --check-fixtures state/tasks/2026-08-11-codex-claude-orchestrator/implementation/fixtures/policy
```

Result: exit `0`

```json
{"invalid_count":2,"invalid_results":[{"fixture":"bool_counter.json","rejected":true,"schema_errors":["True is not of type 'integer'","True should not be valid under {'type': 'boolean'}"]},{"fixture":"unknown_field.json","rejected":true,"schema_errors":["Additional properties are not allowed ('unexpected' was unexpected)","'task_policy' is a required property","'ledger' is a required property","'execution_report' is a required property","'reviewer_report' is a required property","'expected_outcome' is a required property","'expected_rule_id' is a required property"]}],"mode":"fixture_check","passed":true,"valid_count":2,"valid_results":[{"expected_outcome":"ACCEPTED","expected_rule_id":"R17_ACCEPT","fixture":"accepted.json","outcome":"ACCEPTED","rule_id":"R17_ACCEPT","valid":true},{"expected_outcome":"FAILED_INFRA","expected_rule_id":"R05_INFRA_RETRY","fixture":"known_infra.json","outcome":"FAILED_INFRA","rule_id":"R05_INFRA_RETRY","valid":true}]}
```

Python compile:

```sh
python3 -m py_compile state/tasks/2026-08-11-codex-claude-orchestrator/implementation/orchestrator_policy.py state/tasks/2026-08-11-codex-claude-orchestrator/implementation/tests/test_orchestrator_policy.py state/tasks/2026-08-11-codex-claude-orchestrator/implementation/validate_review_verdict.py state/tasks/2026-08-11-codex-claude-orchestrator/implementation/tests/test_review_verdict.py
```

Result: exit `0`, no output.

Scoped diff whitespace check:

```sh
git diff --check -- state/tasks/2026-08-11-codex-claude-orchestrator/implementation
```

Result: exit `0`, no output.

Supplemental implementation whitespace check, because this task folder is
currently untracked and `git diff --check` does not inspect untracked file
contents:

```sh
python3 - <<'PY'
from pathlib import Path
root = Path('state/tasks/2026-08-11-codex-claude-orchestrator/implementation')
problems = []
for path in sorted(root.rglob('*')):
    if not path.is_file() or '__pycache__' in path.parts:
        continue
    data = path.read_bytes()
    if b'\r' in data:
        problems.append(f'{path}: contains CR')
    for index, line in enumerate(data.splitlines(), 1):
        if line.endswith((b' ', b'\t')):
            problems.append(f'{path}:{index}: trailing whitespace')
if problems:
    print('\n'.join(problems))
    raise SystemExit(1)
print('implementation whitespace check passed')
PY
```

## State Machine Final-Full Rework R3

Files changed in this pass:

- `orchestrator_policy.py`
- `orchestrator-state-machine.schema.json`
- `STATE_MACHINE.md`
- `tests/test_orchestrator_policy.py`
- `fixtures/policy/valid/accepted_with_payload.json`
- `fixtures/policy/valid/payload_digest_mismatch.json`
- `fixtures/policy/invalid/missing_payload_digest.json`
- `EVIDENCE.md`

No completed reviewer-contract schema, validator, or reviewer tests were edited.
No task packets, review reports, shared files, configuration, or files outside
`implementation/` were edited. No commit was made, no packages were installed,
and no network, runtime alteration, danger mode, or external action was used.

Implemented `CODEX_STATE_MACHINE_REWORK_3.md` against
`reviews/claude-state-machine-final-full.md`:

- FF-01: `decide()` now enforces the same parsed-input depth, cardinality, and
  string safety boundary before exact digest/deepcopy work. Hostile already
  parsed input falls closed to deterministic `ESCALATED/R01_BINDING`.
- FF-02: `no_progress_streak` is now produced mechanically from a strict
  `ledger.prior_attempts` record plus the current subject progress identity.
  Repeated rework on the same identity advances to `NO_PROGRESS`; changed
  identity resets the streak.
- FF-03: the state-machine schema now matches the paired optional
  `execution_report.payload` and `payload_digest` implementation contract.
- FF-04: `STATE_MACHINE.md` now documents the actual safe precedence:
  validation, binding, replay/stale/incomplete, and fresh derivation precede
  terminal-decision equality/idempotence validation.

Exact R3 regression tests:

```text
python3 -m unittest tests.test_orchestrator_policy.OrchestratorPolicyTests.test_deep_prior_attempts_and_payload_fail_closed_through_decide tests.test_orchestrator_policy.OrchestratorPolicyTests.test_no_progress_advances_from_prior_decision_outputs_and_resets_on_changed_identity tests.test_orchestrator_policy.OrchestratorPolicyTests.test_payload_fixtures_exercise_cli_schema_and_policy_contract tests.test_orchestrator_policy.OrchestratorPolicyTests.test_documented_precedence_matches_safe_source_order
....
----------------------------------------------------------------------
Ran 4 tests in 0.353s

OK
```

Focused policy tests:

```text
python3 -m unittest tests.test_orchestrator_policy
.............................................................
----------------------------------------------------------------------
Ran 61 tests in 0.439s

OK
```

Payload CLI fixture checks:

```text
python3 - <<'PY'
import json
import subprocess
import sys
from pathlib import Path
root = Path.cwd()
cases = [
    ('accepted_with_payload', root / 'fixtures/policy/valid/accepted_with_payload.json', 0),
    ('payload_digest_mismatch', root / 'fixtures/policy/valid/payload_digest_mismatch.json', 0),
    ('missing_payload_digest', root / 'fixtures/policy/invalid/missing_payload_digest.json', 1),
]
for name, fixture, expected_returncode in cases:
    proc = subprocess.run([sys.executable, 'orchestrator_policy.py', '--fixture', str(fixture)], check=False, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    output = json.loads(proc.stdout)
    print(f'{name} returncode={proc.returncode} stderr={proc.stderr!r} valid={output["valid"]} outcome={output.get("outcome")} rule_id={output.get("rule_id")} schema_errors={output.get("schema_errors", [])}')
    if proc.returncode != expected_returncode or proc.stderr != '':
        raise SystemExit(1)
PY
accepted_with_payload returncode=0 stderr='' valid=True outcome=ACCEPTED rule_id=R17_ACCEPT schema_errors=[]
payload_digest_mismatch returncode=0 stderr='' valid=True outcome=ESCALATED rule_id=R04_INCOMPLETE schema_errors=[]
missing_payload_digest returncode=1 stderr='' valid=False outcome=None rule_id=None schema_errors=["'payload_digest' is a dependency of 'payload'"]
```

All tests:

```text
python3 -m unittest discover
...................................................................................
----------------------------------------------------------------------
Ran 83 tests in 3.140s

OK
```

Policy schema self-check:

```text
python3 orchestrator_policy.py --check-schema
{"errors":[],"mode":"schema_self_check","schemas_valid":true}
```

Reviewer-contract schema self-check:

```text
python3 validate_review_verdict.py --check-schema
{"contract_valid":true,"errors":[],"failure_kind":null,"layers":{"schema":true,"semantic":null,"transport":true},"mode":"schema_self_check"}
```

Policy fixture check:

```text
python3 orchestrator_policy.py --check-fixtures fixtures/policy
{"invalid_count":3,"invalid_results":[{"fixture":"bool_counter.json","rejected":true,"schema_errors":["True is not of type 'integer'","True should not be valid under {'type': 'boolean'}"]},{"fixture":"missing_payload_digest.json","rejected":true,"schema_errors":["'payload_digest' is a dependency of 'payload'"]},{"fixture":"unknown_field.json","rejected":true,"schema_errors":["Additional properties are not allowed ('unexpected' was unexpected)","'task_policy' is a required property","'ledger' is a required property","'execution_report' is a required property","'reviewer_report' is a required property","'expected_outcome' is a required property","'expected_rule_id' is a required property"]}],"mode":"fixture_check","passed":true,"valid_count":4,"valid_results":[{"expected_outcome":"ACCEPTED","expected_rule_id":"R17_ACCEPT","fixture":"accepted.json","outcome":"ACCEPTED","rule_id":"R17_ACCEPT","valid":true},{"expected_outcome":"ACCEPTED","expected_rule_id":"R17_ACCEPT","fixture":"accepted_with_payload.json","outcome":"ACCEPTED","rule_id":"R17_ACCEPT","valid":true},{"expected_outcome":"FAILED_INFRA","expected_rule_id":"R05_INFRA_RETRY","fixture":"known_infra.json","outcome":"FAILED_INFRA","rule_id":"R05_INFRA_RETRY","valid":true},{"expected_outcome":"ESCALATED","expected_rule_id":"R04_INCOMPLETE","fixture":"payload_digest_mismatch.json","outcome":"ESCALATED","rule_id":"R04_INCOMPLETE","valid":true}]}
```

Compilation:

```text
python3 -m py_compile orchestrator_policy.py tests/test_orchestrator_policy.py validate_review_verdict.py tests/test_review_verdict.py
```

Result: exit `0`, no output.

Scoped diff whitespace check:

```text
git diff --check -- implementation
```

Result: exit `0`, no output.

Supplemental implementation whitespace check:

```text
python3 - <<'PY'
from pathlib import Path
root = Path('implementation')
problems = []
for path in sorted(root.rglob('*')):
    if not path.is_file() or '__pycache__' in path.parts:
        continue
    data = path.read_bytes()
    if b'\r' in data:
        problems.append(f'{path}: contains CR')
    for index, line in enumerate(data.splitlines(), 1):
        if line.endswith((b' ', b'\t')):
            problems.append(f'{path}:{index}: trailing whitespace')
if problems:
    print('\n'.join(problems))
    raise SystemExit(1)
print('implementation whitespace check passed')
PY
implementation whitespace check passed
```

Scoped implementation status:

```text
git status --short -- implementation
?? implementation/
```

Superseding final rerun after moving rejected-input fallback digests behind the
public `decide()` preflight boundary:

```text
python3 -m unittest tests.test_orchestrator_policy.OrchestratorPolicyTests.test_deep_prior_attempts_and_payload_fail_closed_through_decide tests.test_orchestrator_policy.OrchestratorPolicyTests.test_no_progress_advances_from_prior_decision_outputs_and_resets_on_changed_identity tests.test_orchestrator_policy.OrchestratorPolicyTests.test_payload_fixtures_exercise_cli_schema_and_policy_contract tests.test_orchestrator_policy.OrchestratorPolicyTests.test_documented_precedence_matches_safe_source_order
....
----------------------------------------------------------------------
Ran 4 tests in 0.350s

OK
```

```text
python3 -m unittest tests.test_orchestrator_policy
.............................................................
----------------------------------------------------------------------
Ran 61 tests in 0.411s

OK
```

```text
python3 -m unittest discover
...................................................................................
----------------------------------------------------------------------
Ran 83 tests in 3.135s

OK
```

```text
python3 orchestrator_policy.py --check-schema
{"errors":[],"mode":"schema_self_check","schemas_valid":true}
```

```text
python3 validate_review_verdict.py --check-schema
{"contract_valid":true,"errors":[],"failure_kind":null,"layers":{"schema":true,"semantic":null,"transport":true},"mode":"schema_self_check"}
```

```text
python3 orchestrator_policy.py --check-fixtures fixtures/policy
{"invalid_count":3,"invalid_results":[{"fixture":"bool_counter.json","rejected":true,"schema_errors":["True is not of type 'integer'","True should not be valid under {'type': 'boolean'}"]},{"fixture":"missing_payload_digest.json","rejected":true,"schema_errors":["'payload_digest' is a dependency of 'payload'"]},{"fixture":"unknown_field.json","rejected":true,"schema_errors":["Additional properties are not allowed ('unexpected' was unexpected)","'task_policy' is a required property","'ledger' is a required property","'execution_report' is a required property","'reviewer_report' is a required property","'expected_outcome' is a required property","'expected_rule_id' is a required property"]}],"mode":"fixture_check","passed":true,"valid_count":4,"valid_results":[{"expected_outcome":"ACCEPTED","expected_rule_id":"R17_ACCEPT","fixture":"accepted.json","outcome":"ACCEPTED","rule_id":"R17_ACCEPT","valid":true},{"expected_outcome":"ACCEPTED","expected_rule_id":"R17_ACCEPT","fixture":"accepted_with_payload.json","outcome":"ACCEPTED","rule_id":"R17_ACCEPT","valid":true},{"expected_outcome":"FAILED_INFRA","expected_rule_id":"R05_INFRA_RETRY","fixture":"known_infra.json","outcome":"FAILED_INFRA","rule_id":"R05_INFRA_RETRY","valid":true},{"expected_outcome":"ESCALATED","expected_rule_id":"R04_INCOMPLETE","fixture":"payload_digest_mismatch.json","outcome":"ESCALATED","rule_id":"R04_INCOMPLETE","valid":true}]}
```

```text
accepted_with_payload returncode=0 stderr='' valid=True outcome=ACCEPTED rule_id=R17_ACCEPT schema_errors=[]
payload_digest_mismatch returncode=0 stderr='' valid=True outcome=ESCALATED rule_id=R04_INCOMPLETE schema_errors=[]
missing_payload_digest returncode=1 stderr='' valid=False outcome=None rule_id=None schema_errors=["'payload_digest' is a dependency of 'payload'"]
```

```text
python3 -m py_compile orchestrator_policy.py tests/test_orchestrator_policy.py validate_review_verdict.py tests/test_review_verdict.py
```

Result: exit `0`, no output.

```text
git diff --check -- implementation
```

Result: exit `0`, no output.

```text
implementation whitespace check passed
```

```text
git status --short -- implementation
?? implementation/
```

Final rerun after tightening prior-attempt digest validation to exact SHA-256:

```text
python3 -m unittest tests.test_orchestrator_policy.OrchestratorPolicyTests.test_deep_prior_attempts_and_payload_fail_closed_through_decide tests.test_orchestrator_policy.OrchestratorPolicyTests.test_no_progress_advances_from_prior_decision_outputs_and_resets_on_changed_identity tests.test_orchestrator_policy.OrchestratorPolicyTests.test_payload_fixtures_exercise_cli_schema_and_policy_contract tests.test_orchestrator_policy.OrchestratorPolicyTests.test_documented_precedence_matches_safe_source_order
....
----------------------------------------------------------------------
Ran 4 tests in 0.361s

OK
```

```text
python3 -m unittest tests.test_orchestrator_policy
.............................................................
----------------------------------------------------------------------
Ran 61 tests in 0.429s

OK
```

```text
python3 -m unittest discover
...................................................................................
----------------------------------------------------------------------
Ran 83 tests in 3.261s

OK
```

```text
python3 orchestrator_policy.py --check-schema
{"errors":[],"mode":"schema_self_check","schemas_valid":true}
```

```text
python3 validate_review_verdict.py --check-schema
{"contract_valid":true,"errors":[],"failure_kind":null,"layers":{"schema":true,"semantic":null,"transport":true},"mode":"schema_self_check"}
```

```text
python3 orchestrator_policy.py --check-fixtures fixtures/policy
{"invalid_count":3,"invalid_results":[{"fixture":"bool_counter.json","rejected":true,"schema_errors":["True is not of type 'integer'","True should not be valid under {'type': 'boolean'}"]},{"fixture":"missing_payload_digest.json","rejected":true,"schema_errors":["'payload_digest' is a dependency of 'payload'"]},{"fixture":"unknown_field.json","rejected":true,"schema_errors":["Additional properties are not allowed ('unexpected' was unexpected)","'task_policy' is a required property","'ledger' is a required property","'execution_report' is a required property","'reviewer_report' is a required property","'expected_outcome' is a required property","'expected_rule_id' is a required property"]}],"mode":"fixture_check","passed":true,"valid_count":4,"valid_results":[{"expected_outcome":"ACCEPTED","expected_rule_id":"R17_ACCEPT","fixture":"accepted.json","outcome":"ACCEPTED","rule_id":"R17_ACCEPT","valid":true},{"expected_outcome":"ACCEPTED","expected_rule_id":"R17_ACCEPT","fixture":"accepted_with_payload.json","outcome":"ACCEPTED","rule_id":"R17_ACCEPT","valid":true},{"expected_outcome":"FAILED_INFRA","expected_rule_id":"R05_INFRA_RETRY","fixture":"known_infra.json","outcome":"FAILED_INFRA","rule_id":"R05_INFRA_RETRY","valid":true},{"expected_outcome":"ESCALATED","expected_rule_id":"R04_INCOMPLETE","fixture":"payload_digest_mismatch.json","outcome":"ESCALATED","rule_id":"R04_INCOMPLETE","valid":true}]}
```

```text
accepted_with_payload returncode=0 stderr='' valid=True outcome=ACCEPTED rule_id=R17_ACCEPT schema_errors=[]
payload_digest_mismatch returncode=0 stderr='' valid=True outcome=ESCALATED rule_id=R04_INCOMPLETE schema_errors=[]
missing_payload_digest returncode=1 stderr='' valid=False outcome=None rule_id=None schema_errors=["'payload_digest' is a dependency of 'payload'"]
```

```text
python3 -m py_compile orchestrator_policy.py tests/test_orchestrator_policy.py validate_review_verdict.py tests/test_review_verdict.py
```

Result: exit `0`, no output.

```text
git diff --check -- implementation
```

Result: exit `0`, no output.

```text
implementation whitespace check passed
```

Result: exit `0`

```text
implementation whitespace check passed
```

Scoped git status after checks:

```sh
git status --short -- state/tasks/2026-08-11-codex-claude-orchestrator/implementation state/tasks/2026-08-11-codex-claude-orchestrator/STATE_MACHINE_TASK_PACKET.md state/tasks/2026-08-11-codex-claude-orchestrator/reviews state/tasks/2026-08-11-codex-claude-orchestrator/CODEX_STATE_MACHINE_REWORK_1.md
```

Result: exit `0`

```text
?? state/tasks/2026-08-11-codex-claude-orchestrator/CODEX_STATE_MACHINE_REWORK_1.md
?? state/tasks/2026-08-11-codex-claude-orchestrator/STATE_MACHINE_TASK_PACKET.md
?? state/tasks/2026-08-11-codex-claude-orchestrator/implementation/
?? state/tasks/2026-08-11-codex-claude-orchestrator/reviews/
```

Final rerun after appending this evidence:

```sh
python3 state/tasks/2026-08-11-codex-claude-orchestrator/implementation/orchestrator_policy.py --check-schema && python3 state/tasks/2026-08-11-codex-claude-orchestrator/implementation/validate_review_verdict.py --check-schema && python3 state/tasks/2026-08-11-codex-claude-orchestrator/implementation/orchestrator_policy.py --check-fixtures state/tasks/2026-08-11-codex-claude-orchestrator/implementation/fixtures/policy
```

Result: exit `0`

```text
{"errors":[],"mode":"schema_self_check","schemas_valid":true}
{"contract_valid":true,"errors":[],"failure_kind":null,"layers":{"schema":true,"semantic":null,"transport":true},"mode":"schema_self_check"}
{"invalid_count":2,"invalid_results":[{"fixture":"bool_counter.json","rejected":true,"schema_errors":["True is not of type 'integer'","True should not be valid under {'type': 'boolean'}"]},{"fixture":"unknown_field.json","rejected":true,"schema_errors":["Additional properties are not allowed ('unexpected' was unexpected)","'task_policy' is a required property","'ledger' is a required property","'execution_report' is a required property","'reviewer_report' is a required property","'expected_outcome' is a required property","'expected_rule_id' is a required property"]}],"mode":"fixture_check","passed":true,"valid_count":2,"valid_results":[{"expected_outcome":"ACCEPTED","expected_rule_id":"R17_ACCEPT","fixture":"accepted.json","outcome":"ACCEPTED","rule_id":"R17_ACCEPT","valid":true},{"expected_outcome":"FAILED_INFRA","expected_rule_id":"R05_INFRA_RETRY","fixture":"known_infra.json","outcome":"FAILED_INFRA","rule_id":"R05_INFRA_RETRY","valid":true}]}
```

```sh
cd state/tasks/2026-08-11-codex-claude-orchestrator/implementation
python3 -m unittest discover
```

Result: exit `0`

```text
.............................................................................
----------------------------------------------------------------------
Ran 77 tests in 2.840s

OK
```

```sh
python3 -m py_compile state/tasks/2026-08-11-codex-claude-orchestrator/implementation/orchestrator_policy.py state/tasks/2026-08-11-codex-claude-orchestrator/implementation/tests/test_orchestrator_policy.py state/tasks/2026-08-11-codex-claude-orchestrator/implementation/validate_review_verdict.py state/tasks/2026-08-11-codex-claude-orchestrator/implementation/tests/test_review_verdict.py && git diff --check -- state/tasks/2026-08-11-codex-claude-orchestrator/implementation
```

Result: exit `0`, no output.

```sh
python3 - <<'PY'
from pathlib import Path
root = Path('state/tasks/2026-08-11-codex-claude-orchestrator/implementation')
problems = []
for path in sorted(root.rglob('*')):
    if not path.is_file() or '__pycache__' in path.parts:
        continue
    data = path.read_bytes()
    if b'\r' in data:
        problems.append(f'{path}: contains CR')
    for index, line in enumerate(data.splitlines(), 1):
        if line.endswith((b' ', b'\t')):
            problems.append(f'{path}:{index}: trailing whitespace')
if problems:
    print('\n'.join(problems))
    raise SystemExit(1)
print('implementation whitespace check passed')
PY
```

Result: exit `0`

```text
implementation whitespace check passed
```

## Rework 3 Update

Files changed in this pass:

- `validate_review_verdict.py`
- `tests/test_review_verdict.py`
- `README.md`
- `EVIDENCE.md`

No fixtures, task packets, reviews, shared files, configuration, or files
outside `implementation/` were edited for Rework 3. No commit was made.

Implemented Rework 3 hardening:

- Prior-findings `status` values must be strings before allowed-status set
  membership checks.
- Trusted-manifest `expected_review_mode` and `expected_coverage_scope` values
  must be strings before enum set membership checks.
- Added subprocess/CLI regressions for prior `status: []`,
  trusted-manifest `expected_review_mode: []`, and trusted-manifest
  `expected_coverage_scope: []`.

Rework 3 exact regression command:

```sh
python3 - <<'PY'
from pathlib import Path
import json
import subprocess
import sys

root = Path('state/tasks/2026-08-11-codex-claude-orchestrator/implementation')
out = Path('/tmp/codex-rework-3-regressions')
out.mkdir(exist_ok=True)

prior = out / 'container_status_prior.json'
prior.write_text(json.dumps({
    'document_type': 'prior_findings',
    'schema_version': '1.0.0',
    'findings': [{'finding_id': 'fnd_aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa', 'status': []}],
}, sort_keys=True), encoding='utf-8')

mode_manifest = json.loads((root / 'fixtures' / 'trusted' / 'manifest_initial.json').read_text(encoding='utf-8'))
mode_manifest['expected_review_mode'] = []
mode_manifest_path = out / 'container_expected_review_mode_manifest.json'
mode_manifest_path.write_text(json.dumps(mode_manifest, sort_keys=True), encoding='utf-8')

scope_manifest = json.loads((root / 'fixtures' / 'trusted' / 'manifest_initial.json').read_text(encoding='utf-8'))
scope_manifest['expected_coverage_scope'] = []
scope_manifest_path = out / 'container_expected_coverage_scope_manifest.json'
scope_manifest_path.write_text(json.dumps(scope_manifest, sort_keys=True), encoding='utf-8')

cases = [
    ('prior_status_list', [sys.executable, str(root / 'validate_review_verdict.py'), str(root / 'fixtures' / 'valid' / 'targeted_verification.json'), '--trusted-manifest', str(root / 'fixtures' / 'trusted' / 'manifest_targeted.json'), '--prior-findings', str(prior)], 'prior_findings_invalid'),
    ('manifest_review_mode_list', [sys.executable, str(root / 'validate_review_verdict.py'), str(root / 'fixtures' / 'valid' / 'initial_blocker.json'), '--trusted-manifest', str(mode_manifest_path)], 'trusted_manifest_invalid'),
    ('manifest_coverage_scope_list', [sys.executable, str(root / 'validate_review_verdict.py'), str(root / 'fixtures' / 'valid' / 'initial_blocker.json'), '--trusted-manifest', str(scope_manifest_path)], 'trusted_manifest_invalid'),
]
for name, cmd, expected_code in cases:
    proc = subprocess.run(cmd, cwd=Path.cwd(), check=False, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    output = json.loads(proc.stdout)
    codes = [error['code'] for error in output['errors']]
    print(f'{name} returncode={proc.returncode} stderr={proc.stderr!r} stdout_lines={len(proc.stdout.splitlines())} failure_kind={output["failure_kind"]} codes={codes}')
    if proc.returncode != 2 or proc.stderr != '' or len(proc.stdout.splitlines()) != 1 or output['failure_kind'] != 'tool_input_failure' or expected_code not in codes:
        raise SystemExit(1)
PY
```

Result: exit `0`

```text
prior_status_list returncode=2 stderr='' stdout_lines=1 failure_kind=tool_input_failure codes=['prior_findings_invalid']
manifest_review_mode_list returncode=2 stderr='' stdout_lines=1 failure_kind=tool_input_failure codes=['trusted_manifest_invalid']
manifest_coverage_scope_list returncode=2 stderr='' stdout_lines=1 failure_kind=tool_input_failure codes=['trusted_manifest_invalid']
```

Rework 3 required checks:

```sh
python3 state/tasks/2026-08-11-codex-claude-orchestrator/implementation/validate_review_verdict.py --check-schema
```

Result: exit `0`

```json
{"contract_valid":true,"errors":[],"failure_kind":null,"layers":{"schema":true,"semantic":null,"transport":true},"mode":"schema_self_check"}
```

```sh
cd state/tasks/2026-08-11-codex-claude-orchestrator/implementation
python3 -m unittest discover
```

Result: exit `0`

```text
......................
----------------------------------------------------------------------
Ran 22 tests in 2.641s

OK
```

```sh
python3 - <<'PY'
from pathlib import Path
import importlib.util

root = Path('state/tasks/2026-08-11-codex-claude-orchestrator/implementation')
spec = importlib.util.spec_from_file_location('validator', root / 'validate_review_verdict.py')
validator = importlib.util.module_from_spec(spec)
spec.loader.exec_module(validator)

for expected, folder in ((True, 'valid'), (False, 'invalid')):
    for fixture in sorted((root / 'fixtures' / folder).glob('*.json')):
        targeted = fixture.name in {'targeted_verification.json', 'bad_targeted_mode.json', 'prior_digest_mismatch.json'}
        manifest = root / 'fixtures' / 'trusted' / ('manifest_targeted.json' if targeted else 'manifest_initial.json')
        prior = root / 'fixtures' / 'trusted' / 'prior_findings_targeted.json' if targeted else None
        result = validator.validate_document(fixture, trusted_manifest_path=manifest, prior_findings_path=prior)
        print(f"{fixture.relative_to(root)} expected={expected} actual={result['contract_valid']} codes={[error['code'] for error in result['errors']]}")
        if result['contract_valid'] is not expected:
            raise SystemExit(1)
PY
```

Result: exit `0`

```text
fixtures/valid/initial_blocker.json expected=True actual=True codes=[]
fixtures/valid/targeted_verification.json expected=True actual=True codes=[]
fixtures/invalid/acceptance_field.json expected=False actual=False codes=['schema_validation', 'schema_validation']
fixtures/invalid/bad_line_order.json expected=False actual=False codes=['bad_line_order']
fixtures/invalid/bad_reference.json expected=False actual=False codes=['bad_occurrence_reference']
fixtures/invalid/bad_targeted_mode.json expected=False actual=False codes=['schema_validation', 'schema_validation']
fixtures/invalid/bad_timestamps.json expected=False actual=False codes=['bad_timestamp_order', 'timestamp_out_of_review_window']
fixtures/invalid/count_mismatch.json expected=False actual=False codes=['count_mismatch']
fixtures/invalid/duplicate_key.json expected=False actual=False codes=['duplicate_key']
fixtures/invalid/fingerprint_mismatch.json expected=False actual=False codes=['finding_id_mismatch', 'occurrence_id_mismatch']
fixtures/invalid/missing_evidence.json expected=False actual=False codes=['schema_validation']
fixtures/invalid/null_criterion_omission.json expected=False actual=False codes=['schema_validation']
fixtures/invalid/occurrence_mismatch.json expected=False actual=False codes=['occurrence_id_mismatch']
fixtures/invalid/prior_digest_mismatch.json expected=False actual=False codes=['prior_digest_mismatch', 'prior_digest_mismatch', 'prior_digest_mismatch']
fixtures/invalid/reviewer_infra_classification.json expected=False actual=False codes=['schema_validation']
fixtures/invalid/severity_floor_bypass.json expected=False actual=False codes=['schema_validation']
fixtures/invalid/trailing_json.json expected=False actual=False codes=['trailing_json']
```

```sh
python3 -m py_compile state/tasks/2026-08-11-codex-claude-orchestrator/implementation/validate_review_verdict.py state/tasks/2026-08-11-codex-claude-orchestrator/implementation/tests/test_review_verdict.py
```

Result: exit `0`, no output.

```sh
git diff --check -- state/tasks/2026-08-11-codex-claude-orchestrator/implementation
```

Result: exit `0`, no output.

```sh
python3 - <<'PY'
from pathlib import Path
root = Path('state/tasks/2026-08-11-codex-claude-orchestrator/implementation')
problems = []
for path in sorted(root.rglob('*')):
    if not path.is_file() or path.parts[-2:-1] == ('__pycache__',):
        continue
    data = path.read_bytes()
    if b'\r' in data:
        problems.append(f'{path}: contains CR')
    for index, line in enumerate(data.splitlines(), 1):
        if line.endswith((b' ', b'\t')):
            problems.append(f'{path}:{index}: trailing whitespace')
if problems:
    print('\n'.join(problems))
    raise SystemExit(1)
print('implementation whitespace check passed')
PY
```

Result: exit `0`

```text
implementation whitespace check passed
```

## Scope

Edited only under:

- `state/tasks/2026-08-11-codex-claude-orchestrator/implementation/`

No commit was made. `STATE.md`, `DECISIONS.md`, task packets, reviews, shared
wrappers, skills, configuration, and unrelated workspace files were not edited.
Project memory was not updated because the rework packet allows edits only under
`implementation/`.

## Files Changed

- `validate_review_verdict.py`
- `tests/test_review_verdict.py`
- `README.md`
- `EVIDENCE.md`
- `fixtures/trusted/manifest_initial.json`
- `fixtures/trusted/manifest_targeted.json`

Previous implementation-slice files remain under this directory. The Rework 2
changes above stayed within the allowed `implementation/` subtree.

## Policy Engine Slice

Files changed in this pass:

- `orchestrator_policy.py`
- `orchestrator-state-machine.schema.json`
- `finding-registry.schema.json`
- `STATE_MACHINE.md`
- `tests/test_orchestrator_policy.py`
- `fixtures/policy/valid/accepted.json`
- `fixtures/policy/valid/known_infra.json`
- `fixtures/policy/invalid/unknown_field.json`
- `fixtures/policy/invalid/bool_counter.json`

Checklist updated:

- `../STATE_MACHINE_TASK_PACKET.md`: ticked only "Fresh local Codex implements
  in workspace-write sandbox".

Completed reviewer contract files were not modified. No commit was made.

Implemented:

- Pure `decide(task_policy, ledger, execution_report, reviewer_report)` policy
  function with ordered outcomes `FAILED_INFRA`, `REWORK`, `ESCALATED`, and
  `ACCEPTED`.
- Strict machine decisions with ordered reason codes, directives,
  budgets-after, trusted input digests, registry digest, and deterministic
  SHA-256 decision digest.
- Separate Draft 2020-12 schemas for policy fixtures and the finding registry.
- Thin bounded CLI for schema checks and fixture expectation checks.
- Finding registry merge rules: stable-ID deduplication, monotonic effective
  severity, targeted verified closure only, and later occurrence reopening.
- Tests for precedence, malformed containers/types, bool counters, replay,
  stale inputs, idempotence, deterministic permuted finding order, digest
  mismatch, allowlisted infra budgets, mixed known/unknown signatures, gate and
  evidence failures, final-full review budget, nits, and registry lifecycle.

Policy schema self-check:

```sh
python3 state/tasks/2026-08-11-codex-claude-orchestrator/implementation/orchestrator_policy.py --check-schema
```

Result: exit `0`

```json
{"errors":[],"mode":"schema_self_check","schemas_valid":true}
```

Reviewer contract schema self-check:

```sh
python3 state/tasks/2026-08-11-codex-claude-orchestrator/implementation/validate_review_verdict.py --check-schema
```

Result: exit `0`

```json
{"contract_valid":true,"errors":[],"failure_kind":null,"layers":{"schema":true,"semantic":null,"transport":true},"mode":"schema_self_check"}
```

Unit tests:

```sh
cd state/tasks/2026-08-11-codex-claude-orchestrator/implementation
python3 -m unittest discover
```

Result: exit `0`

```text
...............................................................
----------------------------------------------------------------------
Ran 63 tests in 2.862s

OK
```

Fixture expectations:

```sh
python3 state/tasks/2026-08-11-codex-claude-orchestrator/implementation/orchestrator_policy.py --check-fixtures state/tasks/2026-08-11-codex-claude-orchestrator/implementation/fixtures/policy
```

Result: exit `0`

```json
{"invalid_count":2,"invalid_results":[{"fixture":"bool_counter.json","rejected":true,"schema_errors":["True is not of type 'integer'","True should not be valid under {'type': 'boolean'}"]},{"fixture":"unknown_field.json","rejected":true,"schema_errors":["Additional properties are not allowed ('unexpected' was unexpected)","'task_policy' is a required property","'ledger' is a required property","'execution_report' is a required property","'reviewer_report' is a required property","'expected_outcome' is a required property","'expected_rule_id' is a required property"]}],"mode":"fixture_check","passed":true,"valid_count":2,"valid_results":[{"expected_outcome":"ACCEPTED","expected_rule_id":"R17_ACCEPT","fixture":"accepted.json","outcome":"ACCEPTED","rule_id":"R17_ACCEPT","valid":true},{"expected_outcome":"FAILED_INFRA","expected_rule_id":"R05_INFRA_RETRY","fixture":"known_infra.json","outcome":"FAILED_INFRA","rule_id":"R05_INFRA_RETRY","valid":true}]}
```

Python compile:

```sh
python3 -m py_compile state/tasks/2026-08-11-codex-claude-orchestrator/implementation/orchestrator_policy.py state/tasks/2026-08-11-codex-claude-orchestrator/implementation/tests/test_orchestrator_policy.py state/tasks/2026-08-11-codex-claude-orchestrator/implementation/validate_review_verdict.py state/tasks/2026-08-11-codex-claude-orchestrator/implementation/tests/test_review_verdict.py
```

Result: exit `0`, no output.

Scoped diff whitespace check:

```sh
git diff --check -- state/tasks/2026-08-11-codex-claude-orchestrator/implementation
```

Result: exit `0`, no output.

Supplemental implementation whitespace check, because this task folder is
currently untracked and `git diff --check` does not inspect untracked file
contents:

```sh
python3 - <<'PY'
from pathlib import Path
root = Path('state/tasks/2026-08-11-codex-claude-orchestrator/implementation')
problems = []
for path in sorted(root.rglob('*')):
    if not path.is_file() or '__pycache__' in path.parts:
        continue
    data = path.read_bytes()
    if b'\r' in data:
        problems.append(f'{path}: contains CR')
    for index, line in enumerate(data.splitlines(), 1):
        if line.endswith((b' ', b'\t')):
            problems.append(f'{path}:{index}: trailing whitespace')
if problems:
    print('\n'.join(problems))
    raise SystemExit(1)
print('implementation whitespace check passed')
PY
```

Result: exit `0`

```text
implementation whitespace check passed
```

Earlier slice files already present in this untracked task directory:

- `validate_review_verdict.py`
- `review-verdict.schema.json`
- `tests/test_review_verdict.py`
- `README.md`
- `EVIDENCE.md`
- `fixtures/valid/targeted_verification.json`
- `fixtures/trusted/manifest_initial.json`
- `fixtures/trusted/manifest_targeted.json`
- `fixtures/trusted/prior_findings_targeted.json`

## Implemented Hardening

- Reject decoded lone surrogates and C0 controls in every parsed JSON string.
- Accept leading JSON whitespace and continue rejecting trailing JSON.
- Convert expected file, schema, recursion, and huge-number failures to JSON.
- Separate exit codes: `0` valid/self-check, `1` contract failure, `2`
  validator/tool/input failure.
- Add `mode` and honest layer status; schema self-check uses
  `mode: "schema_self_check"` and `layers.semantic: null`.
- Reject `--check-schema` with a positional document.
- Require `--trusted-manifest` for document validation.
- Require `--prior-findings` for targeted verification and verify canonical
  prior-findings digest plus exact open-finding coverage.
- Strictly validate trusted-manifest completeness before binding: subject keys,
  expected review mode/scope, acceptance/instruction digests, non-empty unique
  criteria records, and per-criterion statement digests.
- Compare coordinator-supplied expected review mode and coverage scope against
  the reviewer document.
- Strictly validate prior-findings structure before digest or coverage use:
  document type, schema version, array shape, entry object shape, finding ID
  uniqueness, and allowed status values.
- Require and validate prior findings when the document contains a verification
  block or when the trusted manifest expects `targeted_verification`, closing
  reviewer-selected mode bypass.
- Preserve legitimate `final_full` documents that include a verification block
  by validating supplied prior findings instead of comparing against an empty
  prior set.
- Return malformed trusted-input failures as one machine-readable JSON object
  with `failure_kind: "tool_input_failure"` and CLI exit `2`.
- Enforce unique evidence IDs and unique verification result finding IDs.
- Collect all evidence before resolving references, including verification and
  infra evidence.
- Strengthen substantive and kind-consistent evidence checks.
- Tighten `appears_fixed` evidence to require command output or a digest-bound
  artifact.
- Parse every timestamp field semantically, reject leap-second-shaped values,
  and require per-run evidence timestamps to fall inside the review window.
- Enforce consistency among findings, criteria coverage, limitations, and clean
  conclusions.
- Bind subject, criteria, and review-instruction digests to the coordinator
  manifest.
- Strengthen `criterion_id: null` handling.
- Add deterministic checks for location/absence conflict and supersession
  references.
- Sanitize schema `not` errors so untrusted payloads are not echoed in full.

## Verification

Targeted Rework 2 reproductions:

```sh
python3 - <<'PY'
from pathlib import Path
import json
import subprocess
import sys

root = Path('state/tasks/2026-08-11-codex-claude-orchestrator/implementation')
out = Path('/tmp/codex-rework-2-regressions')
out.mkdir(exist_ok=True)

incomplete_manifest = out / 'incomplete_manifest.json'
incomplete_manifest.write_text(json.dumps({'document_type': 'trusted_review_manifest'}, sort_keys=True), encoding='utf-8')

malformed_prior = out / 'malformed_prior.json'
malformed_prior.write_text(json.dumps({'document_type': 'prior_findings', 'findings': 5}, sort_keys=True), encoding='utf-8')

forged = json.loads((root / 'fixtures' / 'valid' / 'targeted_verification.json').read_text(encoding='utf-8'))
forged['review']['review_mode'] = 'final_full'
forged['coverage_scope'] = 'full'
forged_doc = out / 'final_full_bypass.json'
forged_doc.write_text(json.dumps(forged, sort_keys=True), encoding='utf-8')

cases = [
    [sys.executable, str(root / 'validate_review_verdict.py'), str(root / 'fixtures' / 'valid' / 'initial_blocker.json'), '--trusted-manifest', str(incomplete_manifest)],
    [sys.executable, str(root / 'validate_review_verdict.py'), str(root / 'fixtures' / 'valid' / 'targeted_verification.json'), '--trusted-manifest', str(root / 'fixtures' / 'trusted' / 'manifest_targeted.json'), '--prior-findings', str(malformed_prior)],
    [sys.executable, str(root / 'validate_review_verdict.py'), str(forged_doc), '--trusted-manifest', str(root / 'fixtures' / 'trusted' / 'manifest_targeted.json')],
]
for index, cmd in enumerate(cases, 1):
    proc = subprocess.run(cmd, cwd=Path.cwd(), check=False, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    parsed = json.loads(proc.stdout)
    print(f'case_{index} returncode={proc.returncode} stderr={proc.stderr!r} stdout_lines={len(proc.stdout.splitlines())} failure_kind={parsed["failure_kind"]} codes={[error["code"] for error in parsed["errors"]]}')
    print(proc.stdout, end='')
PY
```

Result: exit `0`

```text
case_1 returncode=2 stderr='' stdout_lines=1 failure_kind=tool_input_failure codes=['trusted_manifest_invalid', 'trusted_manifest_invalid', 'trusted_manifest_invalid', 'trusted_manifest_invalid', 'trusted_manifest_invalid', 'trusted_manifest_invalid']
{"contract_valid":false,"errors":[{"code":"trusted_manifest_invalid","layer":"tool","message":"trusted manifest subject must be an object","pointer":"/subject"},{"code":"trusted_manifest_invalid","layer":"tool","message":"trusted manifest acceptance_criteria_digest must be a sha256 digest","pointer":"/acceptance_criteria_digest"},{"code":"trusted_manifest_invalid","layer":"tool","message":"trusted manifest review_instructions_digest must be a sha256 digest","pointer":"/review_instructions_digest"},{"code":"trusted_manifest_invalid","layer":"tool","message":"trusted manifest expected_review_mode is missing or invalid","pointer":"/expected_review_mode"},{"code":"trusted_manifest_invalid","layer":"tool","message":"trusted manifest expected_coverage_scope is missing or invalid","pointer":"/expected_coverage_scope"},{"code":"trusted_manifest_invalid","layer":"tool","message":"trusted manifest criteria must be an array","pointer":"/criteria"}],"failure_kind":"tool_input_failure","layers":{"schema":true,"semantic":false,"transport":true},"mode":"document"}
case_2 returncode=2 stderr='' stdout_lines=1 failure_kind=tool_input_failure codes=['prior_findings_invalid', 'prior_findings_invalid']
{"contract_valid":false,"errors":[{"code":"prior_findings_invalid","layer":"tool","message":"prior findings schema_version must be 1.0.0","pointer":"/schema_version"},{"code":"prior_findings_invalid","layer":"tool","message":"prior findings findings must be an array","pointer":"/findings"}],"failure_kind":"tool_input_failure","layers":{"schema":true,"semantic":false,"transport":true},"mode":"document"}
case_3 returncode=1 stderr='' stdout_lines=1 failure_kind=contract_failure codes=['trusted_binding_mismatch', 'trusted_binding_mismatch', 'prior_findings_missing']
{"contract_valid":false,"errors":[{"code":"trusted_binding_mismatch","layer":"semantic","message":"review_mode differs from trusted manifest","pointer":"/review/review_mode"},{"code":"trusted_binding_mismatch","layer":"semantic","message":"coverage_scope differs from trusted manifest","pointer":"/coverage_scope"},{"code":"prior_findings_missing","layer":"semantic","message":"verification requires coordinator-supplied --prior-findings","pointer":""}],"failure_kind":"contract_failure","layers":{"schema":true,"semantic":false,"transport":true},"mode":"document"}
```

Schema self-check:

```sh
python3 state/tasks/2026-08-11-codex-claude-orchestrator/implementation/validate_review_verdict.py --check-schema
```

Result: exit `0`

```json
{"contract_valid":true,"errors":[],"failure_kind":null,"layers":{"schema":true,"semantic":null,"transport":true},"mode":"schema_self_check"}
```

Fixture check:

```sh
python3 - <<'PY'
from pathlib import Path
import importlib.util

root = Path('state/tasks/2026-08-11-codex-claude-orchestrator/implementation')
spec = importlib.util.spec_from_file_location('validator', root / 'validate_review_verdict.py')
validator = importlib.util.module_from_spec(spec)
spec.loader.exec_module(validator)

for expected, folder in ((True, 'valid'), (False, 'invalid')):
    for fixture in sorted((root / 'fixtures' / folder).glob('*.json')):
        targeted = fixture.name in {'targeted_verification.json', 'bad_targeted_mode.json', 'prior_digest_mismatch.json'}
        manifest = root / 'fixtures' / 'trusted' / ('manifest_targeted.json' if targeted else 'manifest_initial.json')
        prior = root / 'fixtures' / 'trusted' / 'prior_findings_targeted.json' if targeted else None
        result = validator.validate_document(fixture, trusted_manifest_path=manifest, prior_findings_path=prior)
        print(f"{fixture.relative_to(root)} expected={expected} actual={result['contract_valid']} codes={[error['code'] for error in result['errors']]}")
        if result['contract_valid'] is not expected:
            raise SystemExit(1)
PY
```

Result: exit `0`

```text
fixtures/valid/initial_blocker.json expected=True actual=True codes=[]
fixtures/valid/targeted_verification.json expected=True actual=True codes=[]
fixtures/invalid/acceptance_field.json expected=False actual=False codes=['schema_validation', 'schema_validation']
fixtures/invalid/bad_line_order.json expected=False actual=False codes=['bad_line_order']
fixtures/invalid/bad_reference.json expected=False actual=False codes=['bad_occurrence_reference']
fixtures/invalid/bad_targeted_mode.json expected=False actual=False codes=['schema_validation', 'schema_validation']
fixtures/invalid/bad_timestamps.json expected=False actual=False codes=['bad_timestamp_order', 'timestamp_out_of_review_window']
fixtures/invalid/count_mismatch.json expected=False actual=False codes=['count_mismatch']
fixtures/invalid/duplicate_key.json expected=False actual=False codes=['duplicate_key']
fixtures/invalid/fingerprint_mismatch.json expected=False actual=False codes=['finding_id_mismatch', 'occurrence_id_mismatch']
fixtures/invalid/missing_evidence.json expected=False actual=False codes=['schema_validation']
fixtures/invalid/null_criterion_omission.json expected=False actual=False codes=['schema_validation']
fixtures/invalid/occurrence_mismatch.json expected=False actual=False codes=['occurrence_id_mismatch']
fixtures/invalid/prior_digest_mismatch.json expected=False actual=False codes=['prior_digest_mismatch', 'prior_digest_mismatch', 'prior_digest_mismatch']
fixtures/invalid/reviewer_infra_classification.json expected=False actual=False codes=['schema_validation']
fixtures/invalid/severity_floor_bypass.json expected=False actual=False codes=['schema_validation']
fixtures/invalid/trailing_json.json expected=False actual=False codes=['trailing_json']
```

Unit tests:

```sh
cd state/tasks/2026-08-11-codex-claude-orchestrator/implementation
python3 -m unittest discover
```

Result: exit `0`

```text
....................
----------------------------------------------------------------------
Ran 20 tests in 2.246s

OK
```

Python compile check:

```sh
python3 -m py_compile state/tasks/2026-08-11-codex-claude-orchestrator/implementation/validate_review_verdict.py state/tasks/2026-08-11-codex-claude-orchestrator/implementation/tests/test_review_verdict.py
```

Result: exit `0`, no output.

Scoped whitespace check:

```sh
git diff --check -- state/tasks/2026-08-11-codex-claude-orchestrator/implementation
```

Result: exit `0`, no output.

Supplemental implementation whitespace check:

```sh
python3 - <<'PY'
from pathlib import Path
root = Path('state/tasks/2026-08-11-codex-claude-orchestrator/implementation')
problems = []
for path in sorted(root.rglob('*')):
    if not path.is_file() or path.parts[-2:-1] == ('__pycache__',):
        continue
    data = path.read_bytes()
    if b'\r' in data:
        problems.append(f'{path}: contains CR')
    for index, line in enumerate(data.splitlines(), 1):
        if line.endswith((b' ', b'\t')):
            problems.append(f'{path}:{index}: trailing whitespace')
if problems:
    print('\n'.join(problems))
    raise SystemExit(1)
print('implementation whitespace check passed')
PY
```

Result: exit `0`

```text
implementation whitespace check passed
```

Scoped git status:

```sh
git status --short -- state/tasks/2026-08-11-codex-claude-orchestrator/implementation
```

Result: exit `0`

```text
?? state/tasks/2026-08-11-codex-claude-orchestrator/implementation/
```

## Residual Limitations

- This slice validates reviewer-contract documents only. It still does not
  accept, merge, resolve, approve, classify `FAILED_INFRA`, or mutate state.
- Trusted manifest and prior-findings files are assumed to be supplied by the
  deterministic coordinator. This slice verifies consistency with those files;
  it does not compute repository diffs, changed-file digests, or instruction
  digests itself.
- Artifact existence, symlink containment, and `content_digest` byte
  verification remain outside this local contract slice because no artifact
  root/access policy is in scope.
- Free-text reviewer fields remain untrusted observation data.

## R4 Targeted Closure Evidence

Scope:

- Implemented only R3-01 and R3-02 from
  `reviews/claude-state-machine-r3-closure.md`.
- Edited only files under `implementation/`.
- No commit was created.

Changed files:

- `implementation/orchestrator_policy.py`
- `implementation/orchestrator-state-machine.schema.json`
- `implementation/STATE_MACHINE.md`
- `implementation/tests/test_orchestrator_policy.py`
- `implementation/EVIDENCE.md`

R4 fixes:

- Added public `progress_identity` to every decision object and documented the
  exact canonical preimage, JSON serialization, hash prefix, and fields.
- Added public `progress_identity(execution_report)` for deterministic
  derivation, while tests build ledger prior attempts from emitted decision
  output.
- Strengthened no-progress coverage: first repeat advances a nonzero streak,
  changed subject resets that nonzero streak to `0`, and the next identical
  repeat reaches the configured `NO_PROGRESS` boundary.
- Replaced weak deep-input coverage with exact 3000-level public `decide()`
  cases under `ledger.prior_attempts` and paired
  `execution_report.payload`/`payload_digest`. The assertions verify rejected
  input digests, so they cannot pass solely because of ordinary schema errors.

Focused R4 tests:

```sh
cd state/tasks/2026-08-11-codex-claude-orchestrator/implementation
python3 -m unittest tests.test_orchestrator_policy.OrchestratorPolicyTests.test_decision_exposes_exact_public_progress_identity tests.test_orchestrator_policy.OrchestratorPolicyTests.test_no_progress_advances_from_prior_decision_outputs_and_resets_on_changed_identity tests.test_orchestrator_policy.OrchestratorPolicyTests.test_deep_prior_attempts_and_payload_fail_closed_through_decide tests.test_orchestrator_policy.OrchestratorPolicyTests.test_payload_fixtures_exercise_cli_schema_and_policy_contract tests.test_orchestrator_policy.OrchestratorPolicyTests.test_documented_precedence_matches_safe_source_order
```

Result: exit `0`

```text
.....
----------------------------------------------------------------------
Ran 5 tests in 0.320s

OK
```

Full unit tests:

```sh
cd state/tasks/2026-08-11-codex-claude-orchestrator/implementation
python3 -m unittest discover
```

Result: exit `0`

```text
....................................................................................
----------------------------------------------------------------------
Ran 84 tests in 3.059s

OK
```

State-machine schema self-check:

```sh
cd state/tasks/2026-08-11-codex-claude-orchestrator/implementation
python3 orchestrator_policy.py --check-schema
```

Result: exit `0`

```json
{"errors":[],"mode":"schema_self_check","schemas_valid":true}
```

Reviewer schema self-check:

```sh
cd state/tasks/2026-08-11-codex-claude-orchestrator/implementation
python3 validate_review_verdict.py --check-schema
```

Result: exit `0`

```json
{"contract_valid":true,"errors":[],"failure_kind":null,"layers":{"schema":true,"semantic":null,"transport":true},"mode":"schema_self_check"}
```

Policy fixture check:

```sh
cd state/tasks/2026-08-11-codex-claude-orchestrator/implementation
python3 orchestrator_policy.py --check-fixtures fixtures/policy
```

Result: exit `0`

```json
{"invalid_count":3,"invalid_results":[{"fixture":"bool_counter.json","rejected":true,"schema_errors":["True is not of type 'integer'","True should not be valid under {'type': 'boolean'}"]},{"fixture":"missing_payload_digest.json","rejected":true,"schema_errors":["'payload_digest' is a dependency of 'payload'"]},{"fixture":"unknown_field.json","rejected":true,"schema_errors":["Additional properties are not allowed ('unexpected' was unexpected)","'task_policy' is a required property","'ledger' is a required property","'execution_report' is a required property","'reviewer_report' is a required property","'expected_outcome' is a required property","'expected_rule_id' is a required property"]}],"mode":"fixture_check","passed":true,"valid_count":4,"valid_results":[{"expected_outcome":"ACCEPTED","expected_rule_id":"R17_ACCEPT","fixture":"accepted.json","outcome":"ACCEPTED","rule_id":"R17_ACCEPT","valid":true},{"expected_outcome":"ACCEPTED","expected_rule_id":"R17_ACCEPT","fixture":"accepted_with_payload.json","outcome":"ACCEPTED","rule_id":"R17_ACCEPT","valid":true},{"expected_outcome":"FAILED_INFRA","expected_rule_id":"R05_INFRA_RETRY","fixture":"known_infra.json","outcome":"FAILED_INFRA","rule_id":"R05_INFRA_RETRY","valid":true},{"expected_outcome":"ESCALATED","expected_rule_id":"R04_INCOMPLETE","fixture":"payload_digest_mismatch.json","outcome":"ESCALATED","rule_id":"R04_INCOMPLETE","valid":true}]}
```

Reviewer fixture check:

```sh
cd state/tasks/2026-08-11-codex-claude-orchestrator/implementation
python3 - <<'PY'
from pathlib import Path
import importlib.util

root = Path('.')
spec = importlib.util.spec_from_file_location('validator', root / 'validate_review_verdict.py')
validator = importlib.util.module_from_spec(spec)
spec.loader.exec_module(validator)

for expected, folder in ((True, 'valid'), (False, 'invalid')):
    for fixture in sorted((root / 'fixtures' / folder).glob('*.json')):
        targeted = fixture.name in {'targeted_verification.json', 'bad_targeted_mode.json', 'prior_digest_mismatch.json'}
        manifest = root / 'fixtures' / 'trusted' / ('manifest_targeted.json' if targeted else 'manifest_initial.json')
        prior = root / 'fixtures' / 'trusted' / 'prior_findings_targeted.json' if targeted else None
        result = validator.validate_document(fixture, trusted_manifest_path=manifest, prior_findings_path=prior)
        codes = [error['code'] for error in result['errors']]
        print(f"{fixture.relative_to(root)} expected={expected} actual={result['contract_valid']} codes={codes}")
        if result['contract_valid'] is not expected:
            raise SystemExit(1)
PY
```

Result: exit `0`

```text
fixtures/valid/initial_blocker.json expected=True actual=True codes=[]
fixtures/valid/targeted_verification.json expected=True actual=True codes=[]
fixtures/invalid/acceptance_field.json expected=False actual=False codes=['schema_validation', 'schema_validation']
fixtures/invalid/bad_line_order.json expected=False actual=False codes=['bad_line_order']
fixtures/invalid/bad_reference.json expected=False actual=False codes=['bad_occurrence_reference']
fixtures/invalid/bad_targeted_mode.json expected=False actual=False codes=['schema_validation', 'schema_validation']
fixtures/invalid/bad_timestamps.json expected=False actual=False codes=['bad_timestamp_order', 'timestamp_out_of_review_window']
fixtures/invalid/count_mismatch.json expected=False actual=False codes=['count_mismatch']
fixtures/invalid/duplicate_key.json expected=False actual=False codes=['duplicate_key']
fixtures/invalid/fingerprint_mismatch.json expected=False actual=False codes=['finding_id_mismatch', 'occurrence_id_mismatch']
fixtures/invalid/missing_evidence.json expected=False actual=False codes=['schema_validation']
fixtures/invalid/null_criterion_omission.json expected=False actual=False codes=['schema_validation']
fixtures/invalid/occurrence_mismatch.json expected=False actual=False codes=['occurrence_id_mismatch']
fixtures/invalid/prior_digest_mismatch.json expected=False actual=False codes=['prior_digest_mismatch', 'prior_digest_mismatch', 'prior_digest_mismatch']
fixtures/invalid/reviewer_infra_classification.json expected=False actual=False codes=['schema_validation']
fixtures/invalid/severity_floor_bypass.json expected=False actual=False codes=['schema_validation']
fixtures/invalid/trailing_json.json expected=False actual=False codes=['trailing_json']
```

Python compile check:

```sh
cd state/tasks/2026-08-11-codex-claude-orchestrator/implementation
python3 -m py_compile orchestrator_policy.py validate_review_verdict.py tests/test_orchestrator_policy.py tests/test_review_verdict.py
```

Result: exit `0`, no output.

Scoped diff check:

```sh
git diff --check -- implementation
```

Result: exit `0`, no output.

Supplemental implementation whitespace check:

```sh
python3 - <<'PY'
from pathlib import Path
root = Path('implementation')
problems = []
for path in sorted(root.rglob('*')):
    if not path.is_file() or '__pycache__' in path.parts:
        continue
    data = path.read_bytes()
    if b'\r' in data:
        problems.append(f'{path}: contains CR')
    for index, line in enumerate(data.splitlines(), 1):
        if line.endswith((b' ', b'\t')):
            problems.append(f'{path}:{index}: trailing whitespace')
if problems:
    print('\n'.join(problems))
    raise SystemExit(1)
print('implementation whitespace check passed')
PY
```

Result: exit `0`

```text
implementation whitespace check passed
```

Scoped git status:

```sh
git status --short -- implementation
```

Result: exit `0`

```text
?? implementation/
```

## R4 Final Verification Addendum

After tightening terminal-decision validation for the new
`progress_identity` field, all required checks were rerun.

Focused R4 tests:

```sh
cd state/tasks/2026-08-11-codex-claude-orchestrator/implementation
python3 -m unittest tests.test_orchestrator_policy.OrchestratorPolicyTests.test_decision_exposes_exact_public_progress_identity tests.test_orchestrator_policy.OrchestratorPolicyTests.test_no_progress_advances_from_prior_decision_outputs_and_resets_on_changed_identity tests.test_orchestrator_policy.OrchestratorPolicyTests.test_deep_prior_attempts_and_payload_fail_closed_through_decide tests.test_orchestrator_policy.OrchestratorPolicyTests.test_payload_fixtures_exercise_cli_schema_and_policy_contract tests.test_orchestrator_policy.OrchestratorPolicyTests.test_documented_precedence_matches_safe_source_order
```

Result: exit `0`

```text
.....
----------------------------------------------------------------------
Ran 5 tests in 0.346s

OK
```

Full unit tests:

```sh
python3 -m unittest discover
```

Result: exit `0`

```text
....................................................................................
----------------------------------------------------------------------
Ran 84 tests in 3.171s

OK
```

Schema self-checks:

```sh
python3 orchestrator_policy.py --check-schema
python3 validate_review_verdict.py --check-schema
```

Results: both exit `0`

```json
{"errors":[],"mode":"schema_self_check","schemas_valid":true}
{"contract_valid":true,"errors":[],"failure_kind":null,"layers":{"schema":true,"semantic":null,"transport":true},"mode":"schema_self_check"}
```

Policy fixture check:

```sh
python3 orchestrator_policy.py --check-fixtures fixtures/policy
```

Result: exit `0`

```json
{"invalid_count":3,"invalid_results":[{"fixture":"bool_counter.json","rejected":true,"schema_errors":["True is not of type 'integer'","True should not be valid under {'type': 'boolean'}"]},{"fixture":"missing_payload_digest.json","rejected":true,"schema_errors":["'payload_digest' is a dependency of 'payload'"]},{"fixture":"unknown_field.json","rejected":true,"schema_errors":["Additional properties are not allowed ('unexpected' was unexpected)","'task_policy' is a required property","'ledger' is a required property","'execution_report' is a required property","'reviewer_report' is a required property","'expected_outcome' is a required property","'expected_rule_id' is a required property"]}],"mode":"fixture_check","passed":true,"valid_count":4,"valid_results":[{"expected_outcome":"ACCEPTED","expected_rule_id":"R17_ACCEPT","fixture":"accepted.json","outcome":"ACCEPTED","rule_id":"R17_ACCEPT","valid":true},{"expected_outcome":"ACCEPTED","expected_rule_id":"R17_ACCEPT","fixture":"accepted_with_payload.json","outcome":"ACCEPTED","rule_id":"R17_ACCEPT","valid":true},{"expected_outcome":"FAILED_INFRA","expected_rule_id":"R05_INFRA_RETRY","fixture":"known_infra.json","outcome":"FAILED_INFRA","rule_id":"R05_INFRA_RETRY","valid":true},{"expected_outcome":"ESCALATED","expected_rule_id":"R04_INCOMPLETE","fixture":"payload_digest_mismatch.json","outcome":"ESCALATED","rule_id":"R04_INCOMPLETE","valid":true}]}
```

Reviewer fixture check:

```sh
python3 - <<'PY'
from pathlib import Path
import importlib.util

root = Path('.')
spec = importlib.util.spec_from_file_location('validator', root / 'validate_review_verdict.py')
validator = importlib.util.module_from_spec(spec)
spec.loader.exec_module(validator)

for expected, folder in ((True, 'valid'), (False, 'invalid')):
    for fixture in sorted((root / 'fixtures' / folder).glob('*.json')):
        targeted = fixture.name in {'targeted_verification.json', 'bad_targeted_mode.json', 'prior_digest_mismatch.json'}
        manifest = root / 'fixtures' / 'trusted' / ('manifest_targeted.json' if targeted else 'manifest_initial.json')
        prior = root / 'fixtures' / 'trusted' / 'prior_findings_targeted.json' if targeted else None
        result = validator.validate_document(fixture, trusted_manifest_path=manifest, prior_findings_path=prior)
        codes = [error['code'] for error in result['errors']]
        print(f"{fixture.relative_to(root)} expected={expected} actual={result['contract_valid']} codes={codes}")
        if result['contract_valid'] is not expected:
            raise SystemExit(1)
PY
```

Result: exit `0`

```text
fixtures/valid/initial_blocker.json expected=True actual=True codes=[]
fixtures/valid/targeted_verification.json expected=True actual=True codes=[]
fixtures/invalid/acceptance_field.json expected=False actual=False codes=['schema_validation', 'schema_validation']
fixtures/invalid/bad_line_order.json expected=False actual=False codes=['bad_line_order']
fixtures/invalid/bad_reference.json expected=False actual=False codes=['bad_occurrence_reference']
fixtures/invalid/bad_targeted_mode.json expected=False actual=False codes=['schema_validation', 'schema_validation']
fixtures/invalid/bad_timestamps.json expected=False actual=False codes=['bad_timestamp_order', 'timestamp_out_of_review_window']
fixtures/invalid/count_mismatch.json expected=False actual=False codes=['count_mismatch']
fixtures/invalid/duplicate_key.json expected=False actual=False codes=['duplicate_key']
fixtures/invalid/fingerprint_mismatch.json expected=False actual=False codes=['finding_id_mismatch', 'occurrence_id_mismatch']
fixtures/invalid/missing_evidence.json expected=False actual=False codes=['schema_validation']
fixtures/invalid/null_criterion_omission.json expected=False actual=False codes=['schema_validation']
fixtures/invalid/occurrence_mismatch.json expected=False actual=False codes=['occurrence_id_mismatch']
fixtures/invalid/prior_digest_mismatch.json expected=False actual=False codes=['prior_digest_mismatch', 'prior_digest_mismatch', 'prior_digest_mismatch']
fixtures/invalid/reviewer_infra_classification.json expected=False actual=False codes=['schema_validation']
fixtures/invalid/severity_floor_bypass.json expected=False actual=False codes=['schema_validation']
fixtures/invalid/trailing_json.json expected=False actual=False codes=['trailing_json']
```

Compile, diff, whitespace, status, and commit checks:

```sh
python3 -m py_compile orchestrator_policy.py validate_review_verdict.py tests/test_orchestrator_policy.py tests/test_review_verdict.py
git diff --check -- implementation
python3 supplemental whitespace check
git status --short -- implementation
git log -1 --oneline
```

Results:

- `py_compile`: exit `0`, no output.
- `git diff --check -- implementation`: exit `0`, no output.
- Supplemental whitespace: exit `0`, `implementation whitespace check passed`.
- Scoped status: exit `0`, `?? implementation/`.
- Last commit unchanged: `f558763 fix: improve Spectech mobile layout and contact links`.

## Coordinator Final Closure

- Fresh targeted R4 Claude review returned `TARGETED_PASS`; R3-01 and R3-02
  are closed with no open blocker/major.
- Fresh current-tree final-full Claude review returned `FINAL_FULL_PASS`; no
  blocker/major findings remain.
- Final mechanical policy run of `fixtures/policy/valid/accepted.json` returned
  `ACCEPTED/R17_ACCEPT` with `valid: true`.
- Final independent rerun: 84/84 tests, both schema self-checks, policy
  fixtures, `py_compile`, scoped diff, and whitespace all passed.
- No commit was created; unrelated dirty-worktree changes were preserved.
