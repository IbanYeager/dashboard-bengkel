import urllib.request
import csv
import io
import json

url = 'https://docs.google.com/spreadsheets/d/1b60d-JO50LU4KyywuULokmDIU7z3Ts_1/gviz/tq?tqx=out:csv&gid=2141708170'
req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
content = urllib.request.urlopen(req).read().decode('utf-8')
reader = list(csv.reader(io.StringIO(content)))
header = reader[0]
rows = reader[1:]

print("Total ATTACKLIST rows:", len(rows))

def build_priority_segments(row_subset):
    # Priority 1: EXPIRED SOON
    ex_soon = {'Eligible': [0,0], 'Not Eligible': [0,0], 'Never claim': [0,0]}
    # Priority 2: ACTIVE
    active = {'Eligible': [0,0], 'Not Eligible': [0,0], 'Never claim': [0,0]}
    # Priority 3: FINISH
    finish = {'Eligible': [0,0], 'Not Eligible': [0,0]}
    # Priority 4: EXPIRED
    expired = {'Eligible': [0,0], 'Not Eligible': [0,0], 'Never claim': [0,0]}
    # Priority 5: CRT MERDEKA
    crt_merdeka = {'HOT': [0,0], 'Medium': [0,0], 'Low': [0,0]}
    # Priority 6: CRT NON MERDEKA
    crt_non_merdeka = {'HOT': [0,0], 'Medium': [0,0], 'Low': [0,0]}

    for r in row_subset:
        if len(r) <= 8: continue
        j = r[8].strip().upper()
        cai = (r[4].strip().upper() == 'CAI')
        cabang = r[20].strip().upper() if len(r) > 20 else ''
        pros = r[11].strip().upper() if len(r) > 11 else 'MEDIUM'
        
        # Normalize pros
        p_label = 'Medium'
        if 'HOT' in pros: p_label = 'HOT'
        elif 'LOW' in pros: p_label = 'Low'

        # P1: Expired Soon
        if 'EXPIRED SOON' in j:
            if 'NEVER' in j:
                ex_soon['Never claim'][0] += 1
                if cai: ex_soon['Never claim'][1] += 1
            elif 'NOT' in j:
                ex_soon['Not Eligible'][0] += 1
                if cai: ex_soon['Not Eligible'][1] += 1
            else:
                ex_soon['Eligible'][0] += 1
                if cai: ex_soon['Eligible'][1] += 1
        elif 'ACTIVE' in j:
            if 'NEVER' in j:
                active['Never claim'][0] += 1
                if cai: active['Never claim'][1] += 1
            elif 'NOT' in j:
                active['Not Eligible'][0] += 1
                if cai: active['Not Eligible'][1] += 1
            else:
                active['Eligible'][0] += 1
                if cai: active['Eligible'][1] += 1
        elif 'FINISH' in j:
            if 'NOT' in j:
                finish['Not Eligible'][0] += 1
                if cai: finish['Not Eligible'][1] += 1
            else:
                finish['Eligible'][0] += 1
                if cai: finish['Eligible'][1] += 1
        elif 'EXPIRED' in j:
            if 'NEVER' in j:
                expired['Never claim'][0] += 1
                if cai: expired['Never claim'][1] += 1
            elif 'NOT' in j:
                expired['Not Eligible'][0] += 1
                if cai: expired['Not Eligible'][1] += 1
            else:
                expired['Eligible'][0] += 1
                if cai: expired['Eligible'][1] += 1
        elif 'CRT' in j:
            target = crt_merdeka if 'MERDEKA' in cabang else crt_non_merdeka
            target[p_label][0] += 1
            if cai: target[p_label][1] += 1

    def make_group(group_name, title, data_dict, total_label):
        subgroups = []
        tot_pot = 0
        tot_cai = 0
        for lbl, (pot, c) in data_dict.items():
            tot_pot += pot
            tot_cai += c
            pct = round(c / pot * 100, 1) if pot > 0 else 0
            if group_name == "Priority 1":
                full_lbl = f"Expired soon - {lbl}"
            elif group_name == "Priority 2":
                full_lbl = f"Active - {lbl}"
            elif group_name == "Priority 3":
                full_lbl = f"Finish - {lbl}"
            elif group_name == "Priority 4":
                full_lbl = f"Expired - {lbl}"
            else:
                full_lbl = lbl
            subgroups.append({
                "label": full_lbl,
                "potensi": pot,
                "cai": c,
                "pct": pct
            })
        tot_pct = round(tot_cai / tot_pot * 100, 1) if tot_pot > 0 else 0
        res = {
            "group": group_name,
            "subgroups": subgroups,
            "total_label": total_label,
            "total_potensi": tot_pot,
            "total_cai": tot_cai,
            "total_pct": tot_pct
        }
        if title:
            res["title"] = title
        return res

    return [
        make_group("Priority 1", None, ex_soon, "TOTAL EX SOON"),
        make_group("Priority 2", None, active, "TOTAL ACTIVE"),
        make_group("Priority 3", None, finish, "TOTAL FINISH"),
        make_group("Priority 4", None, expired, "TOTAL EXPIRED"),
        make_group("Priority 5", "CRT > 8th Merdeka Motor (Pembelian Asal: MERDEKA — Kolom Judgement Cust)", crt_merdeka, "TOTAL CRT MERDEKA"),
        make_group("Priority 6", "CRT > 8th All Penjualan (Pembelian Asal: Selain Merdeka — Kolom Judgement Cust)", crt_non_merdeka, "TOTAL CRT NON MERDEKA"),
    ]

# Overall
p_overall = build_priority_segments(rows)
print("OVERALL Priority 1:")
print(json.dumps(p_overall[0], indent=2))

# By Period (Q1, Q2, Q3, Monthly)
period_priority = {}
for q in ['1', '2', '3']:
    q_rows = [r for r in rows if len(r) > 0 and r[0].strip() == q]
    period_priority[f"Q{q}"] = build_priority_segments(q_rows)

print("\nQ3 Priority 1:")
print(json.dumps(period_priority["Q3"][0], indent=2))

# Save full results to JSON
with open('data/attacklist_priority_segments.json', 'w') as f:
    json.dump({'overall': p_overall, 'by_period': period_priority}, f, indent=2)

print("\nSuccessfully saved data/attacklist_priority_segments.json")
