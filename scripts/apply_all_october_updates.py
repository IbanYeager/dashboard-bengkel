import json
import sqlite3
import datetime

DASHBOARD_JSON = "data/dashboard_data.json"

OCT_2026_CROSS_SELLING = {
    'DIDIN': [
        {'category': 'CHEMICAL SMM', 'qty': 202, 'revenue': 39329923},
        {'category': 'FULL SYNT', 'qty': 112, 'revenue': 16183125},
        {'category': 'OPL CAR CARE', 'qty': 55, 'revenue': 12882706},
        {'category': 'OPL AC', 'qty': 39, 'revenue': 12301575},
        {'category': 'SPOORING', 'qty': 33, 'revenue': 7881000},
        {'category': 'BATTERY', 'qty': 5, 'revenue': 4756750},
        {'category': 'TIRE', 'qty': 4, 'revenue': 3886920},
        {'category': 'REMATCHING', 'qty': 22, 'revenue': 3663000},
        {'category': 'SMM OIL', 'qty': 11, 'revenue': 875250},
        {'category': 'CROSS SELLING TAM', 'qty': 9, 'revenue': 235200},
    ],
    'FICKY': [
        {'category': 'CHEMICAL SMM', 'qty': 133, 'revenue': 23487532},
        {'category': 'FULL SYNT', 'qty': 125, 'revenue': 19379825},
        {'category': 'OPL CAR CARE', 'qty': 25, 'revenue': 7548197},
        {'category': 'OPL AC', 'qty': 20, 'revenue': 6349200},
        {'category': 'SPOORING', 'qty': 23, 'revenue': 4839600},
        {'category': 'BATTERY', 'qty': 3, 'revenue': 2310750},
        {'category': 'TIRE', 'qty': 3, 'revenue': 2019600},
        {'category': 'REMATCHING', 'qty': 12, 'revenue': 1998000},
        {'category': 'SMM OIL', 'qty': 28, 'revenue': 2360250},
        {'category': 'CROSS SELLING TAM', 'qty': 6.3, 'revenue': 244023},
    ],
    'ACEP': [
        {'category': 'CHEMICAL SMM', 'qty': 137, 'revenue': 24768812},
        {'category': 'FULL SYNT', 'qty': 146, 'revenue': 21479725},
        {'category': 'OPL CAR CARE', 'qty': 38, 'revenue': 10526827},
        {'category': 'OPL AC', 'qty': 26, 'revenue': 10476180},
        {'category': 'SPOORING', 'qty': 28, 'revenue': 6632250},
        {'category': 'BATTERY', 'qty': 8, 'revenue': 5972928},
        {'category': 'TIRE', 'qty': 5, 'revenue': 5550840},
        {'category': 'REMATCHING', 'qty': 28, 'revenue': 4662000},
        {'category': 'SMM OIL', 'qty': 14, 'revenue': 1886500},
        {'category': 'CROSS SELLING TAM', 'qty': 15, 'revenue': 428300},
    ]
}

OCT_2026_SA_TOTALS = [
    {'year': 2026, 'month_name': 'October', 'sa': 'ACEP', 'ue': 166, 'cpus': 137, 'tcare': 71, 'revenue': 250365377},
    {'year': 2026, 'month_name': 'October', 'sa': 'DIDIN', 'ue': 158, 'cpus': 142, 'tcare': 69, 'revenue': 281757579},
    {'year': 2026, 'month_name': 'October', 'sa': 'FICKY', 'ue': 161, 'cpus': 148, 'tcare': 67, 'revenue': 252086835},
]

def main():
    print("Loading", DASHBOARD_JSON)
    with open(DASHBOARD_JSON, 'r', encoding='utf-8') as f:
        data = json.load(f)

    # 1. Update sa_cross_selling for October 2026
    print("1. Updating sa_cross_selling...")
    retained_sa_cross = [
        x for x in data.get('sa_cross_selling', [])
        if not (str(x.get('year')) == '2026' and x.get('month_name') == 'October')
    ]
    new_sa_cross = []
    for sa, items in OCT_2026_CROSS_SELLING.items():
        for item in items:
            new_sa_cross.append({
                'year': 2026,
                'month_name': 'October',
                'sa': sa,
                'category': item['category'],
                'qty': item['qty'],
                'revenue': item['revenue']
            })
    data['sa_cross_selling'] = retained_sa_cross + new_sa_cross
    print(f"  sa_cross_selling now has {len(data['sa_cross_selling'])} records.")

    # 2. Update cross_selling for October 2026
    print("2. Updating cross_selling...")
    retained_cross = [
        x for x in data.get('cross_selling', [])
        if not (str(x.get('year')) == '2026' and x.get('month_name') == 'October')
    ]
    new_cross = []
    for sa, items in sorted(OCT_2026_CROSS_SELLING.items()):
        for item in sorted(items, key=lambda x: x['category']):
            new_cross.append({
                'year': 2026,
                'month_name': 'October',
                'quartal': 4,
                'sa': sa,
                'category': item['category'],
                'qty': item['qty'],
                'revenue': item['revenue']
            })
    data['cross_selling'] = retained_cross + new_cross
    print(f"  cross_selling now has {len(data['cross_selling'])} records.")

    # 3. Update sa_monthly_totals for October 2026
    print("3. Updating sa_monthly_totals...")
    retained_sa_totals = [
        x for x in data.get('sa_monthly_totals', [])
        if not (str(x.get('year')) == '2026' and x.get('month_name') == 'October')
    ]
    data['sa_monthly_totals'] = retained_sa_totals + OCT_2026_SA_TOTALS
    print(f"  sa_monthly_totals now has {len(data['sa_monthly_totals'])} records.")

    # 4. Update meta timestamp
    data['meta']['generated_at'] = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    with open(DASHBOARD_JSON, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    print("Successfully wrote updated", DASHBOARD_JSON)

    # 5. Also update bengkel.db raw_so for consistency
    try:
        conn = sqlite3.connect('data/bengkel.db')
        cur = conn.cursor()
        # Check if the missing TIRE row is already in raw_so
        cur.execute("SELECT COUNT(1) FROM raw_so WHERE wo LIKE '%2610-0456%' AND cross_category='TIRE'")
        exists = cur.fetchone()[0]
        if not exists:
            cur.execute("""
            INSERT INTO raw_so (tanggal, bulan, tahun, month_name, sa, wo, product_type, product_desc, cross_category, type_service, qty, transaction_amount)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, ('17', '10', 2026, 'October', 'DIDIN', '146PKB2610-0456', 'Material', 'DUNLOP ENASAVE EC300+ 215/60 R17', 'TIRE', 'SBE', 2.0, 2896920.0))
            conn.commit()
            print("  Inserted missing DIDIN TIRE transaction into bengkel.db raw_so.")
        conn.close()
    except Exception as e:
        print("  Warning updating sqlite:", e)

if __name__ == '__main__':
    main()
