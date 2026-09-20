import markdown, os, re

os.chdir('/Users/mcharni/Projects/DQ/hol')
os.makedirs('docs', exist_ok=True)

HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{title} - DQ HOL</title>
<style>
:root {{ --sf-blue: #29B5E8; --sf-dark: #1B2A4A; --sf-light: #F0F9FF; }}
* {{ margin: 0; padding: 0; box-sizing: border-box; }}
body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; line-height: 1.6; color: #333; max-width: 900px; margin: 0 auto; padding: 2rem; background: #fafbfc; }}
h1 {{ color: var(--sf-dark); border-bottom: 3px solid var(--sf-blue); padding-bottom: 0.5rem; margin: 1.5rem 0 1rem; }}
h2 {{ color: var(--sf-dark); border-bottom: 1px solid #e1e4e8; padding-bottom: 0.3rem; margin: 1.5rem 0 0.8rem; }}
h3 {{ color: var(--sf-dark); margin: 1.2rem 0 0.5rem; }}
table {{ border-collapse: collapse; width: 100%; margin: 1rem 0; }}
th {{ background: var(--sf-blue); color: white; padding: 0.6rem; text-align: left; }}
td {{ border: 1px solid #e1e4e8; padding: 0.5rem; }}
tr:nth-child(even) {{ background: var(--sf-light); }}
code {{ background: #f0f0f0; padding: 0.15rem 0.4rem; border-radius: 3px; font-size: 0.9em; }}
pre {{ background: var(--sf-dark); color: #e6e6e6; padding: 1rem; border-radius: 6px; overflow-x: auto; margin: 1rem 0; }}
pre code {{ background: none; color: inherit; padding: 0; }}
blockquote {{ border-left: 4px solid var(--sf-blue); padding: 0.5rem 1rem; margin: 1rem 0; background: var(--sf-light); }}
a {{ color: var(--sf-blue); }}
nav {{ background: var(--sf-dark); padding: 1rem 1.5rem; border-radius: 6px; margin-bottom: 2rem; display: flex; align-items: center; gap: 1.5rem; flex-wrap: wrap; }}
nav .logo {{ display: flex; align-items: center; gap: 0.5rem; margin-right: auto; }}
nav .logo svg {{ width: 28px; height: 28px; }}
nav .logo span {{ color: white; font-weight: 700; font-size: 1.1em; }}
nav a {{ color: white; text-decoration: none; font-weight: 500; }}
nav a:hover {{ text-decoration: underline; }}
footer {{ margin-top: 3rem; padding: 1.5rem; background: var(--sf-dark); color: #ccc; border-radius: 6px; text-align: center; font-size: 0.85em; }}
footer a {{ color: var(--sf-blue); }}
.mermaid {{ background: white; padding: 1rem; border-radius: 6px; border: 1px solid #e1e4e8; margin: 1rem 0; overflow-x: auto; }}
.mermaid svg {{ min-width: 800px; }}
</style>
<script src="mermaid.min.js"></script>
<script>mermaid.initialize({{startOnLoad:true, theme:'default'}});</script>
</head>
<body>
<nav>
<div class="logo">
<svg viewBox="0 0 24 24" fill="white"><path d="M11 1v4.07A6.007 6.007 0 0 0 6.07 10H2v2h4.07A6.007 6.007 0 0 0 11 16.93V21h2v-4.07A6.007 6.007 0 0 0 17.93 12H22v-2h-4.07A6.007 6.007 0 0 0 13 5.07V1h-2zm1 6a4 4 0 1 1 0 8 4 4 0 0 1 0-8z"/></svg>
<span>Snowflake DQ Lab</span>
</div>
<a href="index.html">Home</a>
<a href="start_here.html">Start Here</a>
<a href="prerequisites.html">Prerequisites</a>
<a href="student_guide.html">Student Guide</a>
<a href="workshop_cards.html">Workshop Cards</a>
<a href="lab_map.html">Lab Map</a>
</nav>
{content}
<footer>
<p>Data Quality Monitoring with Snowflake &mdash; Hands-On Lab</p>
<p>Facilitated by <strong>Marawen Charni</strong> | Senior Partner Solutions Engineer, Snowflake</p>
<p style="margin-top:0.5rem; color:#666;">&copy; 2026 Snowflake Inc. All rights reserved.</p>
</footer>
</body>
</html>"""

def convert_mermaid(html):
    pattern = r'<pre><code class="language-mermaid">(.*?)</code></pre>'
    def replacer(m):
        code = m.group(1).replace('&amp;', '&').replace('&lt;', '<').replace('&gt;', '>')
        return '<div class="mermaid">' + code + '</div>'
    return re.sub(pattern, replacer, html, flags=re.DOTALL)

# Map from .md paths to .html filenames
link_map = {
    'START_HERE.md': 'start_here.html',
    'README.md': 'index.html',
    'guide/PREREQUISITES.md': 'prerequisites.html',
    'guide/STUDENT_GUIDE.md': 'student_guide.html',
    'guide/WORKSHOP_CARDS.md': 'workshop_cards.html',
    'guide/LAB_MAP.md': 'lab_map.html',
    'guide/APPENDIX_DBT_DEVELOPMENT.md': 'appendix_dbt.html',
    'PREREQUISITES.md': 'prerequisites.html',
    'STUDENT_GUIDE.md': 'student_guide.html',
    'WORKSHOP_CARDS.md': 'workshop_cards.html',
    'LAB_MAP.md': 'lab_map.html',
    'APPENDIX_DBT_DEVELOPMENT.md': 'appendix_dbt.html',
}

def rewrite_links(html):
    import re
    for md_path, html_path in link_map.items():
        # Match with or without anchor fragments
        pattern = re.escape(f'href="{md_path}') + r'([^"]*)"'
        html = re.sub(pattern, f'href="{html_path}\\1"', html)
        pattern2 = re.escape(f'href="guide/{md_path}') + r'([^"]*)"'
        html = re.sub(pattern2, f'href="{html_path}\\1"', html)
    return html

files = {
    'README.md': ('index.html', 'Data Quality Monitoring HOL'),
    'START_HERE.md': ('start_here.html', 'Start Here'),
    'guide/PREREQUISITES.md': ('prerequisites.html', 'Prerequisites'),
    'guide/STUDENT_GUIDE.md': ('student_guide.html', 'Student Guide'),
    'guide/WORKSHOP_CARDS.md': ('workshop_cards.html', 'Workshop Cards'),
    'guide/LAB_MAP.md': ('lab_map.html', 'Lab Map'),
    'guide/APPENDIX_DBT_DEVELOPMENT.md': ('appendix_dbt.html', 'Appendix: dbt Development'),
}

md = markdown.Markdown(extensions=['tables', 'fenced_code', 'toc'])

for src, (dst, title) in files.items():
    if not os.path.exists(src):
        print(f'SKIP {src} (not found)')
        continue
    with open(src) as f:
        content = f.read()
    md.reset()
    html_content = md.convert(content)
    html_content = convert_mermaid(html_content)
    html_content = rewrite_links(html_content)
    full_html = HTML_TEMPLATE.format(title=title, content=html_content)
    with open(f'docs/{dst}', 'w') as f:
        f.write(full_html)
    print(f'{src} -> docs/{dst}')

print(f'\nStatic site generated in docs/')
