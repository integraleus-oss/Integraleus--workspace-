# Bounded R4 Review Repair

Repair the isolated R4 snapshot only. The snapshot commit `72b06e7` is an
unaccepted local baseline made solely so the trusted builder can measure this
repair; it is not canonical Alpha BPR and must not be transferred.

Fix all seven findings from the sealed R4 review without expanding the product
slice:

1. Make JSON member matching case-sensitive and numeric parsing strict while
   retaining deliberate camelCase serialization. Add negative tests for a
   case-variant member and a quoted numeric member.
2. Fail closed with diagnostics for integer transform overflow and non-finite
   double results. Add focused tests for both.
3. Load, validate, fixture, and test Alpha BPR Contract v1; eliminate duplicated
   private supported-value literals by deriving validation from the contract or
   a single typed contract source.
4. Remove fixture-transport identity from the application validator. Transport
   proof belongs in infrastructure/test composition, not product validation.
5. Exercise multiple endpoints and rejection of non-read-only or non-OPC-UA
   endpoints.
6. Fail closed, without `NullReferenceException`, when observation readings are
   absent.
7. Correct the ADR-009 heading.

Preserve the read-only boundary, arbitrary NodeIds/equipment, deterministic
`ORCHESTRATOR_FIXTURE_ROOT` discovery, closed schemas, existing examples, and
the explicit statement that fixture proof is not connected Alpha Platform or
customer compatibility evidence.

Change only the paths allowed by `PRODUCTION_TASK.json`. Do not read or reuse
v1/R2/R3 worktrees or outputs. Do not modify canonical Alpha BPR. Do not commit,
transfer, push, deploy, access credentials/private endpoints, or touch VMs,
services, Gateway, or Alpha packages. Never invoke dotnet directly; use only the
sealed harness modes.
