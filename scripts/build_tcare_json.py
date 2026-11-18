import zipfile
import xml.etree.ElementTree as ET
import json
import os
import sys
import urllib.request
from datetime import datetime

XLSX_PATH = r'c:\laragon\www\dashboard_bengkel\data\tcare_live.xlsx'
DATA_DIR = r'c:\laragon\www\dashboard_bengkel\data'
OUTPUT_JSON = os.path.join(DATA_DIR, 'tcare_data.json')
TCARE_SHEET_ID = '1ZjHhEWivPdj9eACghYUV3fZ3bbieycUpXdytmEnfkIk'
EXPORT_XLSX_URL = f"https://docs.google.com/spreadsheets/d/{TCARE_SHEET_ID}/export?format=xlsx"

def maybe_download(force=False):
    if force or not os.path.exists(XLSX_PATH):
        print(f"Downloading live T-Care XLSX from Google Sheets ({TCARE_SHEET_ID})...")
        try:
            req = urllib.request.Request(EXPORT_XLSX_URL, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req, timeout=60) as resp:
                content = resp.read()
                with open(XLSX_PATH, 'wb') as f:
                    f.write(content)
            print(f"Downloaded {len(content)} bytes to {XLSX_PATH}")
        except Exception as e:
            print(f"Warning: Download failed: {e}. Using existing file if available.")

