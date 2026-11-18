#!/usr/bin/env python3
"""
Direct fix for ao_report_data.json using exact values from the AO spreadsheet.
"""
import json

AO_JSON = r"c:\laragon\www\dashboard_bengkel\data\ao_report_data.json"

with open(AO_JSON, 'r', encoding='utf-8') as f:
    ao = json.load(f)

# ═══════════════════════════════════════════════════════════════════════════
# Section 1: Already fixed by previous script. Verify:
# ═══════════════════════════════════════════════════════════════════════════
wp = ao['section_1_target_setting']['weekly_performance']

# Set Section 1 weekly performance values from spreadsheet
wp['total_cpus_actual'] = [99, 182, 188, 0, 0]
wp['walkin_actual'] = [42, 45, 50, 0, 0]
wp['booking_show_actual'] = [57, 137, 138, 0, 0]
wp['no_show_actual'] = [31, 45, 48, 56, 42]
wp['booking_actual'] = [88, 182, 186, 56, 42]

# Fix remaining Section 1 values
wp['total_cpus_actual_total'] = 469
wp['total_gap'] = [26, 22, 28, -160, -160]
wp['cumulative_gap_cpus'] = [26, 48, 76, -85, -245]
wp['walkin_gap'] = [15, -15, -10, -60, -60]
wp['cumulative_gap_walkin'] = [15, -1, -11, -71, -131]
wp['booking_show_actual_total'] = 332
wp['booking_show_gap'] = [11, 37, 38, -100, -100]
wp['booking_show_gap_total'] = -114
wp['booking_show_gap_cumulative'] = [11, 48, 86, -14, -114]
wp['no_show_actual_total'] = 222
wp['no_show_ratio'] = ["35%", "25%", "26%", "100%", "100%"]
wp['no_show_ratio_total'] = "40%"
wp['cumulative_no_show'] = [31, 76, 124, 180, 222]
wp['cumulative_no_show_total'] = 222
wp['booking_actual_total'] = 554
wp['booking_gap'] = [32, 60, 64, -66, -80]
wp['booking_gap_total'] = 10
wp['cumulative_gap_booking'] = [32, 92, 156, 90, 10]

# Cumulative chart
ao['section_1_target_setting']['cumulative_chart']['target'] = [73, 233, 393, 554, 714]
ao['section_1_target_setting']['cumulative_chart']['actual'] = [99, 281, 469, 469, 469]

# Mini week
ao['section_1_target_setting']['mini_week_performance']['actual'] = 188
ao['section_1_target_setting']['mini_week_performance']['vs_tar'] = "118%"
ao['section_1_target_setting']['mini_week_performance']['week'] = "W3"

# Summary
ao['summary']['total_cpus_gap_fm'] = -245   # 469 - 714
ao['summary']['gap_cpus_walkin_fm'] = -131   # 137 - 268
ao['summary']['act_cpus_walkin_fm'] = 137    # W1+W2+W3 = 42+45+50
ao['summary']['gap_cpus_booking_fm'] = -114  # 332 - 446
ao['summary']['act_cpus_booking_fm'] = 332   # W1+W2+W3 = 57+137+138

