import zipfile
import xml.etree.ElementTree as ET

with zipfile.ZipFile('data/ao_report.xlsx') as z:
    wb_xml = z.read('xl/workbook.xml')
    wb_root = ET.fromstring(wb_xml)
    ns = {'main': 'http://schemas.openxmlformats.org/spreadsheetml/2006/main'}
    
    # Styles
    styles_xml = z.read('xl/styles.xml')
    styles_root = ET.fromstring(styles_xml)
    
    # Fills
    fills = []
    for fill in styles_root.findall('.//main:fill', ns):
        pf = fill.find('main:patternFill', ns)
        if pf is not None:
            fg = pf.find('main:fgColor', ns)
            if fg is not None:
                rgb = fg.attrib.get('rgb') or fg.attrib.get('theme') or fg.attrib.get('indexed')
                fills.append(rgb)
            else:
                fills.append(None)
        else:
            fills.append(None)
            
    # Fonts
    fonts = []
    for f in styles_root.findall('.//main:font', ns):
        b = f.find('main:b', ns) is not None
        sz = f.find('main:sz', ns)
        sz_val = sz.attrib.get('val') if sz is not None else '11'
        col = f.find('main:color', ns)
        c_rgb = col.attrib.get('rgb') if col is not None else '000000'
        name_e = f.find('main:name', ns)
        font_name = name_e.attrib.get('val') if name_e is not None else 'Calibri'
        fonts.append({'bold': b, 'size': sz_val, 'color': c_rgb, 'name': font_name})
        
    # CellXfs
    cell_xfs = []
    for xf in styles_root.findall('.//main:cellXfs/main:xf', ns):
        fid = int(xf.attrib.get('fillId', 0))
        font_id = int(xf.attrib.get('fontId', 0))
        cell_xfs.append({'fillId': fid, 'fontId': font_id})

    # Shared strings
    shared_strings = []
    if 'xl/sharedStrings.xml' in z.namelist():
        ss_xml = z.read('xl/sharedStrings.xml')
        ss_root = ET.fromstring(ss_xml)
        for si in ss_root.findall('.//main:si', ns):
            t_elems = si.findall('.//main:t', ns)
            text = "".join(t.text or "" for t in t_elems)
            shared_strings.append(text)

    # Sheet 2
    s_xml = z.read('xl/worksheets/sheet2.xml')
    s_root = ET.fromstring(s_xml)
    
    # Merges
    merges = [m.attrib.get('ref') for m in s_root.findall('.//main:mergeCell', ns)]
    
    # Rows
    rows = {}
    for row in s_root.findall('.//main:row', ns):
        r_num = int(row.attrib.get('r'))
        row_cells = {}
        for c in row.findall('.//main:c', ns):
            coord = c.attrib.get('r')
            s_idx = int(c.attrib.get('s', 0))
            t_type = c.attrib.get('t', '')
            v_elem = c.find('main:v', ns)
            f_elem = c.find('main:f', ns)
            val = v_elem.text if v_elem is not None else None
            formula = f_elem.text if f_elem is not None else None
            if t_type == 's' and val is not None:
                val = shared_strings[int(val)]
                
            style_info = {}
            if s_idx < len(cell_xfs):
                xf = cell_xfs[s_idx]
                fill_val = fills[xf['fillId']] if xf['fillId'] < len(fills) else None
                font_val = fonts[xf['fontId']] if xf['fontId'] < len(fonts) else None
                style_info = {'fill': fill_val, 'font': font_val}
                
            row_cells[coord] = {'val': val, 'formula': formula, 'style': style_info}
        rows[r_num] = row_cells
        
    print(f"Loaded {len(rows)} rows with styles and formulas.")
    
    # Let's inspect rows 1 to 70 and print cleanly
    with open('data/dashboard_ao_layout_detail.txt', 'w', encoding='utf-8') as out:
        out.write(f"=== MERGED RANGES ({len(merges)}) ===\n")
        out.write(", ".join(merges) + "\n\n")
        out.write("=== ROWS 1 TO 70 ===\n")
        for r in range(1, 71):
            if r in rows:
                out.write(f"--- ROW {r} ---\n")
                for coord, data in sorted(rows[r].items()):
                    val_s = str(data['val']) if data['val'] is not None else ""
                    f_s = f" [FORMULA: ={data['formula']}]" if data['formula'] else ""
                    st_s = f" [FILL: {data['style'].get('fill')}, BOLD: {data['style'].get('font', {}).get('bold')}]"
                    out.write(f"  {coord:4s}: '{val_s}'{f_s}{st_s}\n")
                    
    print("Detail saved to data/dashboard_ao_layout_detail.txt")
