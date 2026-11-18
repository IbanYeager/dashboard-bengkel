import zipfile
import xml.etree.ElementTree as ET

for fn in ['DASH KIARACONDONG 24-26.xlsx', 'DASH KIARACONDONG 24-26.backup.xlsx', 'DASH KIARACONDONG 24-26(1).xlsx', 'Dashboard AFS Kiaracondong-start 2024.xlsx']:
    try:
        with zipfile.ZipFile(fn, 'r') as z:
            wb = ET.fromstring(z.read('xl/workbook.xml'))
            sheets = [s.attrib['name'] for s in wb.findall('{http://schemas.openxmlformats.org/spreadsheetml/2006/main}sheets/{http://schemas.openxmlformats.org/spreadsheetml/2006/main}sheet')]
            print(f"{fn}: {sheets}")
    except Exception as e:
        print(f"{fn}: {e}")
