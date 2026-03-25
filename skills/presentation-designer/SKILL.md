---
name: presentation-designer
description: >
  Create professional .pptx presentations for industrial automation (SCADA, DCS, MES, PLC, IIoT, Industry 4.0).
  Supports branded styles of major vendors: Siemens, AVEVA, Honeywell, ABB, Emerson, Yokogawa, Rockwell,
  and Russian vendors: Атомик Софт, IEC Digital, Реглаб, ТРЭИ, Инкомсистем, Прософт, ОВЕН, Элеси.
  Use when: user asks to create a presentation, design slides, make a .pptx, or needs help with
  presentation structure for industrial automation topics. Also triggers on: презентация, слайды,
  PowerPoint, pptx, presentation design, slide deck.
---

# Presentation Designer — Industrial Automation

Expert presentation designer for industrial automation, SCADA/DCS/MES, digitalization, and Industry 4.0.

## Workflow

1. **Clarify brief** — ask about audience (engineers / management / customer), goal (sales / training / report), preferred style (vendor-specific or neutral)
2. **Propose structure** — numbered slide plan with brief description of each
3. **Define style** — palette, typography, visual approach (see references/vendor-styles.md)
4. **Generate content** — for each slide: title, bullet points, visual element descriptions, speaker notes
5. **Build .pptx** — generate file using `scripts/build_pptx.py` or python-pptx directly

## Key Rules

- One slide = one idea
- Data > decoration — every visual must carry meaning
- Use correct terminology: КИПиА, АСУ ТП, MES, SCADA, DCS, OPC UA, ПЛК, ШМР, ПНР, ИБ АСУ ТП
- Always propose speaker notes for each slide
- For импортозамещение topics — always include a mapping table (foreign → domestic solutions)

## Default Neutral Style

- Dark navy: `#1B2A4A`
- Steel gray: `#5A6B7F`
- White background
- Accent: teal `#00A5B5`, orange `#E87722`, or green `#2ECC71`
- Fonts: Inter, Source Sans Pro, Roboto (or vendor-specific)

## Standard Slide Templates

1. **Title** — industrial background image, semi-transparent overlay, large heading
2. **Company overview** — partner logos, certs, key metrics in icon blocks
3. **Architecture diagram** — ISA-95 levels with products/technologies per level
4. **Problem → Solution** — two-column layout with contrasting colors
5. **Project timeline** — phases: survey, design, supply, installation, commissioning, go-live
6. **Comparison table** — vendors or technologies side by side
7. **Case study / results** — before/after, large metric numbers
8. **Digitalization roadmap** — from basic automation to Industry 4.0
9. **Technology stack** — layered visual with software/hardware icons
10. **Final CTA** — contacts, QR code, call to action

## Vendor Styles

For detailed brand guidelines (palettes, typography, visual approach) of all supported vendors:

→ Read `references/vendor-styles.md`

## Conference Templates

### PROавтоматизацию 2025
Pre-built conference template with 14 layouts (light/dark variants), proper theme colors, and placeholder structure.

→ Read `references/proavtomatizaciyu-template.md`

**Usage**: Open the .pptx as template base, remove sample slides, add slides using layout indices and placeholder maps. The template handles fonts, colors, backgrounds, and decorative elements automatically.

**Template files** (in `templates/` directory):
- `templates/proavtomatizaciyu-2025.pptx` — conference template (14 layouts)
- `templates/atomicsoft-about.pptx` — Атомик Софт corporate "О компании" (13 slides, reference)
- `templates/atomicsoft-tpu2.pptx` — Атомик Софт university presentation (17 slides, reference)

## Industry Visualization Standards

- Purdue / ISA-95 architecture levels
- Automation pyramid and data flows
- Simplified P&ID for presentations
- Industrial network topologies (Profinet, Modbus, OPC UA, Ethernet/IP)
- Dashboards and HMI screens
- Digital twins and 3D models
- IEC 62443 cybersecurity diagrams (zones and conduits)
- Automation project lifecycle
- ROI calculations and business cases

## Building .pptx Files

Use python-pptx to generate presentations. The script `scripts/build_pptx.py` provides helper functions for common slide layouts with proper styling.

```bash
python3 scripts/build_pptx.py --output presentation.pptx --style neutral
```

For custom presentations, use python-pptx directly with the color palettes and layout patterns from this skill.
