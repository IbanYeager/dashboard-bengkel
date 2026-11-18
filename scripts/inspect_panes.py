with open('index.html', 'r', encoding='utf-8') as f:
    text = f.read()

import re

for match in re.finditer(r'<[a-z0-9]+[^>]+id="(pane-[^"]+)"[^>]*>', text):
    pane_id = match.group(1)
    tag = match.group(0)
    print(f"=== {pane_id} === -> {tag[:100]}")
