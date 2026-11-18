import urllib.request

sheet_id = '1b60d-JO50LU4KyywuULokmDIU7z3Ts_1'
gids = ['177004909', '2141708170', '1137757859', '943118321', '1727895687']

for gid in gids:
    url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/gviz/tq?tqx=out:csv&gid={gid}"
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=8) as r:
            first_line = r.readline().decode('utf-8', errors='ignore').strip()
            print(f"GID {gid}: {first_line[:120]}")
    except Exception as e:
        print(f"GID {gid}: Error {e}")
