# Review: hmi-screen-design archive

Date: 2026-07-31
Archive: `telegram_archive.zip`
Extracted root: `extracted/hmi-screen-design/`

## Inventory

The archive is a platform-independent HMI/SCADA screen-design skill package.
It is not an Alpha Platform project and contains no executable Alpha artifacts.

Main files:
- `CORE.md` / `SKILL.md`: full reusable skill instructions.
- `COMPACT.md`: short self-contained version for constrained instruction fields.
- `ALL-IN-ONE.md`: all material combined.
- `references/*.md`: focused references for hierarchy, layout, display elements, colors, schematic completeness, alarms, and review.
- `rules/hmi-rules.json`: 84 atomic rules with category, severity, rationale, and check method.
- `assets/hphmi-palette.json`: machine-readable palette, typography, spacing, line, touch-target, performance, and alarm-audio values.

## Verdict

This is useful and should be used in Alpha Platform work as a design/review layer, not as a replacement for Alpha documentation or Alpha tooling.

Its strongest value is converting "make a better HMI" into checkable rules:
- normal screen must be calm and mostly gray;
- alarm colors are reserved only for alarms;
- key values need context, preferably scale + limits + setpoint + trend;
- measurement connections must be visually distinct from process pipes;
- screen cuts must be labeled and navigable;
- alarm display must show source, priority, acknowledgement state, and suppression/shelving state;
- review findings should use the format: defect -> violated rule -> concrete fix.

## How To Apply To Alpha Platform

Use it before and after building Alpha.HMI screens:

1. Requirements parsing
   - Split operator tasks into screen levels 1-4.
   - Start with level 2 working screens, then derive level 1 overview.
   - List equipment, signals, commands, alarms, trends, roles, and faceplates before drawing.

2. Alpha.HMI object library
   - Build reusable symbols for pumps, valves, motors, vessels, analog indicators, alarm frames, trend blocks, navigation buttons, and faceplates.
   - Use `hphmi-palette.json` as the first draft for colors, line widths, typography, spacing, and touch targets.
   - Map each symbol state to Alpha.HMI bindings instead of recoloring objects ad hoc.

3. Alpha.HMI / WebViewer screen review
   - Run the `review-checklist.md` sequence on the rendered screenshot, not only on source XML.
   - Prioritize defects that hide alarms or confuse operator action over cosmetic issues.
   - For pump-station screens like PS01, this directly addresses the defects we saw: clutter, floating sensor taps, inconsistent labels, decorative valves, and unclear line meaning.

4. Alpha.HMI.Alarms
   - Use the alarm guidance as the visual policy for alarm banner, alarm frames, navigation alarm badges, faceplate alarm tabs, acknowledgement, and shelved/suppressed indication.
   - Keep "requires operator action" as the criterion for whether a signal is an alarm.

5. alpha.hmi.charts / Alpha.Historian
   - Use trends where direction and stability matter: PV/SP/deviation, running-pump count, output/speed, flows, levels.
   - Do not show bare values without limits, setpoints, quality/stale status, and units where they matter.

6. Alpha.Security
   - Do not hide unavailable controls; show them disabled with a visible reason when possible.
   - Tie access to operator, maintenance, engineer, and commissioning roles.

7. Alpha.Imitator / validation
   - Test both normal and alarm states.
   - A screenshot in only the normal state is insufficient; the package explicitly expects normal + active alarm review.

## Limitations

- The package is not Alpha-specific. It must be mapped to Alpha.HMI object types, bindings, WebViewer behavior, Alpha.HMI.Alarms, Historian, Reports, and Security.
- Several concrete values come from Rockwell PlantPAx as a reference implementation. They are good defaults, but should be documented as internal project style values, not as direct ISA-101 mandates.
- The "schematic completeness" rules about topological decisions and stored energy are partly engineering-practice reconstruction. Treat them as internal enterprise rules unless separately justified.
- It does not solve exact Alpha.HMI XML/base-type details. Those still need local Alpha docs, course materials, and known-good exported `.hmi` / `.omobj` examples.

## Recommendation

Fold this package into the existing `asu-tp-hmi-checklist` workflow as a reference set:
- keep the current Alpha Platform-first rule as higher priority;
- add this package as the detailed HPHMI/ISA-101 design and review source;
- create an Alpha-specific mapping document: "HPHMI rule -> Alpha component/object/template/check";
- eventually make a small linter/check script that reads `hmi-rules.json` and checks exported screen metadata or rendered screenshots where possible.
