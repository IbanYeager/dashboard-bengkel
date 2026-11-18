import urllib.request
import urllib.parse

sheet_id = '1b60d-JO50LU4KyywuULokmDIU7z3Ts_1'
# Col C is TAHUN (or col 2), Col B is BULAN (or col 1)
# Let's test a simple query
query = "SELECT B, count(A) GROUP BY B"
encoded_query = urllib.parse.quote(query)
url = f'https://docs.google.com/spreadsheets/d/{sheet_id}/gviz/tq?tqx=out:csv&sheet=INPUT%20PKB&tq={encoded_query}'

print("Testing URL:", url)
req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
try:
    with urllib.request.urlopen(req, timeout=15) as resp:
        text = resp.read().decode('utf-8')
        print("Query result (first 500 chars):")
        print(text[:500])
except Exception as e:
    print("Query error:", e)
