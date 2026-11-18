import urllib.request, csv, io

sheet_id = '1b60d-JO50LU4KyywuULokmDIU7z3Ts_1'
url = f'https://docs.google.com/spreadsheets/d/{sheet_id}/gviz/tq?tqx=out:csv&sheet=Daftar%20List%20SO'
req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
with urllib.request.urlopen(req, timeout=90) as resp:
    content = resp.read().decode('utf-8', errors='replace')

reader = csv.reader(io.StringIO(content))
headers = next(reader)

for idx, r in enumerate(reader):
    if '146PKB2610-0456' in ' '.join(r):
        print(f"Row {idx+2}:")
        for i, val in enumerate(r):
            h_name = headers[i] if i < len(headers) else "?"
            if val.strip():
                print(f"  Col {i:2d} [{h_name}]: {val}")
