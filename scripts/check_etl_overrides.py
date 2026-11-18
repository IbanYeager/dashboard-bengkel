with open('scripts/etl_sync.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

for idx, line in enumerate(lines, 1):
    if any(k in line.lower() for k in ['september', 'october', 'hardcode', 'override', '722', '1857785']):
        print(f"Line {idx}: {line.strip()}")
