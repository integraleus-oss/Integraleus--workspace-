#!/usr/bin/env python3
"""Add dark/light theme switcher to all specialtechnology.ru pages."""
import re, os, glob

SPECTECH_DIR = os.path.dirname(os.path.abspath(__file__))

# Light theme CSS to inject after :root { ... }
LIGHT_THEME_CSS = """
/* ── LIGHT THEME ── */
:root.theme-light {
  --ink:        #f0f2f5;
  --ink1:       #ffffff;
  --ink2:       #f7f8fa;
  --steel:      #e8ecf0;
  --wire:       #d0d7e0;
  --wire2:      #bcc5d0;

  --volt:       #0088cc;
  --volt-lo:    rgba(0,136,204,0.08);
  --volt-glow:  rgba(0,136,204,0.25);
  --flame:      #e85d2a;
  --flame-lo:   rgba(232,93,42,0.08);
  --lime:       #15a87e;
  --lime-lo:    rgba(21,168,126,0.08);
  --crimson:    #e0294a;
  --amber:      #d9a000;

  --text:       #1a2332;
  --text2:      #4a5d75;
  --text3:      #8a9bb5;

  color-scheme: light;
}

/* Light theme overrides for elements with hardcoded colors */
:root.theme-light body {
  color: var(--text);
}
:root.theme-light body::before {
  background-image:
    radial-gradient(ellipse 60% 50% at 20% 20%, rgba(0,136,204,0.04) 0%, transparent 70%),
    radial-gradient(ellipse 50% 40% at 80% 80%, rgba(21,168,126,0.03) 0%, transparent 70%);
}
:root.theme-light nav {
  background: rgba(255,255,255,0.92);
  border-bottom-color: var(--wire);
}
:root.theme-light .btn-volt {
  color: #ffffff;
}
:root.theme-light .btn-flame {
  color: #ffffff;
}
:root.theme-light input[type=range]::-webkit-slider-thumb {
  border-color: var(--ink1);
}
:root.theme-light ::placeholder {
  color: var(--text3);
}
:root.theme-light ::-webkit-scrollbar-track {
  background: var(--ink);
}
:root.theme-light ::-webkit-scrollbar-thumb {
  background: var(--wire2);
}
/* SVG strokes that were hardcoded for dark theme */
:root.theme-light .hero-orb {
  opacity: 0.3;
}
:root.theme-light .nav-logo-hex::after,
:root.theme-light .logo-hex::after {
  background: var(--ink1);
}
/* Cards and sections */
:root.theme-light .card,
:root.theme-light .product-card,
:root.theme-light .blog-card,
:root.theme-light .tech-card {
  background: var(--ink1);
  border-color: var(--wire);
}
/* Footer */
:root.theme-light footer,
:root.theme-light .footer {
  background: var(--steel);
}

/* Theme toggle button */
.theme-toggle {
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
}
/* Show/hide icons based on theme */
.theme-toggle .icon-moon { display: block; }
.theme-toggle .icon-sun  { display: none;  }
:root.theme-light .theme-toggle .icon-moon { display: none;  }
:root.theme-light .theme-toggle .icon-sun  { display: block; }
"""

# Theme toggle button HTML
THEME_TOGGLE_HTML = '''<button class="theme-toggle" onclick="toggleTheme()" title="Сменить тему" aria-label="Сменить тему">
      <svg class="icon-moon" viewBox="0 0 24 24" fill="none"><path d="M21 12.79A9 9 0 1111.21 3a7 7 0 109.79 9.79z" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/></svg>
      <svg class="icon-sun" viewBox="0 0 24 24" fill="none"><circle cx="12" cy="12" r="5" stroke="currentColor" stroke-width="1.5"/><line x1="12" y1="1" x2="12" y2="3" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/><line x1="12" y1="21" x2="12" y2="23" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/><line x1="4.22" y1="4.22" x2="5.64" y2="5.64" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/><line x1="18.36" y1="18.36" x2="19.78" y2="19.78" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/><line x1="1" y1="12" x2="3" y2="12" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/><line x1="21" y1="12" x2="23" y2="12" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/><line x1="4.22" y1="19.78" x2="5.64" y2="18.36" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/><line x1="18.36" y1="5.64" x2="19.78" y2="4.22" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/></svg>
    </button>'''

