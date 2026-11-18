import csv
from collections import Counter

csv_path = 'data/mra_raw_sheet.csv'
with open(csv_path, 'r', encoding='utf-8') as f:
    reader = csv.reader(f)
    headers = next(reader)
    
    quartals = Counter()
    bulans = Counter()
    pic_mras = Counter()
    cais = Counter()
    kriteria1 = Counter()
    kriteria2 = Counter()
    kriteria3 = Counter()
    ths_col = Counter()
    nama_sa = Counter()
    
    rows_2026 = []
    
    for r in reader:
        if len(r) > 15:
            q = r[0].strip()
            k1 = r[1].strip()
            k2 = r[2].strip()
            k3 = r[3].strip()
            cai = r[4].strip()
            pic = r[14].strip()
            bln = r[15].strip()
            ths = r[72].strip() if len(r) > 72 else ''
            sa = r[76].strip() if len(r) > 76 else ''
            
            quartals[q] += 1
            bulans[bln] += 1
            pic_mras[pic] += 1
            cais[cai] += 1
            kriteria1[k1] += 1
            kriteria2[k2] += 1
            kriteria3[k3] += 1
            ths_col[ths] += 1
            nama_sa[sa] += 1

print("Quartals:", quartals)
print("Bulans:", bulans.most_common(20))
print("PIC MRAs:", pic_mras)
print("CAI values:", cais)
print("Kriteria 1:", kriteria1)
print("Kriteria 2:", kriteria2)
print("Kriteria 3:", kriteria3)
print("THS:", ths_col)
print("NAMA SA:", nama_sa)
