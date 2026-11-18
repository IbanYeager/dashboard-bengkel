import os
import zipfile
import xml.etree.ElementTree as ET
import re
import json

EXCEL_KABENG = 'KPI Dashboard Kabeng GR-ags.xlsx'
DATA_JSON = 'data/dashboard_data.json'

def extract():
    if not os.path.exists(EXCEL_KABENG):
        print(f"Error: {EXCEL_KABENG} not found.")
        return

    with zipfile.ZipFile(EXCEL_KABENG, 'r') as z:
        # 1. Read shared strings
        shared_strings = []
        if 'xl/sharedStrings.xml' in z.namelist():
            ss_tree = ET.fromstring(z.read('xl/sharedStrings.xml'))
            for si in ss_tree.findall('{http://schemas.openxmlformats.org/spreadsheetml/2006/main}si'):
                t = ''.join([node.text for node in si.iter() if node.text])
                shared_strings.append(t)

        wb_tree = ET.fromstring(z.read('xl/workbook.xml'))
        rels_tree = ET.fromstring(z.read('xl/_rels/workbook.xml.rels'))
        rel_map = {r.attrib['Id']: r.attrib['Target'] for r in rels_tree}

        # 2. Locate 'Dash update' sheet (Kiaracondong Dashboard)
        target_sheet = None
        sheets_list = wb_tree.findall('{http://schemas.openxmlformats.org/spreadsheetml/2006/main}sheets/{http://schemas.openxmlformats.org/spreadsheetml/2006/main}sheet')
        for sheet in sheets_list:
            s_name = sheet.attrib['name'].strip().lower()
            if s_name in ('dash update', 'dash_update', 'realisasi', 'kpi kabeng', 'ws matrix', 'matrix'):
                r_id = sheet.attrib['{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id']
                target_sheet = 'xl/' + rel_map[r_id] if not rel_map[r_id].startswith('xl/') else rel_map[r_id]
                break
        
        if not target_sheet:
            for sheet in sheets_list:
                s_name = sheet.attrib['name'].strip().lower()
                if 'dash' in s_name or 'kabeng' in s_name or 'kpi' in s_name or 'matrix' in s_name or 'realisasi' in s_name:
                    r_id = sheet.attrib['{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id']
                    target_sheet = 'xl/' + rel_map[r_id] if not rel_map[r_id].startswith('xl/') else rel_map[r_id]
                    break

        if not target_sheet and len(sheets_list) > 0:
            r_id = sheets_list[0].attrib['{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id']
            target_sheet = 'xl/' + rel_map[r_id] if not rel_map[r_id].startswith('xl/') else rel_map[r_id]

        sheet_xml = z.read(target_sheet)
        s_tree = ET.fromstring(sheet_xml)

        # 3. Parse cell values
        rows_dict = {}
        for r in s_tree.findall('{http://schemas.openxmlformats.org/spreadsheetml/2006/main}sheetData/{http://schemas.openxmlformats.org/spreadsheetml/2006/main}row'):
            r_num = int(r.attrib['r'])
            cells = {}
            for c in r.findall('{http://schemas.openxmlformats.org/spreadsheetml/2006/main}c'):
                ref = c.attrib['r']
                col_letters = re.match(r'([A-Z]+)', ref).group(1)
                t = c.attrib.get('t')
                v_el = c.find('{http://schemas.openxmlformats.org/spreadsheetml/2006/main}v')
                val = ''
                if v_el is not None and v_el.text:
                    val = v_el.text
                    if t == 's':
                        val = shared_strings[int(val)]
                cells[col_letters] = val
            rows_dict[r_num] = cells

        months_cols = ['E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P']
        
        # Row 5: Hari Kerja
        row5 = rows_dict.get(5, {})
        hari_kerja = []
        for c in months_cols:
            raw = row5.get(c, '')
            try:
                hari_kerja.append(float(raw) if raw else 0.0)
            except:
                hari_kerja.append(0.0)
        total_hari_kerja = float(row5.get('Q', 0) or 0)

        # Rows 7 to 52: 46 KPIs
        matrix_rows = []
        for r_num in range(7, 53):
            cells = rows_dict.get(r_num, {})
            num = cells.get('B', '').strip()
            name = cells.get('C', '').strip()
            satuan = cells.get('D', '').strip()

            if not name:
                continue

            m_vals = []
            for c in months_cols:
                raw_v = cells.get(c, '')
                if raw_v == '' or raw_v == '-' or raw_v == '_' or raw_v is None:
                    m_vals.append(None)
                else:
                    try:
                        m_vals.append(float(raw_v))
                    except ValueError:
                        m_vals.append(raw_v)

            total_v = cells.get('Q', '')
            if total_v != '' and total_v != '-' and total_v != '_' and total_v is not None:
                try:
                    total_v = float(total_v)
                except ValueError:
                    pass
            else:
                total_v = None

            nas_v = cells.get('S', '')
            if nas_v != '' and nas_v != '-' and nas_v != '_' and nas_v is not None:
                try:
                    nas_v = float(nas_v)
                except ValueError:
                    pass
            else:
                nas_v = None

            target_v = cells.get('U', '')
            if target_v != '' and target_v != '-' and target_v != '_' and target_v is not None:
                try:
                    target_v = float(target_v)
                except ValueError:
                    pass
            else:
                target_v = None

            # Category segmentation for clear visual grouping
            cat_group = 'VOLUME & SERVIS'
            if int(num) if num.isdigit() else 0 in range(1, 12):
                cat_group = 'VOLUME & SERVIS'
            elif int(num) if num.isdigit() else 0 in range(12, 22):
                cat_group = 'REVENUE & SALES/UNIT'
            elif int(num) if num.isdigit() else 0 in range(22, 32):
                cat_group = 'GROSS PROFIT (GP)'
            elif int(num) if num.isdigit() else 0 in range(32, 36):
                cat_group = 'OPEX & PROFITABILITY (PBT)'
            elif int(num) if num.isdigit() else 0 in range(36, 39):
                cat_group = 'KEPUASAN & RETENSI PELANGGAN'
            elif int(num) if num.isdigit() else 0 in range(39, 45):
                cat_group = 'PRODUKTIVITAS STALL, SA & MEKANIK'
            else:
                cat_group = 'KUALITAS & ABSORPTION'

            matrix_rows.append({
                'row_idx': r_num,
                'no': num,
                'kpi': name,
                'satuan': satuan,
                'category': cat_group,
                'months': m_vals,
                'total': total_v,
                'nas_tunas': nas_v,
                'target': target_v
            })

        kabeng_result = {
            'branch': 'KIARA CONDONG',
            'year': 2026,
            'source_file': EXCEL_KABENG,
            'sheet_name': 'Dash update',
            'hari_kerja': {
                'months': hari_kerja,
                'total': total_hari_kerja
            },
            'rows': matrix_rows
        }

        print(f"Extracted {len(matrix_rows)} Kabeng KPI rows for Kiaracondong.")

        # Update data/dashboard_data.json
        if os.path.exists(DATA_JSON):
            with open(DATA_JSON, 'r', encoding='utf-8') as f:
                dash_data = json.load(f)

            # Bridge September 2026 data from monthly_kpis if present
            sep_data = dash_data.get('monthly_kpis', {}).get('2026', {}).get('September', {})
            if sep_data:
                for row in matrix_rows:
                    no = str(row.get('no', ''))
                    if no == '1' and sep_data.get('ue_total'): row['months'][8] = sep_data.get('ue_total')
                    elif no == '2' and sep_data.get('cpus'): row['months'][8] = sep_data.get('cpus')
                    elif no == '5' and sep_data.get('sbe_count'): row['months'][8] = sep_data.get('sbe_count')
                    elif no == '7' and sep_data.get('tcare_count'): row['months'][8] = sep_data.get('tcare_count')
                    elif no == '8':
                        sbe_c = sep_data.get('sbe_count', 0)
                        tc_c = sep_data.get('tcare_count', 0)
                        if sbe_c > 0: row['months'][8] = round(tc_c / sbe_c, 3)
                    elif no == '9':
                        sbe_c = sep_data.get('sbe_count', 0)
                        tc_c = sep_data.get('tcare_count', 0)
                        if sbe_c > 0: row['months'][8] = round((sbe_c - tc_c) / sbe_c, 3)
                    elif no == '12' and sep_data.get('total_revenue'):
                        row['months'][8] = round(sep_data.get('total_revenue') / 1000.0, 3)
                    
                    nums = [v for v in row['months'] if isinstance(v, (int, float))]
                    if nums and no in ['1', '2', '5', '7', '12', '13', '14', '15', '16', '26', '34']:
                        row['total'] = round(sum(nums), 1)

            dash_data['ws_matrix_kabeng'] = kabeng_result
            # Also keep ws_matrix_excel updated with kabeng data for backwards compatibility
            dash_data['ws_matrix_excel'] = {
                '2026': matrix_rows,
                'kabeng': kabeng_result
            }

            with open(DATA_JSON, 'w', encoding='utf-8') as f:
                json.dump(dash_data, f, indent=2, ensure_ascii=False)

            print(f"Successfully integrated into {DATA_JSON}.")

if __name__ == '__main__':
    extract()