# Theme JS (goes before </body>)
THEME_JS = '''<script>
/* ── Theme Switcher ── */
(function(){
  var saved = localStorage.getItem('sptech-theme');
  if (saved === 'light') document.documentElement.classList.add('theme-light');
  else if (saved === 'dark') document.documentElement.classList.remove('theme-light');
  else {
    // Respect system preference
    if (window.matchMedia && window.matchMedia('(prefers-color-scheme: light)').matches) {
      document.documentElement.classList.add('theme-light');
    }
  }
})();
function toggleTheme() {
  var root = document.documentElement;
  var isLight = root.classList.toggle('theme-light');
  localStorage.setItem('sptech-theme', isLight ? 'light' : 'dark');
}
</script>'''

# Early theme flash prevention (goes in <head>)
THEME_EARLY_JS = '''<script>
(function(){var t=localStorage.getItem('sptech-theme');if(t==='light')document.documentElement.classList.add('theme-light');else if(!t&&window.matchMedia&&window.matchMedia('(prefers-color-scheme:light)').matches)document.documentElement.classList.add('theme-light');})();
</script>'''

def process_file(filepath):
    basename = os.path.basename(filepath)
    if basename in ('index.light-backup.html', 'reference-blog-product.html', 'add-theme-switcher.py'):
        print(f"  SKIP: {basename}")
        return False
    
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Skip if already processed
    if 'theme-toggle' in content and 'theme-light' in content:
        print(f"  ALREADY DONE: {basename}")
        return False
    
    original = content
    
    # 1. Add early JS in <head> after <meta charset>
    if THEME_EARLY_JS.strip() not in content:
        # Find good insertion point - after charset meta
        charset_pattern = r'(<meta\s+charset="UTF-8"\s*/?>)'
        m = re.search(charset_pattern, content, re.IGNORECASE)
        if m:
            content = content[:m.end()] + '\n' + THEME_EARLY_JS + content[m.end():]
        else:
            # Fallback: after <head>
            content = content.replace('<head>', '<head>\n' + THEME_EARLY_JS, 1)
    
    # 2. Insert light theme CSS after the :root { ... } block
    if ':root.theme-light' not in content:
        # Find end of :root block - handle both formatted and minified
        # Minified: :root{...}
        # Formatted: :root { ... }
        
        # Strategy: find the closing } of the :root block
        root_match = re.search(r':root\s*\{', content)
        if root_match:
            # Count braces to find matching }
            start = root_match.start()
            brace_start = content.index('{', start)
            depth = 0
            pos = brace_start
            for i in range(brace_start, len(content)):
                if content[i] == '{':
                    depth += 1
                elif content[i] == '}':
                    depth -= 1
                    if depth == 0:
                        pos = i
                        break
            
            # Insert light theme after :root closing }
            insert_pos = pos + 1
            content = content[:insert_pos] + '\n' + LIGHT_THEME_CSS + content[insert_pos:]
    
    # 3. Add theme toggle button in nav
    if 'theme-toggle' not in content:
        # Different nav structures:
        # a) Has nav-cta div: insert toggle inside nav-cta
        # b) Calculator has different nav structure
        
        if 'nav-cta' in content:
            # Insert before the closing </div> of nav-cta
            # Find: <div class="nav-cta"> ... </div>  and insert toggle before first <a> in it
            cta_match = re.search(r'(<div\s+class="nav-cta">\s*\n?)', content)
            if cta_match:
                content = content[:cta_match.end()] + '    ' + THEME_TOGGLE_HTML + '\n' + content[cta_match.end():]
        elif '<nav>' in content:
            # Calculator-style nav: insert before </nav>
            content = content.replace('</nav>', '  ' + THEME_TOGGLE_HTML + '\n</nav>', 1)
    
    # 4. Add theme JS before </body>
    if 'toggleTheme' not in content:
        content = content.replace('</body>', THEME_JS + '\n</body>', 1)
    
    if content != original:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"  UPDATED: {basename}")
        return True
    else:
        print(f"  NO CHANGE: {basename}")
        return False

# Process all HTML files
files = sorted(glob.glob(os.path.join(SPECTECH_DIR, '*.html')))
print(f"Found {len(files)} HTML files\n")

updated = 0
for f in files:
    result = process_file(f)
    if result:
        updated += 1

print(f"\nDone! Updated {updated} files.")
