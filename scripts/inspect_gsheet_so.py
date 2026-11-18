import urllib.request
import csv
import io

sheet_id = '1b60d-JO50LU4KyywuULokmDIU7z3Ts_1'
url = f'https://docs.google.com/spreadsheets/d/{sheet_id}/gviz/tq?tqx=out:csv&sheet=Daftar%20List%20SO'
print("Fetching Google Sheets 'Daftar List SO'...")
req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
try:
    with urllib.request.urlopen(req, timeout=15) as resp:
        content = resp.read().decode('utf-8', errors='replace')
        reader = csv.reader(io.StringIO(content))
        headers = next(reader)
        print("Total headers in Daftar List SO:", len(headers))
        for i, h in enumerate(headers):
            if any(k in h.lower() for k in ['pkb', 'so', 'rev', 'tgl', 'total', 'net', 'jasa', 'part']):
                print(f"Col {i:2d}: '{h}'")
        
        # Check rows with 2609 or Sep
        sep_rows = []
        for r in reader:
            line_str = ' '.join(r)
            if '2609' in line_str or 'Sep' in line_str or '09/2026' in line_str:
                sep_rows.append(r)
        print(f"Total September rows in Daftar List SO: {len(sep_rows)}")
        if sep_rows:
            print("Sample September row in Daftar List SO:")
            for i, (h, v) in enumerate(zip(headers, sep_rows[0])):
                if v.strip():
                    print(f"  Col {i:2d} ({h}): '{v}'")
except Exception as e:
    print("Error fetching Daftar List SO:", e)
