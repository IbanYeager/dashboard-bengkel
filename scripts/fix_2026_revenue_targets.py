import json
import sqlite3

# Target Revenue from Dashboard AFS Kiaracondong-start 2024.xlsx (sheet TARGET)
# Formula: Target CPUS * 1,500,000
AFS_2026_TARGETS = {
    'January':   {'cpus': 675, 'revenue_total': 1012500000.0},
    'February':  {'cpus': 635, 'revenue_total':  952500000.0},
    'March':     {'cpus': 683, 'revenue_total': 1024500000.0},
    'April':     {'cpus': 717, 'revenue_total': 1075500000.0},
    'May':       {'cpus': 633, 'revenue_total':  949500000.0},
    'June':      {'cpus': 695, 'revenue_total': 1042500000.0},
    'July':      {'cpus': 750, 'revenue_total': 1125000000.0},
    'August':    {'cpus': 591, 'revenue_total':  886500000.0},
    'September': {'cpus': 690, 'revenue_total': 1035000000.0},
    'October':   {'cpus': 714, 'revenue_total': 1071000000.0},
    'November':  {'cpus': 676, 'revenue_total': 1014000000.0},
    'December':  {'cpus': 750, 'revenue_total': 1125000000.0}
}

# 1. Update data/dashboard_data.json
json_path = 'data/dashboard_data.json'
with open(json_path, 'r', encoding='utf-8') as f:
    data = json.load(f)

targets_2026 = data.get('targets', {}).get('2026', {})
print("=== UPDATING 2026 TARGETS IN dashboard_data.json ===")
for m, vals in AFS_2026_TARGETS.items():
    if m in targets_2026:
        old_rev = targets_2026[m].get('revenue_total', 0)
        targets_2026[m]['revenue_total'] = vals['revenue_total']
        targets_2026[m]['cpus'] = vals['cpus']
        print(f"  {m:<10}: Old Rev Tgt={old_rev/1e6:>7.1f}M -> New Rev Tgt={vals['revenue_total']/1e6:>7.1f}M (CPUS Tgt={vals['cpus']})")

with open(json_path, 'w', encoding='utf-8') as f:
    json.dump(data, f, indent=2, ensure_ascii=False)
print("[OK] dashboard_data.json updated successfully.")

# 2. Update bengkel.db targets table
db_path = 'data/bengkel.db'
try:
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    for m, vals in AFS_2026_TARGETS.items():
        cur.execute("""
            UPDATE targets 
            SET rev_total_target = ?, cpus_target = ?
            WHERE year = 2026 AND month_name = ?
        """, (vals['revenue_total'], vals['cpus'], m))
    conn.commit()
    conn.close()
    print("[OK] bengkel.db targets table updated successfully.")
except Exception as e:
    print(f"[WARN] bengkel.db update: {e}")

# 3. Print comparison against actuals
print("\n=== VERIFICATION: 2026 ACTUALS VS NEW TARGETS ===")
monthly_kpis = data.get('monthly_kpis', {}).get('2026', {})
for m, vals in AFS_2026_TARGETS.items():
    act = monthly_kpis.get(m, {})
    act_rev = (act.get('total_revenue') or act.get('cpus_revenue') or 0)
    tgt_rev = vals['revenue_total']
    achieve = (act_rev / tgt_rev * 100) if tgt_rev > 0 else 0
    status = "DI ATAS TARGET ✓" if act_rev >= tgt_rev else ("Bulan Berjalan" if m == 'September' else "Di Bawah Target")
    print(f"  {m:<10}: Aktual={act_rev/1e6:>7.1f}M vs Target={tgt_rev/1e6:>7.1f}M | Pencapaian={achieve:>5.1f}% -> {status}")
