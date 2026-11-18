with open(r'c:\laragon\www\dashboard_bengkel\assets\js\dashboard.js', 'r', encoding='utf-8') as f:
    lines = f.readlines()

for i, l in enumerate(lines):
    if 'pane-booking' in l or 'data-target' in l or 'tab-nav-link' in l:
        print(f"Line {i+1}: {l.strip()[:100]}")
