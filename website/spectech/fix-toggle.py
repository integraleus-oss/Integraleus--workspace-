#!/usr/bin/env python3
"""Fix theme toggle button visibility — add explicit colors."""
import glob, os

SPECTECH_DIR = os.path.dirname(os.path.abspath(__file__))

OLD_TOGGLE_CSS = """.theme-toggle {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 36px;
  height: 36px;
  border: 1px solid var(--wire);
  border-radius: 50%;
  background: var(--ink2);
  cursor: pointer;
  transition: all 0.3s ease;
  padding: 0;
  margin-left: 12px;
  flex-shrink: 0;
}
.theme-toggle:hover {
  border-color: var(--volt);
  background: var(--volt-lo);
}
.theme-toggle svg {
  width: 18px;
  height: 18px;
  transition: transform 0.3s ease;
}
.theme-toggle:hover svg {
  transform: rotate(30deg);
}"""

NEW_TOGGLE_CSS = """.theme-toggle {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 40px;
  height: 40px;
  border: 1px solid var(--volt);
  border-radius: 50%;
  background: transparent;
  cursor: pointer;
  transition: all 0.3s ease;
  padding: 0;
  margin-left: 12px;
  flex-shrink: 0;
  color: var(--volt);
}
.theme-toggle:hover {
  background: var(--volt);
  color: #fff;
}
.theme-toggle svg {
  width: 20px;
  height: 20px;
  stroke: currentColor;
  transition: transform 0.3s ease;
}
.theme-toggle:hover svg {
  transform: rotate(30deg);
}"""

files = sorted(glob.glob(os.path.join(SPECTECH_DIR, '*.html')))
updated = 0
for filepath in files:
    bn = os.path.basename(filepath)
    if bn in ('index.light-backup.html', 'reference-blog-product.html'):
        continue
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    if OLD_TOGGLE_CSS in content:
        content = content.replace(OLD_TOGGLE_CSS, NEW_TOGGLE_CSS)
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"FIXED: {bn}")
        updated += 1
    else:
        print(f"SKIP: {bn} (pattern not found)")

print(f"\nDone: {updated} files fixed.")
