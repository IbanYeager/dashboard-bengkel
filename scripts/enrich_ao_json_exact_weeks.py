import json

with open('data/ao_report_data.json', 'r', encoding='utf-8') as f:
    d = json.load(f)

# Update T-Care stages with exact weekly arrays
d['section_2_prospecting_funneling']['tcare']['data']['target_weeks'] = [872, 872, 872, 872, 872]
d['section_2_prospecting_funneling']['tcare']['data']['vs_tar_weeks'] = [18, 40, 64, 90, 100]

d['section_2_prospecting_funneling']['tcare']['connected']['target_weeks'] = [160, 192, 192, 192, 128]
d['section_2_prospecting_funneling']['tcare']['connected']['vs_tar_weeks'] = [83, 91, 99, 109, 59]

d['section_2_prospecting_funneling']['tcare']['contacted']['target_weeks'] = [106, 140, 152, 168, 60]
d['section_2_prospecting_funneling']['tcare']['contacted']['vs_tar_weeks'] = [75, 88, 69, 86, 90]

d['section_2_prospecting_funneling']['tcare']['booking']['target_weeks'] = [54, 67, 54, 67, 24]
d['section_2_prospecting_funneling']['tcare']['booking']['vs_tar_weeks'] = [39, 58, 107, 34, 42]

d['section_2_prospecting_funneling']['tcare']['booking_show']['target_weeks'] = [23, 51, 51, 51, 51]
d['section_2_prospecting_funneling']['tcare']['booking_show']['vs_tar_weeks'] = [120, 76, 0, 0, 0]

# Update Non T-Care stages with exact weekly arrays
d['section_2_prospecting_funneling']['non_tcare']['data']['target_weeks'] = [725, 725, 725, 725, 725]
d['section_2_prospecting_funneling']['non_tcare']['data']['vs_tar_weeks'] = [23, 42, 66, 87, 100]

d['section_2_prospecting_funneling']['non_tcare']['connected']['target_weeks'] = [118, 142, 142, 142, 95]
d['section_2_prospecting_funneling']['non_tcare']['connected']['vs_tar_weeks'] = [110, 92, 118, 107, 94]

d['section_2_prospecting_funneling']['non_tcare']['contacted']['target_weeks'] = [83, 99, 99, 99, 67]
d['section_2_prospecting_funneling']['non_tcare']['contacted']['vs_tar_weeks'] = [128, 98, 151, 123, 113]

d['section_2_prospecting_funneling']['non_tcare']['booking']['target_weeks'] = [27, 59, 59, 59, 59]
d['section_2_prospecting_funneling']['non_tcare']['booking']['vs_tar_weeks'] = [170, 88, 49, 53, 41]

d['section_2_prospecting_funneling']['non_tcare']['booking_show']['target_weeks'] = [22, 49, 49, 49, 49]
d['section_2_prospecting_funneling']['non_tcare']['booking_show']['vs_tar_weeks'] = [113, 51, 0, 0, 0]

with open('data/ao_report_data.json', 'w', encoding='utf-8') as f:
    json.dump(d, f, indent=2)

print('Enriched ao_report_data.json successfully with weekly targets and vs_tar!')
