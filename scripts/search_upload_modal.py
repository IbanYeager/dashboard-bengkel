import re

with open('index.html', encoding='utf-8') as f:
    text = f.read()

for m in re.finditer(r'<button[^>]*>.*?(?:sync|upload|import).*?</button>', text, re.I | re.DOTALL):
    print(m.group(0)[:150])

for m in re.finditer(r'id=["\'][^"\']*(?:sync|upload|import|excel)[^"\']*["\']', text, re.I):
    print(m.group(0))
