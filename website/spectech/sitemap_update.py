import re

with open('sitemap.xml', 'r') as f:
    content = f.read()

new_entries = """  <url><loc>https://specialtechnology.ru/blog/devstudio-migration.html</loc><lastmod>2026-04-01</lastmod><priority>0.7</priority></url>
  <url><loc>https://specialtechnology.ru/blog/hmi-frames-posters.html</loc><lastmod>2026-04-01</lastmod><priority>0.7</priority></url>
  <url><loc>https://specialtechnology.ru/blog/historian-licensing.html</loc><lastmod>2026-04-01</lastmod><priority>0.7</priority></url>"""

# Insert before </urlset>
content = content.replace('</urlset>', new_entries + '\n</urlset>')

with open('sitemap.xml', 'w') as f:
    f.write(content)

# Count URLs
count = content.count('<url>')
print(f"Sitemap updated: {count} URLs")
