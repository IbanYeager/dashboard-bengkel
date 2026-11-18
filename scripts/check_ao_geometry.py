import re

with open('data/ao_html/Dashboard AO.html', 'r', encoding='utf-8') as f:
    html = f.read()

widths = [int(w) for w in re.findall(r'style="width:(\d+)px;"', html)]
print('Total columns:', len(widths), 'Sum widths:', sum(widths))
heights = [int(h) for h in re.findall(r'style="height:\s*(\d+)px"', html)]
print('Total rows:', len(heights), 'Sum heights:', sum(heights))
print('First 10 col widths:', widths[:10])
print('First 10 row heights:', heights[:10])
