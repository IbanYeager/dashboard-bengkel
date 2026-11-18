with open('index.html', 'r', encoding='utf-8') as f:
    text = f.read()

import re

for pane in ['pane-booking', 'pane-tiktok']:
    pos = text.find(f'id="{pane}"')
    if pos != -1:
        print(f"==================== {pane} ====================")
        # find closing </div> for this container or first 80 lines
        snippet = text[pos:pos+2500]
        print(snippet)
