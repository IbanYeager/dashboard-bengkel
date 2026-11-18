import json

with open('data/dashboard_data.json', 'r', encoding='utf-8') as f:
    d = json.load(f)

def search_july(obj, path=""):
    if isinstance(obj, dict):
        for k, v in obj.items():
            new_path = f"{path}.{k}" if path else k
            if k == 'July' or k == '2026-07' or k == '07':
                print(f"Found Key '{new_path}':", str(v)[:120])
            search_july(v, new_path)
    elif isinstance(obj, list):
        for i, item in enumerate(obj):
            if isinstance(item, dict):
                if item.get('month_name') == 'July' and str(item.get('year') or item.get('tahun')) == '2026':
                    print(f"Found Item in '{path}[{i}]':", str(item)[:120])
                search_july(item, f"{path}[{i}]")

search_july(d)
