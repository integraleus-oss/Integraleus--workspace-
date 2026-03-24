#!/usr/bin/env python3
"""
Comprehensive Website Audit Script for specialtechnology.ru
"""

import os
import re
from bs4 import BeautifulSoup
import json
from urllib.parse import urlparse
from pathlib import Path

class WebsiteAuditor:
    def __init__(self, base_path):
        self.base_path = Path(base_path)
        self.results = {
            'seo': {},
            'links': {},
            'consistency': {},
            'mobile': {},
            'forms': {},
            'compliance': {},
            'performance': {},
            'content': {}
        }
        
        # Core pages from checklist
        self.core_pages = [
            'index.html', 'about.html', 'alpha-platform.html', 'blog.html', 
            'calculator.html', 'compograph.html', 'dataplat.html', 'dataplat-reports.html',
            'dpp-alarms.html', 'dpp-balance.html', 'dpp-dobycha.html', 'dpp-tm.html', 
            'dpp-ur.html', 'infteh.html', 'ipredicta.html', 'kompograf.html', 
            'lacerta.html', 'wertsim.html', 'privacy.html', 'consent.html'
        ]
        
    def load_html(self, file_path):
        """Load and parse HTML file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            return BeautifulSoup(content, 'html.parser'), content
        except Exception as e:
            print(f"Error loading {file_path}: {e}")
            return None, None
    
    def audit_seo(self, file_path, soup):
        """Audit SEO elements"""
        filename = os.path.basename(file_path)
        seo_data = {
            'title': None,
            'meta_description': None,
            'meta_keywords': None,
            'h1_count': 0,
            'h1_text': [],
            'lang_ru': False,
            'img_without_alt': [],
            'canonical': None
        }
        
        # Check title
        title = soup.find('title')
        seo_data['title'] = title.text.strip() if title else None
        
        # Check meta description
        meta_desc = soup.find('meta', attrs={'name': 'description'})
        seo_data['meta_description'] = meta_desc.get('content') if meta_desc else None
        
        # Check meta keywords
        meta_keywords = soup.find('meta', attrs={'name': 'keywords'})
        seo_data['meta_keywords'] = meta_keywords.get('content') if meta_keywords else None
        
        # Check H1 tags
        h1_tags = soup.find_all('h1')
        seo_data['h1_count'] = len(h1_tags)
        seo_data['h1_text'] = [h1.get_text().strip() for h1 in h1_tags]
        
        # Check lang="ru"
        html_tag = soup.find('html')
        seo_data['lang_ru'] = html_tag and html_tag.get('lang') == 'ru'
        
        # Check img alt attributes
        images = soup.find_all('img')
        for img in images:
            if not img.get('alt'):
                seo_data['img_without_alt'].append(img.get('src', 'no-src'))
        
        # Check canonical URL
        canonical = soup.find('link', attrs={'rel': 'canonical'})
        seo_data['canonical'] = canonical.get('href') if canonical else None
        
        self.results['seo'][filename] = seo_data
    
    def audit_links(self, file_path, soup):
        """Audit internal and external links"""
        filename = os.path.basename(file_path)
        links_data = {
            'internal_links': [],
            'broken_internal': [],
            'anchor_links': [],
            'broken_anchors': [],
            'external_links': []
        }
        
        # Get all links
        links = soup.find_all('a', href=True)
        
        # Get all IDs on the page for anchor checking
        page_ids = set()
        for element in soup.find_all(attrs={"id": True}):
            page_ids.add(element.get('id'))
        
        for link in links:
            href = link.get('href')
            
            if href.startswith('#'):
                # Anchor link
                anchor_id = href[1:]
                links_data['anchor_links'].append(href)
                if anchor_id not in page_ids:
                    links_data['broken_anchors'].append(href)
                    
            elif href.startswith('http'):
                # External link
                links_data['external_links'].append(href)
                
            elif href.endswith('.html') or '/' in href:
                # Internal link
                links_data['internal_links'].append(href)
                
                # Check if file exists
                if href.endswith('.html'):
                    target_path = self.base_path / href
                    if not target_path.exists():
                        links_data['broken_internal'].append(href)
        
        self.results['links'][filename] = links_data
    
    def audit_consistency(self, file_path, soup):
        """Check consistency across pages"""
        filename = os.path.basename(file_path)
        consistency_data = {
            'nav_structure': False,
            'footer_structure': False,
            'cookie_banner': False,
            'alpha_bot_widget': False,
            'theme_switcher': False,
            'yandex_metrika': False,
            'privacy_link_footer': False
        }
        
        # Check nav structure (look for common nav patterns)
        nav = soup.find('nav') or soup.find('header')
        if nav:
            consistency_data['nav_structure'] = True
        
        # Check footer
        footer = soup.find('footer')
        if footer:
            consistency_data['footer_structure'] = True
            # Check for privacy link in footer
            if footer.find('a', href=re.compile(r'privacy')):
                consistency_data['privacy_link_footer'] = True
        
        # Check cookie banner
        cookie_banner = soup.find(attrs={'class': re.compile(r'cookie|consent', re.I)})
        if cookie_banner:
            consistency_data['cookie_banner'] = True
        
        # Check Alpha-Bot widget
        scripts = soup.find_all('script')
        for script in scripts:
            if script.string and 'alpha-bot' in script.string.lower():
                consistency_data['alpha_bot_widget'] = True
                break
        
        # Check theme switcher
        theme_switcher = soup.find(attrs={'class': re.compile(r'theme', re.I)}) or \
                        soup.find(attrs={'id': re.compile(r'theme', re.I)})
        if theme_switcher:
            consistency_data['theme_switcher'] = True
        
        # Check Yandex.Metrika
        for script in scripts:
            if script.string and ('metrika' in script.string.lower() or 'ym(' in script.string):
                consistency_data['yandex_metrika'] = True
                break
        
        self.results['consistency'][filename] = consistency_data
    
    def audit_mobile(self, file_path, soup, content):
        """Check mobile responsiveness"""
        filename = os.path.basename(file_path)
        mobile_data = {
            'viewport_meta': False,
            'media_queries': False,
            'nav_mobile_hidden': False,
            'fixed_width_elements': []
        }
        
        # Check viewport meta tag
        viewport = soup.find('meta', attrs={'name': 'viewport'})
        if viewport:
            mobile_data['viewport_meta'] = True
        
        # Check for media queries in CSS
        if '@media' in content:
            mobile_data['media_queries'] = True
        
        # Check for mobile navigation patterns
        if 'nav-links' in content and 'display: none' in content:
            mobile_data['nav_mobile_hidden'] = True
        
        # Look for potential fixed-width issues
        fixed_width_patterns = re.findall(r'width:\s*\d+px', content)
        mobile_data['fixed_width_elements'] = list(set(fixed_width_patterns))
        
        self.results['mobile'][filename] = mobile_data
    
    def audit_forms(self, file_path, soup):
        """Audit forms for compliance and validation"""
        filename = os.path.basename(file_path)
        forms_data = {
            'forms_found': [],
            'consent_checkboxes': [],
            'required_fields': [],
            'action_urls': []
        }
        
        forms = soup.find_all('form')
        
        for i, form in enumerate(forms):
            form_info = {
                'index': i,
                'action': form.get('action', ''),
                'method': form.get('method', 'GET'),
                'has_consent': False,
                'required_fields': []
            }
            
            forms_data['action_urls'].append(form.get('action', ''))
            
            # Check for consent checkboxes
            checkboxes = form.find_all('input', type='checkbox')
            for checkbox in checkboxes:
                if checkbox.get('required') and 'consent' in str(checkbox).lower():
                    form_info['has_consent'] = True
                    forms_data['consent_checkboxes'].append({
                        'form': i,
                        'name': checkbox.get('name', ''),
                        'required': checkbox.get('required') is not None
                    })
            
            # Check required fields
            required_inputs = form.find_all(attrs={'required': True})
            for inp in required_inputs:
                forms_data['required_fields'].append({
                    'form': i,
                    'name': inp.get('name', ''),
                    'type': inp.get('type', 'text')
                })
            
            forms_data['forms_found'].append(form_info)
        
        self.results['forms'][filename] = forms_data
    
    def get_file_size(self, file_path):
        """Get file size in bytes"""
        return os.path.getsize(file_path)
    
    def run_full_audit(self):
        """Run complete audit on all core pages"""
        print("Starting comprehensive website audit...")
        
        # Audit core pages
        for page in self.core_pages:
            file_path = self.base_path / page
            if file_path.exists():
                print(f"Auditing {page}...")
                soup, content = self.load_html(file_path)
                if soup and content:
                    self.audit_seo(file_path, soup)
                    self.audit_links(file_path, soup)
                    self.audit_consistency(file_path, soup)
                    self.audit_mobile(file_path, soup, content)
                    self.audit_forms(file_path, soup)
                    
                    # Performance data
                    self.results['performance'][page] = {
                        'file_size': self.get_file_size(file_path)
                    }
            else:
                print(f"Warning: {page} not found!")
        
        # Check sitemap and robots
        self.check_sitemap_robots()
        
        return self.results
    
    def check_sitemap_robots(self):
        """Check sitemap.xml and robots.txt"""
        sitemap_path = self.base_path / 'sitemap.xml'
        robots_path = self.base_path / 'robots.txt'
        
        sitemap_data = {'exists': False, 'pages_listed': []}
        robots_data = {'exists': False, 'content': ''}
        
        if sitemap_path.exists():
            sitemap_data['exists'] = True
            try:
                with open(sitemap_path, 'r', encoding='utf-8') as f:
                    sitemap_content = f.read()
                    # Extract URLs from sitemap
                    urls = re.findall(r'<loc>(.*?)</loc>', sitemap_content)
                    sitemap_data['pages_listed'] = [url.split('/')[-1] for url in urls if url.endswith('.html')]
            except Exception as e:
                print(f"Error reading sitemap: {e}")
        
        if robots_path.exists():
            robots_data['exists'] = True
            try:
                with open(robots_path, 'r', encoding='utf-8') as f:
                    robots_data['content'] = f.read()
            except Exception as e:
                print(f"Error reading robots.txt: {e}")
        
        self.results['sitemap'] = sitemap_data
        self.results['robots'] = robots_data

if __name__ == "__main__":
    auditor = WebsiteAuditor("/root/.openclaw/workspace/agents/main/website/spectech")
    results = auditor.run_full_audit()
    
    # Save results to JSON for further processing
    with open("/root/.openclaw/workspace/agents/main/website/spectech/audit_results.json", "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    
    print("Audit complete! Results saved to audit_results.json")