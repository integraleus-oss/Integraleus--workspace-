---
name: "asu-tp-hmi-checklist"
description: "АСУ ТП HMI/SCADA with Alpha HPHMI review layer."
---

# ASU TP HMI Checklist

Use this skill before creating, reviewing, or revising any ASU TP, SCADA, Alpha.HMI, pump-station, process-control, P&ID-like, or industrial mnemonic screen.

Primary references:
- The approved `hmi-screen-design` archive recovered and reviewed on 2026-07-31, especially `CORE.md`, `references/review-checklist.md`, `references/color-and-symbols.md`, `references/layout-and-typography.md`, `references/display-elements.md`, `references/schematic-completeness.md`, `references/alarms.md`, `rules/hmi-rules.json`, and `assets/hphmi-palette.json`.
- Rockwell Automation Process HMI Style Guide RU, especially screen hierarchy, layout, color, lines, equipment, labels, dynamic values, trends, faceplates, alarms, and performance.
- The High Performance HMI Handbook, especially principles for low-clutter operator graphics, grayscale equipment, restrained color, trends, alarm behavior, instrument lines, and display hierarchy.

## Hard Alpha Platform Rule

When Stanislav says to make a project on Alpha Platform, make it with Alpha Platform means.

Home has Alpha Platform installed and has hosted prior Alpha projects. Do not assume Alpha tools are unavailable. Before falling back to import-only artifacts or non-Alpha companions, check the local Home install, services, CLI tools, and existing project roots, especially `/opt/Automiq` and `/home/stanislav/work/alpha-hmi-dev`.

Home also has local Alpha Platform documentation and training-course material. Before guessing, inventing APIs, declaring a documentation gap, or hand-rolling behavior, consult the available sources in this order:
- product guardrail: `docs/alpha_platform/PRODUCT_CHEATSHEET.md`;
- local documentation index and extracted manuals: `docs/alpha_platform/INDEX.md`, `AlphaPlatform_*_text.md`, module notes, support guides;
- training course material such as `docs/alpha_platform/Alpha_Basic_Course_text.md` and local course PDFs;
- real exported/import-validated Alpha.HMI `.omobj` / `.hmi` examples for exact XML/base-type details.

Web access is valid when it is the native Alpha web path, especially Alpha.HMI.WebViewer serving an Alpha.HMI project through a browser.
Process/PLC signal imitation is valid when it uses the native Alpha testing path, especially Alpha.Imitator, or another explicitly specified Alpha Platform component.
Do not substitute a standalone non-Alpha web/Python/HTML application or simulator for the requested Alpha project.
A separate non-Alpha browser-accessible simulator, export, screenshot, ZIP, or documentation may be added only as a companion artifact, and it must be clearly labeled as such.

For an Alpha Platform project, the expected deliverable should use the actual current Alpha components that apply to the spec, such as:
- Alpha.Server for server configuration, signals, calculations, data source bindings, and command handling;
- Alpha.HMI / Alpha.HMI.WebViewer for HMI screens and browser viewing;
- Alpha.HMI.Alarms for alarms and event handling;
- alpha.hmi.charts inside Alpha.HMI for trends;
- Alpha.Historian for historical values/events;
- Alpha.Reports for reports;
- Alpha.Security for roles/audit when the spec requires access control;
- Alpha.Imitator for process/PLC signal imitation in a test stand;
- Alpha.DevStudio / Alpha.Om where project configuration, formulas, procedures, compilation, or deployment are needed.

If a required Alpha tool/module/license is actually missing or inaccessible after checking Home and docs, say that explicitly before building and create the closest valid Alpha import/config/package plus a separate runnable non-Alpha companion only if useful. Do not present that companion as the Alpha Platform project.

Before final delivery of any requested Alpha Platform project, verify and report which Alpha modules are actually used and which are stubbed, simulated through Alpha.Imitator, externally simulated, or unavailable.

## Detailed HPHMI / ISA-101 Layer

The `hmi-screen-design` archive is an approved detailed design and review layer for Alpha.HMI and SCADA screens. It does not replace Alpha Platform documentation or local known-good Alpha exports. Use it to decide what a good operator screen should look like, then implement the result with actual Alpha components.

