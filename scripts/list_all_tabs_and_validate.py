import re
import json

with open('index.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Find all tab buttons
tabs = re.findall(r'<button[^>]*class="[^"]*tab-nav-link[^"]*"[^>]*data-target="([^"]+)"[^>]*>(.*?)</button>', content, re.DOTALL)
print("=== ALL DASHBOARD TABS / MENUS ===")
clean_tabs = []
for target, html in tabs:
    # clean tags from html
    text = re.sub(r'<[^>]+>', '', html).strip()
    clean_tabs.append((target, text))
    print(f"  * Tab: {text:<32} -> ID: #{target}")

print("\n=== TOTAL TABS:", len(clean_tabs))

# Check data sources backing each tab
with open('data/dashboard_data.json', 'r', encoding='utf-8') as f:
    db = json.load(f)

with open('data/funnelling_data.json', 'r', encoding='utf-8') as f:
    fn = json.load(f)

with open('data/booking_data.json', 'r', encoding='utf-8') as f:
    bk = json.load(f)

print("\n=== DATA SOURCE KEYS CHECK ===")
print("dashboard_data.json keys:", list(db.keys()))
print("funnelling_data.json keys:", list(fn.keys()))
print("booking_data.json keys:", list(bk.keys()))
