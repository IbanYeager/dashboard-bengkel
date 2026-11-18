# remove openpyxl
import zipfile
import xml.etree.ElementTree as ET
import glob

# Check available excel files
excel_files = glob.glob('*.xlsx')
print("Excel files:", excel_files)

# Let's inspect the sheets in the primary file
fpath = 'DASH KIARACONDONG 24-26.xlsx'
if not fpath:
    fpath = 'DASH KIARACONDONG 24-26(1).xlsx'

print(f"Reading {fpath}...")
with zipfile.ZipFile(fpath, 'r') as z:
    wb_root = ET.fromstring(z.read('xl/workbook.xml'))
    rels_root = ET.fromstring(z.read('xl/_rels/workbook.xml.rels'))
    rel_map = {r.attrib['Id']: r.attrib['Target'] for r in rels_root.findall('{http://schemas.openxmlformats.org/package/2006/relationships}Relationship')}
    sheet_files = {s.attrib.get('name'): 'xl/' + rel_map[s.attrib.get('{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id')].lstrip('/') for s in wb_root.findall('{http://schemas.openxmlformats.org/spreadsheetml/2006/main}sheets/{http://schemas.openxmlformats.org/spreadsheetml/2006/main}sheet')}
    print("Sheets:", list(sheet_files.keys()))
