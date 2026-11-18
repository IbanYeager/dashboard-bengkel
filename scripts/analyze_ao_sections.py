import zipfile
import xml.etree.ElementTree as ET
import re

with zipfile.ZipFile('data/ao_report.xlsx') as z:
    shared_strings = []
    ns = {'main': 'http://schemas.openxmlformats.org/spreadsheetml/2006/main'}
    if 'xl/sharedStrings.xml' in z.namelist():
        ss_root = ET.fromstring(z.read('xl/sharedStrings.xml'))
        for si in ss_root.findall('.//main:si', ns):
            shared_strings.append("".join(t.text or "" for t in si.findall('.//main:t', ns)))

    s_root = ET.fromstring(z.read('xl/worksheets/sheet2.xml'))

    def col2num(col_str):
        num = 0
        for ch in col_str: num = num * 26 + (ord(ch) - ord('A') + 1)
        return num
    def num2col(num):
        res = ""
        while num > 0:
            num, rem = divmod(num - 1, 26)
            res = chr(ord('A') + rem) + res
        return res

    cells = {}
    for row in s_root.findall('.//main:row', ns):
        r_num = int(row.attrib.get('r'))
        for c in row.findall('.//main:c', ns):
            coord = c.attrib.get('r')
            m = re.match(r'([A-Z]+)(\d+)', coord)
            if not m: continue
            col_str, row_str = m.groups()
            c_num = col2num(col_str)
            t_type = c.attrib.get('t', '')
            v_elem = c.find('main:v', ns)
            val = v_elem.text if v_elem is not None else ""
            if t_type == 's' and val: val = shared_strings[int(val)]
            cells[(r_num, c_num)] = val

    merges = [m.attrib.get('ref') for m in s_root.findall('.//main:mergeCell', ns)]

    with open('data/ao_sections_analysis.txt', 'w', encoding='utf-8') as out:
        out.write("=== DETAILED BREAKDOWN OF DASHBOARD AO ===\n\n")
        
        out.write("--- HEADER BLOCK (Rows 1 to 4) ---\n")
        for r in range(1, 5):
            line = [f"{num2col(c)}{r}: '{cells.get((r,c), '')}'" for c in range(1, 26) if cells.get((r,c))]
            out.write(" | ".join(line) + "\n")
            
        out.write("\n--- KPI TREE (Columns B to E, Rows 5 to 45) ---\n")
        for r in range(5, 46):
            line = [f"{num2col(c)}{r}: '{cells.get((r,c), '')}'" for c in range(2, 6) if cells.get((r,c))]
            if line: out.write(f"R{r:2d}: " + " | ".join(line) + "\n")
            
        out.write("\n--- SUMMARY KPI CALLOUT CARDS (Column O, Rows 4 to 33) ---\n")
        for r in range(4, 34):
            v = cells.get((r, 15), '')
            v_title = cells.get((r, 14), '') or cells.get((r-1, 15), '')
            if v: out.write(f"R{r:2d} (Col O): '{v}' (Context: '{cells.get((r, 15), '')}')\n")

        out.write("\n--- WEEKLY MONITORING (Columns G to M, Rows 12 to 21) ---\n")
        for r in range(12, 22):
            line = [f"{num2col(c)}{r}: '{cells.get((r,c), '')}'" for c in range(7, 14) if cells.get((r,c))]
            if line: out.write(f"R{r:2d}: " + " | ".join(line) + "\n")

        out.write("\n--- BOOKING & NO-SHOW MONITORING (Columns G to O, Rows 47 to 66) ---\n")
        for r in range(47, 67):
            line = [f"{num2col(c)}{r}: '{cells.get((r,c), '')}'" for c in range(7, 16) if cells.get((r,c))]
            if line: out.write(f"R{r:2d}: " + " | ".join(line) + "\n")

        out.write("\n--- II. TCARE FUNNELING (Columns Q to X, Rows 5 to 21) ---\n")
        for r in range(5, 22):
            line = [f"{num2col(c)}{r}: '{cells.get((r,c), '')}'" for c in range(17, 25) if cells.get((r,c))]
            if line: out.write(f"R{r:2d}: " + " | ".join(line) + "\n")

        out.write("\n--- II. NON TCARE FUNNELING (Columns Q to X, Rows 26 to 42) ---\n")
        for r in range(26, 43):
            line = [f"{num2col(c)}{r}: '{cells.get((r,c), '')}'" for c in range(17, 25) if cells.get((r,c))]
            if line: out.write(f"R{r:2d}: " + " | ".join(line) + "\n")

        out.write("\n--- III. SBI TCARE / TCARE LIGHT (Columns Q to X, Rows 43 to 53) ---\n")
        for r in range(43, 54):
            line = [f"{num2col(c)}{r}: '{cells.get((r,c), '')}'" for c in range(17, 25) if cells.get((r,c))]
            if line: out.write(f"R{r:2d}: " + " | ".join(line) + "\n")

        out.write("\n--- IV. ACTION PLAN (Columns Q to X, Rows 54 to 68) ---\n")
        for r in range(54, 69):
            line = [f"{num2col(c)}{r}: '{cells.get((r,c), '')}'" for c in range(17, 25) if cells.get((r,c))]
            if line: out.write(f"R{r:2d}: " + " | ".join(line) + "\n")

    print("Sections analysis written to data/ao_sections_analysis.txt")
