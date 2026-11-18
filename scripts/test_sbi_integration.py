import urllib.request
import json

print("1. Checking sbi_data.json...")
res = urllib.request.urlopen('http://localhost:8088/data/sbi_data.json')
content = res.read().decode('utf-8')
data = json.loads(content)
print(f"   [OK] Total records: {len(data['records'])}")
print(f"   [OK] Meta title: {data['meta']['title']}")
print(f"   [OK] Monthly 2026 months count: {len(data['summary']['monthly_2026'])}")

print("\n2. Checking index.html...")
res_html = urllib.request.urlopen('http://localhost:8088/')
html = res_html.read().decode('utf-8')
assert 'pane-sbi' in html, "pane-sbi not in index.html"
assert 'sbi-detail-modal' in html, "sbi-detail-modal not in index.html"
assert 'data-target="pane-sbi"' in html, "SBI tab not in index.html"
print("   [OK] All HTML elements found in index.html")

print("\n3. Checking dashboard.js...")
res_js = urllib.request.urlopen('http://localhost:8088/assets/js/dashboard.js')
js = res_js.read().decode('utf-8')
assert 'renderSbi' in js, "renderSbi missing"
assert 'openSbiDetailModal' in js, "openSbiDetailModal missing"
assert 'loadSbiData' in js, "loadSbiData missing"
assert 'renderSbiTable' in js, "renderSbiTable missing"
print("   [OK] All JS functions found in dashboard.js")

print("\n4. Checking style.css...")
res_css = urllib.request.urlopen('http://localhost:8088/assets/css/style.css')
css = res_css.read().decode('utf-8')
assert '.sbi-header-card' in css, ".sbi-header-card missing"
assert '.sbi-data-table' in css, ".sbi-data-table missing"
assert '.sbi-modal-container' in css, ".sbi-modal-container missing"
print("   [OK] All SBI CSS styles found in style.css")

print("\n--> ALL INTEGRATION CHECKS PASSED 100%!")
