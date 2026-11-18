import zipfile
import xml.etree.ElementTree as ET

with zipfile.ZipFile('data/ao_report.xlsx') as z:
    shared_strings = []
    ns = {'main': 'http://schemas.openxmlformats.org/spreadsheetml/2006/main'}
    if 'xl/sharedStrings.xml' in z.namelist():
        ss_root = ET.fromstring(z.read('xl/sharedStrings.xml'))
        for si in ss_root.findall('.//main:si', ns):
            shared_strings.append("".join(t.text or "" for t in si.findall('.//main:t', ns)))

    def inspect_sheet(sheet_file, name):
        s_root = ET.fromstring(z.read(sheet_file))
        rows = s_root.findall('.//main:row', ns)
        print(f"\n--- {name} ({sheet_file}): {len(rows)} rows ---")
        for r in rows[:15]:
            r_num = r.attrib.get('r')
            cells = []
            for c in r.findall('.//main:c', ns):
                coord = c.attrib.get('r')
                t_type = c.attrib.get('t', '')
                v_elem = c.find('main:v', ns)
                val = v_elem.text if v_elem is not None else ""
                if t_type == 's' and val: val = shared_strings[int(val)]
                if val: cells.append(f"{coord}:{val}")
            if cells:
                print(f"R{r_num}: " + " | ".join(cells[:8]))

    inspect_sheet('xl/worksheets/sheet4.xml', 'Weekly Monitoring')
    inspect_sheet('xl/worksheets/sheet5.xml', 'Daily Input')
    inspect_sheet('xl/worksheets/sheet1.xml', 'KPI Tree Setting')
