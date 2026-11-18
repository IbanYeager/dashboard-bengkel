import zipfile
import xml.etree.ElementTree as ET

with zipfile.ZipFile('DASH KIARACONDONG 24-26.xlsx', 'r') as z:
    with z.open('xl/worksheets/sheet3.xml') as f:
        for event, elem in ET.iterparse(f, events=('end',)):
            if elem.tag.endswith('c'):
                ref = elem.attrib.get('r', '')
                if ref.startswith('BF') and int(ref[2:]) > 20000:
                    f_el = elem.find('{http://schemas.openxmlformats.org/spreadsheetml/2006/main}f')
                    v_el = elem.find('{http://schemas.openxmlformats.org/spreadsheetml/2006/main}v')
                    formula = f_el.text if f_el is not None else ''
                    val = v_el.text if v_el is not None else ''
                    print(f"Cell {ref}: formula = '{formula}', value = '{val}'")
                    break
            elem.clear()
