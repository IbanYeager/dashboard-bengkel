import zipfile
import xml.etree.ElementTree as ET

z = zipfile.ZipFile('KPI Dashboard Kabeng GR-ags.xlsx', 'r')
ss = []
if 'xl/sharedStrings.xml' in z.namelist():
    tree = ET.fromstring(z.read('xl/sharedStrings.xml'))
    for si in tree.findall('{http://schemas.openxmlformats.org/spreadsheetml/2006/main}si'):
        ss.append(''.join([n.text for n in si.iter() if n.text]))

s_tree = ET.fromstring(z.read('xl/worksheets/sheet2.xml'))
for r in s_tree.findall('{http://schemas.openxmlformats.org/spreadsheetml/2006/main}sheetData/{http://schemas.openxmlformats.org/spreadsheetml/2006/main}row'):
    r_num = int(r.attrib['r'])
    if r_num in [5, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18]:
        vals = {}
        for c in r.findall('{http://schemas.openxmlformats.org/spreadsheetml/2006/main}c'):
            ref = c.attrib['r']
            col = ''.join([ch for ch in ref if ch.isalpha()])
            t = c.attrib.get('t')
            v = c.find('{http://schemas.openxmlformats.org/spreadsheetml/2006/main}v')
            val = v.text if v is not None else ''
            if t == 's' and val: val = ss[int(val)]
            vals[col] = val
        print(f"Row {r_num} (B={vals.get('B')} C={vals.get('C')}):")
        cols = ['E','F','G','H','I','J','K','L','M','N','O','P']
        print("  ", {c: vals.get(c) for c in cols})
