import json

with open('data/dashboard_data.json', 'r', encoding='utf-8') as f:
    d = json.load(f)

print('2026 months in monthly_kpis:', sorted(list(d['monthly_kpis']['2026'].keys())))
print('Jan 2026 UE:', d['monthly_kpis']['2026']['January']['ue_total'], 'Rev:', d['monthly_kpis']['2026']['January']['total_revenue'])
print('Aug 2026 UE:', d['monthly_kpis']['2026']['August']['ue_total'], 'Rev:', d['monthly_kpis']['2026']['August']['total_revenue'])
print('Sep 2026:', d['monthly_kpis']['2026']['September'])

sa_sept = [x for x in d['sa_performance'] if x.get('year') == 2026 and x.get('month_name') == 'September']
print('\nSeptember SA Performance:')
for s in sa_sept:
    print(f"  {s['sa']}: UE={s['ue']}, CPUS={s['cpus']}, Rev=Rp {s['revenue']:,.0f}, T-Care={s['tcare_ue']}, SBE={s['sbe_ue']}")

print('\nws_matrix_kabeng (September col index 8):')
for r in d['ws_matrix_kabeng']['rows']:
    if str(r['no']) in ['1', '2', '5', '7', '8', '12']:
        print(f"  #{r['no']} {r['kpi']}: {r['months'][8]} (Total YTD: {r['total']})")
