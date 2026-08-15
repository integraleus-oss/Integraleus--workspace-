# Task Packet: Alpha/SCADA Engineer Agent Trial On PS01

## Role Prompt
Use the accepted prompt at:
`/home/stanislav/.openclaw/workspace/agents/main/state/tasks/2026-07-31-scada-engineer-prompt-alpha-review/scada-engineer-prompt-alpha-corrected.md`

Treat it as your role and behavior contract for this trial.

## Project To Review
Review the PS01 pump-station project as an Alpha Platform candidate:

- Primary demo package:
  `/home/stanislav/.openclaw/workspace/agents/main/outbound/2026-07-30-ps01-full-scada`
- Native Alpha package candidate:
  `/home/stanislav/.openclaw/workspace/agents/main/outbound/2026-07-30-ps01-alpha-platform-project/PS01_AlphaPlatform_native.zip`
- Alpha.HMI dev root:
  `/home/stanislav/work/alpha-hmi-dev`
- Alpha.HMI native PS01 output:
  `/home/stanislav/work/alpha-hmi-dev/out/ps01_pump_station_cascade_native_20260729`

## Required Sources
Before judging Alpha product/module names, read:
`/home/stanislav/.openclaw/workspace/agents/main/docs/alpha_platform/PRODUCT_CHEATSHEET.md`

Before judging HMI design, read:
`/home/stanislav/.openclaw/workspace/agents/main/skills/asu-tp-hmi-checklist/SKILL.md`

Use local project files and evidence screenshots/reports. Do not use internet.

## Scope
This is a read-only review pass. Do not edit project files.

Evaluate:
- whether the deliverable is truly an Alpha Platform project or a companion/demo;
- which Alpha modules are actually represented and which are stubbed or external;
- HMI completeness for PS01: 4 pumps H1..H4, cascade pressure control, measurements, alarm state, trends, reports;
- HPHMI/ISA-101 quality: calm palette, alarm color reservation, process topology clarity, labels, sensor hookups, no decorative P&ID behavior;
- tag/object structure and reuse readiness;
- alarm philosophy and operator action clarity;
- evidence quality: screenshots, smoke checks, ZIP checks, native compile/viewer evidence;
- top 5 defects or risks blocking a serious Alpha handoff;
- top 5 practical improvements for the next iteration.

## Output
Write your report to:
`/home/stanislav/.openclaw/workspace/agents/main/state/tasks/2026-07-31-alpha-scada-agent-ps01-trial/AGENT_REPORT.md`

Format:
- Verdict: GO / CONDITIONAL GO / NO-GO for “use as Alpha Platform project candidate”.
- Evidence reviewed.
- Module mapping table in bullets, not Markdown table.
- Findings ordered by severity.
- Concrete next actions.
- Explicit uncertainty list.

Do not send messages to Stanislav. The main agent will review and send the final summary.
