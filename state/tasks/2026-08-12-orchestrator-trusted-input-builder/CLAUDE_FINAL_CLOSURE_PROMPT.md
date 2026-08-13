# Final targeted closure: trusted builder

Read both prior reviews and verify the current scoped files. Confirm specifically:

- all generated identifiers satisfy the accepted reviewer schema;
- a builder-generated manifest + verdict now reaches real projection and policy
  admission in an automated test and returns `R17_ACCEPT`;
- post-gate HEAD is rechecked;
- review prompt requests exact JSON rather than a nonexistent output path;
- attempt-1 counters, progress identity, seen nonce, and finding registry are
  carried into attempt 2 instead of reset.

Run/read tests if permitted; otherwise perform static verification. Report only
remaining blocker/major findings. End with exactly
`TRUSTED_BUILDER_FINAL_PASS` or `TRUSTED_BUILDER_FINAL_REWORK`.
