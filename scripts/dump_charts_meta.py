import zipfile
import xml.etree.ElementTree as ET

z = zipfile.ZipFile('data/tcare_live.xlsx')
for c_idx in range(1, 14):
    path = f'xl/charts/chart{c_idx}.xml'
    tree = ET.fromstring(z.read(path))
    title = ''.join([t.text for t in tree.findall('.//{http://schemas.openxmlformats.org/drawingml/2006/chart}title//{http://schemas.openxmlformats.org/drawingml/2006/main}t') if t.text])
    p_tags = [e.tag.split('}')[-1] for e in tree.findall('.//{http://schemas.openxmlformats.org/drawingml/2006/chart}plotArea/*') if 'Chart' in e.tag]
    
    # Formulas or references
    f_refs = [f.text for f in tree.findall('.//{http://schemas.openxmlformats.org/drawingml/2006/chart}f') if f.text]
    print(f'chart{c_idx}.xml | Title: "{title}" | Type: {p_tags} | Refs: {f_refs}')
