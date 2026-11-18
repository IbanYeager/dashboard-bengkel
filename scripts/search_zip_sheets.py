import zipfile
import re

def search_july_in_zip(zip_path):
    print(f"Searching {zip_path}...")
    with zipfile.ZipFile(zip_path, 'r') as z:
        # Find PKB sheet name
        for name in z.namelist():
            if 'sheet' in name and name.endswith('.xml'):
                # Read chunks and search for 2026 / 07 dates
                with z.open(name) as f:
                    content = f.read(5000000) # first 5MB
                    # check if this sheet has PKB headers
                    if b'POLICE NO' in content or b'PKB NO' in content or b'TYPE UE' in content or b'NO POLISI' in content:
                        print(f"  Found potential PKB sheet: {name}")

search_july_in_zip('DASH KIARACONDONG 24-26.backup.xlsx')
search_july_in_zip('DASH KIARACONDONG 24-26(1).xlsx')
search_july_in_zip('Dashboard AFS Kiaracondong-start 2024.xlsx')