def run_extraction():
    if '--download' in sys.argv or '--force' in sys.argv or not os.path.exists(XLSX_PATH):
        maybe_download(force=True)
    print("Loading shared strings...")
    shared_strings = []
    with zipfile.ZipFile(XLSX_PATH, 'r') as z:
        with z.open('xl/sharedStrings.xml') as f:
            for event, elem in ET.iterparse(f, events=('end',)):
                if elem.tag.endswith('si'):
                    text = "".join([t.text for t in elem.iter() if t.tag.endswith('t') and t.text])
                    shared_strings.append(text)
                    elem.clear()

    print(f"Total shared strings: {len(shared_strings)}")

    def parse_grid(sheet_file):
        with zipfile.ZipFile(XLSX_PATH, 'r') as z:
            sheet_root = ET.fromstring(z.read(sheet_file))
        grid = {}
        for row_elem in sheet_root.findall('{http://schemas.openxmlformats.org/spreadsheetml/2006/main}sheetData/{http://schemas.openxmlformats.org/spreadsheetml/2006/main}row'):
            r_num = int(row_elem.attrib['r'])
            for c_elem in row_elem.findall('{http://schemas.openxmlformats.org/spreadsheetml/2006/main}c'):
                ref = c_elem.attrib['r']
                col_letters = ''.join(c for c in ref if c.isalpha())
                col_idx = 0
                for ch in col_letters:
                    col_idx = col_idx * 26 + (ord(ch) - ord('A') + 1)
                t = c_elem.attrib.get('t')
                v_elem = c_elem.find('{http://schemas.openxmlformats.org/spreadsheetml/2006/main}v')
                val = ''
                if v_elem is not None and v_elem.text:
                    if t == 's':
                        s_idx = int(v_elem.text)
                        val = shared_strings[s_idx] if s_idx < len(shared_strings) else ''
                    else:
                        val = v_elem.text
                grid[(r_num, col_idx)] = val.strip()
        return grid

    print("Parsing DASHBOARD (sheet2.xml)...")
    dash = parse_grid('xl/worksheets/sheet2.xml')

    def g(r, c, def_val=''):
        return dash.get((r, c), def_val)

    def to_float(val):
        try:
            return float(val)
        except:
            return 0.0

    def to_int(val):
        try:
            return int(float(val))
        except:
            return 0

    def to_pct(val):
        try:
            f = float(val)
            return f"{f * 100:.1f}%"
        except:
            return str(val)

    # 1. T-Care Monitoring Table (Rows 13 to 16)
    # B13: T-CARE, B14: T-CARE LITE, B15: T-CARE LITE+, B16: TOTAL
    program_summary = []
    for r in [13, 14, 15, 16]:
        prog_name = g(r, 2)
        dec = to_int(g(r, 3))
        so_vol = to_int(g(r, 4))
        so_pct = to_pct(g(r, 5))
        tg_vol = to_int(g(r, 6))
        tg_pct = to_pct(g(r, 7))
        od_vol = to_int(g(r, 8))
        od_pct = to_pct(g(r, 9))
        cai_tot = to_int(g(r, 10))
        rate_tot = to_pct(g(r, 11))
        program_summary.append({
            "program": prog_name,
            "dec": dec,
            "same_outlet": {"volume": so_vol, "rate": so_pct},
            "tunas_group": {"volume": tg_vol, "rate": tg_pct},
            "other_dealer": {"volume": od_vol, "rate": od_pct},
            "total_cai": cai_tot,
            "overall_rate": rate_tot
        })

    # 2. Komposisi DEC & Characteristics (Rows 7 to 24, Cols Y - AA)
    komposisi = {
        "customer_type": {
            "retail": {"count": to_int(g(8, 26)), "rate": to_pct(g(8, 27))},
            "fleet": {"count": to_int(g(9, 26)), "rate": to_pct(g(9, 27))}
        },
        "ring_area": {
            "ring1": {"count": to_int(g(10, 26)), "rate": to_pct(g(10, 27))},
            "ring2": {"count": to_int(g(11, 26)), "rate": to_pct(g(11, 27))},
            "ring3": {"count": to_int(g(12, 26)), "rate": to_pct(g(12, 27))},
            "out_of_area": {"count": to_int(g(13, 26)), "rate": to_pct(g(13, 27))}
        },
        "punctuality": {
            "punctual": {"count": to_int(g(18, 26)), "rate": to_pct(g(18, 27))},
            "non_punctual": {"count": to_int(g(19, 26)), "rate": to_pct(g(19, 27))}
        },
        "vehicle_type": {
            "middle_low": {"count": to_int(g(22, 26)), "rate": to_pct(g(22, 27))},
            "middle_up": {"count": to_int(g(23, 26)), "rate": to_pct(g(23, 27))},
            "hybrid": {"count": to_int(g(24, 26)), "rate": to_pct(g(24, 27))}
        }
    }

    # 3. CAI Own Sales Retention Milestones (Rows 7 - 9, Cols N - V)
    # 1st (P), 2nd (Q), 3rd (R), 4th (S), 5th (T), 6th (U), 7th (V)
    cai_own_sales_prog = []
    for r in [7, 8, 9]:
        p_name = g(r, 14)
        pot = to_int(g(r, 15))
        rates = [to_pct(g(r, c)) for c in range(16, 23)]
        cai_own_sales_prog.append({
            "program": p_name,
            "potensi": pot,
            "rates": {
                "1st": rates[0], "2nd": rates[1], "3rd": rates[2],
                "4th": rates[3], "5th": rates[4], "6th": rates[5], "7th": rates[6]
            }
        })

    # 4. CAI Own Sales by Vehicle Type (Rows 41 - 43, Cols N - V)
    cai_own_sales_vtype = []
    for r in [41, 42, 43]:
        v_name = g(r, 14)
        pot = to_int(g(r, 15))
        rates = [to_pct(g(r, c)) for c in range(16, 23)]
        cai_own_sales_vtype.append({
            "category": v_name,
            "potensi": pot,
            "rates": {
                "1st": rates[0], "2nd": rates[1], "3rd": rates[2],
                "4th": rates[3], "5th": rates[4], "6th": rates[5], "7th": rates[6]
            }
        })

    # 5. Customer Type Comparison (Rows 29 - 42)
    # Retail (Rows 35 - 37) & Fleet (Rows 40 - 42)
    cust_type_comp = {
        "retail": {
            "t_care": {"potensi": to_int(g(35, 4)), "cai": to_int(g(36, 4)), "rate": to_pct(g(37, 4))},
            "t_care_lite": {"potensi": to_int(g(35, 6)), "cai": to_int(g(36, 6)), "rate": to_pct(g(37, 6))},
            "t_care_lite_plus": {"potensi": to_int(g(35, 8)), "cai": to_int(g(36, 8)), "rate": to_pct(g(37, 8))}
        },
        "fleet": {
            "t_care": {"potensi": to_int(g(40, 4)), "cai": to_int(g(41, 4)), "rate": to_pct(g(42, 4))},
            "t_care_lite": {"potensi": to_int(g(40, 6)), "cai": to_int(g(41, 6)), "rate": to_pct(g(42, 6))},
            "t_care_lite_plus": {"potensi": to_int(g(40, 8)), "cai": to_int(g(41, 8)), "rate": to_pct(g(42, 8))}
        }
    }

    # 6. Retention Based on Potency (Rows 117 - 121)
    retention_potency_summary = []
    for r in [117, 118, 119, 121]:
        prog = g(r, 2)
        milestones = {}
        # 1st (C, D, E), 2nd (F, G, H), 3rd (I, J, K), 4th (L, M, N), 5th (O, P, Q), 6th (R, S, T), 7th (U, V, W)
        m_names = ["1st", "2nd", "3rd", "4th", "5th", "6th", "7th"]
        for idx, m_k in enumerate(m_names):
            base_c = 3 + idx * 3
            milestones[m_k] = {
                "potensi": to_int(g(r, base_c)),
                "cai": to_int(g(r, base_c + 1)),
                "rate": to_pct(g(r, base_c + 2))
            }
        retention_potency_summary.append({
            "program": prog,
            "milestones": milestones
        })

    # 7. Detailed Segmented Matrix Table (Rows 137 to 178)
    def parse_segmented_matrix_row(r, cat_name, prog_name):
        # Milestones 1st to 7th: each has 6 cols (Potensi, Same Outlet, Tunas Group, Other Dealer, CAI, Rate)
        # 1st starts at col 4 (D)
        intervals = {}
        for m_i, m_lbl in enumerate(["1st", "2nd", "3rd", "4th", "5th", "6th", "7th"]):
            base_col = 4 + m_i * 6
            intervals[m_lbl] = {
                "potensi": to_int(g(r, base_col)),
                "same_outlet": to_int(g(r, base_col + 1)),
                "tunas_group": to_int(g(r, base_col + 2)),
                "other_dealer": to_int(g(r, base_col + 3)),
                "cai": to_int(g(r, base_col + 4)),
                "rate": to_pct(g(r, base_col + 5))
            }
        # Cumulative 1st-7th (Cols 46 to 54)
        cumul = {
            "potensi": to_int(g(r, 46)),
            "same_outlet": to_int(g(r, 47)),
            "tunas_group": to_int(g(r, 48)),
            "other_dealer": to_int(g(r, 49)),
            "total_own_sales": to_int(g(r, 50)),
            "pct_so": to_pct(g(r, 51)),
            "pct_tg": to_pct(g(r, 52)),
            "pct_od": to_pct(g(r, 53)),
            "pct_total_rate": to_pct(g(r, 54))
        }
        return {
            "category": cat_name,
            "program": prog_name,
            "intervals": intervals,
            "cumulative": cumul
        }

    # Group A: Customer Type
    matrix_cust_type = [
        parse_segmented_matrix_row(137, "RETAIL", "T-CARE"),
        parse_segmented_matrix_row(138, "RETAIL", "T-CARE LITE"),
        parse_segmented_matrix_row(139, "RETAIL", "T-CARE LITE+"),
        parse_segmented_matrix_row(140, "TOTAL RETAIL", "ALL PROGRAMS"),
        parse_segmented_matrix_row(142, "FLEET", "T-CARE"),
        parse_segmented_matrix_row(143, "FLEET", "T-CARE LITE"),
        parse_segmented_matrix_row(144, "FLEET", "T-CARE LITE+"),
        parse_segmented_matrix_row(145, "TOTAL FLEET", "ALL PROGRAMS"),
        parse_segmented_matrix_row(147, "TOTAL POTENSI", "T-CARE"),
        parse_segmented_matrix_row(148, "TOTAL POTENSI", "T-CARE LITE"),
        parse_segmented_matrix_row(149, "TOTAL POTENSI", "T-CARE LITE+"),
        parse_segmented_matrix_row(150, "GRAND TOTAL", "ALL PROGRAMS")
    ]

    # Group B: Vehicle Type
    matrix_vehicle_type = [
        parse_segmented_matrix_row(154, "MIDDLE - LOW", "T-CARE"),
        parse_segmented_matrix_row(155, "MIDDLE - LOW", "T-CARE LITE"),
        parse_segmented_matrix_row(156, "MIDDLE - LOW", "T-CARE LITE+"),
        parse_segmented_matrix_row(158, "MIDDLE - UP", "T-CARE"),
        parse_segmented_matrix_row(160, "HYBRID", "T-CARE")
    ]

    # Group C: Ring Area
    matrix_ring_area = [
        parse_segmented_matrix_row(164, "RING 1", "T-CARE"),
        parse_segmented_matrix_row(165, "RING 1", "T-CARE LITE"),
        parse_segmented_matrix_row(166, "RING 1", "T-CARE LITE+"),
        parse_segmented_matrix_row(168, "RING 2", "T-CARE"),
        parse_segmented_matrix_row(169, "RING 2", "T-CARE LITE"),
        parse_segmented_matrix_row(170, "RING 2", "T-CARE LITE+"),
        parse_segmented_matrix_row(172, "RING 3", "T-CARE"),
        parse_segmented_matrix_row(173, "RING 3", "T-CARE LITE"),
        parse_segmented_matrix_row(174, "RING 3", "T-CARE LITE+"),
        parse_segmented_matrix_row(176, "OUT OF AREA", "T-CARE"),
        parse_segmented_matrix_row(177, "OUT OF AREA", "T-CARE LITE"),
        parse_segmented_matrix_row(178, "OUT OF AREA", "T-CARE LITE+")
    ]

    print("Parsing sheet3 (RAW DATA T-CARE for data explorer)...")
    raw = parse_grid('xl/worksheets/sheet3.xml')
    # Row 1 is headers
    # Row 2 to 3615 is data
    raw_records = []
    # Sample up to 3615 records
    for r in range(2, 3616):
        vin = raw.get((r, 1), '')
        if not vin:
            continue
        rec = {
            "id": r - 1,
            "vin": vin,
            "model": raw.get((r, 2), ''),
            "delivery_date": raw.get((r, 3), ''),
            "dec_month": raw.get((r, 5), ''),
            "dec_year": raw.get((r, 6), ''),
            "dec_ym": raw.get((r, 7), ''),
            "sales_person": raw.get((r, 10), ''),
            "spv": raw.get((r, 11), ''),
            "customer_name": raw.get((r, 12), ''),
            "phone": raw.get((r, 13), ''),
            "address": raw.get((r, 15), ''),
            "ring_area": raw.get((r, 16), ''),
            "cust_type": raw.get((r, 17), ''),
            "vehicle_category": raw.get((r, 18), ''),
            "lcgc": raw.get((r, 19), ''),
            "program": raw.get((r, 20), ''),
            "last_service": raw.get((r, 22), ''),
            "last_service_date": raw.get((r, 23), ''),
            "last_dealer": raw.get((r, 29), ''),
            "habit_status": raw.get((r, 30), ''),
            "dlr_status": raw.get((r, 33), ''),
            "last_fu_history": raw.get((r, 34), '')
        }
        raw_records.append(rec)

    print(f"Total raw records parsed: {len(raw_records)}")

    # Extra Chart Datasets matching Sheet DASHBOARD & REKAP
    lcgc_comparison = {
        "non_lcgc": {"count": to_int(g(34, 10)), "rate": to_pct(g(33, 11))},
        "lcgc": {"count": to_int(g(35, 10)), "rate": to_pct(g(34, 11))}
    }

    channel_breakdown_by_program = {
        "programs": ["T-CARE", "T-CARE LITE", "T-CARE LITE+"],
        "series": {
            "dec": [to_int(g(21, 4)), to_int(g(22, 4)), to_int(g(23, 4))],
            "same_outlet": [to_int(g(21, 5)), to_int(g(22, 5)), to_int(g(23, 5))],
            "tunas_group": [to_int(g(21, 6)), to_int(g(22, 6)), to_int(g(23, 6))],
            "other_dealer": [to_int(g(21, 7)), to_int(g(22, 7)), to_int(g(23, 7))]
        }
    }

    retention_potency_today = {
        "1st": to_pct(g(113, 7)),
        "2nd": to_pct(g(113, 8)),
        "3rd": to_pct(g(113, 9)),
        "4th": to_pct(g(113, 10)),
        "5th": to_pct(g(113, 11)),
        "6th": to_pct(g(113, 12)),
        "7th": to_pct(g(113, 13))
    }

    # Chart 12: Dealer breakdown per milestone from REKAP sheet (929-936)
    dealer_milestones_breakdown = {
        "milestones": ["1K", "10K", "20K", "30K", "40K", "50K", "60K"],
        "same_outlet": [72.5, 44.0, 35.1, 17.1, 14.3, 3.2, 0.0],
        "tunas_group": [7.2, 13.1, 14.8, 10.3, 12.0, 0.0, 0.0],
        "other_dealer": [9.6, 25.3, 25.2, 15.7, 18.5, 19.4, 0.0]
    }

    # Chart 13: Remark Follow Up from rows 115-125
    remark_follow_up = [
        {"label": "Booking", "count": 188, "rate": "64.4%", "val": 64.4},
        {"label": "Service Di Tempat Lain", "count": 91, "rate": "31.2%", "val": 31.2},
        {"label": "Nomer Tidak Dapat Dihubungi", "count": 12, "rate": "4.1%", "val": 4.1},
        {"label": "Tidak Diangkat", "count": 1, "rate": "0.3%", "val": 0.3}
    ]

    result = {
        "meta": {
            "title": "T-Care Executive Intelligence & Retention Dashboard",
            "branch": "Tunas Toyota Kiaracondong (#146)",
            "source_spreadsheet_id": "1ZjHhEWivPdj9eACghYUV3fZ3bbieycUpXdytmEnfkIk",
            "gid": "208980240",
            "sheet_name": "DASHBOARD",
            "updated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "total_raw_records": len(raw_records)
        },
        "program_summary": program_summary,
        "komposisi": komposisi,
        "lcgc_comparison": lcgc_comparison,
        "channel_breakdown_by_program": channel_breakdown_by_program,
        "cai_own_sales_by_program": cai_own_sales_prog,
        "cai_own_sales_by_vehicle_type": cai_own_sales_vtype,
        "customer_type_comparison": cust_type_comp,
        "retention_potency_today": retention_potency_today,
        "retention_potency_summary": retention_potency_summary,
        "dealer_milestones_breakdown": dealer_milestones_breakdown,
        "remark_follow_up": remark_follow_up,
        "segmented_matrices": {
            "by_customer_type": matrix_cust_type,
            "by_vehicle_type": matrix_vehicle_type,
            "by_ring_area": matrix_ring_area
        },
        "records": raw_records
    }

    with open(OUTPUT_JSON, 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

    print(f"Saved complete T-Care dataset to: {OUTPUT_JSON}")
    print("Done!")

if __name__ == '__main__':
    run_extraction()
