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

    # Let's extract the table
    header_row = rows_dict.get(6, {})
    months_cols = ['E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P']
    months_names = [header_row.get(c, '') for c in months_cols]
    total_col = 'Q'
    benchmark_col = 'S'
    target_col = 'U'

    print("Header months:", months_names)

    kpis = []
    for r_num in range(7, 53):
        cells = rows_dict.get(r_num, {})
        num = cells.get('B', '')
        name = cells.get('C', '')
        satuan = cells.get('D', '')
        monthly_values = [cells.get(c, '') for c in months_cols]
        total_val = cells.get(total_col, '')
        nas_val = cells.get(benchmark_col, '')
        target_val = cells.get(target_col, '')
        kpis.append({
            'row_num': r_num,
            'no': num,
            'kpi': name,
            'satuan': satuan,
            'months': monthly_values,
            'total': total_val,
            'nas_tunas': nas_val,
            'target': target_val
        })

    print(f"Extracted {len(kpis)} KPI rows.")
    for k in kpis:
        print(f"#{k['no']:2s} | {k['kpi']:35s} | Satuan: {k['satuan']:10s} | Jan:{k['months'][0][:8]} | Aug:{k['months'][7][:8]} | Total:{str(k['total'])[:10]} | Nas:{str(k['nas_tunas'])[:8]} | Target:{str(k['target'])[:8]}")