# Staircase matrix (from spreadsheet rows 24-42, cols 10-12)
ao['section_1_target_setting']['staircase_matrix'] = [
    {"row": 1, "cells": [
        {"col": 4, "val": -49, "type": "neg"},
        {"col": 5, "val": 49, "type": "pos"},
        {"col": 6, "val": -62, "type": "neg"}
    ]},
    {"row": 2, "cells": [
        {"col": 4, "val": -51, "type": "neg"},
        {"col": 5, "val": 51, "type": "pos"},
        {"col": 6, "val": -52, "type": "neg"}
    ]},
    {"row": 3, "cells": [
        {"col": 3, "val": -49, "type": "neg"},
        {"col": 4, "val": 49, "type": "pos"},
        {"col": 5, "val": -13, "type": "neg"}
    ]},
    {"row": 4, "cells": [
        {"col": 3, "val": -51, "type": "neg"},
        {"col": 4, "val": 51, "type": "pos"},
        {"col": 5, "val": -1, "type": "neg"}
    ]},
    {"row": 5, "cells": [
        {"col": 2, "val": -49, "type": "neg"},
        {"col": 3, "val": 49, "type": "pos"},
        {"col": 4, "val": -11, "type": "neg"}  # Fixed from -11
    ]},
    {"row": 6, "cells": [
        {"col": 2, "val": -51, "type": "neg"},
        {"col": 3, "val": 51, "type": "pos"},
        {"col": 4, "val": 39, "type": "pos"}
    ]},
    {"row": 7, "cells": [
        {"col": 1, "val": 18, "type": "pos"},
        {"col": 2, "val": 49, "type": "pos"},
        {"col": 3, "val": 17, "type": "pos"}
    ]},
    {"row": 8, "cells": [
        {"col": 1, "val": 20, "type": "pos"},
        {"col": 2, "val": 51, "type": "pos"},
        {"col": 3, "val": 51, "type": "pos"}
    ]},
    {"row": 9, "cells": [
        {"col": 0, "val": 10, "type": "pos"},
        {"col": 1, "val": 49, "type": "pos"},
        {"col": 2, "val": 36, "type": "pos"}
    ]},
    {"row": 10, "cells": [
        {"col": 0, "val": 27, "type": "pos"},
        {"col": 1, "val": 51, "type": "pos"},
        {"col": 2, "val": 31, "type": "pos"}
    ]}
]

# ═══════════════════════════════════════════════════════════════════════════
# Section 2: Prospecting Funneling - EXACT values from spreadsheet
# ═══════════════════════════════════════════════════════════════════════════
print("Fixing Section 2: Prospecting Funneling...")

# TCARE
tcare = ao['section_2_prospecting_funneling']['tcare']

tcare['data'] = {
    "target_total": 872,
    "actual": [155, 190, 235, 0, 0],
    "actual_total": 580,
    "vs_tar_weeks": [18, 40, 67, 67, 67],
    "vs_tar_total_pct": 67
}

tcare['connected'] = {
    "target_weeks": [160, 192, 192, 192, 128],
    "target_total": 864,
    "actual": [133, 175, 190, 0, 0],
    "actual_total": 498,
    "vs_tar_weeks": [83, 91, 99, 0, 0],
    "vs_tar_total_pct": 58
}

tcare['contacted'] = {
    "target_weeks": [106, 140, 152, 0, 0],
    "target_total": 398,
    "actual": [80, 123, 105, 0, 0],
    "actual_total": 307,  # 80+123+105 = 308, but spreadsheet says 307
    "vs_tar_weeks": [75, 88, 69, 0, 0],
    "vs_tar_total_pct": 77
}

tcare['booking'] = {
    "target_weeks": [54, 67, 54, 67, 24],
    "target_total": 266,
    "actual": [21, 39, 58, 23, 10],
    "actual_total": 130,  # Spreadsheet total column is missing so sum = 151, but sheet says 130
    "vs_tar_weeks": [39, 58, 107, 34, 42],
    "vs_tar_total_pct": 49
}

tcare['booking_show'] = {
    "target_weeks": [23, 51, 51, 51, 51],
    "target_total": 229,
    "actual": [28, 78, 71, 0, 0],
    "actual_total": 177,
    "vs_tar_weeks": [120, 152, 138, 0, 0],
    "vs_tar_total_pct": 77
}

# NON-TCARE
non_tcare = ao['section_2_prospecting_funneling']['non_tcare']

non_tcare['data'] = {
    "target_total": 725,
    "actual": [165, 139, 175, 0, 0],
    "actual_total": 479,
    "vs_tar_weeks": [23, 42, 66, 66, 66],
    "vs_tar_total_pct": 66
}

non_tcare['connected'] = {
    "target_weeks": [118, 142, 142, 142, 95],
    "target_total": 639,
    "actual": [130, 130, 168, 0, 0],
    "actual_total": 428,
    "vs_tar_weeks": [110, 92, 118, 0, 0],
    "vs_tar_total_pct": 67
}

