with open('index.html', 'r', encoding='utf-8') as f:
    lines = f.readlines()

for i, l in enumerate(lines):
    if 'pane-executive' in l or 'tab-nav-link' in l:
        print(f"Line {i+1}: {l.strip()}")
        start = max(0, i - 10)
        end = min(len(lines), i + 35)
        for j in range(start, end):
            print(f"{j+1:4d}: {lines[j]}", end='')
        break
