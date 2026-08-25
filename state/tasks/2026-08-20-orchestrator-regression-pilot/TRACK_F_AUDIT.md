# Track F Audit

Verdict: ACCEPTED FOR SCOPED LOCAL COMMIT

The unfinished worktree is one coherent portable-appliance slice: an x86_64
OVA route for Windows, Linux, and Intel macOS hosts, with Ubuntu 24.04 retained
as the guest runtime and ARM64 explicitly deferred. The slice includes build
integration, customer-safe documentation, compatibility data, first-boot
credential setup, export tooling, tests, and regenerated checksummed packs.

Verified:

- appliance regression tests 4/4;
- shell syntax;
- OVA, complete offline archive, and verification-pack ZIP checksums;
- expected OVA and offline-archive members;
- no embedded password/private SSH key in the tested first-boot contract;
- `git diff --check`.

Known boundary: KVM conversion/import/start/smoke is the accepted rehearsal.
VirtualBox and VMware host-specific rehearsals remain explicitly required and
are not claimed complete.

Next gate: create one scoped local Track F commit, verify a clean worktree and
rerun the focused checks. Only then prepare pilot #4; no push or deploy is part
of this gate.
