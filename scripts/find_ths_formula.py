import zipfile
import xml.etree.ElementTree as ET

for fn in ['DASH KIARACONDONG 24-26.xlsx', 'Dashboard AFS Kiaracondong-start 2024.xlsx']:
    with zipfile.ZipFile(fn, 'r') as z:
        print(f"\nChecking {fn}...")
        for name in z.namelist():
            if name.startswith('xl/worksheets/sheet') and name.endswith('.xml'):
                content = z.read(name)
                if b'458' in content or b'THS' in content:
                    print(f"Found in {name}")
                    # Let's inspect formulas
                    root = ET.fromstring(content)
                    for c in root.findall('.//{http://schemas.openxmlformats.org/spreadsheetml/2006/main}c'):
                        f = c.find('{http://schemas.openxmlformats.org/spreadsheetml/2006/main}f')
                        if f is not None and f.text and 'THS' in f.text.upper():
                            r_attr = c.attrib.get('r')
                            print(f"  Cell {r_attr}: formula = {f.text}")
