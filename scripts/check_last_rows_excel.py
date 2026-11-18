import zipfile
import xml.etree.ElementTree as ET

fpath = 'DASH KIARACONDONG 24-26.xlsx'
with zipfile.ZipFile(fpath, 'r') as z:
    wb = ET.fromstring(z.read('xl/workbook.xml'))
    rels = ET.fromstring(z.read('xl/_rels/workbook.xml.rels'))
    rel_map = {r.attrib['Id']: r.attrib['Target'] for r in rels.findall('{http://schemas.openxmlformats.org/package/2006/relationships}Relationship')}
    sheets = {s.attrib.get('name').strip().lower(): 'xl/' + rel_map[s.attrib.get('{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id')].lstrip('/') for s in wb.findall('{http://schemas.openxmlformats.org/spreadsheetml/2006/main}sheets/{http://schemas.openxmlformats.org/spreadsheetml/2006/main}sheet')}
    
    pkb_sheet = sheets.get('input pkb')
    print("PKB sheet path in zip:", pkb_sheet)
    
    # Read the last 20 rows of the sheet
    # We can get max row r
    row_count = 0
    last_rows = []
    with z.open(pkb_sheet) as sf:
        for event, elem in ET.iterparse(sf, events=('end',)):
            if elem.tag.endswith('row'):
                row_count += 1
                r = int(elem.attrib.get('r', 0))
                # collect last 10 rows
                cols = {}
                for c in elem.findall('{http://schemas.openxmlformats.org/spreadsheetml/2006/main}c'):
                    ref = c.attrib.get('r')
                    col = ''.join([ch for ch in ref if ch.isalpha()])
                    v = c.find('{http://schemas.openxmlformats.org/spreadsheetml/2006/main}v')
                    cols[col] = (c.attrib.get('t'), v.text if v is not None else '')
                last_rows.append((r, cols))
                if len(last_rows) > 10:
                    last_rows.pop(0)
                elem.clear()
    
    print(f"Total rows in sheet: {row_count}")
    print("Last row r:", last_rows[-1][0] if last_rows else None)
    print("Sample last row cols:")
    for r, cols in last_rows[-3:]:
        print(f"Row {r}: A={cols.get('A')}, B={cols.get('B')}, C={cols.get('C')}, K={cols.get('K')}, M={cols.get('M')}")
