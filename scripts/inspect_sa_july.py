import json

with open('data/dashboard_data.json', 'r', encoding='utf-8') as f:
    d = json.load(f)

print("SA Keys in dashboard_data.json:")
for k in d.keys():
    if 'sa' in k.lower():
        print(f"  {k}: type={type(d[k])}")

# Check sa_monthly or similar
if 'sa_performance' in d:
    sa_perf = d['sa_performance']
    print("\nSA Performance 2026:")
    if isinstance(sa_perf, dict):
        for sa_name, val in sa_perf.items():
            print(f"  SA: {sa_name}")
            if isinstance(val, dict):
                for sub_k, sub_v in val.items():
                    print(f"    {sub_k}: {sub_v}")

if 'sa_cross_selling' in d:
    print("\nSA cross selling available.")

# Check radar or monthly SA breakdown
if 'sa_monthly' in d:
    print("\nsa_monthly:", d['sa_monthly'])
