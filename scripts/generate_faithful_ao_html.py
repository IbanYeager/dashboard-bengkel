import json

with open('data/ao_report_data.json', 'r', encoding='utf-8') as f:
    d = json.load(f)

print('Data loaded successfully!')
