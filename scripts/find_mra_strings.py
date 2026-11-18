import zipfile
import xml.etree.ElementTree as ET

for fname in ['DASH KIARACONDONG 24-26(1).xlsx', 'Dashboard AFS Kiaracondong-start 2024.xlsx']:
    print(f"\n--- Checking {fname} ---")
    with zipfile.ZipFile(fname) as z:
        ss_xml = z.read('xl/sharedStrings.xml')
        root_ss = ET.fromstring(ss_xml)
        for i, si in enumerate(root_ss.findall('{http://schemas.openxmlformats.org/spreadsheetml/2006/main}si')):
            text = ''.join([t.text for t in si.findall('.//{http://schemas.openxmlformats.org/spreadsheetml/2006/main}t') if t.text])
            if text in ['RANIH', 'RANI', 'NURI', 'PIC MRA', 'JUDGEMENT CUST', 'Cust Prospecting Type', 'Sequence Service SBE (Month)', 'DUE DATE NEXT SERVICE']:
                print(f"  String {i}: '{text}'")
            elif any(k in text for k in ['PIC MRA', 'DUE DATE NEXT SERVICE', 'Sequence Service SBE']):
                print(f"  String {i} (contains): '{text}'")
