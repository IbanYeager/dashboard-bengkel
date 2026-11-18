import zipfile
import xml.etree.ElementTree as ET

def examine_charts(filename):
    print(f"=== CHARTS IN {filename} ===")
    with zipfile.ZipFile(filename, 'r') as z:
        for name in z.namelist():
            if name.startswith('xl/charts/chart') and name.endswith('.xml'):
                content = z.read(name)
                root = ET.fromstring(content)
                # Find chart title
                title_elem = root.findall('.//{http://schemas.openxmlformats.org/drawingml/2006/chart}title')
                title_text = ''
                if title_elem:
                    t_nodes = title_elem[0].findall('.//{http://schemas.openxmlformats.org/drawingml/2006/main}t')
                    title_text = ''.join([t.text for t in t_nodes if t.text])
                    if not title_text:
                        v_nodes = title_elem[0].findall('.//{http://schemas.openxmlformats.org/drawingml/2006/chart}v')
                        title_text = ''.join([v.text for v in v_nodes if v.text])
                # Find formula references f
                f_nodes = root.findall('.//{http://schemas.openxmlformats.org/drawingml/2006/chart}f')
                formulas = [f.text for f in f_nodes if f.text][:5]
                print(f"{name}: Title='{title_text}'")
                if formulas:
                    print(f"   Refs: {formulas}")

examine_charts('Dashboard AFS Kiaracondong-start 2024.xlsx')
examine_charts('DASH KIARACONDONG 24-26.xlsx')
