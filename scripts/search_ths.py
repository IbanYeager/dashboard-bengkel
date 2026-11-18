import zipfile
import xml.etree.ElementTree as ET

EXCEL_PATH = r"c:\laragon\www\dashboard_bengkel\DASH KIARACONDONG 24-26.xlsx"

with zipfile.ZipFile(EXCEL_PATH, 'r') as z:
    # Read shared strings to see where 'THS' appears
    print("Reading shared strings...")
    ths_indices = []
    if 'xl/sharedStrings.xml' in z.namelist():
        with z.open('xl/sharedStrings.xml') as f:
            idx = 0
            for event, elem in ET.iterparse(f, events=('end',)):
                if elem.tag.endswith('si'):
                    text = "".join([t.text for t in elem.iter() if t.tag.endswith('t') and t.text])
                    if 'THS' in text.upper():
                        print(f"String #{idx}: {text}")
                        ths_indices.append(idx)
                    idx += 1
                    elem.clear()

print(f"Total THS strings: {len(ths_indices)}")
