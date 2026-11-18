import os, zipfile

for fname in os.listdir('.'):
    if not fname.endswith('.xlsx'): continue
    print('Checking:', fname)
    try:
        with zipfile.ZipFile(fname) as z:
            if 'xl/sharedStrings.xml' in z.namelist():
                ss = z.read('xl/sharedStrings.xml').decode('utf-8', errors='ignore')
                for kw in ['PIC MRA', 'PROMO YG DITAWARKAN', 'JUDGEMENT CUST', 'DUE DATE NEXT SERVICE', 'RANIH', 'RANI']:
                    if kw in ss:
                        print(f'  FOUND "{kw}" in sharedStrings of {fname}!')
    except Exception as e:
        print('  Err:', e)
