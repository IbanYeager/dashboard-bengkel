import urllib.request
import zipfile
import io
import xml.etree.ElementTree as ET
import os

doc_id = '1LQYpCsXsU3o6N4cAMQH7Da44rXhSlksO'
url = f'https://docs.google.com/spreadsheets/d/{doc_id}/export?format=xlsx'
req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'})

try:
    print('Downloading spreadsheet as XLSX...')
    with urllib.request.urlopen(req) as resp:
        data = resp.read()
    print('XLSX downloaded, size:', len(data))
    os.makedirs('data', exist_ok=True)
    with open('data/ao_report.xlsx', 'wb') as f:
        f.write(data)
    print('Saved to data/ao_report.xlsx')

    # Read sheet names from zip
    with zipfile.ZipFile(io.BytesIO(data)) as z:
        wb_xml = z.read('xl/workbook.xml')
        root = ET.fromstring(wb_xml)
        ns = {'main': 'http://schemas.openxmlformats.org/spreadsheetml/2006/main'}
        sheets = root.findall('.//main:sheet', ns)
        print(f'Total sheets in workbook: {len(sheets)}')
        for s in sheets:
            s_name = s.attrib.get('name')
            s_id = s.attrib.get('sheetId')
            print(f"  - Sheet: '{s_name}' (sheetId: {s_id})")

except Exception as e:
    print('Error:', e)
