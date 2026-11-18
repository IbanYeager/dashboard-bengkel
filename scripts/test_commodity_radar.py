import json

with open('data/dashboard_data.json', 'r', encoding='utf-8') as f:
    d = json.load(f)

CANONICAL_COMMODITIES = [
    'CHEMICAL SMM', 'FULL SYNT', 'OPL CAR CARE', 'OPL AC',
    'SPOORING', 'BATTERY', 'TIRE', 'REMATCHING',
    'CROSS SELLING TAM', 'SMM OIL'
]

# Calculate for 2026 YTD
sas = ['DIDIN', 'FICKY', 'ACEP']

# YTD Totals
tot_ytd = {c: 0 for c in CANONICAL_COMMODITIES}
sa_ytd = {sa: {c: {'rev': 0, 'qty': 0} for c in CANONICAL_COMMODITIES} for sa in sas}

# September Totals
tot_sep = {c: 0 for c in CANONICAL_COMMODITIES}
sa_sep = {sa: {c: {'rev': 0, 'qty': 0} for c in CANONICAL_COMMODITIES} for sa in sas}

for item in d.get('sa_cross_selling', []):
    if item.get('year') == 2026:
        sa = item.get('sa')
        cat = (item.get('category') or '').upper().strip()
        if cat in CANONICAL_COMMODITIES and sa in sas:
            rev = item.get('revenue', 0)
            qty = item.get('qty', 0)
            tot_ytd[cat] += rev
            sa_ytd[sa][cat]['rev'] += rev
            sa_ytd[sa][cat]['qty'] += qty
            
            if item.get('month_name') == 'September':
                tot_sep[cat] += rev
                sa_sep[sa][cat]['rev'] += rev
                sa_sep[sa][cat]['qty'] += qty

print("=== 2026 YTD RESULTS (Ach vs 33.3% fair share) ===")
for sa in sas:
    print(f"\n--- {sa} (YTD) ---")
    achs = []
    for c in CANONICAL_COMMODITIES:
        tot = tot_ytd[c]
        rev = sa_ytd[sa][c]['rev']
        share = rev / tot if tot > 0 else 0
        ach = round((share / (1/3)) * 100, 1)
        achs.append(ach)
        print(f"  {c:20s}: Rev=Rp {rev:12,.0f} | Share={share*100:5.1f}% | Ach={ach:5.1f}%")
    print(f"  Average YTD Ach: {round(sum(achs)/len(achs), 1)}%")

print("\n=== September 2026 RESULTS (Ach vs 33.3% fair share) ===")
for sa in sas:
    print(f"\n--- {sa} (September) ---")
    achs = []
    for c in CANONICAL_COMMODITIES:
        tot = tot_sep[c]
        rev = sa_sep[sa][c]['rev']
        share = rev / tot if tot > 0 else 0
        ach = round((share / (1/3)) * 100, 1)
        achs.append(ach)
        print(f"  {c:20s}: Rev=Rp {rev:12,.0f} | Share={share*100:5.1f}% | Ach={ach:5.1f}%")
    print(f"  Average Sep Ach: {round(sum(achs)/len(achs), 1)}%")