non_tcare['contacted'] = {
    "target_weeks": [83, 99, 99, 99, 67],
    "target_total": 447,
    "actual": [107, 98, 150, 0, 0],
    "actual_total": 354,  # Spreadsheet shows 354
    "vs_tar_weeks": [128, 98, 151, 0, 0],
    "vs_tar_total_pct": 79
}

non_tcare['booking'] = {
    "target_weeks": [27, 59, 59, 59, 59],
    "target_total": 263,
    "actual": [50, 87, 101, 31, 24],
    "actual_total": 293,
    "vs_tar_weeks": [185, 147, 171, 53, 41],
    "vs_tar_total_pct": 111
}

non_tcare['booking_show'] = {
    "target_weeks": [22, 49, 49, 49, 49],
    "target_total": 217,
    "actual": [29, 59, 67, 0, 0],
    "actual_total": 155,
    "vs_tar_weeks": [131, 121, 138, 0, 0],
    "vs_tar_total_pct": 72
}

# ═══════════════════════════════════════════════════════════════════════════
# Section 3: SBI T-Care / T-Care Light
# ═══════════════════════════════════════════════════════════════════════════
print("Fixing Section 3: SBI...")

sect3 = ao['section_3_sbi']
sect3['target_rate_badge'] = "81,82%"
sect3['weight_row'] = ["4,5", "5,5", "4,5", "5,5", "1"]

sect3['target'] = {
    "ncs_m1": [16, 20, 20, 20, 13],
    "ncs_m1_total": 88,
    "not_cai": [5, 4, 3, 2, 2],
    "not_cai_total": 16,
    "total": [21, 24, 23, 22, 15],
    "total_total": 104  # Spreadsheet shows 104
}

sect3['actual'] = {
    "ncs_m1": [9, 13, 19, 0, 0],
    "ncs_m1_total": 41,
    "not_cai": [7, 7, 1, 20, 13],
    "not_cai_total": 47,  # Spreadsheet shows 47
    "total": [16, 20, 20, 20, 13],
    "total_total": 88   # Spreadsheet shows 88
}

sect3['gap'] = {
    "gap_kumulatif": [-5, -4, -3, -2, -2],
    "gap_kumulatif_total": -16
}

# ═══════════════════════════════════════════════════════════════════════════
# Save
# ═══════════════════════════════════════════════════════════════════════════
with open(AO_JSON, 'w', encoding='utf-8') as f:
    json.dump(ao, f, indent=2, ensure_ascii=False)

print("\nAO Report fully synced with spreadsheet.")
print("\nVerification summary:")
print(f"  CPUS Actual: {wp['total_cpus_actual']} = {sum(wp['total_cpus_actual'])}")
print(f"  Walk-in Actual: {wp['walkin_actual']} = {sum(wp['walkin_actual'])}")
print(f"  Booking Show Actual: {wp['booking_show_actual']} = {sum(wp['booking_show_actual'])}")
print(f"  TCARE data actual: {tcare['data']['actual']} = {tcare['data']['actual_total']}")
print(f"  TCARE booking actual: {tcare['booking']['actual']} = {tcare['booking']['actual_total']}")
print(f"  TCARE booking show actual: {tcare['booking_show']['actual']} = {tcare['booking_show']['actual_total']}")
print(f"  NON-TCARE data actual: {non_tcare['data']['actual']} = {non_tcare['data']['actual_total']}")
print(f"  NON-TCARE booking actual: {non_tcare['booking']['actual']} = {non_tcare['booking']['actual_total']}")
print(f"  NON-TCARE booking show actual: {non_tcare['booking_show']['actual']} = {non_tcare['booking_show']['actual_total']}")
print(f"  SBI target total: {sect3['target']['total']} = {sect3['target']['total_total']}")
print(f"  SBI actual total: {sect3['actual']['total']} = {sect3['actual']['total_total']}")
print(f"  Cumulative target: {ao['section_1_target_setting']['cumulative_chart']['target']}")
print(f"  Cumulative actual: {ao['section_1_target_setting']['cumulative_chart']['actual']}")
