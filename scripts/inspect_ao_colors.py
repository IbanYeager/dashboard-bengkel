import zipfile
import xml.etree.ElementTree as ET

with zipfile.ZipFile('data/ao_report.xlsx') as z:
    styles_root = ET.fromstring(z.read('xl/styles.xml'))
    ns = {'main': 'http://schemas.openxmlformats.org/spreadsheetml/2006/main'}
    
    fills = []
    for fill in styles_root.findall('.//main:fill', ns):
        pf = fill.find('main:patternFill', ns)
        if pf is not None:
            fg = pf.find('main:fgColor', ns)
            if fg is not None:
                rgb = fg.attrib.get('rgb') or fg.attrib.get('theme') or fg.attrib.get('indexed')
                fills.append(rgb)
            else: fills.append(None)
        else: fills.append(None)
        
    cell_xfs = []
    for xf in styles_root.findall('.//main:cellXfs/main:xf', ns):
        fid = int(xf.attrib.get('fillId', 0))
        font_id = int(xf.attrib.get('fontId', 0))
        align = xf.find('main:alignment', ns)
        align_info = align.attrib if align is not None else {}
        cell_xfs.append({'fill': fills[fid] if fid < len(fills) else None, 'align': align_info})

    # Let's see what unique fills are used in Dashboard AO
    s_root = ET.fromstring(z.read('xl/worksheets/sheet2.xml'))
    s_fills = set()
    for row in s_root.findall('.//main:row', ns):
        for c in row.findall('.//main:c', ns):
            s_idx = int(c.attrib.get('s', 0))
            if s_idx < len(cell_xfs):
                f = cell_xfs[s_idx]['fill']
                if f: s_fills.add(f)
                
    print(f"Unique fills in Dashboard AO: {s_fills}")
