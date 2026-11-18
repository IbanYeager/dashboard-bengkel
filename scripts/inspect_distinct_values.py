import zipfile
import xml.etree.ElementTree as ET
from collections import Counter

def get_shared_strings(z):
    shared_strings = []
    if 'xl/sharedStrings.xml' in z.namelist():
        with z.open('xl/sharedStrings.xml') as f:
            for event, elem in ET.iterparse(f, events=('end',)):
                if elem.tag.endswith('si'):
                    text = ''.join([t.text for t in elem.iter() if t.tag.endswith('t') and t.text])
                    shared_strings.append(text)
                    elem.clear()
    return shared_strings

with zipfile.ZipFile('DASH KIARACONDONG 24-26.xlsx', 'r') as z:
    wb_root = ET.fromstring(z.read('xl/workbook.xml'))
    rels_root = ET.fromstring(z.read('xl/_rels/workbook.xml.rels'))
    rel_map = {r.attrib['Id']: r.attrib['Target'] for r in rels_root.findall('{http://schemas.openxmlformats.org/package/2006/relationships}Relationship')}
    sheet_files = {s.attrib.get('name'): 'xl/' + rel_map[s.attrib.get('{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id')].lstrip('/') for s in wb_root.findall('{http://schemas.openxmlformats.org/spreadsheetml/2006/main}sheets/{http://schemas.openxmlformats.org/spreadsheetml/2006/main}sheet')}
    
    shared_strings = get_shared_strings(z)
    
    counts = {
        'ring_area': Counter(),
        'type_cust': Counter(),
        'lookup_job': Counter(),
        'model_segment': Counter(),
        'fleet_retail': Counter(),
        'type_service': Counter(),
        'type_ue': Counter()
    }
    
    with z.open(sheet_files['INPUT PKB']) as sf:
        for event, elem in ET.iterparse(sf, events=('end',)):
            if elem.tag.endswith('row'):
                r = elem.attrib.get('r')
                if r != '1':
                    c_dict = {}
                    for c in elem.findall('{http://schemas.openxmlformats.org/spreadsheetml/2006/main}c'):
                        ref = c.attrib.get('r')
                        col = ''.join([ch for ch in ref if ch.isalpha()])
                        t = c.attrib.get('t')
                        v = c.find('{http://schemas.openxmlformats.org/spreadsheetml/2006/main}v')
                        val = ""
                        if v is not None and v.text:
                            val = shared_strings[int(v.text)] if t == 's' and int(v.text) < len(shared_strings) else v.text
                        c_dict[col] = val.strip()
                    
                    counts['ring_area'][c_dict.get('BC', '')] += 1
                    counts['type_cust'][c_dict.get('AV', '')] += 1
                    counts['lookup_job'][c_dict.get('H', '')] += 1
                    counts['model_segment'][c_dict.get('BD', '')] += 1
                    counts['fleet_retail'][c_dict.get('AO', '')] += 1
                    counts['type_service'][c_dict.get('AS', '')] += 1
                    counts['type_ue'][c_dict.get('AR', '')] += 1
                elem.clear()

for k, v in counts.items():
    print(f"\n=== {k.upper()} ===")
    for val, count in v.most_common(20):
        print(f"  {repr(val)}: {count}")
