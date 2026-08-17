# Independent review request

Review the current uncommitted diff for the reviewer transport normalization.

Focus on fail-open risks, mutation of substantive reviewer meaning, evidence-chain
integrity, schema/semantic validation ordering, deterministic behavior, and test
gaps. The only permitted repairs are truncating `findings[].title` to the sealed
160-character limit and removing undefined evidence references. A satisfied
criterion affected by an undefined reference must become not verifiable and must
not permit ACCEPT. The original verdict file must remain preserved in the runner
snapshot. Report findings by severity (blocker/major/nit) and finish with ACCEPT
only if there are no blocker or major findings.
