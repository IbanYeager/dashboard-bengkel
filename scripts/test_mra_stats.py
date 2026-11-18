import csv
from collections import Counter, defaultdict

month_map = {
    'Jan-26': 'Jan', 'Feb-26': 'Feb', 'Mar-26': 'Mar',
    'Apr-26': 'Apr', 'Jun-26': 'Jun', 'Jul-26': 'Jul', 'Sep-26': 'Sep'
}

mra_stats = defaultdict(lambda: defaultdict(Counter))
ths_stats = defaultdict(Counter)
sa_stats = defaultdict(lambda: defaultdict(Counter))

with open('data/mra_raw_sheet.csv', 'r', encoding='utf-8') as f:
    reader = csv.reader(f)
    headers = next(reader)
    for r in reader:
        if not r or len(r) < 16: continue
        q = r[0].strip()
        k1 = r[1].strip()
        k2 = r[2].strip()
        k3 = r[3].strip()
        cai = r[4].strip()
        due = r[13].strip()
        pic = r[14].strip()
        bln_raw = r[15].strip()
        ths_val = r[72].strip() if len(r) > 72 else ''
        sa_val = r[76].strip().upper() if len(r) > 76 else ''
        
        # normalize month
        if bln_raw in month_map:
            m = month_map[bln_raw]
        elif q == '2' or '30/5/26' in due:
            m = 'Mei'
        elif q == '3' or 'Agu' in (r[39] if len(r)>39 else ''):
            m = 'Agt'
        else:
            m = 'Unknown'
            
        # normalize PIC
        if 'RANI' in pic.upper():
            pic_norm = 'RANI'
        elif 'NURI' in pic.upper():
            pic_norm = 'NURI'
        else:
            pic_norm = 'OTHER'
            
        # MRA stats
        mra_stats[m][pic_norm]['potensi'] += 1
        if k1 == 'CUST FU':
            mra_stats[m][pic_norm]['fu'] += 1
        if k3 == 'CONTACTED':
            mra_stats[m][pic_norm]['contacted'] += 1
        if cai == 'CAI':
            mra_stats[m][pic_norm]['cai'] += 1
            
        # THS stats
        if ths_val == 'THS':
            ths_stats[m]['potensi'] += 1
            if k3 == 'CONTACTED':
                ths_stats[m]['contacted'] += 1
            if cai == 'CAI':
                ths_stats[m]['cai'] += 1
                
        # SA stats
        if sa_val in ['DIDIN', 'FICKY', 'ACEP']:
            sa_stats[m][sa_val]['potensi'] += 1
            if k3 == 'CONTACTED':
                sa_stats[m][sa_val]['contacted'] += 1
            if cai == 'CAI':
                sa_stats[m][sa_val]['cai'] += 1

print('=== MRA MONTHLY STATS ===')
for m in ['Jan', 'Feb', 'Mar', 'Apr', 'Mei', 'Jun', 'Jul', 'Agt', 'Sep']:
    print(f'{m}:')
    for p in ['RANI', 'NURI']:
        s = mra_stats[m][p]
        pct = (s['cai']/s['contacted']*100) if s['contacted'] else 0
        print(f"  {p}: {s['potensi']} Potensi | {s['fu']} FU | {s['contacted']} Contacted | {s['cai']} CAI ({pct:.1f}%)")

print('\n=== THS MONTHLY STATS ===')
tot_ths_pot = 0
tot_ths_cont = 0
tot_ths_cai = 0
for m in ['Jan', 'Feb', 'Mar', 'Apr', 'Mei', 'Jun', 'Jul', 'Agt', 'Sep']:
    s = ths_stats[m]
    pct = (s['cai']/s['contacted']*100) if s['contacted'] else 0
    tot_ths_pot += s['potensi']
    tot_ths_cont += s['contacted']
    tot_ths_cai += s['cai']
    print(f"{m}: Potensi {s['potensi']} | Contacted {s['contacted']} | CAI {s['cai']} ({pct:.1f}%)")
tot_pct = (tot_ths_cai/tot_ths_cont*100) if tot_ths_cont else 0
print(f"THS YTD Total: Potensi {tot_ths_pot} | Contacted {tot_ths_cont} | CAI {tot_ths_cai} ({tot_pct:.1f}%)")

print('\n=== SA MONTHLY STATS (CAI & CONTACTED) ===')
for m in ['Jan', 'Feb', 'Mar', 'Apr', 'Mei', 'Jun', 'Jul', 'Agt', 'Sep']:
    tot_cai = sum(sa_stats[m][sa]['cai'] for sa in ['DIDIN', 'FICKY', 'ACEP'])
    tot_contacted = sum(sa_stats[m][sa]['contacted'] for sa in ['DIDIN', 'FICKY', 'ACEP'])
    print(f"{m}: Total All SA Contacted={tot_contacted}, CAI={tot_cai}")
    for sa in ['DIDIN', 'FICKY', 'ACEP']:
        s = sa_stats[m][sa]
        pct_cont = (s['cai']/tot_cai*100) if tot_cai else 0
        pct_cai = (s['cai']/s['contacted']*100) if s['contacted'] else 0
        print(f"  {sa}: Contacted={s['contacted']}, CAI={s['cai']} ({pct_cai:.1f}%), Contrib={pct_cont:.1f}%")