Use its references this way:
- `CORE.md`: default reasoning model for HPHMI/ISA-101 decisions.
- `references/review-checklist.md`: final screenshot review and defect triage.
- `references/color-and-symbols.md`: palette, line styles, equipment symbols, state colors, alarm-color reservation.
- `references/layout-and-typography.md`: screen layout, grouping, labels, alignment, type, spacing.
- `references/display-elements.md`: analog displays, trends, sparklines, controls, buttons, input behavior, performance.
- `references/schematic-completeness.md`: labeled cuts, topological completeness, stored energy, electrical/hydraulic/pneumatic caveats.
- `references/alarms.md`: alarm display, priorities, acknowledgement, shelving/suppression, banner/table/faceplate behavior.
- `rules/hmi-rules.json`: machine-readable rule source for future review tooling or linting.
- `assets/hphmi-palette.json`: first-draft machine-readable Alpha.HMI style values for palette, typography, spacing, line widths, touch targets, and alarm audio.

When creating Alpha.HMI object libraries, map the package to concrete Alpha patterns:
- HPHMI symbol state -> Alpha.HMI bindings and object properties;
- alarm frame/icon/banner/table behavior -> Alpha.HMI.Alarms and faceplate templates;
- trend and sparkline rules -> `alpha.hmi.charts` plus Alpha.Historian data;
- command availability and disabled states -> Alpha.Security roles, mode, interlocks, communication quality, and local/remote state;
- process simulation for validation -> Alpha.Imitator when available.

## Default Position

Treat the screen as an operator HMI, not as a decorative P&ID copy.

Prefer a calm, functional, task-oriented mnemonic:
- only information needed for monitoring, diagnosis, and control;
- clear process context;
- standard object placement;
- consistent labels and value formatting;
- no decorative pseudo-realism.

## Before Drawing

1. Read the task/specification and list required equipment, signals, commands, alarms, trends, and roles.
2. Separate controlled/tagged objects from optional physical context.
3. Do not draw valves, fittings, devices, or sensors as functional elements unless the spec has signals, commands, alarms, or an explicit operator purpose for them.
4. Choose screen level:
   - Level 1: object/process overview and abnormal situation awareness. Do not put process controls here.
   - Level 2: main unit control screen. Design these first.
   - Level 3: equipment/process detail, manual mode, troubleshooting.
   - Level 4: diagnostics, configuration, reports, maintenance details, often via faceplates.
5. For each key analog value, decide the context it needs: scale, limits, setpoint, deviation, trend, quality/stale status, and units.

## Visual Style

- Use a light gray, low-glare background, with `#E0E0E0` from `hphmi-palette.json` as the default starting point.
- Use gray process lines and equipment outlines by default.
- Avoid gradients, shadows, 3D, glossy fills, photographs, and decorative realism.
- Use saturated colors mainly for alarms and abnormal states.
- Do not use alarm colors for ordinary running/stopped/open/closed states.
- Do not encode state by color alone; add text, icon, fill/shape, line style, or another redundant cue.
- Prefer working/running/open equipment as off-white and stopped/closed equipment as gray, unless a verified local style guide overrides this.

## Lines And Connections

- Main process lines: gray and thicker than secondary lines.
- Secondary process lines: gray and thinner.
- Measurement/instrument connection lines: visually distinct from process pipes, preferably thin dashed/dash-dot gray.
- Keep flow paths simple and physically plausible.
- Prefer horizontal/vertical routes and avoid diagonals unless the target platform or real topology makes a diagonal unavoidable and clear.
- Minimize crossings. If a crossing remains, make it unambiguous.
- A sensor connection must visibly land on the measured object/collector/tapping point, not float into empty space or run through unrelated equipment.
- Never let a pipe pass through text, instruments, or equipment unless the crossing is intentionally represented and visually clear.
- Every process line cut at a screen boundary must have a labeled arrow/connector and, where possible, navigation to the adjacent screen.

## Equipment

- Draw pumps, vessels, motors, valves, and instruments as simple 2D symbols or outlines.
- Avoid filled or bright equipment bodies unless fill is a deliberate non-color-only state cue.
- Dynamic equipment should show meaningful operator state: running, stopped/ready, fault, local, disabled, unavailable, maintenance, bad quality.
- For duplicated equipment, keep symbols, labels, and value blocks aligned and identical.
- Do not create a unique hand-drawn variant for every object; build/reuse an Alpha.HMI object library.

## Text, Labels, Values

