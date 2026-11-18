import sqlite3

conn = sqlite3.connect(r"c:\laragon\www\dashboard_bengkel\data\bengkel.db")
cur = conn.cursor()

MONTH_NAMES = [
    'January', 'February', 'March', 'April', 'May', 'June',
    'July', 'August', 'September', 'October', 'November', 'December'
]

sbi_cpus_dict = {
    '2024': {'March': 2, 'April': 14, 'May': 21, 'June': 35, 'July': 37, 'August': 56, 'September': 48, 'October': 70, 'November': 45, 'December': 69},
    '2025': {'January': 20, 'February': 15, 'March': 12, 'April': 15, 'May': 9, 'June': 7, 'July': 11, 'August': 12, 'September': 20, 'October': 20, 'November': 20, 'December': 9},
    '2026': {'January': 13, 'February': 8, 'March': 57, 'April': 63, 'May': 59, 'June': 53, 'July': 73, 'August': 0, 'September': 0, 'October': 0, 'November': 0, 'December': 0}
}

print("=== ACTUAL CPUS (RAW + SBI CPUS) ===")
for yr in ['2024', '2025', '2026']:
    total_raw = 0
    total_sbi = 0
    total_act = 0
    print(f"\n--- YEAR {yr} ---")
    for m in MONTH_NAMES:
        cur.execute("SELECT count(*) FROM raw_pkb WHERE tahun=? AND month_name=? AND type_ue='CPUS'", (int(yr), m))
        raw_cnt = cur.fetchone()[0]
        sbi_cnt = sbi_cpus_dict.get(yr, {}).get(m, 0)
        act_cnt = raw_cnt + sbi_cnt if raw_cnt > 0 else 0
        total_raw += raw_cnt
        total_sbi += sbi_cnt
        total_act += act_cnt
        if act_cnt > 0:
            print(f"  {m:10s}: Raw={raw_cnt:4d} + SBI={sbi_cnt:2d} -> Actual CPUS={act_cnt:4d}")
    print(f"  TOTAL {yr}: Raw={total_raw} + SBI={total_sbi} -> Actual CPUS={total_act}")
