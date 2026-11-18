import urllib.request
import urllib.parse

sheet_id = '1b60d-JO50LU4KyywuULokmDIU7z3Ts_1'
# Col D is TAHUN, Col C is BULAN, Col F is SA, Col L is cross_category, Col AO is transaction_amount
query = "SELECT D, C, F, L, sum(AO) WHERE D = 2026 AND L != '' GROUP BY D, C, F, L"
encoded_query = urllib.parse.quote(query)
url = f'https://docs.google.com/spreadsheets/d/{sheet_id}/gviz/tq?tqx=out:csv&sheet=Daftar%20List%20SO&tq={encoded_query}'

print("Testing SO Query URL...")
req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
try:
    with urllib.request.urlopen(req, timeout=15) as resp:
        text = resp.read().decode('utf-8')
        print("SO Query result (first 1000 chars):")
        print(text[:1000])
except Exception as e:
    print("SO Query error:", e)
