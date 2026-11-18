import json

path = 'data/booking_data.json'
with open(path, 'r', encoding='utf-8') as f:
    d = json.load(f)

d['meta']['valid_until'] = 'September 2026'
d['meta']['active_months_count'] = 9
d['meta']['note'] = 'Data tervalidasi hanya sampai September 2026. Periode Oktober, November, dan Desember 2026 belum berjalan.'

# Set Okt, Nov, Des to null for each channel and recompute ytd_total
for k, ch in d['channels'].items():
    m = ch.get('monthly', [])
    clean_m = []
    for i in range(12):
        if i < 9 and i < len(m):
            clean_m.append(m[i])
        else:
            clean_m.append(None)
    ch['monthly'] = clean_m
    ch['ytd_total'] = sum(x for x in clean_m if x is not None)
    print(f"{k}: YTD Jan-Sep = {ch['ytd_total']}, monthly = {ch['monthly']}")

# Clean tiktok live
for item in d['tiktok_live']['monthly_trend']:
    if item['month'] in ['Okt', 'Nov', 'Des']:
        item['duration'] = None
        item['likes'] = None
        item['comments'] = None
        item['booking'] = None
        item['has_data'] = False
    else:
        item['has_data'] = True

with open(path, 'w', encoding='utf-8') as f:
    json.dump(d, f, indent=2, ensure_ascii=False)

print('[OK] booking_data.json updated successfully!')
