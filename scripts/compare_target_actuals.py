import zipfile
import xml.etree.ElementTree as ET
import json
import sqlite3

# 1. Inspect TARGET in DASH KIARACONDONG 24-26.xlsx
print("=== 1. DASH KIARACONDONG 24-26.xlsx -> TARGET ===")
with zipfile.ZipFile('DASH KIARACONDONG 24-26.xlsx', 'r') as z:
    ss_xml = z.read('xl/sharedStrings.xml')
    ss_root = ET.fromstring(ss_xml)
    ns = {'main': 'http://schemas.openxmlformats.org/spreadsheetml/2006/main'}
    shared_strings = []
    for si in ss_root.findall('main:si', ns):
        text_parts = [t_el.text for t_el in si.findall('.//main:t', ns) if t_el.text]
        shared_strings.append(''.join(text_parts))
    
    sheet_xml = z.read('xl/worksheets/sheet3.xml')
    sheet_root = ET.fromstring(sheet_xml)
    
    target_data = {}
    for row in sheet_root.findall('main:sheetData/main:row', ns):
        r_num = int(row.attrib.get('r', 0))
        cells = {}
        for c in row.findall('main:c', ns):
            ref = c.attrib.get('r')
            t = c.attrib.get('t')
            v = c.find('main:v', ns)
            val = v.text if v is not None else ''
            if t == 's' and val.isdigit():
                val = shared_strings[int(val)]
            cells[ref] = val
        target_data[r_num] = cells

# Print row labels
for r in [5, 10, 12, 19, 21, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41]:
    lbl = target_data.get(r, {}).get('A' + str(r), '')
    print(f"Row {r:2d} label: '{lbl}'")

# Check 2026 columns: AF=Jan, AG=Feb, AH=Mar, AI=Apr, AJ=May, AK=Jun, AL=Jul, AM=Aug, AN=Sep
cols_2026 = [('Jan', 'AF'), ('Feb', 'AG'), ('Mar', 'AH'), ('Apr', 'AI'), ('Mei', 'AJ'), ('Jun', 'AK'), ('Jul', 'AL'), ('Agu', 'AM'), ('Sep', 'AN')]
print("\n--- 2026 Data in TARGET Sheet ---")
print(f"{'Bulan':<6} | {'Row 5 CPUS':<12} | {'Row 12 RevTot':<15} | {'Row 33 KirconTot':<18} | {'Row 29 Jasa':<12} | {'Row 30 Parts':<12}")
for m, col in cols_2026:
    cpus_val = target_data.get(5, {}).get(col + '5', '')
    r12_val = target_data.get(12, {}).get(col + '12', '')
    r33_val = target_data.get(33, {}).get(col + '33', '')
    r29_val = target_data.get(29, {}).get(col + '29', '')
    r30_val = target_data.get(30, {}).get(col + '30', '')
    r12_m = float(r12_val)/1e6 if r12_val and r12_val != '' else 0
    r33_m = float(r33_val)/1e6 if r33_val and r33_val != '' else 0
    print(f"{m:<6} | {cpus_val:<12} | {r12_m:>12.1f} Jt | {r33_m:>15.1f} Jt | {r29_val:<12} | {r30_val:<12}")

# 2. Check Dashboard AFS TARGET sheet
print("\n=== 2. Dashboard AFS Kiaracondong-start 2024.xlsx -> TARGET ===")
with zipfile.ZipFile('Dashboard AFS Kiaracondong-start 2024.xlsx', 'r') as z:
    wb_xml = z.read('xl/workbook.xml')
    wb_root = ET.fromstring(wb_xml)
    target_rid = None
    for s in wb_root.findall('main:sheets/main:sheet', ns):
        if s.attrib.get('name') == 'TARGET':
            target_rid = s.attrib.get('{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id')
            break
    
    rels_xml = z.read('xl/_rels/workbook.xml.rels')
    rels_root = ET.fromstring(rels_xml)
    target_file = None
    for r in rels_root.findall('{http://schemas.openxmlformats.org/package/2006/relationships}Relationship'):
        if r.attrib.get('Id') == target_rid:
            target_file = 'xl/' + r.attrib.get('Target')
            break
    
    print("AFS Target file:", target_file)
    ss_xml = z.read('xl/sharedStrings.xml')
    ss_root = ET.fromstring(ss_xml)
    shared_strings_afs = []
    for si in ss_root.findall('main:si', ns):
        text_parts = [t_el.text for t_el in si.findall('.//main:t', ns) if t_el.text]
        shared_strings_afs.append(''.join(text_parts))
    
    sheet_xml = z.read(target_file)
    sheet_root = ET.fromstring(sheet_xml)
    for row in sheet_root.findall('main:sheetData/main:row', ns):
        r_num = int(row.attrib.get('r', 0))
        if r_num in [1, 2, 5, 10, 12, 28, 29, 30, 31, 32, 33]:
            cells = {}
            for c in row.findall('main:c', ns):
                ref = c.attrib.get('r')
                t = c.attrib.get('t')
                v = c.find('main:v', ns)
                val = v.text if v is not None else ''
                if t == 's' and val.isdigit():
                    val = shared_strings_afs[int(val)]
                cells[ref] = val
            print(f"AFS Row {r_num:2d}: {list(cells.items())[:5]}")
