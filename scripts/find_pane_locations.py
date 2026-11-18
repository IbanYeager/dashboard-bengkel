with open('index.html', 'r', encoding='utf-8') as f:
    text = f.read()

import re

# find where pane-tiktok ends or where all panes are defined
matches = list(re.finditer(r'<div id="(pane-[^"]+)"', text))
for idx, m in enumerate(matches):
    start = m.start()
    pane_name = m.group(1)
    print(f"Pane: {pane_name} at pos {start}")

# also find the last pane
last_pane = matches[-1]
print("Last pane starts at:", last_pane.start())
print(text[last_pane.start():last_pane.start()+200])
