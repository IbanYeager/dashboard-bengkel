import zipfile
import xml.etree.ElementTree as ET

z = zipfile.ZipFile('data/tcare_live.xlsx')

d2 = ET.fromstring(z.read('xl/drawings/drawing2.xml'))
ns = {'xdr': 'http://schemas.openxmlformats.org/drawingml/2006/spreadsheetDrawing',
      'a': 'http://schemas.openxmlformats.org/drawingml/2006/main',
      'c': 'http://schemas.openxmlformats.org/drawingml/2006/chart'}

rels = {}
for r in ET.fromstring(z.read('xl/drawings/_rels/drawing2.xml.rels')):
    rels[r.attrib['Id']] = r.attrib['Target']

anchors = d2.findall('.//xdr:oneCellAnchor', ns)
print(f'Total oneCellAnchors in drawing2: {len(anchors)}')

for i, anchor in enumerate(anchors):
    from_row = anchor.find('xdr:from/xdr:row', ns).text
    from_col = anchor.find('xdr:from/xdr:col', ns).text
    
    chart_elem = anchor.find('.//c:chart', ns)
    pic_elem = anchor.find('.//xdr:pic', ns)
    
    info = f'Anchor {i+1}: from (Row {int(from_row)+1}, Col {int(from_col)+1})'
    
    if chart_elem is not None:
        r_id = chart_elem.attrib['{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id']
        target = rels.get(r_id, '')
        c_path = 'xl/charts/' + target.split('/')[-1]
        try:
            c_tree = ET.fromstring(z.read(c_path))
            title_text = ''.join([t.text for t in c_tree.findall('.//c:title//a:t', ns) if t.text])
            plot_tags = [e.tag.split('}')[-1] for e in c_tree.findall('.//c:plotArea/*', ns) if 'Chart' in e.tag]
            
            # Series names and categories
            ser_info = []
            for s in c_tree.findall('.//c:ser', ns):
                tx = ''.join([t.text for t in s.findall('.//c:tx//c:v', ns) if t.text])
                cat_vals = [t.text for t in s.findall('.//c:cat//c:v', ns) if t.text]
                num_vals = [t.text for t in s.findall('.//c:val//c:v', ns) if t.text]
                ser_info.append({'name': tx, 'cats': cat_vals, 'vals': num_vals})
                
            info += f' -> CHART: {target} | Title: "{title_text}" | Type: {plot_tags}\n     Series: {ser_info}'
        except Exception as e:
            info += f' -> CHART: {target} (err: {e})'
    elif pic_elem is not None:
        blip = pic_elem.find('.//a:blip', ns)
        if blip is not None:
            r_id = blip.attrib.get('{http://schemas.openxmlformats.org/officeDocument/2006/relationships}embed', '')
            info += f' -> PIC: {rels.get(r_id, "")}'
    print(info)
