import zipfile
import xml.etree.ElementTree as ET

def search_charts_in_file(filename):
    print(f"\n=== Searching charts in {filename} ===")
    with zipfile.ZipFile(filename, 'r') as z:
        for name in z.namelist():
            if name.startswith('xl/charts/chart') and name.endswith('.xml'):
                content = z.read(name)
                root = ET.fromstring(content)
                title_nodes = root.findall('.//{http://schemas.openxmlformats.org/drawingml/2006/chart}title//{http://schemas.openxmlformats.org/drawingml/2006/main}t')
                title = ''.join([t.text for t in title_nodes if t.text])
                
                # Check for values like 252, 80, 133, 40, 62
                v_nodes = [v.text for v in root.findall('.//{http://schemas.openxmlformats.org/drawingml/2006/chart}v') if v.text]
                if any(num in v_nodes for num in ['252', '80', '133', '62', '271', '318', '0.471', '0.676']):
                    print(f"MATCH IN {name}! Title='{title}'")
                    print(f"  Values: {v_nodes[:15]}")

search_charts_in_file('Dashboard AFS Kiaracondong-start 2024.xlsx')
search_charts_in_file('DASH KIARACONDONG 24-26.xlsx')
