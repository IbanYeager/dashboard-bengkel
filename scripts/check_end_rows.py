import zipfile
import xml.etree.ElementTree as ET

fpath = 'DASH KIARACONDONG 24-26.xlsx'
with zipfile.ZipFile(fpath, 'r') as z:
    shared_strings = []
    if 'xl/sharedStrings.xml' in z.namelist():
        with z.open('xl/sharedStrings.xml') as f:
            for event, elem in ET.iterparse(f, events=('end',)):
                if elem.tag.endswith('si'):
                    shared_strings.append(''.join([t.text for t in elem.iter() if t.tag.endswith('t') and t.text]))
                    elem.clear()

    with z.open('xl/worksheets/sheet1.xml') as sf:
        for event, elem in ET.iterparse(sf, events=('end',)):
            if elem.tag.endswith('row'):
                r = int(elem.attrib.get('r', 0))
                if r >= 24035:
                    cols = {}
                    for c in elem.findall('{http://schemas.openxmlformats.org/spreadsheetml/2006/main}c'):
                        ref = c.attrib.get('r')
                        col = ''.join([ch for ch in ref if ch.isalpha()])
                        t = c.attrib.get('t')
                        v = c.find('{http://schemas.openxmlformats.org/spreadsheetml/2006/main}v')
                        val = v.text if v is not None else ''
                        if t == 's' and val: val = shared_strings[int(val)]
                        cols[col] = val
                    print(f"Row {r}: A={cols.get('A')}, B={cols.get('B')}, C={cols.get('C')}, K={cols.get('K')}, M={cols.get('M')}, AR={cols.get('AR')}")
                elem.clear()
