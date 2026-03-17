#!/usr/bin/env python3
"""Fix SVG logos visibility in light theme — add CSS class to invert white fills."""
import glob, os

SPECTECH_DIR = os.path.dirname(os.path.abspath(__file__))

# CSS to add: in light theme, SVGs inside partner-brand and product-brand
# that have white fills should become dark
LIGHT_SVG_FIX = """
/* Fix white SVG logos in light theme */
:root.theme-light .partner-brand svg path[fill="#FFFFFF"],
:root.theme-light .partner-brand svg path[fill="white"],
:root.theme-light .partner-brand svg path[fill="#fff"],
:root.theme-light .product-brand svg path[fill="#FFFFFF"],
:root.theme-light .product-brand svg path[fill="white"],
:root.theme-light .product-brand svg path[fill="#fff"] {
  fill: #1a2332;
}
/* Hero SVG text elements */
:root.theme-light svg text[fill="white"] {
  fill: var(--text);
}
"""

files = sorted(glob.glob(os.path.join(SPECTECH_DIR, '*.html')))
updated = 0
for filepath in files:
    bn = os.path.basename(filepath)
    if bn in ('index.light-backup.html', 'reference-blog-product.html', 'fix-toggle.py', 'fix-svg-light.py', 'add-theme-switcher.py'):
        continue
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    if 'Fix white SVG logos in light theme' in content:
        print(f"SKIP: {bn} (already fixed)")
        continue
    
    # Insert after the theme-light icon-sun rule
    marker = ':root.theme-light .theme-toggle .icon-sun  { display: block; }'
    if marker in content:
        content = content.replace(marker, marker + '\n' + LIGHT_SVG_FIX)
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"FIXED: {bn}")
        updated += 1
    else:
        print(f"WARN: {bn} — marker not found")

print(f"\nDone: {updated} files fixed.")
