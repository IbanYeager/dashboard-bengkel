import zipfile
import xml.etree.ElementTree as ET

charts_to_check = ['chart19.xml', 'chart23.xml', 'chart24.xml', 'chart25.xml', 'chart26.xml', 'chart30.xml']

with zipfile.ZipFile('DASH KIARACONDONG 24-26.xlsx', 'r') as z:
    for c_name in charts_to_check:
        path = f'xl/charts/{c_name}'
        if path in z.namelist():
            print(f"\n=== {c_name} ===")
            content = z.read(path)
            root = ET.fromstring(content)
            
            # Title
            title_nodes = root.findall('.//{http://schemas.openxmlformats.org/drawingml/2006/chart}title//{http://schemas.openxmlformats.org/drawingml/2006/main}t')
            title = ''.join([t.text for t in title_nodes if t.text])
            print(f"Title: {title}")
            
            # Series
            for ser in root.findall('.//{http://schemas.openxmlformats.org/drawingml/2006/chart}ser'):
                ser_title = ''.join([t.text for t in ser.findall('.//{http://schemas.openxmlformats.org/drawingml/2006/chart}tx//{http://schemas.openxmlformats.org/drawingml/2006/main}t') if t.text])
                if not ser_title:
                    ser_title = ''.join([v.text for v in ser.findall('.//{http://schemas.openxmlformats.org/drawingml/2006/chart}tx//{http://schemas.openxmlformats.org/drawingml/2006/chart}v') if v.text])
                
                # Categories
                cat_vals = [v.text for v in ser.findall('.//{http://schemas.openxmlformats.org/drawingml/2006/chart}cat//{http://schemas.openxmlformats.org/drawingml/2006/chart}v') if v.text]
                # Values
                num_vals = [v.text for v in ser.findall('.//{http://schemas.openxmlformats.org/drawingml/2006/chart}val//{http://schemas.openxmlformats.org/drawingml/2006/chart}v') if v.text]
                
                print(f"  Series: '{ser_title}'")
                print(f"    Categories ({len(cat_vals)}): {cat_vals}")
                print(f"    Values     ({len(num_vals)}): {num_vals}")
