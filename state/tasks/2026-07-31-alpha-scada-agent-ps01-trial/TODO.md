# Alpha SCADA Agent PS01 Trial

## Goal
Run the accepted Alpha/SCADA engineer prompt against the PS01 project package and see how the agent handles a real Alpha Platform project review.

## Target Project
- Primary package: `/home/stanislav/.openclaw/workspace/agents/main/outbound/2026-07-30-ps01-full-scada`
- Native Alpha package candidate: `/home/stanislav/.openclaw/workspace/agents/main/outbound/2026-07-30-ps01-alpha-platform-project/PS01_AlphaPlatform_native.zip`
- Alpha.HMI dev source/root: `/home/stanislav/work/alpha-hmi-dev`
- Alpha.HMI PS01 native output: `/home/stanislav/work/alpha-hmi-dev/out/ps01_pump_station_cascade_native_20260729`

## Checklist
- [x] Create task packet before launching the agent.
- [x] Launch Alpha/SCADA engineer agent trial.
- [x] Receive agent report.
- [x] Main-agent review of report quality.
- [x] Send Stanislav verdict and next action.
- [x] Translate agent report to Russian after language issue.

## Guardrails
- Read-only review pass first.
- No production deployment.
- No live service changes.
- No real PLC/OPC/IEC connections.
- No external sending by the subagent.
- No licensing/TKP final calculations.
- Any code/project changes require a separate explicit approval after the report.
