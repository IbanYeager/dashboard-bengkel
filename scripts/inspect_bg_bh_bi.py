import zipfile
import xml.etree.ElementTree as ET
from collections import Counter

filename = 'DASH KIARACONDONG 24-26.xlsx'
with zipfile.ZipFile(filename, 'r') as z:
    wb_tree = ET.fromstring(z.read('xl/workbook.xml'))
    rels_tree = ET.fromstring(z.read('xl/_rels/workbook.xml.rels'))
    rel_map = {r.attrib['Id']: r.attrib['Target'] for r in rels_tree.findall('{http://schemas.openxmlformats.org/package/2006/relationships}Relationship')}
    sheet_files = {s.attrib.get('name').strip().lower(): 'xl/' + rel_map[s.attrib.get('{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id')].lstrip('/') for s in wb_tree.findall('{http://schemas.openxmlformats.org/spreadsheetml/2006/main}sheets/{http://schemas.openxmlformats.org/spreadsheetml/2006/main}sheet')}

    ss_tree = ET.fromstring(z.read('xl/sharedStrings.xml'))
    shared_strings = []
    for si in ss_tree.findall('{http://schemas.openxmlformats.org/spreadsheetml/2006/main}si'):
        t = si.find('{http://schemas.openxmlformats.org/spreadsheetml/2006/main}t')
        if t is not None and t.text is not None:
            shared_strings.append(t.text)
        else:
            txt = ''.join([elem.text for elem in si.findall('.//{http://schemas.openxmlformats.org/spreadsheetml/2006/main}t') if elem.text])
            shared_strings.append(txt)

    sheet_path = sheet_files['input pkb']
    print(f"Reading sample rows of BG, BH, BI from {sheet_path}...")
    
    bg_vals = Counter()
    bh_vals = Counter()
    bi_vals = Counter()
    
    with z.open(sheet_path) as f:
        for event, elem in ET.iterparse(f, events=('end',)):
            if elem.tag.endswith('row'):
                r_idx = int(elem.attrib.get('r', 0))
                if r_idx > 1:
                    row_data = {}
                    for c in elem.findall('{http://schemas.openxmlformats.org/spreadsheetml/2006/main}c'):
                        ref = c.attrib.get('r')
                        col = ''.join([ch for ch in ref if ch.isalpha()])
                        if col in ['BG', 'BH', 'BI']:
                            t = c.attrib.get('t')
                            v = c.find('{http://schemas.openxmlformats.org/spreadsheetml/2006/main}v')
                            val = shared_strings[int(v.text)] if (t == 's' and v is not None and v.text) else (v.text if v is not None else '')
                            row_data[col] = val
                    bg_vals[row_data.get('BG', '')] += 1
                    bh_vals[row_data.get('BH', '')] += 1
                    bi_vals[row_data.get('BI', '')] += 1
                elem.clear()

print("BG (Range Ravenue):")
for k, v in bg_vals.most_common(10):
    print(f"  {k}: {v}")

print("\nBH (QTY GR):")
for k, v in bh_vals.most_common(10):
    print(f"  {k}: {v}")

print("\nBI (QTY SBE):")
for k, v in bi_vals.most_common(10):
    print(f"  {k}: {v}")
