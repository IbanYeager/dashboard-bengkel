import sqlite3
import json

def update_sa_cross_data():
    conn = sqlite3.connect('data/bengkel.db')
    cur = conn.cursor()

    # 1. Detailed breakdown: Year, Month, SA, Category, Qty, Revenue (EXCLUDING SYNT and WIPER FLUID)
    cur.execute("""
    SELECT 
        tahun,
        month_name,
        sa,
        cross_category,
        SUM(qty) as total_qty,
        SUM(transaction_amount) as total_revenue
    FROM raw_so
    WHERE cross_category != '' 
      AND cross_category IS NOT NULL 
      AND UPPER(cross_category) NOT IN ('SYNT', 'WIPER FLUID', 'OLI SMM')
      AND sa IN ('DIDIN', 'FICKY', 'ACEP')
    GROUP BY tahun, month_name, sa, cross_category
    ORDER BY tahun, sa, total_revenue DESC
    """)
    rows = cur.fetchall()

    sa_cross_selling = []
    for r in rows:
        sa_cross_selling.append({
            'year': r[0],
            'month_name': r[1],
            'sa': r[2],
            'category': r[3],
            'qty': round(float(r[4] or 0), 1),
            'revenue': round(float(r[5] or 0), 2)
        })

    # 2. Total revenue per SA per month from raw_pkb (for contribution %)
    cur.execute("""
    SELECT 
        tahun,
        month_name,
        sa,
        COUNT(*) as total_ue,
        COUNT(CASE WHEN type_ue = 'CPUS' THEN 1 END) as total_cpus,
        COUNT(CASE WHEN tcare_national = 't-care' THEN 1 END) as total_tcare,
        SUM(revenue) as total_revenue
    FROM raw_pkb
    WHERE sa IN ('DIDIN', 'FICKY', 'ACEP')
    GROUP BY tahun, month_name, sa
    """)
    sa_rev_rows = cur.fetchall()
    sa_total_revenue = []
    for r in sa_rev_rows:
        sa_total_revenue.append({
            'year': r[0],
            'month_name': r[1],
            'sa': r[2],
            'ue': int(r[3] or 0),
            'cpus': int(r[4] or 0),
            'tcare': int(r[5] or 0),
            'revenue': round(float(r[6] or 0), 2)
        })

    with open('data/dashboard_data.json', 'r', encoding='utf-8') as f:
        data = json.load(f)

    data['sa_cross_selling'] = sa_cross_selling
    data['sa_monthly_totals'] = sa_total_revenue

    with open('data/dashboard_data.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2)

    print(f"Successfully added {len(sa_cross_selling)} sa_cross_selling records (excluding SYNT & WIPER FLUID) and {len(sa_total_revenue)} sa_monthly_totals records to data/dashboard_data.json.")
    conn.close()

if __name__ == '__main__':
    update_sa_cross_data()
