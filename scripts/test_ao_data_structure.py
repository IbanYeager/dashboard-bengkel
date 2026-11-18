import json

# Let's inspect data from ao_report_data.json
with open('data/ao_report_data.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

print('Summary keys:', data['summary'])
print('Section 1 weekly keys:', list(data['section_1_target_setting']['weekly_performance'].keys()))
print('Section 2 T-Care stages:', list(data['section_2_prospecting_funneling']['tcare'].keys()))
print('Section 2 Non T-Care stages:', list(data['section_2_prospecting_funneling']['non_tcare'].keys()))
print('Section 3 SBI keys:', list(data['section_3_sbi'].keys()))
print('Section 4 Action plan count:', len(data['section_4_action_plan']))
