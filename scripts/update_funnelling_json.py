import json

with open('data/funnelling_data.json', 'r', encoding='utf-8') as f:
    fn = json.load(f)

with open('data/attacklist_priority_segments.json', 'r', encoding='utf-8') as f:
    atk = json.load(f)

# Update overall priority segments
fn['priority_segments'] = atk['overall']

# Update by_period priority segments if present
if 'priority_segments_by_period' not in fn:
    fn['priority_segments_by_period'] = {}

for k, v in atk['by_period'].items():
    fn['priority_segments_by_period'][k] = v

with open('data/funnelling_data.json', 'w', encoding='utf-8') as f:
    json.dump(fn, f, indent=2, ensure_ascii=False)

print("Updated funnelling_data.json with exact ATTACKLIST priority segments!")
print("Priority 1 Subgroups:")
for sg in fn['priority_segments'][0]['subgroups']:
    print(f"  {sg['label']}: Potensi={sg['potensi']}, CAI={sg['cai']}, Pct={sg['pct']}%")
