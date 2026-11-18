import zipfile
import xml.etree.ElementTree as ET

with zipfile.ZipFile('data/ao_report.xlsx') as z:
    xml = z.read('xl/drawings/drawing2.xml')
    root = ET.fromstring(xml)
    
    ns = {
        'xdr': 'http://schemas.openxmlformats.org/drawingml/2006/spreadsheetDrawing',
        'a': 'http://schemas.openxmlformats.org/drawingml/2006/main',
        'r': 'http://schemas.openxmlformats.org/officeDocument/2006/relationships'
    }
    
    anchors = root.findall('.//xdr:oneCellAnchor', ns)
    print(f"Total oneCellAnchors: {len(anchors)}")
    for i, anc in enumerate(anchors):
        f_col = anc.find('.//xdr:from/xdr:col', ns)
        f_row = anc.find('.//xdr:from/xdr:row', ns)
        from_pos = f"Col {f_col.text}, Row {f_row.text}" if f_col is not None else ""
        
        # text inside shape
        texts = [t.text for t in anc.findall('.//a:t', ns) if t.text]
        text_summary = " ".join(texts)
        
        # shape type
        sp = anc.find('.//xdr:sp', ns)
        prst = anc.find('.//a:prstGeom', ns)
        geom = prst.attrib.get('prst') if prst is not None else "unknown"
        
        print(f"Anchor {i+1}: at ({from_pos}) [geom: {geom}] -> text: '{text_summary}'")
