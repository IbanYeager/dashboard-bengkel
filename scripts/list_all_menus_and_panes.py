import re

with open('index.html', 'r', encoding='utf-8') as f:
    html = f.read()

panes = re.findall(r'<div[^>]*id="(pane-[^"]+)"', html)
print('All Panes in index.html:')
for p in panes:
    print(' -', p)

nav_items = re.findall(r'href="#(pane-[^"]+)"[^>]*>(.*?)</a>', html)
print('\nNav items:')
for h, t in nav_items:
    clean = re.sub(r'<[^>]+>', '', t).strip()
    print(' -', h, ':', clean)
