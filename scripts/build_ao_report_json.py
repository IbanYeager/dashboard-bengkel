import json
import zipfile
import xml.etree.ElementTree as ET
import re

with zipfile.ZipFile('data/ao_report.xlsx') as z:
    shared_strings = []
    ns = {'main': 'http://schemas.openxmlformats.org/spreadsheetml/2006/main'}
    if 'xl/sharedStrings.xml' in z.namelist():
        ss_root = ET.fromstring(z.read('xl/sharedStrings.xml'))
        for si in ss_root.findall('.//main:si', ns):
            shared_strings.append("".join(t.text or "" for t in si.findall('.//main:t', ns)))

    def col2num(col_str):
        num = 0
        for ch in col_str: num = num * 26 + (ord(ch) - ord('A') + 1)
        return num
    def num2col(num):
        res = ""
        while num > 0:
            num, rem = divmod(num - 1, 26)
            res = chr(ord('A') + rem) + res
        return res

    def get_sheet_cells(sheet_path):
        s_root = ET.fromstring(z.read(sheet_path))
        cells = {}
        for row in s_root.findall('.//main:row', ns):
            r_num = int(row.attrib.get('r'))
            for c in row.findall('.//main:c', ns):
                coord = c.attrib.get('r')
                m = re.match(r'([A-Z]+)(\d+)', coord)
                if not m: continue
                col_str, row_str = m.groups()
                c_num = col2num(col_str)
                t_type = c.attrib.get('t', '')
                v_elem = c.find('main:v', ns)
                val = v_elem.text if v_elem is not None else ""
                if t_type == 's' and val: val = shared_strings[int(val)]
                cells[(r_num, c_num)] = val
        return cells

    c_ao = get_sheet_cells('xl/worksheets/sheet2.xml')
    c_kpi = get_sheet_cells('xl/worksheets/sheet1.xml')

    def to_float(val, default=0.0):
        try:
            return float(str(val).replace(',', '.'))
        except:
            return default

    def to_int(val, default=0):
        try:
            return int(round(float(str(val).replace(',', '.'))))
        except:
            return default

    ao_data = {
        "meta": {
            "title": "AO REPORT GR - Executive Intelligence & Monitoring",
            "outlet": "TUNAS TOYOTA KIARA CONDONG",
            "active_week": "W1",
            "active_month": "October",
            "active_year": "2026",
            "source_url": "https://docs.google.com/spreadsheets/d/1LQYpCsXsU3o6N4cAMQH7Da44rXhSlksO/edit?gid=1124551793#gid=1124551793"
        },
        "summary": {
            "this_month_closing_estimation": {
                "cpus": to_int(c_ao.get((2, 23), 714)),
                "vs_tar_pct": round(to_float(c_ao.get((2, 24), 1.05)) * 100, 1)
            },
            "closing_commitment": to_int(c_ao.get((5, 15), 714)),
            "total_cpus_gap_fm": to_int(c_ao.get((10, 15), -619)),
            "gap_cpus_walkin_fm": to_int(c_ao.get((15, 15), -226)),
            "act_cpus_walkin_fm": to_int(c_ao.get((20, 15), 42)),
            "gap_cpus_booking_fm": to_int(c_ao.get((25, 15), -393)),
            "act_cpus_booking_fm": to_int(c_ao.get((32, 15), 53))
        },
        "section_1_target_setting": {
            "kpi_tree": {
                "cpus_target": to_int(c_ao.get((10, 2), 714)),
                "walk_in": {
                    "target": to_int(c_ao.get((10, 4), 268)),
                    "pct": round(to_float(c_ao.get((11, 4), 0.375)) * 100, 1)
                },
                "booking_show": {
                    "target": to_int(c_ao.get((25, 4), 446)),
                    "pct": round(to_float(c_ao.get((26, 4), 0.625)) * 100, 1),
                    "tcare": {
                        "target": round(to_float(c_ao.get((25, 5), 229.3)), 1),
                        "pct": round(to_float(c_ao.get((26, 5), 0.514)) * 100, 1)
                    },
                    "non_tcare": {
                        "target": round(to_float(c_ao.get((36, 5), 216.7)), 1),
                        "pct": round(to_float(c_ao.get((37, 5), 0.486)) * 100, 1),
                        "oil": {
                            "target": round(to_float(c_ao.get((35, 7), 26.4)), 1),
                            "pct": round(to_float(c_ao.get((36, 7), 0.122)) * 100, 1)
                        },
                        "gr": {
                            "target": round(to_float(c_ao.get((38, 7), 140.4)), 1),
                            "pct": round(to_float(c_ao.get((39, 7), 0.648)) * 100, 1)
                        },
                        "sbe": {
                            "target": round(to_float(c_ao.get((41, 7), 50.0)), 1),
                            "pct": round(to_float(c_ao.get((42, 7), 0.231)) * 100, 1)
                        }
                    }
                }
            },
            "weekly_performance": {
                "weeks": ["W1", "W2", "W3", "W4", "W5"],
                "total_cpus_plan": [round(to_float(c_ao.get((14, c))), 1) for c in [9, 10, 11, 12, 13]],
                "total_cpus_plan_total": to_int(c_ao.get((13, 9), 714)),
                "total_cpus_actual": [to_int(c_ao.get((15, c))) for c in [9, 10, 11, 12, 13]],
                "total_cpus_actual_total": to_int(c_ao.get((15, 9))) + to_int(c_ao.get((15, 10))),
                "total_gap": [round(to_float(c_ao.get((16, c))), 1) for c in [9, 10, 11, 12, 13]],
                "cumulative_gap_cpus": [round(to_float(c_ao.get((17, c))), 1) for c in [9, 10, 11, 12, 13]],
                
                "walkin_assumpt": [round(to_float(c_ao.get((18, c))), 1) for c in [9, 10, 11, 12, 13]],
                "walkin_actual": [to_int(c_ao.get((19, c))) for c in [9, 10, 11, 12, 13]],
                "walkin_gap": [round(to_float(c_ao.get((20, c))), 1) for c in [9, 10, 11, 12, 13]],
                "cumulative_gap_walkin": [round(to_float(c_ao.get((21, c))), 1) for c in [9, 10, 11, 12, 13]],
                
                "working_days": [to_int(c_ao.get((47, c))) for c in [9, 10, 11, 12, 13]],
                "working_days_total": to_int(c_ao.get((47, 15), 27)),
                
                "booking_show_plan": [round(to_float(c_ao.get((51, c))), 1) for c in [9, 10, 11, 12, 13]],
                "booking_show_plan_total": to_int(c_ao.get((50, 9), 446)),
                "booking_show_actual": [to_int(c_ao.get((52, c))) for c in [9, 10, 11, 12, 13]],
                "booking_show_actual_total": to_int(c_ao.get((52, 15), 117)),
                "booking_show_gap": [round(to_float(c_ao.get((53, c))), 1) for c in [9, 10, 11, 12, 13]],
                "cumulative_gap_booking_show": [round(to_float(c_ao.get((54, c))), 1) for c in [9, 10, 11, 12, 13]],
                
                "no_show_assumption": [to_int(c_ao.get((55, c))) for c in [9, 10, 11, 12, 13]],
                "no_show_assumption_total": to_int(c_ao.get((55, 15), 98)),
                "no_show_actual": [to_int(c_ao.get((56, c))) for c in [9, 10, 11, 12, 13]],
                "no_show_actual_total": to_int(c_ao.get((56, 15), 226)),
                "no_show_ratio_pct": [round(to_float(c_ao.get((57, c))) * 100, 1) for c in [9, 10, 11, 12, 13]],
                "cumulative_no_show": [to_int(c_ao.get((58, c))) for c in [9, 10, 11, 12, 13]],
                
                "booking_gross_plan": [round(to_float(c_ao.get((60, c))), 1) for c in [9, 10, 11, 12, 13]],
                "booking_gross_plan_total": to_int(c_ao.get((59, 9), 544)),
                "initial_n_minus_1": [to_int(c_ao.get((61, c))) for c in [9, 10, 11, 12, 13]],
                "booking_n": [round(to_float(c_ao.get((62, c))), 1) for c in [9, 10, 11, 12, 13]],
                "booking_actual": [to_int(c_ao.get((63, c))) for c in [9, 10, 11, 12, 13]],
                "booking_actual_total": to_int(c_ao.get((63, 15), 343)),
                "booking_gap": [round(to_float(c_ao.get((64, c))), 1) for c in [9, 10, 11, 12, 13]],
                "cumulative_gap_booking": [round(to_float(c_ao.get((65, c))), 1) for c in [9, 10, 11, 12, 13]],
                
                "next_month_booking_plan": to_int(c_ao.get((68, 11), 422))
            },
            "cumulative_chart": {
                "weeks": ["W1", "W2", "W3", "W4", "W5"],
                "target_cumulative": [round(to_float(c_ao.get((72, c))), 1) for c in [9, 10, 11, 12, 13]],
                "actual_cumulative": [to_int(c_ao.get((73, c))) for c in [9, 10, 11, 12, 13]]
            }
        },
        "section_2_prospecting_funneling": {
            "tcare": {
                "weeks": ["W1", "W2", "W3", "W4", "W5"],
                "data": {
                    "target": to_int(c_ao.get((6, 19), 872)),
                    "actual": [to_int(c_ao.get((7, c))) for c in [19, 20, 21, 22, 23]],
                    "actual_total": to_int(c_ao.get((7, 24), 870)),
                    "vs_tar_pct": [round(to_float(c_ao.get((8, c))) * 100, 1) for c in [19, 20, 21, 22, 23]],
                    "vs_tar_total_pct": round(to_float(c_ao.get((8, 24), 0.998)) * 100, 1)
                },
                "connected": {
                    "target": to_int(c_ao.get((9, 24), 864)),
                    "target_weeks": [to_int(c_ao.get((9, c))) for c in [19, 20, 21, 22, 23]],
                    "actual": [to_int(c_ao.get((10, c))) for c in [19, 20, 21, 22, 23]],
                    "actual_total": to_int(c_ao.get((10, 24), 783)),
                    "vs_tar_pct": [round(to_float(c_ao.get((11, c))) * 100, 1) for c in [19, 20, 21, 22, 23]],
                    "vs_tar_total_pct": round(to_float(c_ao.get((11, 24), 0.906)) * 100, 1)
                },
                "contacted": {
                    "target": to_int(c_ao.get((12, 24), 626)),
                    "target_weeks": [to_int(c_ao.get((12, c))) for c in [19, 20, 21, 22, 23]],
                    "actual": [round(to_float(c_ao.get((13, c))), 1) for c in [19, 20, 21, 22, 23]],
                    "actual_total": round(to_float(c_ao.get((13, 24), 505.7)), 1),
                    "vs_tar_pct": [round(to_float(c_ao.get((14, c))) * 100, 1) for c in [19, 20, 21, 22, 23]],
                    "vs_tar_total_pct": round(to_float(c_ao.get((14, 24), 0.808)) * 100, 1)
                },
                "booking": {
                    "target": to_int(c_ao.get((15, 24), 266)),
                    "target_weeks": [to_int(c_ao.get((15, c))) for c in [19, 20, 21, 22, 23]],
                    "actual": [to_int(c_ao.get((16, c))) for c in [19, 20, 21, 22, 23]],
                    "actual_total": to_int(c_ao.get((16, 24), 130)),
                    "vs_tar_pct": [round(to_float(c_ao.get((17, c))) * 100, 1) for c in [19, 20, 21, 22, 23]],
                    "vs_tar_total_pct": round(to_float(c_ao.get((17, 24), 0.489)) * 100, 1)
                },
                "booking_show": {
                    "target": round(to_float(c_ao.get((18, 24), 229.3)), 1),
                    "target_weeks": [round(to_float(c_ao.get((18, c))), 1) for c in [19, 20, 21, 22, 23]],
                    "actual": [to_int(c_ao.get((19, c))) for c in [19, 20, 21, 22, 23]],
                    "actual_total": to_int(c_ao.get((19, 24), 67)),
                    "vs_tar_pct": [round(to_float(c_ao.get((20, c))) * 100, 1) for c in [19, 20, 21, 22, 23]],
                    "vs_tar_total_pct": round(to_float(c_ao.get((20, 24), 0.292)) * 100, 1)
                }
            },
            "non_tcare": {
                "weeks": ["W1", "W2", "W3", "W4", "W5"],
                "data": {
                    "target": to_int(c_ao.get((27, 19), 725)),
                    "actual": [to_int(c_ao.get((28, c))) for c in [19, 20, 21, 22, 23]],
                    "actual_total": to_int(c_ao.get((28, 24), 725)),
                    "vs_tar_pct": [round(to_float(c_ao.get((29, c))) * 100, 1) for c in [19, 20, 21, 22, 23]],
                    "vs_tar_total_pct": round(to_float(c_ao.get((29, 24), 1.0)) * 100, 1)
                },
                "connected": {
                    "target": to_int(c_ao.get((30, 24), 639)),
                    "target_weeks": [to_int(c_ao.get((30, c))) for c in [19, 20, 21, 22, 23]],
                    "actual": [to_int(c_ao.get((31, c))) for c in [19, 20, 21, 22, 23]],
                    "actual_total": to_int(c_ao.get((31, 24), 669)),
                    "vs_tar_pct": [round(to_float(c_ao.get((32, c))) * 100, 1) for c in [19, 20, 21, 22, 23]],
                    "vs_tar_total_pct": round(to_float(c_ao.get((32, 24), 1.047)) * 100, 1)
                },
                "contacted": {
                    "target": to_int(c_ao.get((33, 24), 447)),
                    "target_weeks": [to_int(c_ao.get((33, c))) for c in [19, 20, 21, 22, 23]],
                    "actual": [round(to_float(c_ao.get((34, c))), 1) for c in [19, 20, 21, 22, 23]],
                    "actual_total": round(to_float(c_ao.get((34, 24), 550.9)), 1),
                    "vs_tar_pct": [round(to_float(c_ao.get((35, c))) * 100, 1) for c in [19, 20, 21, 22, 23]],
                    "vs_tar_total_pct": round(to_float(c_ao.get((35, 24), 1.232)) * 100, 1)
                },
                "booking": {
                    "target": to_int(c_ao.get((36, 24), 263)),
                    "target_weeks": [to_int(c_ao.get((36, c))) for c in [19, 20, 21, 22, 23]],
                    "actual": [to_int(c_ao.get((37, c))) for c in [19, 20, 21, 22, 23]],
                    "actual_total": to_int(c_ao.get((37, 24), 182)),
                    "vs_tar_pct": [round(to_float(c_ao.get((38, c))) * 100, 1) for c in [19, 20, 21, 22, 23]],
                    "vs_tar_total_pct": round(to_float(c_ao.get((38, 24), 0.692)) * 100, 1)
                },
                "booking_show": {
                    "target": round(to_float(c_ao.get((39, 24), 216.7)), 1),
                    "target_weeks": [round(to_float(c_ao.get((39, c))), 1) for c in [19, 20, 21, 22, 23]],
                    "actual": [to_int(c_ao.get((40, c))) for c in [19, 20, 21, 22, 23]],
                    "actual_total": to_int(c_ao.get((40, 24), 50)),
                    "vs_tar_pct": [round(to_float(c_ao.get((41, c))) * 100, 1) for c in [19, 20, 21, 22, 23]],
                    "vs_tar_total_pct": round(to_float(c_ao.get((41, 24), 0.231)) * 100, 1)
                }
            }
        },
        "section_3_sbi": {
            "weeks": ["W1", "W2", "W3", "W4", "W5"],
            "target": {
                "ncs_m_minus_1": [round(to_float(c_ao.get((46, c))), 1) for c in [19, 20, 21, 22, 23]],
                "ncs_m_minus_1_total": to_int(c_ao.get((46, 24), 87)),
                "not_cai": [round(to_float(c_ao.get((47, c))), 1) for c in [19, 20, 21, 22, 23]],
                "not_cai_total": to_int(c_ao.get((47, 24), 16)),
                "total": [round(to_float(c_ao.get((48, c))), 1) for c in [19, 20, 21, 22, 23]],
                "total_total": to_int(c_ao.get((48, 24), 103))
            },
            "actual": {
                "ncs_m_minus_1": [round(to_float(c_ao.get((49, c))), 1) for c in [19, 20, 21, 22, 23]],
                "ncs_m_minus_1_total": to_int(c_ao.get((49, 24), 62)),
                "not_cai": [round(to_float(c_ao.get((50, c))), 1) for c in [19, 20, 21, 22, 23]],
                "not_cai_total": to_int(c_ao.get((50, 24), 25)),
                "total": [round(to_float(c_ao.get((51, c))), 1) for c in [19, 20, 21, 22, 23]],
                "total_total": to_int(c_ao.get((51, 24), 87))
            },
            "gap": {
                "weeks": [to_int(c_ao.get((52, c))) for c in [19, 20, 21, 22, 23]],
                "total": to_int(c_ao.get((52, 24), -16))
            }
        },
        "section_4_action_plan": [
            {
                "category": "TCARE",
                "plan": "reminder by MRA - Akselerasi Reminder potency W4-W5",
                "pic": "MRA",
                "status": "on process"
            },
            {
                "category": "TCARE",
                "plan": "THS aktivitas reminder cust fleet (sudeco-TPI-Movus)",
                "pic": "THS",
                "status": "on process"
            },
            {
                "category": "TCARE",
                "plan": "REMINDER BY SA potency by appsheet",
                "pic": "SA",
                "status": "on process"
            },
            {
                "category": "NON TCARE",
                "plan": "reminder by MRA",
                "pic": "MRA",
                "status": "on process"
            },
            {
                "category": "NON TCARE",
                "plan": "THS aktivitas by app sheet",
                "pic": "THS",
                "status": "on process"
            },
            {
                "category": "NON TCARE",
                "plan": "REMINDER BY SA potency",
                "pic": "SA",
                "status": "on process"
            },
            {
                "category": "SBI",
                "plan": "reminder by MRA dan Sales - report monitoring SPV & Branch Head",
                "pic": "MRA - Kabeng",
                "status": "on process"
            }
        ],
        "kpi_tree_monthly_targets": {
            "January": {"target": 675, "booking_show": 422, "tcare": 217, "non_tcare": 205},
            "February": {"target": 635, "booking_show": 397, "tcare": 204, "non_tcare": 193},
            "March": {"target": 683, "booking_show": 427, "tcare": 220, "non_tcare": 207},
            "April": {"target": 717, "booking_show": 448, "tcare": 230, "non_tcare": 218},
            "May": {"target": 633, "booking_show": 396, "tcare": 204, "non_tcare": 192},
            "June": {"target": 695, "booking_show": 434, "tcare": 223, "non_tcare": 211},
            "July": {"target": 750, "booking_show": 469, "tcare": 241, "non_tcare": 228},
            "August": {"target": 750, "booking_show": 469, "tcare": 241, "non_tcare": 228},
            "September": {"target": 730, "booking_show": 456, "tcare": 234, "non_tcare": 222},
            "October": {"target": 714, "booking_show": 446, "tcare": 229, "non_tcare": 217},
            "November": {"target": 718, "booking_show": 449, "tcare": 231, "non_tcare": 218},
            "December": {"target": 718, "booking_show": 449, "tcare": 231, "non_tcare": 218}
        }
    }

    with open('data/ao_report_data.json', 'w', encoding='utf-8') as f:
        json.dump(ao_data, f, indent=2, ensure_ascii=False)
        
    print("Saved comprehensive ao_report_data.json!")
    print(f"File size: {len(json.dumps(ao_data))} bytes")
