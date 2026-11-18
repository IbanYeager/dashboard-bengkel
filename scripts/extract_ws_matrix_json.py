import zipfile
import xml.etree.ElementTree as ET
import re
import json

with zipfile.ZipFile('KPI Dashboard Kabeng GR-ags.xlsx') as z:
    shared_strings = []
    if 'xl/sharedStrings.xml' in z.namelist():
        ss_tree = ET.fromstring(z.read('xl/sharedStrings.xml'))
        for si in ss_tree.findall('{http://schemas.openxmlformats.org/spreadsheetml/2006/main}si'):
            t = ''.join([node.text for node in si.iter() if node.text])
            shared_strings.append(t)

    wb_tree = ET.fromstring(z.read('xl/workbook.xml'))
    rels_tree = ET.fromstring(z.read('xl/_rels/workbook.xml.rels'))
    rel_map = {r.attrib['Id']: r.attrib['Target'] for r in rels_tree}

    for sheet in wb_tree.findall('{http://schemas.openxmlformats.org/spreadsheetml/2006/main}sheets/{http://schemas.openxmlformats.org/spreadsheetml/2006/main}sheet'):
        if sheet.attrib['name'] == 'Dash update':
            r_id = sheet.attrib['{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id']
            target_sheet = 'xl/' + rel_map[r_id] if not rel_map[r_id].startswith('xl/') else rel_map[r_id]
            break

    sheet_xml = z.read(target_sheet)
    s_tree = ET.fromstring(sheet_xml)

    rows_dict = {}
    for r in s_tree.findall('{http://schemas.openxmlformats.org/spreadsheetml/2006/main}sheetData/{http://schemas.openxmlformats.org/spreadsheetml/2006/main}row'):
        r_num = int(r.attrib['r'])
        cells = {}
        for c in r.findall('{http://schemas.openxmlformats.org/spreadsheetml/2006/main}c'):
            ref = c.attrib['r']
            m = re.match(r'([A-Z]+)(\d+)', ref)
            col_letters = m.group(1)
            t = c.attrib.get('t')
            v_el = c.find('{http://schemas.openxmlformats.org/spreadsheetml/2006/main}v')
            val = ''
            if v_el is not None and v_el.text:
                val = v_el.text
                if t == 's':
                    val = shared_strings[int(val)]
            cells[col_letters] = val
        rows_dict[r_num] = cells

    # Export structured JSON
    months_cols = ['E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P']
    months_names = ['Januari', 'Februari', 'Maret', 'April', 'Mei', 'Juni', 'Juli', 'Agustus', 'September', 'Oktober', 'November', 'Desember']
    
    hari_kerja = [float(rows_dict[5].get(c, 0) or 0) for c in months_cols]
    total_hari_kerja = float(rows_dict[5].get('Q', 0) or 0)

    matrix_rows = []
    for r_num in range(7, 53):
        cells = rows_dict.get(r_num, {})
        num = cells.get('B', '')
        name = cells.get('C', '').strip()
        satuan = cells.get('D', '').strip()
        
        # Monthly values
        m_vals = []
        for c in months_cols:
            raw_v = cells.get(c, '')
            if raw_v == '' or raw_v == '-' or raw_v == '_':
                m_vals.append(None)
            else:
                try:
                    m_vals.append(float(raw_v))
                except ValueError:
                    m_vals.append(raw_v)
                    
        total_v = cells.get('Q', '')
        if total_v != '' and total_v != '-' and total_v != '_':
            try:
                total_v = float(total_v)
            except ValueError:
                pass
        else:
            total_v = None

        nas_v = cells.get('S', '')
        if nas_v != '' and nas_v != '-' and nas_v != '_':
            try:
                nas_v = float(nas_v)
            except ValueError:
                pass
        else:
            nas_v = None

        target_v = cells.get('U', '')
        if target_v != '' and target_v != '-' and target_v != '_':
            try:
                target_v = float(target_v)
            except ValueError:
                pass
        else:
            target_v = None

        matrix_rows.append({
            'no': num,
            'kpi': name,
            'satuan': satuan,
            'months': m_vals,
            'total': total_v,
            'nas_tunas': nas_v,
            'target': target_v
        })

    result = {
        'branch': 'KIARA CONDONG',
        'year': 2026,
        'hari_kerja': {
            'months': hari_kerja,
            'total': total_hari_kerja
        },
        'rows': matrix_rows
    }

    with open('scripts/extracted_ws_matrix.json', 'w', encoding='utf-8') as f:
        json.dump(result, f, indent=2, ensure_ascii=False)

    print("Saved scripts/extracted_ws_matrix.json successfully. Total rows:", len(matrix_rows))
