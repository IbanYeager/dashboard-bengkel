import zipfile
import xml.etree.ElementTree as ET
import re
from collections import Counter

def check_excel_july(filename):
    print(f"\nChecking {filename}...")
    try:
        with zipfile.ZipFile(filename, 'r') as z:
            # Read shared strings
            ss = []
            if 'xl/sharedStrings.xml' in z.namelist():
                tree = ET.fromstring(z.read('xl/sharedStrings.xml'))
                for si in tree.findall('{http://schemas.openxmlformats.org/spreadsheetml/2006/main}si'):
                    t = ''.join([n.text for n in si.iter() if n.text])
                    ss.append(t)
            
            wb = ET.fromstring(z.read('xl/workbook.xml'))
            rels = ET.fromstring(z.read('xl/_rels/workbook.xml.rels'))
            rel_map = {r.attrib['Id']: r.attrib['Target'] for r in rels}
            
            pkb_target = None
            for s in wb.findall('{http://schemas.openxmlformats.org/spreadsheetml/2006/main}sheets/{http://schemas.openxmlformats.org/spreadsheetml/2006/main}sheet'):
                name = s.attrib.get('name', '')
                if 'pkb' in name.lower() or 'input' in name.lower():
                    rId = s.attrib['{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id']
                    target = rel_map[rId]
                    pkb_target = 'xl/' + target if not target.startswith('xl/') else target
                    print(f"Found PKB sheet: '{name}' -> {pkb_target}")
                    break
            
            if not pkb_target:
                print("No PKB sheet found!")
                return
            
            # Count 2026 months in PKB sheet
            sheet_xml = z.read(pkb_target)
            s_tree = ET.fromstring(sheet_xml)
            
            # Find column letters for Year, Month, etc. from Row 1
            # Usually row 1 has headers
            header_map = {}
            for c in s_tree.findall('{http://schemas.openxmlformats.org/spreadsheetml/2006/main}sheetData/{http://schemas.openxmlformats.org/spreadsheetml/2006/main}row[1]/{http://schemas.openxmlformats.org/spreadsheetml/2006/main}c'):
                ref = c.attrib['r']
                col = re.match(r'([A-Z]+)', ref).group(1)
                t = c.attrib.get('t')
                v_el = c.find('{http://schemas.openxmlformats.org/spreadsheetml/2006/main}v')
                val = ''
                if v_el is not None and v_el.text:
                    val = v_el.text
                    if t == 's': val = ss[int(val)]
                header_map[col] = val.strip().lower()
            
            print(f"Headers sample: {list(header_map.items())[:15]}")
            
            # Let's count rows per year & month
            year_col = None
            month_col = None
            for col, h in header_map.items():
                if h in ['tahun', 'year', 'thn']: year_col = col
                if h in ['bulan', 'month', 'bln']: month_col = col
            
            print(f"year_col={year_col}, month_col={month_col}")
            
            counter = Counter()
            for r in s_tree.findall('{http://schemas.openxmlformats.org/spreadsheetml/2006/main}sheetData/{http://schemas.openxmlformats.org/spreadsheetml/2006/main}row'):
                r_num = int(r.attrib['r'])
                if r_num == 1: continue
                cells = {}
                for c in r.findall('{http://schemas.openxmlformats.org/spreadsheetml/2006/main}c'):
                    ref = c.attrib['r']
                    col = re.match(r'([A-Z]+)', ref).group(1)
                    if col in [year_col, month_col]:
                        t = c.attrib.get('t')
                        v_el = c.find('{http://schemas.openxmlformats.org/spreadsheetml/2006/main}v')
                        val = ''
                        if v_el is not None and v_el.text:
                            val = v_el.text
                            if t == 's': val = ss[int(val)]
                        cells[col] = val.strip()
                
                yr = cells.get(year_col, '')
                mo = cells.get(month_col, '')
                if yr in ['2026', '2026.0']:
                    counter[mo] += 1
            
            print(f"2026 Month counts in {filename}:")
            for m, cnt in sorted(counter.items()):
                print(f"  {m:15}: {cnt}")
                
    except Exception as e:
        print(f"Error checking {filename}: {e}")

check_excel_july('DASH KIARACONDONG 24-26.backup.xlsx')
check_excel_july('DASH KIARACONDONG 24-26(1).xlsx')
check_excel_july('DASH KIARACONDONG 24-26.xlsx')
