import urllib.request
import csv
import io
from collections import Counter

url = 'https://docs.google.com/spreadsheets/d/1b60d-JO50LU4KyywuULokmDIU7z3Ts_1/gviz/tq?tqx=out:csv&sheet=INPUT%20PKB'
print("Fetching INPUT PKB from Google Sheets...")
req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
try:
    with urllib.request.urlopen(req, timeout=30) as resp:
        content = resp.read().decode('utf-8', errors='replace')
        reader = csv.reader(io.StringIO(content))
        headers = next(reader)
        print(f"Loaded {len(headers)} columns.")
        
        # Find index of tahun, bulan, tgl, pkb_no, revenue
        idx_thn = -1
        idx_bln = -1
        idx_tgl = -1
        idx_rev = -1
        idx_ue = -1
        for i, h in enumerate(headers):
            hl = h.strip().lower()
            if hl in ['tahun', 'thn', 'year']: idx_thn = i
            if hl in ['bulan', 'bln', 'month']: idx_bln = i
            if hl in ['tgl', 'tanggal', 'date', 'day']: idx_tgl = i
            if hl in ['total revenue', 'revenue', 'rev']: idx_rev = i
            if hl in ['type ue', 'ue']: idx_ue = i
        
        print(f"Col indices: thn={idx_thn}, bln={idx_bln}, tgl={idx_tgl}, rev={idx_rev}, ue={idx_ue}")
        
        july_dates = Counter()
        months_2026 = Counter()
        total_rows_2026 = 0
        
        for row in reader:
            if len(row) <= max(idx_thn, idx_bln): continue
            yr = row[idx_thn].strip().replace('.0', '')
            if yr == '2026':
                total_rows_2026 += 1
                mo = row[idx_bln].strip()
                months_2026[mo] += 1
                if mo in ['07', '7', '7.0', 'July', 'Juli', 'jul']:
                    tgl = row[idx_tgl].strip() if idx_tgl >= 0 else '?'
                    july_dates[tgl] += 1
        
        print("\n2026 Months in Live Google Sheets INPUT PKB:")
        for mo, cnt in sorted(months_2026.items()):
            print(f"  Bulan {mo:6}: {cnt} rows")
            
        print("\nJuly dates in Live Google Sheets INPUT PKB:")
        for d, cnt in sorted(july_dates.items(), key=lambda x: int(float(x[0])) if x[0].replace('.0','').isdigit() else 999):
            print(f"  Tgl {d:4}: {cnt} rows")
            
except Exception as e:
    print("Error fetching Google Sheets:", e)