- Use one label convention across the screen.
- Labels should be consistently placed, usually left of or above their value; binary indicators, checkboxes, and radio buttons usually have labels to the right.
- Do not alternate labels above/left/right for similar sensors.
- Align labels and numeric values to a grid.
- Avoid center alignment except buttons, table cells, and explicit titles.
- Numeric values that users compare must have the same precision and right alignment.
- Units should sit to the right of values and align consistently.
- Use larger/bolder type only for the most important live values.
- Keep static labels dark gray, not pure black when possible.
- Minimize abbreviations unless they are standard for the target operators.
- Prefer operator-language names with tag names as secondary context when needed.
- Leave enough space for Russian text and future localization.

## Data Context

- Data alone is not information. Add context:
  - setpoint;
  - normal/tolerance range;
  - alarm limits;
  - deviation;
  - recent trend;
  - quality/bad-data state.
- Prefer analog display for key process values, with a nearby numeric value.
- Do not show excessive decimal places.
- Handle bad/invalid values visibly: bad quality, NaN, unavailable, stale, communication loss.

## Trends

Use trends when the operator needs to understand direction, stability, oscillation, or prior upset.

For cascade pressure control screens, prefer at least:
- pressure PV;
- pressure SP;
- deviation or tolerance band;
- number of running pumps;
- optionally leading pump speed/output.

For Alpha Platform work, implement trend behavior through `alpha.hmi.charts` and Alpha.Historian when the project requires real history.

## Alarms

- Alarm colors are reserved for alarms. Do not use them for normal states.
- A signal is an alarm only if it requires operator intervention; otherwise classify it as warning, notification, or event.
- Alarm indication must be consistent and not rely on color alone.
- Show priority, acknowledgement state, and active/unacknowledged behavior clearly.
- Place alarm indication near the source object, not only in a central journal.
- Put highest-priority active alarms in a visible banner/table appropriate to screen level.
- Use Alpha.HMI.Alarms for actual alarm behavior when the project requires Alpha Platform alarms.
- Do not create alarms for normal states, such as a pump simply being stopped, unless the logic says it should be running.

## Controls And Faceplates

- Commands that affect equipment or process state should use confirmation when required by the spec.
- Disable or gray controls when mode, role, local control, bad communication, or interlock prevents action. Do not hide normal operating controls merely because they are unavailable.
- Use separate command buttons for start and stop instead of a two-position start/stop toggle.
- Use faceplates for detailed equipment state, commands, diagnostics, permissives, protections, and alarms.
- Keep the overview screen readable; push detail into faceplates or Level 3/4 screens.
- Tie command availability to Alpha.Security roles and runtime state where applicable.

## Final Review Before Sending A Screenshot Or Archive

Before sending any HMI screenshot or archive:
1. Verify the required equipment count and process topology against the spec.
2. Check all duplicated objects for identical placement, size, label position, and value formatting.
3. Check that no labels overlap equipment or lines.
4. Check that no pipe passes through a sensor, label, pump, tank, or unrelated object.
5. Check that every sensor hookup has a clear destination.
6. Check that no untagged valve/fitting is drawn as a controlled object.
7. Check that colors do not make the screen look like a decorative diagram.
8. Check alarm colors are reserved for abnormal/alarm conditions.
9. Check the main operator value has context: SP/range/deviation/trend.
10. Check boundary cuts: every outgoing/incoming line is labeled and navigable when the screen is part of a hierarchy.
11. Check normal state and at least one active alarm state.
12. Compile/render/open the screen and inspect the actual rendered screenshot, not just source XML/HTML.
13. Report which Alpha modules are actually used and which are stubbed, simulated, external, or unavailable.

When reviewing, write findings as: defect -> violated rule -> concrete fix. Prioritize issues that hide alarms, mislead operator action, or confuse topology before cosmetic issues.

## PS01 Pump Station Bias

For PS01-style pump stations:
- show exactly four pumps when the spec says H1..H4;
- keep pump branches visually identical;
- show cascade panel values: running N of 4, lead pump, next start, next stop, lead speed, pressure PV/SP/deviation, capacity low;
- show pressure, suction pressure, flow, and tank level at clear measurement points;
- do not draw extra valves unless controlled/monitored or explicitly requested;
- use a compact lower trend for pressure + setpoint + running-pump count;
- favor a sparse engineering mnemonic over a crowded pseudo-realistic P&ID.
