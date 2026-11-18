import urllib.request
import urllib.parse

sheet_id = '1b60d-JO50LU4KyywuULokmDIU7z3Ts_1'
# Col D is TAHUN, Col C is BULAN, Col F is SA, Col L is cross_category
query = "SELECT D, C, F, L, AO LIMIT 20 OFFSET 145550"
encoded_query = urllib.parse.quote(query)
url = f'https://docs.google.com/spreadsheets/d/{sheet_id}/gviz/tq?tqx=out:csv&sheet=Daftar%20List%20SO&tq={encoded_query}'

req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
try:
    with urllib.request.urlopen(req, timeout=15) as resp:
        text = resp.read().decode('utf-8')
        print(text)
except Exception as e:
    print("Error:", e)
