import zipfile
import xml.etree.ElementTree as ET

wb_path = 'data/tcare_live.xlsx'
with zipfile.ZipFile(wb_path, 'r') as z:
    for c_id in [1, 2, 3, 4, 5, 6, 7, 12, 13]:
        cname = f"xl/charts/chart{c_id}.xml"
        ctree = ET.fromstring(z.read(cname))
        
        # Title
        title = ""
        for t in ctree.iter('{http://schemas.openxmlformats.org/drawingml/2006/main}t'):
            if t.text: title += t.text + " "
        title = title.strip()
        
        # Colors (srgbClr)
        colors = []
        for clr in ctree.iter('{http://schemas.openxmlformats.org/drawingml/2006/main}srgbClr'):
            colors.append(clr.attrib.get('val'))
            
        # Legend pos
        leg = ctree.find('.//{http://schemas.openxmlformats.org/drawingml/2006/chart}legendPos')
        leg_pos = leg.attrib.get('val') if leg is not None else 'none'
        
        # Data labels
        dLbls = ctree.find('.//{http://schemas.openxmlformats.org/drawingml/2006/chart}dLbls')
        has_labels = dLbls is not None
        
        print(f"Chart {c_id}: Title='{title}', Legend={leg_pos}, HasLabels={has_labels}, Colors={colors[:8]}")
