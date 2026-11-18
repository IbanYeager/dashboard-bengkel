import re

with open('data/ao_html/Dashboard AO.html', 'r', encoding='utf-8') as f:
    text = f.read()

# Check style tag
style_match = re.search(r'<style[^>]*>(.*?)</style>', text, re.DOTALL)
if style_match:
    style_content = style_match.group(1)
    print(f'Style length: {len(style_content)}')

# Check grid table
table_match = re.search(r'(<div class="ritz grid-container".*?</div>\s*</div>)', text, re.DOTALL)
if not table_match:
    table_match = re.search(r'(<div class="ritz grid-container".*)', text, re.DOTALL)

if table_match:
    grid_html = table_match.group(1)
    print(f'Grid HTML length: {len(grid_html)}')
    print('Preview of grid HTML:')
    print(grid_html[:500])
    
    # Let's count rows in waffle table
    rows = re.findall(r'<tr[^>]*>', grid_html)
    print(f'Number of <tr> elements: {len(rows)}')
