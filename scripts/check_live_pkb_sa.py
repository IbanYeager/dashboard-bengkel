import urllib.request, csv, io, re
from collections import defaultdict

url = 'https://docs.google.com/spreadsheets/d/1b60d-JO50LU4KyywuULokmDIU7z3Ts_1/export?format=csv&gid=177004909'
req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
with urllib.request.urlopen(req, timeout=60) as resp:
    content = resp.read().decode('utf-8', errors='replace')

reader = csv.reader(io.StringIO(content))
headers = next(reader)

def clean_rev(s):
    if not s or s.strip() in ['-', '#REF!', '#N/A', '#VALUE!', 'FALSE', 'TRUE', '']:
        return 0.0
    s = re.sub(r'^(?:Rp\.?|RP\.?|rp\.?)\s*', '', s.strip()).strip()
    if '.' in s and ',' in s:
        if s.rfind('.') < s.rfind(','): s = s.replace('.', '').replace(',', '.')
        else: s = s.replace(',', '')
    elif '.' in s:
        dots = s.count('.')
        if dots > 1: s = s.replace('.', '')
        else:
            parts = s.split('.')
            if len(parts[1]) == 3 and len(parts[0]) <= 3: s = s.replace('.', '')
    elif ',' in s:
        commas = s.count(',')
        if commas > 1: s = s.replace(',', '')
        else:
            parts = s.split(',')
            if len(parts[1]) == 3 and len(parts[0]) <= 3: s = s.replace(',', '')
            else: s = s.replace(',', '.')
    s = re.sub(r'[^0-9.-]', '', s)
    try: return float(s)
    except: return 0.0

sa_oct = defaultdict(lambda: {'ue': 0, 'cpus': 0, 'tcare': 0, 'rev': 0.0})
for r in reader:
    if len(r) > 2 and r[2].strip() == '2026' and r[1].strip() in ['10', '10.0']:
        sa = r[42].strip().upper() if len(r) > 42 else ''
        if not sa and len(r) > 25:
            sa = r[25].strip().upper()
        if sa in ['DIDIN', 'FICKY', 'ACEP']:
            sa_oct[sa]['ue'] += 1
            if len(r) > 43 and r[43].strip() == 'CPUS':
                sa_oct[sa]['cpus'] += 1
            if len(r) > 49 and r[49].strip() == 'T-CARE':
                sa_oct[sa]['tcare'] += 1
            rev = clean_rev(r[57]) if len(r) > 57 else 0.0
            sa_oct[sa]['rev'] += rev

print("Live PKB October 2026 SA Totals:")
for sa, d in sorted(sa_oct.items()):
    print(f"  {sa}: UE={d['ue']}, CPUS={d['cpus']}, T-Care={d['tcare']}, Rev=Rp {d['rev']:,.0f}")
