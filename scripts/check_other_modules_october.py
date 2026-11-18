import json
import os

files_to_check = [
    'data/booking_data.json',
    'data/sbi_data.json',
    'data/tcare_data.json',
    'data/ao_data.json'
]

for fpath in files_to_check:
    if not os.path.exists(fpath):
        print(f"File {fpath} does NOT exist!")
        continue
    with open(fpath, 'r', encoding='utf-8') as f:
        data = json.load(f)
    print(f"\n==================== {fpath} ====================")
    if 'booking_data' in fpath:
        print("Channels in booking_data:", list(data.get('channels', {}).keys()))
        for ch, ch_data in data.get('channels', {}).items():
            monthly = ch_data.get('monthly', {})
            print(f"  {ch} monthly: {monthly}")
        print("TikTok Live monthly_trend:", data.get('tiktok_live', {}).get('monthly_trend', []))
    elif 'sbi_data' in fpath:
        print("SBI summary keys:", list(data.keys())[:10])
        monthly_2026 = data.get('monthly_2026', {})
        print("SBI monthly_2026:", monthly_2026)
        if 'monthly' in data:
            print("SBI monthly:", data.get('monthly'))
        if 'summary' in data:
            print("SBI summary:", data.get('summary'))
    elif 'tcare_data' in fpath:
        print("TCARE keys:", list(data.keys())[:10])
        if 'monthly' in data:
            print("TCARE monthly:", data.get('monthly'))
        if 'summary' in data:
            print("TCARE summary:", data.get('summary'))
    elif 'ao_data' in fpath:
        print("AO keys:", list(data.keys())[:10])
        if 'monthly' in data:
            print("AO monthly:", data.get('monthly'))
        if 'by_month' in data:
            print("AO by_month keys:", list(data.get('by_month', {}).keys()))
