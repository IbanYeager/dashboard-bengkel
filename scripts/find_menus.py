import re

with open('index.html', 'r', encoding='utf-8') as f:
    html = f.read()

# find buttons, links, or nav elements
print("--- Navigation / Menu Buttons ---")
for m in re.finditer(r'<button[^>]*class="[^"]*nav[^"]*"[^>]*>(.*?)</button>', html, re.DOTALL | re.IGNORECASE):
    print(m.group(0)[:200])

for m in re.finditer(r'<button[^>]*class="[^"]*tab[^"]*"[^>]*>(.*?)</button>', html, re.DOTALL | re.IGNORECASE):
    print(m.group(0)[:200])

print("\n--- Sections with id ---")
for m in re.finditer(r'<section[^>]+id="([^"]+)"[^>]*>', html):
    print(m.group(0))

print("\n--- Any divs with tab / menu ---")
for m in re.finditer(r'<(div|nav)[^>]+class="[^"]*(menu|tab|nav)[^"]*"[^>]*>', html, re.IGNORECASE):
    print(m.group(0)[:150])
