import re
import json

with open('index.html', 'r', encoding='utf-8') as f:
    html = f.read()

panes = re.findall(r'id=["\'](pane-[a-zA-Z0-9_-]+)["\']', html)
print('All panes in index.html:', panes)

# Check all selects with period/month in index.html
selects = re.findall(r'<select[^>]*id=["\']([^"\']+)["\'][^>]*>(.*?)</select>', html, re.DOTALL)
print(f"\nFound {len(selects)} select elements. Inspecting period/month dropdowns:")
for s_id, s_content in selects:
    if any(k in s_id.lower() for k in ['period', 'month', 'filter', 'funnel', 'sbi', 'advisor', 'mra']):
        options = re.findall(r'<option[^>]*value=["\']([^"\']*)["\'][^>]*>([^<]*)</option>', s_content)
        opt_vals = [f"{v}:{t.strip()}" for v, t in options]
        print(f"\nSelect ID: {s_id}")
        print("  Options:", opt_vals)
