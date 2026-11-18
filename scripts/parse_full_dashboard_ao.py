import zipfile
import xml.etree.ElementTree as ET
import re

with zipfile.ZipFile('data/ao_report.xlsx') as z:
    wb_root = ET.fromstring(z.read('xl/workbook.xml'))
    rels_root = ET.fromstring(z.read('xl/_rels/workbook.xml.rels'))
    ns = {'main': 'http://schemas.openxmlformats.org/spreadsheetml/2006/main'}
    r_ns = {'rel': 'http://schemas.openxmlformats.org/package/2006/relationships'}
    
    # Read shared strings
    shared_strings = []
    if 'xl/sharedStrings.xml' in z.namelist():
        ss_root = ET.fromstring(z.read('xl/sharedStrings.xml'))
        for si in ss_root.findall('.//main:si', ns):
            shared_strings.append(''.join(t.text or '' for t in si.findall('.//main:t', ns)))
            
    # Read sheet2.xml (Dashboard AO)
    s_root = ET.fromstring(z.read('xl/worksheets/sheet2.xml'))
    
    # Read merged cells
    merges = []
    for merge in s_root.findall('.//main:mergeCells/main:mergeCell', ns):
        merges.append(merge.attrib.get('ref', ''))
    print(f'Total merged cell regions: {len(merges)}')
    print('Sample merges:', merges[:10])
    
    # Read rows
    print('\n--- ALL ROWS IN SHEET 2 ---')
    for row in s_root.findall('.//main:row', ns):
        r_idx = int(row.attrib.get('r', 0))
        cells = []
        for c in row.findall('.//main:c', ns):
            coord = c.attrib.get('r', '')
            t = c.attrib.get('t', '')
            v = c.find('main:v', ns)
            val = v.text if v is not None else ''
            if t == 's' and val.isdigit():
                val = shared_strings[int(val)]
            if val:
                cells.append(f'{coord}: {val}')
        if cells:
            print(f'Row {r_idx:2d} ({len(cells)} cells): ' + ' | '.join(cells[:8]))
