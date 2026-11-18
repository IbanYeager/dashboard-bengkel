import zipfile
import xml.etree.ElementTree as ET

with zipfile.ZipFile('data/ao_report.xlsx') as z:
    ns = {'main': 'http://schemas.openxmlformats.org/spreadsheetml/2006/main'}
    
    # Read shared strings
    shared_strings = []
    if 'xl/sharedStrings.xml' in z.namelist():
        ss_root = ET.fromstring(z.read('xl/sharedStrings.xml'))
        for si in ss_root.findall('.//main:si', ns):
            shared_strings.append(''.join(t.text or '' for t in si.findall('.//main:t', ns)))
            
    s_root = ET.fromstring(z.read('xl/worksheets/sheet2.xml'))
    
    # Merged cells map
    merges = {}
    for merge in s_root.findall('.//main:mergeCells/main:mergeCell', ns):
        ref = merge.attrib.get('ref', '')
        # e.g. B2:E2
        merges[ref.split(':')[0]] = ref
        
    print(f'Total merged ranges: {len(merges)}')
    
    # Let's inspect rows 1 to 70 and print non-empty rows
    grid = {}
    for row in s_root.findall('.//main:row', ns):
        r_idx = int(row.attrib.get('r', 0))
        grid[r_idx] = {}
        for c in row.findall('.//main:c', ns):
            coord = c.attrib.get('r', '')
            t = c.attrib.get('t', '')
            v = c.find('main:v', ns)
            val = v.text if v is not None else ''
            if t == 's' and val.isdigit():
                val = shared_strings[int(val)]
            grid[r_idx][coord] = val

    # Print summary of important regions
    for r in range(1, 65):
        cells = [f'{c}:{v}' for c, v in grid.get(r, {}).items() if v]
        if cells:
            print(f'R{r:2d}:', ' | '.join(cells[:10]))
