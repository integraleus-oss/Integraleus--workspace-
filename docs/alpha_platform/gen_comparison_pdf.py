#!/usr/bin/env python3
import markdown
from weasyprint import HTML

md_content = open('/root/.openclaw/workspace/agents/main/docs/alpha_platform/Alpha_vs_Competitors.md').read()

# Convert markdown to HTML
html_body = markdown.markdown(md_content, extensions=['tables', 'fenced_code'])

html_full = f"""<!DOCTYPE html>
<html lang="ru">
<head>
<meta charset="utf-8">
<style>
@page {{
    size: A4 landscape;
    margin: 15mm 12mm;
    @bottom-center {{
        content: counter(page) " / " counter(pages);
        font-size: 9px;
        color: #888;
    }}
}}

body {{
    font-family: 'DejaVu Sans', 'Liberation Sans', Arial, sans-serif;
    font-size: 10px;
    line-height: 1.45;
    color: #1a1a2e;
    max-width: 100%;
}}

h1 {{
    text-align: center;
    font-size: 22px;
    color: #0f3460;
    border-bottom: 3px solid #e94560;
    padding-bottom: 12px;
    margin-bottom: 8px;
    letter-spacing: 0.5px;
}}

h1 + blockquote {{
    text-align: center;
    font-style: italic;
    color: #555;
    border: none;
    font-size: 9px;
    margin: 0 0 15px 0;
    padding: 0;
}}

h2 {{
    font-size: 14px;
    color: #16213e;
    background: linear-gradient(90deg, #0f3460 0%, #533483 100%);
    color: white;
    padding: 6px 14px;
    border-radius: 4px;
    margin-top: 18px;
    margin-bottom: 8px;
    page-break-after: avoid;
}}

h3 {{
    font-size: 12px;
    color: #0f3460;
    margin-top: 12px;
    margin-bottom: 4px;
    border-left: 3px solid #e94560;
    padding-left: 8px;
}}

table {{
    width: 100%;
    border-collapse: collapse;
    margin: 8px 0 14px 0;
    font-size: 9px;
    page-break-inside: auto;
}}

thead {{
    background: #16213e;
    color: white;
}}

th {{
    padding: 6px 8px;
    text-align: left;
    font-weight: 600;
    font-size: 9px;
    border: 1px solid #0f3460;
}}

td {{
    padding: 4px 8px;
    border: 1px solid #ddd;
    vertical-align: top;
}}

tr:nth-child(even) {{
    background: #f0f4ff;
}}

tr:nth-child(odd) {{
    background: #fff;
}}

/* Highlight Alpha column */
td:nth-child(2), th:nth-child(2) {{
    background: rgba(233, 69, 96, 0.08);
    font-weight: 500;
}}

thead th:nth-child(2) {{
    background: #e94560;
    color: white;
    font-weight: 700;
}}

strong {{
    color: #0f3460;
}}

ol, ul {{
    margin: 4px 0;
    padding-left: 20px;
}}

li {{
    margin-bottom: 3px;
}}

code {{
    background: #f5f5f5;
    padding: 1px 4px;
    border-radius: 2px;
    font-size: 9px;
}}

pre {{
    background: #1a1a2e;
    color: #e0e0e0;
    padding: 10px 14px;
    border-radius: 6px;
    font-size: 9px;
    overflow-x: auto;
    white-space: pre;
    line-height: 1.4;
}}

blockquote {{
    border-left: 3px solid #533483;
    padding: 4px 12px;
    margin: 8px 0;
    background: #f9f5ff;
    color: #333;
    font-size: 9px;
}}

/* Cover styling */
h1:first-of-type {{
    margin-top: 20px;
    font-size: 24px;
}}

/* Emoji sizing */
p {{
    margin: 4px 0;
}}
</style>
</head>
<body>
{html_body}
</body>
</html>"""

out = '/root/.openclaw/workspace/agents/main/docs/alpha_platform/Alpha_vs_Competitors.pdf'
HTML(string=html_full).write_pdf(out)
print(f"PDF saved: {out}")

import os
size = os.path.getsize(out)
print(f"Size: {size/1024:.0f} KB")
