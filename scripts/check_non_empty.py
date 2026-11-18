import zipfile
import xml.etree.ElementTree as ET

fpath = 'DASH KIARACONDONG 24-26.xlsx'
with zipfile.ZipFile(fpath, 'r') as z:
    with z.open('xl/worksheets/sheet1.xml') as sf:
        non_empty = []
        for event, elem in ET.iterparse(sf, events=('end',)):
            if elem.tag.endswith('row'):
                r = int(elem.attrib.get('r', 0))
                # check if has cells
                cells = elem.findall('{http://schemas.openxmlformats.org/spreadsheetml/2006/main}c')
                if len(cells) > 5:
                    non_empty.append(r)
                elem.clear()
        print(f"Total non-empty rows (>5 cells): {len(non_empty)}, max r: {max(non_empty) if non_empty else 0}")
