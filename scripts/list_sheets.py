import zipfile
import xml.etree.ElementTree as ET

for fn in ['DASH KIARACONDONG 24-26.xlsx', 'Dashboard AFS Kiaracondong-start 2024.xlsx']:
    with zipfile.ZipFile(fn, 'r') as z:
        wb_tree = ET.fromstring(z.read('xl/workbook.xml'))
        sheets = [s.attrib.get('name') for s in wb_tree.findall('{http://schemas.openxmlformats.org/spreadsheetml/2006/main}sheets/{http://schemas.openxmlformats.org/spreadsheetml/2006/main}sheet')]
        print(f"\nSheets in {fn}:")
        for s in sheets:
            print(" -", s)
