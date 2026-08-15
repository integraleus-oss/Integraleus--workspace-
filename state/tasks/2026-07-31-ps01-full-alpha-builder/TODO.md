# PS01 Full Alpha Builder

## Goal
Give the accepted Alpha/SCADA engineer agent a controlled builder task to create a fuller PS01 Alpha Platform project candidate from the new TZ v2.0.

## Inputs
- TZ: `/home/stanislav/.openclaw/media/inbound/ТЗ_HMI_для_ИИ_агента_2---e88c5794-8d33-42d6-8783-d4ee2a4b5b97.md`
- Accepted role prompt: `/home/stanislav/.openclaw/workspace/agents/main/state/tasks/2026-07-31-scada-engineer-prompt-alpha-review/scada-engineer-prompt-alpha-corrected.md`
- Existing PS01 review: `/home/stanislav/.openclaw/workspace/agents/main/state/tasks/2026-07-31-alpha-scada-agent-ps01-trial/AGENT_REPORT_RU.md`
- Existing PS01 work: `/home/stanislav/work/alpha-hmi-dev`

## Checklist
- [x] Read current Alpha product guardrail.
- [x] Read live HMI checklist skill.
- [x] Read accepted Alpha/SCADA role prompt.
- [x] Read TZ v2.0.
- [x] Create controlled builder task packet.
- [x] Launch Alpha/SCADA builder agent.
- [x] Receive builder result.
- [x] Parent review of files, evidence, and risks.
- [x] Send Stanislav concise result and artifacts.

## Delivered Artifacts

- Sent Telegram package from workspace outbound mirror:
  `/home/stanislav/.openclaw/workspace/agents/main/outbound/2026-07-31-ps01-full-alpha-builder/PS01_FullAlpha_Project_20260731.zip`
- Sent report:
  `/home/stanislav/.openclaw/workspace/agents/main/outbound/2026-07-31-ps01-full-alpha-builder/PS01_FullAlpha_BUILDER_REPORT.md`
- Sent screenshots:
  `/home/stanislav/.openclaw/workspace/agents/main/outbound/2026-07-31-ps01-full-alpha-builder/ps01_normal_viewer.png`
  `/home/stanislav/.openclaw/workspace/agents/main/outbound/2026-07-31-ps01-full-alpha-builder/ps01_alarm_viewer.png`
- ZIP SHA-256:
  `91e840bae37b9f4f5ec74f0d09c907b14a2c439629165ea5a2333877bf33c426`

## Boundaries
- Work in a new isolated output folder; do not modify existing PS01 packages unless explicitly justified.
- No production deployment.
- No changes to live Alpha services in `/opt/Automiq`.
- No real PLC/OPC/IEC connection attempts.
- No external sending.
- Final report and artifacts must be in Russian.
