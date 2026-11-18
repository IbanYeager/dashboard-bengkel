import json

with open('data/dashboard_data.json', 'r', encoding='utf-8') as f:
    d = json.load(f)

print("Keys in dashboard_data.json:", list(d.keys()))
print("executive_frequency_revenue length:", len(d.get('executive_frequency_revenue', [])))
print("area_characteristics length:", len(d.get('area_characteristics', [])))
print("cross_selling sample categories:", list(set(c['category'] for c in d.get('cross_selling', [])[:100])))
print("Check if SYNT or WIPER FLUID in cross_selling:", [c['category'] for c in d.get('cross_selling', []) if c['category'] in ['SYNT', 'WIPER FLUID']])
