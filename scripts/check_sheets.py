import zipfile
import xml.etree.ElementTree as ET

wb_path = r"c:\laragon\www\dashboard_bengkel\DASH KIARACONDONG 24-26.xlsx"

# Fast inspection using zipfile
with zipfile.ZipFile(wb_path, 'r') as z:
    # get sheet names
    wb_xml = z.read('xl/workbook.xml')
    root = ET.fromstring(wb_xml)
    sheets = root.findall('.//{http://schemas.openxmlformats.org/spreadsheetml/2006/main}sheet')
    for s in sheets:
        print("Sheet:", s.attrib.get('name'), "r:id:", s.attrib.get('{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id'))
