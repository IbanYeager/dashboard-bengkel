import json

with open(r'c:\laragon\www\dashboard_bengkel\data\dashboard_data.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

print('=== dashboard_data.json CURRENT VALUES ===')
for mn in ['January','February','March','April','May','June','July','August','September','October']:
    d = data['monthly_kpis']['2026'].get(mn, {})
    ue = d.get('ue_total')
    cpus = d.get('cpus')
    sbe = d.get('sbe_count')
    tcare = d.get('tcare_count')
    rev = d.get('total_revenue')
    print(f'  {mn}: UE={ue} CPUS={cpus} SBE={sbe} T-Care={tcare} Revenue={rev}')

with open(r'c:\laragon\www\dashboard_bengkel\data\ao_report_data.json', 'r', encoding='utf-8') as f:
    ao = json.load(f)

print()
print('=== ao_report_data.json CURRENT VALUES ===')
wp = ao['section_1_target_setting']['weekly_performance']
print('  CPUS Actual:', wp['total_cpus_actual'])
print('  Walk-in Actual:', wp['walkin_actual'])
print('  Booking Show Actual:', wp['booking_show_actual'])
print('  No Show Actual:', wp['no_show_actual'])
print('  Booking Actual:', wp['booking_actual'])
print('  Cumulative Actual:', ao['section_1_target_setting']['cumulative_chart']['actual'])
print()
print('  TCARE booking actual:', ao['section_2_prospecting_funneling']['tcare']['booking']['actual'])
print('  TCARE booking show actual:', ao['section_2_prospecting_funneling']['tcare']['booking_show']['actual'])
print('  NON-TCARE booking actual:', ao['section_2_prospecting_funneling']['non_tcare']['booking']['actual'])
print('  NON-TCARE booking show actual:', ao['section_2_prospecting_funneling']['non_tcare']['booking_show']['actual'])
print()
print('  SBI target total:', ao['section_3_sbi']['target']['total'])
print('  SBI actual total:', ao['section_3_sbi']['actual']['total'])
