import os
import sys
import json
import csv
import io
import urllib.request
from datetime import datetime

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data')
SBI_JSON_PATH = os.path.join(DATA_DIR, 'sbi_data.json')
RAW_CSV_PATH = os.path.join(DATA_DIR, 'sbi_raw.csv')

SHEET_ID = '1b60d-JO50LU4KyywuULokmDIU7z3Ts_1'
GID = '457735933'
SBI_CSV_URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&gid={GID}"

def fetch_or_read_sbi_csv(force_download=False):
    if force_download or not os.path.exists(RAW_CSV_PATH):
        print(f"Mengunduh data SBI live dari Google Sheets (GID: {GID})...")
        req = urllib.request.Request(SBI_CSV_URL, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=30) as resp:
            data = resp.read().decode('utf-8', errors='ignore')
            with open(RAW_CSV_PATH, 'w', encoding='utf-8') as f:
                f.write(data)
            return data
    else:
        print(f"Membaca data SBI dari cache lokal: {RAW_CSV_PATH}")
        with open(RAW_CSV_PATH, 'r', encoding='utf-8') as f:
            return f.read()

def process_sbi_data(csv_text):
    raw_rows = list(csv.reader(io.StringIO(csv_text)))
    non_empty = [r for r in raw_rows if any(cell.strip() for cell in r)]

    # Header is at index 6 in non_empty
    header_idx = None
    for idx, r in enumerate(non_empty):
        r_str = " | ".join(r)
        if "VIN" in r_str and "Nama" in r_str and "Model" in r_str:
            header_idx = idx
            break

    if header_idx is None:
        raise Exception("Header baris data SBI tidak ditemukan!")

    headers = [c.strip().replace('\r', '').replace('\n', ' ') for c in non_empty[header_idx]]
    # Normalize headers
    # Col 0: CAI, Col 1: month, Col 2: Bulan, Col 3: BULAN FU, Col 4: Tahun, Col 5: Tahun FU
    # Col 6: VIN, Col 7: No., Col 8: Tgl. Transaksi, Col 9: Nama, Col 10: Nama Cust, Col 11: TYPE CUST
    # Col 12: Telepon1, Col 13: Telepon 2, Col 14: Telepon 3, Col 15: Model, Col 16: PLAT NO
    # Col 17: Sales Person, Col 18: Nomor Rangka, Col 19: Alamat, Col 20: KAB, Col 21: SS
    # Col 22: CAR TYPE, Col 23: NO WA, Col 24: Follow up by, Col 25: tanggal FU, Col 26: Notes Follow Up
    # Col 27: Penggalian MRS, Col 28: CAI TO DEALER, Col 29: Ket FU, Col 30: SALES
    # Col 31: POTENCY SALES, Col 32: FU Sales, Col 33: FOLLOW UP BY SALES, Col 34: STATUS T-CARE
    # Col 35: bulan CAI (SO), Col 36: RING AREA CUST, Col 37: CAI 10K IN KC, Col 38: CAI 20K IN KC
    # Col 39: CAI 30K IN KC, Col 40: CAI 40K IN KC, Col 41: CAI 50K IN KC, Col 42: CAI 60K IN KC
    # Col 43: CAI 70K IN KC, Col 44: Habit Ring Area Service, Col 45: HABIT DEALER SERVICE, Col 46: Judgement Cust

    data_rows = non_empty[header_idx + 1:]

    records = []
    for idx, r in enumerate(data_rows):
        while len(r) < len(headers):
            r.append('')

        # Clean up cell values
        row_clean = [cell.strip() for cell in r]
        
        # Build structured object for high performance
        rec = {
            "id": idx + 1,
            "cai": row_clean[0],
            "month_num": row_clean[1],
            "month": row_clean[2],
            "month_fu": row_clean[3],
            "year": row_clean[4],
            "year_fu": row_clean[5],
            "vin": row_clean[6],
            "no": row_clean[7],
            "tgl_transaksi": row_clean[8],
            "nama": row_clean[9],
            "nama_cust": row_clean[10] if len(row_clean) > 10 else '',
            "type_cust": row_clean[11] if len(row_clean) > 11 else '',
            "telepon1": row_clean[12] if len(row_clean) > 12 else '',
            "telepon2": row_clean[13] if len(row_clean) > 13 else '',
            "telepon3": row_clean[14] if len(row_clean) > 14 else '',
            "model": row_clean[15] if len(row_clean) > 15 else '',
            "plat_no": row_clean[16] if len(row_clean) > 16 else '',
            "sales_person": row_clean[17] if len(row_clean) > 17 else '',
            "nomor_rangka": row_clean[18] if len(row_clean) > 18 else '',
            "alamat": row_clean[19] if len(row_clean) > 19 else '',
            "kab": row_clean[20] if len(row_clean) > 20 else '',
            "ss": row_clean[21] if len(row_clean) > 21 else '',
            "car_type": row_clean[22] if len(row_clean) > 22 else '',
            "no_wa": row_clean[23] if len(row_clean) > 23 else '',
            "fu_by": row_clean[24] if len(row_clean) > 24 else '',
            "tgl_fu": row_clean[25] if len(row_clean) > 25 else '',
            "notes_fu": row_clean[26] if len(row_clean) > 26 else '',
            "penggalian_mrs": row_clean[27] if len(row_clean) > 27 else '',
            "cai_to_dealer": row_clean[28] if len(row_clean) > 28 else '',
            "ket_fu": row_clean[29] if len(row_clean) > 29 else '',
            "sales": row_clean[30] if len(row_clean) > 30 else '',
            "potency_sales": row_clean[31] if len(row_clean) > 31 else '',
            "fu_sales": row_clean[32] if len(row_clean) > 32 else '',
            "fu_by_sales": row_clean[33] if len(row_clean) > 33 else '',
            "status_tcare": row_clean[34] if len(row_clean) > 34 else '',
            "bulan_cai_so": row_clean[35] if len(row_clean) > 35 else '',
            "ring_area": row_clean[36] if len(row_clean) > 36 else '',
            "cai_10k": row_clean[37] if len(row_clean) > 37 else '',
            "cai_20k": row_clean[38] if len(row_clean) > 38 else '',
            "cai_30k": row_clean[39] if len(row_clean) > 39 else '',
            "cai_40k": row_clean[40] if len(row_clean) > 40 else '',
            "cai_50k": row_clean[41] if len(row_clean) > 41 else '',
            "cai_60k": row_clean[42] if len(row_clean) > 42 else '',
            "cai_70k": row_clean[43] if len(row_clean) > 43 else '',
            "habit_ring_area": row_clean[44] if len(row_clean) > 44 else '',
            "habit_dealer": row_clean[45] if len(row_clean) > 45 else '',
            "judgement_cust": row_clean[46] if len(row_clean) > 46 else ''
        }
        records.append(rec)

    # Parse Top Summary Tables
    # Monthly 2026 Table (Rows 1 - 4)
    # Month list
    months_order = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]
    monthly_2026 = {}
    row_months = non_empty[1]
    row_dec = non_empty[2]
    row_cai = non_empty[3]
    row_acv = non_empty[4]

    for m_col in range(3, 15):
        m_name = row_months[m_col].strip() if m_col < len(row_months) else ''
        if not m_name and m_col - 3 < len(months_order):
            m_name = months_order[m_col - 3]
        dec_val = int(row_dec[m_col].strip()) if m_col < len(row_dec) and row_dec[m_col].strip().isdigit() else 0
        cai_val = int(row_cai[m_col].strip()) if m_col < len(row_cai) and row_cai[m_col].strip().isdigit() else 0
        acv_str = row_acv[m_col].strip() if m_col < len(row_acv) else ''
        monthly_2026[m_name] = {
            "dec": dec_val,
            "cai": cai_val,
            "acv": acv_str
        }

    # Yearly Performance (2024, 2025, 2026)
    yearly_perf = {
        "2024": {
            "dec": 677, "hybrid": 54, "pct_hybrid": "8.0%",
            "feryanto": 17, "adrian": 27, "caisariva": 10, "alvin": 0
        },
        "2025": {
            "dec": 854, "hybrid": 105, "pct_hybrid": "12.3%",
            "feryanto": 29, "adrian": 9, "caisariva": 36, "alvin": 31
        },
        "2026": {
            "dec": 649, "hybrid": 130, "pct_hybrid": "20.0%",
            "feryanto": 48, "adrian": 0, "caisariva": 30, "alvin": 52
        }
    }

    # Summary by Judgement
    judgement_counts = {}
    for r in records:
        j = r['judgement_cust'] or 'TIDAK TERDEFINISI'
        judgement_counts[j] = judgement_counts.get(j, 0) + 1

    # Summary by Potency Sales
    potency_sales_counts = {}
    for r in records:
        p = r['potency_sales'] or 'LAINNYA'
        potency_sales_counts[p] = potency_sales_counts.get(p, 0) + 1

    # Summary by T-Care
    tcare_counts = {}
    for r in records:
        t = r['status_tcare'] or '-'
        tcare_counts[t] = tcare_counts.get(t, 0) + 1

    # Summary by Car Type
    car_type_counts = {}
    for r in records:
        ct = r['car_type'] or 'NON LCGC'
        car_type_counts[ct] = car_type_counts.get(ct, 0) + 1

    # Summary by Ring Area
    ring_counts = {}
    for r in records:
        rg = r['ring_area'] or 'OUT OF AREA'
        ring_counts[rg] = ring_counts.get(rg, 0) + 1

    # Summary by SS
    ss_counts = {}
    for r in records:
        s = r['ss'] or 'LAINNYA'
        ss_counts[s] = ss_counts.get(s, 0) + 1

    # Summary by Cust Type
    cust_type_counts = {}
    for r in records:
        ct = r['type_cust'] or 'Retail'
        cust_type_counts[ct] = cust_type_counts.get(ct, 0) + 1

    # Summary by Year
    year_counts = {}
    for r in records:
        y = r['year'] or '2026'
        year_counts[y] = year_counts.get(y, 0) + 1

    result = {
        "meta": {
            "title": "SBI (Service Berkala Internal) Intelligence & Monitoring",
            "spreadsheet_id": SHEET_ID,
            "gid": GID,
            "sheet_name": "SBI",
            "updated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "total_records": len(records),
            "headers": headers,
            "source_url": f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/edit?gid={GID}#gid={GID}"
        },
        "summary": {
            "monthly_2026": monthly_2026,
            "yearly_perf": yearly_perf,
            "by_judgement": judgement_counts,
            "by_potency_sales": potency_sales_counts,
            "by_tcare": tcare_counts,
            "by_car_type": car_type_counts,
            "by_ring_area": ring_counts,
            "by_ss": ss_counts,
            "by_cust_type": cust_type_counts,
            "by_year": year_counts
        },
        "records": records
    }

    with open(SBI_JSON_PATH, 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

    print(f"Data SBI berhasil diproses! Total {len(records)} records tersimpan di: {SBI_JSON_PATH}")
    return result

if __name__ == '__main__':
    force = '--force' in sys.argv
    csv_data = fetch_or_read_sbi_csv(force_download=force)
    process_sbi_data(csv_data)
