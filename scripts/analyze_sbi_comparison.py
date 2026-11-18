import json
from collections import defaultdict

with open('data/sbi_data.json', 'r', encoding='utf-8') as f:
    d = json.load(f)

months = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']
by_yr_m = {yr: {m: {'dec': 0, 'cai': 0} for m in months} for yr in ['2024', '2025', '2026']}

for r in d['records']:
    yr = str(r.get('year'))
    m = r.get('month')
    if yr in by_yr_m and m in by_yr_m[yr]:
        by_yr_m[yr][m]['dec'] += 1
        if (r.get('cai') or '').upper() == 'CAI':
            by_yr_m[yr][m]['cai'] += 1

print('=== MONTHLY COMPARISON ACROSS YEARS ===')
for m in months:
    d24 = by_yr_m['2024'][m]
    d25 = by_yr_m['2025'][m]
    d26 = by_yr_m['2026'][m]
    print(f"{m[:3]:4s} | 2024: DEC={d24['dec']:2d}, CAI={d24['cai']:2d} | 2025: DEC={d25['dec']:2d}, CAI={d25['cai']:2d} | 2026: DEC={d26['dec']:2d}, CAI={d26['cai']:2d}")

# Let's also check SS breakdown per year
ss_yr = defaultdict(lambda: defaultdict(int))
for r in d['records']:
    yr = str(r.get('year'))
    ss = (r.get('ss') or 'OTHER').strip().upper()
    if ss:
        ss_yr[yr][ss] += 1

print('\n=== SERVICE SALES (SS) BREAKDOWN PER YEAR ===')
for yr in ['2024', '2025', '2026']:
    print(f"Year {yr}: {dict(ss_yr[yr])}")

# Let's check Ring Area breakdown per year
ring_yr = defaultdict(lambda: defaultdict(int))
for r in d['records']:
    yr = str(r.get('year'))
    ring = (r.get('ring_area') or 'OUT OF AREA').strip().upper()
    ring_yr[yr][ring] += 1

print('\n=== RING AREA BREAKDOWN PER YEAR ===')
for yr in ['2024', '2025', '2026']:
    print(f"Year {yr}: {dict(ring_yr[yr])}")
