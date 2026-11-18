#!/usr/bin/env python3
"""
Sync ao_report_data.json with live Google Sheets AO Report spreadsheet.
Parses the exact values from the spreadsheet CSV and updates the JSON.
"""
import csv, io, json, re

AO_CSV = r"C:\Users\HP\.gemini\antigravity-ide\brain\789226ba-a5f1-4894-af21-94487dd8f2a1\.system_generated\steps\7\content.md"
AO_JSON = r"c:\laragon\www\dashboard_bengkel\data\ao_report_data.json"

with open(AO_CSV, 'r', encoding='utf-8') as f:
    ao_content = f.read()
ao_idx = ao_content.index('---')
ao_text = ao_content[ao_idx+4:].strip()

ao_reader = csv.reader(io.StringIO(ao_text))
ao_rows = list(ao_reader)

def safe_int(s):
    try:
        s = s.strip().replace(',', '').replace('%', '').replace(' ', '')
        if not s or s in ['-', '#REF!', '#N/A', '']:
            return None
        return int(float(s))
    except:
        return None

def safe_pct(s):
    try:
        s = s.strip().replace('%', '').replace(' ', '')
        return int(float(s))
    except:
        return None

def extract_week_values(row, start_col, count=5):
    """Extract numeric values from row starting at start_col."""
    vals = []
    for i in range(start_col, min(start_col + count, len(row))):
        v = safe_int(row[i])
        if v is not None:
            vals.append(v)
        else:
            vals.append(0)
    return vals

# Helper to find row containing a specific text
def find_row(text, rows, start=0):
    for i in range(start, len(rows)):
        joined = ','.join(rows[i])
        if text in joined:
            return i, rows[i]
    return None, None

# Load existing AO JSON
with open(AO_JSON, 'r', encoding='utf-8') as f:
    ao_data = json.load(f)

print("Parsing AO Report spreadsheet...")
print(f"Total rows: {len(ao_rows)}")

# ── Section 1: Target Setting & Weekly Performance ─────────────────────────

# Parse TOTAL CPUS ACTUAL (row 14 in spreadsheet, 0-indexed)
# Structure: col 6="TOTAL CPUS ACTUAL", cols 8-12 = W1..W5
wp = ao_data['section_1_target_setting']['weekly_performance']

# TOTAL CPUS PLAN (row 12)
idx, row = find_row('TOTAL CPUS PLAN', ao_rows)
if row:
    print(f"\nTOTAL CPUS PLAN found at row {idx}: extracting from col 8")
    vals = extract_week_values(row, 8, 5)
    total = safe_int(row[13]) if len(row) > 13 else None
    print(f"  Plan: {vals}, total from row: {total}")
    # The plan total is shown separately on a different row
    
# TOTAL CPUS ACTUAL
idx, row = find_row('TOTAL CPUS ACTUAL', ao_rows)
if row:
    vals = extract_week_values(row, 8, 5)
    print(f"\nTOTAL CPUS ACTUAL: {vals}")
    old = wp['total_cpus_actual']
    wp['total_cpus_actual'] = vals
    print(f"  Updated: {old} -> {vals}")
    
    # Calculate total
    wp['total_cpus_actual_total'] = sum(vals)

# TOTAL GAP
idx, row = find_row('TOTAL GAP', ao_rows)
if row:
    vals = extract_week_values(row, 8, 5)
    print(f"TOTAL GAP: {vals}")
    wp['total_gap'] = vals

# COMMULATIVE GAP CPUS
idx, row = find_row('COMMULATIVE GAP CPUS', ao_rows)
if row:
    vals = extract_week_values(row, 8, 5)
    print(f"COMMULATIVE GAP CPUS: {vals}")
    wp['cumulative_gap_cpus'] = vals

# WALK-IN ACTUAL
idx, row = find_row('WALK-IN ACTUAL', ao_rows)
if row:
    vals = extract_week_values(row, 8, 5)
    print(f"WALK-IN ACTUAL: {vals}")
    old = wp['walkin_actual']
    wp['walkin_actual'] = vals
    print(f"  Updated: {old} -> {vals}")

# WALK-IN GAP  
idx, row = find_row('GAP', ao_rows, 17)  # After walk-in section
if idx and idx < 22:
    # Actually, let's find specific row 19 which has walk-in gap
    pass

# Find walk-in gap specifically
for i in range(16, 25):
    if i < len(ao_rows):
        joined = ','.join(ao_rows[i])
        if 'GAP' in joined and 'COMMULATIVE' not in joined and 'CPUS' not in joined:
            vals = extract_week_values(ao_rows[i], 8, 5)
            if any(v != 0 for v in vals):
                print(f"WALK-IN GAP (row {i}): {vals}")
                wp['walkin_gap'] = vals
                break

# COMMULATIVE GAP WALK-IN
idx, row = find_row('COMMULATIVE GAP WALK-IN', ao_rows)
if row:
    vals = extract_week_values(row, 8, 5)
    print(f"COMMULATIVE GAP WALK-IN: {vals}")
    wp['cumulative_gap_walkin'] = vals

# BOOKING SHOW ACTUAL
idx, row = find_row('BOOKING SHOW ACTUAL', ao_rows)
if row:
    vals = extract_week_values(row, 8, 5)
    print(f"BOOKING SHOW ACTUAL: {vals}")
    old = wp['booking_show_actual']
    wp['booking_show_actual'] = vals
    wp['booking_show_actual_total'] = sum(vals)
    print(f"  Updated: {old} -> {vals}")

# BOOKING SHOW GAP
idx2, row2 = find_row('GAP', ao_rows, idx+1 if idx else 50)
if idx2 and idx2 < (idx or 0) + 5:
    vals = extract_week_values(row2, 8, 5)
    if any(v != 0 for v in vals):
        print(f"BOOKING SHOW GAP (row {idx2}): {vals}")
        wp['booking_show_gap'] = vals
        wp['booking_show_gap_total'] = sum(vals)

# CUMULATIVE GAP BOOKING SHOW
idx, row = find_row('COMMULATIVE GAP BOOKING SHOW', ao_rows)
if row:
    vals = extract_week_values(row, 8, 5)
    print(f"COMMULATIVE GAP BOOKING SHOW: {vals}")
    wp['booking_show_gap_cumulative'] = vals

# NO SHOW ACTUAL
idx, row = find_row('NO SHOW ACTUAL', ao_rows)
if row:
    vals = extract_week_values(row, 8, 5)
    print(f"NO SHOW ACTUAL: {vals}")
    old = wp['no_show_actual']
    wp['no_show_actual'] = vals
    wp['no_show_actual_total'] = sum(vals)
    print(f"  Updated: {old} -> {vals}")

# NO SHOW RATIO
idx, row = find_row('NO SHOW RATIO', ao_rows)
if row:
    pcts = []
    for i in range(8, min(13, len(row))):
        v = row[i].strip()
        if v:
            pcts.append(v)
        else:
            pcts.append('0%')
    print(f"NO SHOW RATIO: {pcts}")
    wp['no_show_ratio'] = pcts

# CUMULATIVE NO-SHOW
idx, row = find_row('COMMULATIVE NO-SHOW', ao_rows)
if row:
    vals = extract_week_values(row, 8, 5)
    print(f"COMMULATIVE NO-SHOW: {vals}")
    wp['cumulative_no_show'] = vals
    wp['cumulative_no_show_total'] = sum(vals) if vals else 0

# BOOKING ACTUAL (not booking show)
idx, row = find_row('BOOKING ACTUAL', ao_rows)
if row:
    vals = extract_week_values(row, 8, 5)
    print(f"BOOKING ACTUAL: {vals}")
    old = wp['booking_actual']
    wp['booking_actual'] = vals
    wp['booking_actual_total'] = sum(vals)
    print(f"  Updated: {old} -> {vals}")

# BOOKING GAP
idx2, row2 = find_row('GAP', ao_rows, idx+1 if idx else 60)
if idx2 and idx2 < (idx or 0) + 5:
    vals = extract_week_values(row2, 8, 5)
    if any(v != 0 for v in vals):
        print(f"BOOKING GAP (row {idx2}): {vals}")
        wp['booking_gap'] = vals
        wp['booking_gap_total'] = sum(vals)

# CUMULATIVE GAP BOOKING
idx, row = find_row('COMMULATIVE GAP BOOKING', ao_rows)
if row and 'SHOW' not in ','.join(row):
    vals = extract_week_values(row, 8, 5)
    print(f"COMMULATIVE GAP BOOKING: {vals}")
    wp['cumulative_gap_booking'] = vals

# NEXT MONTH BOOKING  
idx, row = find_row('NEXT MONTH BOOKING', ao_rows)
if row:
    val = safe_int(row[10]) if len(row) > 10 else None
    if val:
        print(f"NEXT MONTH BOOKING: {val}")

# ── Update cumulative chart ───────────────────────────────────────────────
# CPUS TARGET COMMULATIVE
idx, row = find_row('CPUS TARGET COMMULATIVE', ao_rows)
if row:
    vals = extract_week_values(row, 8, 5)
    print(f"\nCPUS TARGET COMMULATIVE: {vals}")
    ao_data['section_1_target_setting']['cumulative_chart']['target'] = vals

# CPUS ACTUAL COMMULATIVE
idx, row = find_row('CPUS ACTUAL COMMULATIVE', ao_rows)
if row:
    vals = extract_week_values(row, 8, 5)
    print(f"CPUS ACTUAL COMMULATIVE: {vals}")
    ao_data['section_1_target_setting']['cumulative_chart']['actual'] = vals

# ── Update summary ────────────────────────────────────────────────────────
total_cpus_actual = wp['total_cpus_actual']
total_actual = sum(total_cpus_actual)
total_walkin = sum(wp['walkin_actual'])
total_booking = sum(wp['booking_show_actual'])

ao_data['summary']['act_cpus_walkin_fm'] = total_walkin
ao_data['summary']['act_cpus_booking_fm'] = total_booking

# Recalculate gap
target = ao_data['summary']['closing_commitment']
ao_data['summary']['total_cpus_gap_fm'] = total_actual - target
ao_data['summary']['gap_cpus_walkin_fm'] = total_walkin - ao_data['section_1_target_setting']['kpi_tree']['walk_in']['target']
ao_data['summary']['gap_cpus_booking_fm'] = total_booking - ao_data['section_1_target_setting']['kpi_tree']['booking_show']['target']

# ── Mini week performance update ──────────────────────────────────────────
# W3 actual = total_cpus_actual[2] (index 2)
# vs_tar = actual W3 / plan W3
w3_actual = total_cpus_actual[2] if len(total_cpus_actual) > 2 else 0
w3_plan = wp['total_cpus_plan'][2] if len(wp.get('total_cpus_plan', [])) > 2 else 160

ao_data['section_1_target_setting']['mini_week_performance']['actual'] = w3_actual
if w3_plan > 0:
    ao_data['section_1_target_setting']['mini_week_performance']['vs_tar'] = f"{round(w3_actual/w3_plan*100)}%"

# ── Section 2: Prospecting Funneling ──────────────────────────────────────
print("\n\nParsing Section 2: Service Prospecting Management...")

sect2 = ao_data['section_2_prospecting_funneling']

# TCARE section (right side of spreadsheet, starting col 17)
# Parse TCARE DATA
for i, row in enumerate(ao_rows):
    joined = ','.join(row[:23])
    
    # TCARE DATA actual
    if i >= 4 and i <= 8:
        # Row 5 (0-indexed): TCARE DATA with ACTUAL
        if len(row) > 22 and 'ACTUAL' in row[17]:
            vals = extract_week_values(row, 18, 5)
            total_val = safe_int(row[23]) if len(row) > 23 else sum(vals)
            print(f"  TCARE DATA ACTUAL: {vals}, total={total_val}")
            sect2['tcare']['data']['actual'] = vals
            sect2['tcare']['data']['actual_total'] = total_val if total_val else sum(vals)
        
        # VS TAR
        if len(row) > 22 and 'VS TAR' in row[17]:
            pcts = []
            for j in range(18, min(23, len(row))):
                v = safe_pct(row[j])
                pcts.append(v if v is not None else 0)
            print(f"  TCARE DATA VS TAR: {pcts}")
            sect2['tcare']['data']['vs_tar_weeks'] = pcts

# Parse from specific known rows based on spreadsheet structure
# TCARE section starts at column 16 (0-indexed)
# Row by row parsing for the funnel section

def parse_funnel_block(label, start_search, col_offset=17):
    """Parse a funnel block (DATA/CONNECTED/CONTACTED/BOOKING/BOOKING SHOW)."""
    result = {}
    for i, row in enumerate(ao_rows):
        if len(row) <= col_offset:
            continue
        cell = row[col_offset].strip().upper() if row[col_offset] else ''
        
        if label.upper() in cell:
            # Check if this row has TARGET or ACTUAL
            next_cell = row[col_offset+1].strip() if len(row) > col_offset+1 else ''
            if 'TARGET' in next_cell.upper():
                vals = extract_week_values(row, col_offset+2, 5)
                total = safe_int(row[col_offset+7]) if len(row) > col_offset+7 else sum(vals)
                result['target_weeks'] = vals
                result['target_total'] = total if total else sum(vals)
            elif 'ACTUAL' in next_cell.upper():
                vals = extract_week_values(row, col_offset+2, 5)
                total = safe_int(row[col_offset+7]) if len(row) > col_offset+7 else sum(vals)
                result['actual'] = vals
                result['actual_total'] = total if total else sum(vals)
    return result

# Better approach: parse row by row with the known structure
# The AO spreadsheet has a specific layout, let me parse it more carefully

# TCARE section (columns 16-23)
tcare_funnel = sect2['tcare']
non_tcare_funnel = sect2['non_tcare']

# Parse each row for TCARE and NON-TCARE funnel data
for i, row in enumerate(ao_rows):
    if len(row) < 24:
        continue
    
    # Column 16 or 17 typically has the category label
    label16 = (row[16] or '').strip().upper()
    label17 = (row[17] or '').strip().upper()
    
    # Check for TCARE section indicators (right side, cols ~16-23)
    # DATA row
    if 'ACTUAL' in label17:
        vals = extract_week_values(row, 18, 5)
        total = safe_int(row[23]) if len(row) > 23 else sum(vals)
        
        # Determine if this is TCARE or NON-TCARE based on nearby rows
        # Check previous rows for section header
        section = None
        for j in range(max(0, i-5), i):
            joined_prev = ','.join(ao_rows[j])
            if 'NON TCARE' in joined_prev.upper():
                section = 'non_tcare'
                break
            elif 'TCARE' in joined_prev.upper() and 'NON' not in joined_prev.upper():
                section = 'tcare'
                break
        
        if section and label16 == '':
            pass  # This is a sub-row, skip complex parsing

    # CONNECTED rows
    if 'CONNECTED' in label16:
        if 'TARGET' in label17:
            vals = extract_week_values(row, 18, 5)
            total = safe_int(row[23]) if len(row) > 23 else sum(vals)
        elif 'ACTUAL' in label17:
            vals = extract_week_values(row, 18, 5)
            total = safe_int(row[23]) if len(row) > 23 else sum(vals)

# Since the spreadsheet structure is complex, let me directly parse the known data
# from the CSV content more carefully

print("\nDirect parsing of AO spreadsheet sections...")

# The spreadsheet layout (0-indexed rows):
# Section II starts around row 3
# TCARE section: rows 5-19 (right half, cols 16-23)
# NON TCARE section: rows 25-41 (right half, cols 16-23)

# Let me re-parse with exact row references from the CSV

# TCARE DATA
for i, row in enumerate(ao_rows):
    if len(row) < 24:
        continue
    
    # TCARE section
    if i == 5:  # DATA row with TARGET
        if 'TARGET' in str(row[17]):
            vals = []
            for j in [18, 19, 20, 21, 22]:
                v = safe_int(row[j])
                vals.append(v if v is not None else 0)
            total = safe_int(row[23])
            print(f"  TCARE DATA TARGET: {vals}, total={total}")
            tcare_funnel['data']['target_total'] = total if total else sum(vals)
    
    if i == 6:  # DATA ACTUAL
        if 'ACTUAL' in str(row[17]):
            vals = []
            for j in [18, 19, 20, 21, 22]:
                v = safe_int(row[j])
                vals.append(v if v is not None else 0)
            total = safe_int(row[23])
            print(f"  TCARE DATA ACTUAL: {vals}, total={total}")
            tcare_funnel['data']['actual'] = vals
            tcare_funnel['data']['actual_total'] = total if total else sum(vals)
    
    if i == 7:  # VS TAR
        if 'VS TAR' in str(row[17]):
            pcts = []
            for j in [18, 19, 20, 21, 22]:
                v = safe_pct(row[j])
                pcts.append(v if v is not None else 0)
            total_pct = safe_pct(row[23])
            print(f"  TCARE DATA VS TAR: {pcts}, total={total_pct}")
            tcare_funnel['data']['vs_tar_weeks'] = pcts
            tcare_funnel['data']['vs_tar_total_pct'] = total_pct if total_pct else 0

    # TCARE CONNECTED
    if i == 8:  # CONNECTED TARGET
        if 'TARGET' in str(row[17]):
            vals = [safe_int(row[j]) or 0 for j in [18,19,20,21,22]]
            total = safe_int(row[23])
            print(f"  TCARE CONNECTED TARGET: {vals}, total={total}")
            tcare_funnel['connected']['target_weeks'] = vals
            tcare_funnel['connected']['target_total'] = total if total else sum(vals)
    
    if i == 9:  # CONNECTED ACTUAL
        if 'ACTUAL' in str(row[17]):
            vals = [safe_int(row[j]) or 0 for j in [18,19,20,21,22]]
            total = safe_int(row[23])
            print(f"  TCARE CONNECTED ACTUAL: {vals}, total={total}")
            tcare_funnel['connected']['actual'] = vals
            tcare_funnel['connected']['actual_total'] = total if total else sum(vals)
    
    if i == 10:  # CONNECTED VS TAR
        if 'VS TAR' in str(row[17]):
            pcts = [safe_pct(row[j]) or 0 for j in [18,19,20,21,22]]
            total_pct = safe_pct(row[23])
            print(f"  TCARE CONNECTED VS TAR: {pcts}")
            tcare_funnel['connected']['vs_tar_weeks'] = pcts
            tcare_funnel['connected']['vs_tar_total_pct'] = total_pct if total_pct else 0

    # TCARE CONTACTED
    if i == 11:  # CONTACTED TARGET
        if 'TARGET' in str(row[17]):
            vals = [safe_int(row[j]) or 0 for j in [18,19,20,21,22]]
            total = safe_int(row[23])
            print(f"  TCARE CONTACTED TARGET: {vals}, total={total}")
            tcare_funnel['contacted']['target_weeks'] = vals
            tcare_funnel['contacted']['target_total'] = total if total else sum(vals)
    
    if i == 12:  # CONTACTED ACTUAL
        if 'ACTUAL' in str(row[17]):
            vals = [safe_int(row[j]) or 0 for j in [18,19,20,21,22]]
            total = safe_int(row[23])
            print(f"  TCARE CONTACTED ACTUAL: {vals}, total={total}")
            tcare_funnel['contacted']['actual'] = vals
            tcare_funnel['contacted']['actual_total'] = total if total else sum(vals)
    
    if i == 13:  # CONTACTED VS TAR
        if 'VS TAR' in str(row[17]):
            pcts = [safe_pct(row[j]) or 0 for j in [18,19,20,21,22]]
            total_pct = safe_pct(row[23])
            print(f"  TCARE CONTACTED VS TAR: {pcts}")
            tcare_funnel['contacted']['vs_tar_weeks'] = pcts
            tcare_funnel['contacted']['vs_tar_total_pct'] = total_pct if total_pct else 0

    # TCARE BOOKING
    if i == 14:  # BOOKING TARGET
        if 'TARGET' in str(row[17]):
            vals = [safe_int(row[j]) or 0 for j in [18,19,20,21,22]]
            total = safe_int(row[23])
            print(f"  TCARE BOOKING TARGET: {vals}, total={total}")
            tcare_funnel['booking']['target_weeks'] = vals
            tcare_funnel['booking']['target_total'] = total if total else sum(vals)
    
    if i == 15:  # BOOKING ACTUAL
        if 'ACTUAL' in str(row[17]):
            vals = [safe_int(row[j]) or 0 for j in [18,19,20,21,22]]
            total = safe_int(row[23])
            print(f"  TCARE BOOKING ACTUAL: {vals}, total={total}")
            tcare_funnel['booking']['actual'] = vals
            tcare_funnel['booking']['actual_total'] = total if total else sum(vals)
    
    if i == 16:  # BOOKING VS TAR
        if 'VS TAR' in str(row[17]):
            pcts = [safe_pct(row[j]) or 0 for j in [18,19,20,21,22]]
            total_pct = safe_pct(row[23])
            print(f"  TCARE BOOKING VS TAR: {pcts}")
            tcare_funnel['booking']['vs_tar_weeks'] = pcts
            tcare_funnel['booking']['vs_tar_total_pct'] = total_pct if total_pct else 0

    # TCARE BOOKING SHOW
    if i == 17:  # BOOKING SHOW TARGET
        if 'TARGET' in str(row[17]):
            vals = [safe_int(row[j]) or 0 for j in [18,19,20,21,22]]
            total = safe_int(row[23])
            print(f"  TCARE BOOKING SHOW TARGET: {vals}, total={total}")
            tcare_funnel['booking_show']['target_weeks'] = vals
            tcare_funnel['booking_show']['target_total'] = total if total else sum(vals)
    
    if i == 18:  # BOOKING SHOW ACTUAL
        if 'ACTUAL' in str(row[17]):
            vals = [safe_int(row[j]) or 0 for j in [18,19,20,21,22]]
            total = safe_int(row[23])
            print(f"  TCARE BOOKING SHOW ACTUAL: {vals}, total={total}")
            tcare_funnel['booking_show']['actual'] = vals
            tcare_funnel['booking_show']['actual_total'] = total if total else sum(vals)
    
    if i == 19:  # BOOKING SHOW VS TAR
        if 'VS TAR' in str(row[17]):
            pcts = [safe_pct(row[j]) or 0 for j in [18,19,20,21,22]]
            total_pct = safe_pct(row[23])
            print(f"  TCARE BOOKING SHOW VS TAR: {pcts}")
            tcare_funnel['booking_show']['vs_tar_weeks'] = pcts
            tcare_funnel['booking_show']['vs_tar_total_pct'] = total_pct if total_pct else 0

# NON-TCARE section (same columns, rows shifted down)
for i, row in enumerate(ao_rows):
    if len(row) < 24:
        continue
    
    # NON-TCARE DATA
    if i == 26:
        if 'TARGET' in str(row[17]):
            vals = [safe_int(row[j]) or 0 for j in [18,19,20,21,22]]
            total = safe_int(row[23])
            print(f"\n  NON-TCARE DATA TARGET: {vals}, total={total}")
            non_tcare_funnel['data']['target_total'] = total if total else sum(vals)
    
    if i == 27:
        if len(row) > 17:
            label = str(row[17]).strip().upper()
        else:
            label = ''
        # Handle multiline: the ACTUAL might be on row 28
    
    if i == 28:
        if 'ACTUAL' in str(row[17]):
            vals = [safe_int(row[j]) or 0 for j in [18,19,20,21,22]]
            total = safe_int(row[23])
            print(f"  NON-TCARE DATA ACTUAL: {vals}, total={total}")
            non_tcare_funnel['data']['actual'] = vals
            non_tcare_funnel['data']['actual_total'] = total if total else sum(vals)
    
    if i == 29:
        if 'VS TAR' in str(row[17]):
            pcts = [safe_pct(row[j]) or 0 for j in [18,19,20,21,22]]
            total_pct = safe_pct(row[23])
            print(f"  NON-TCARE DATA VS TAR: {pcts}")
            non_tcare_funnel['data']['vs_tar_weeks'] = pcts
            non_tcare_funnel['data']['vs_tar_total_pct'] = total_pct if total_pct else 0

    # NON-TCARE CONNECTED
    if i == 30:
        if 'TARGET' in str(row[17]):
            vals = [safe_int(row[j]) or 0 for j in [18,19,20,21,22]]
            total = safe_int(row[23])
            print(f"  NON-TCARE CONNECTED TARGET: {vals}, total={total}")
            non_tcare_funnel['connected']['target_weeks'] = vals
            non_tcare_funnel['connected']['target_total'] = total if total else sum(vals)
    
    if i == 31:
        if 'ACTUAL' in str(row[17]):
            vals = [safe_int(row[j]) or 0 for j in [18,19,20,21,22]]
            total = safe_int(row[23])
            print(f"  NON-TCARE CONNECTED ACTUAL: {vals}, total={total}")
            non_tcare_funnel['connected']['actual'] = vals
            non_tcare_funnel['connected']['actual_total'] = total if total else sum(vals)
    
    if i == 32:
        if 'VS TAR' in str(row[17]):
            pcts = [safe_pct(row[j]) or 0 for j in [18,19,20,21,22]]
            total_pct = safe_pct(row[23])
            print(f"  NON-TCARE CONNECTED VS TAR: {pcts}")
            non_tcare_funnel['connected']['vs_tar_weeks'] = pcts
            non_tcare_funnel['connected']['vs_tar_total_pct'] = total_pct if total_pct else 0

    # NON-TCARE CONTACTED
    if i == 33:
        if 'TARGET' in str(row[17]):
            vals = [safe_int(row[j]) or 0 for j in [18,19,20,21,22]]
            total = safe_int(row[23])
            print(f"  NON-TCARE CONTACTED TARGET: {vals}, total={total}")
            non_tcare_funnel['contacted']['target_weeks'] = vals
            non_tcare_funnel['contacted']['target_total'] = total if total else sum(vals)
    
    if i == 34:
        if 'ACTUAL' in str(row[17]):
            vals = [safe_int(row[j]) or 0 for j in [18,19,20,21,22]]
            total = safe_int(row[23])
            print(f"  NON-TCARE CONTACTED ACTUAL: {vals}, total={total}")
            non_tcare_funnel['contacted']['actual'] = vals
            non_tcare_funnel['contacted']['actual_total'] = total if total else sum(vals)
    
    if i == 35:
        if 'VS TAR' in str(row[17]):
            pcts = [safe_pct(row[j]) or 0 for j in [18,19,20,21,22]]
            total_pct = safe_pct(row[23])
            print(f"  NON-TCARE CONTACTED VS TAR: {pcts}")
            non_tcare_funnel['contacted']['vs_tar_weeks'] = pcts
            non_tcare_funnel['contacted']['vs_tar_total_pct'] = total_pct if total_pct else 0

    # NON-TCARE BOOKING
    if i == 36:
        if 'TARGET' in str(row[17]):
            vals = [safe_int(row[j]) or 0 for j in [18,19,20,21,22]]
            total = safe_int(row[23])
            print(f"  NON-TCARE BOOKING TARGET: {vals}, total={total}")
            non_tcare_funnel['booking']['target_weeks'] = vals
            non_tcare_funnel['booking']['target_total'] = total if total else sum(vals)
    
    if i == 37:
        if 'ACTUAL' in str(row[17]):
            vals = [safe_int(row[j]) or 0 for j in [18,19,20,21,22]]
            total = safe_int(row[23])
            print(f"  NON-TCARE BOOKING ACTUAL: {vals}, total={total}")
            non_tcare_funnel['booking']['actual'] = vals
            non_tcare_funnel['booking']['actual_total'] = total if total else sum(vals)
    
    if i == 38:
        if 'VS TAR' in str(row[17]):
            pcts = [safe_pct(row[j]) or 0 for j in [18,19,20,21,22]]
            total_pct = safe_pct(row[23])
            print(f"  NON-TCARE BOOKING VS TAR: {pcts}")
            non_tcare_funnel['booking']['vs_tar_weeks'] = pcts
            non_tcare_funnel['booking']['vs_tar_total_pct'] = total_pct if total_pct else 0

    # NON-TCARE BOOKING SHOW
    if i == 39:
        if 'TARGET' in str(row[17]):
            vals = [safe_int(row[j]) or 0 for j in [18,19,20,21,22]]
            total = safe_int(row[23])
            print(f"  NON-TCARE BOOKING SHOW TARGET: {vals}, total={total}")
            non_tcare_funnel['booking_show']['target_weeks'] = vals
            non_tcare_funnel['booking_show']['target_total'] = total if total else sum(vals)
    
    if i == 40:
        if 'ACTUAL' in str(row[17]):
            vals = [safe_int(row[j]) or 0 for j in [18,19,20,21,22]]
            total = safe_int(row[23])
            print(f"  NON-TCARE BOOKING SHOW ACTUAL: {vals}, total={total}")
            non_tcare_funnel['booking_show']['actual'] = vals
            non_tcare_funnel['booking_show']['actual_total'] = total if total else sum(vals)
    
    if i == 41:
        if 'VS TAR' in str(row[17]):
            pcts = [safe_pct(row[j]) or 0 for j in [18,19,20,21,22]]
            total_pct = safe_pct(row[23])
            print(f"  NON-TCARE BOOKING SHOW VS TAR: {pcts}")
            non_tcare_funnel['booking_show']['vs_tar_weeks'] = pcts
            non_tcare_funnel['booking_show']['vs_tar_total_pct'] = total_pct if total_pct else 0

# ── Section 3: SBI ────────────────────────────────────────────────────────
print("\n\nParsing Section 3: SBI T-Care/T-Care Light...")
sect3 = ao_data['section_3_sbi']

# SBI data - NCS section around rows 46-50
# Target rate badge
for i, row in enumerate(ao_rows):
    if len(row) < 24:
        continue
    
    # NCS section
    if i == 46:  # NCS M-1 TARGET
        if 'NCS M-1' in str(row[17]):
            vals = [safe_int(row[j]) or 0 for j in [18,19,20,21,22]]
            total = safe_int(row[23])
            print(f"  SBI NCS M-1 TARGET: {vals}, total={total}")
            sect3['target']['ncs_m1'] = vals
            sect3['target']['ncs_m1_total'] = total if total else sum(vals)
    
    if i == 47:  # NOT CAI TARGET
        if 'NOT CAI' in str(row[17]):
            vals = [safe_int(row[j]) or 0 for j in [18,19,20,21,22]]
            total = safe_int(row[23])
            print(f"  SBI NOT CAI TARGET: {vals}, total={total}")
            sect3['target']['not_cai'] = vals
            sect3['target']['not_cai_total'] = total if total else sum(vals)
    
    if i == 48:  # TOTAL TARGET
        if 'TOTAL' in str(row[17]):
            vals = [safe_int(row[j]) or 0 for j in [18,19,20,21,22]]
            total = safe_int(row[23])
            print(f"  SBI TOTAL TARGET: {vals}, total={total}")
            sect3['target']['total'] = vals
            sect3['target']['total_total'] = total if total else sum(vals)
    
    if i == 49:  # NCS M-1 ACTUAL
        if 'NCS M-1' in str(row[17]):
            vals = [safe_int(row[j]) or 0 for j in [18,19,20,21,22]]
            total = safe_int(row[23])
            print(f"  SBI NCS M-1 ACTUAL: {vals}, total={total}")
            sect3['actual']['ncs_m1'] = vals
            sect3['actual']['ncs_m1_total'] = total if total else sum(vals)
    
    if i == 50:  # NOT CAI ACTUAL
        if 'NOT CAI' in str(row[17]):
            vals = [safe_int(row[j]) or 0 for j in [18,19,20,21,22]]
            total = safe_int(row[23])
            print(f"  SBI NOT CAI ACTUAL: {vals}, total={total}")
            sect3['actual']['not_cai'] = vals
            sect3['actual']['not_cai_total'] = total if total else sum(vals)
    
    if i == 51:  # TOTAL ACTUAL
        if 'TOTAL' in str(row[17]):
            vals = [safe_int(row[j]) or 0 for j in [18,19,20,21,22]]
            total = safe_int(row[23])
            print(f"  SBI TOTAL ACTUAL: {vals}, total={total}")
            sect3['actual']['total'] = vals
            sect3['actual']['total_total'] = total if total else sum(vals)
    
    if i == 52:  # GAP
        if 'GAP' in str(row[17]):
            vals = [safe_int(row[j]) or 0 for j in [18,19,20,21,22]]
            total = safe_int(row[23])
            print(f"  SBI GAP: {vals}, total={total}")
            sect3['gap']['gap_kumulatif'] = vals
            sect3['gap']['gap_kumulatif_total'] = total if total else sum(vals)

# Target rate badge
for i, row in enumerate(ao_rows):
    if len(row) > 24:
        for j, cell in enumerate(row):
            if '81' in str(cell) and '%' in str(cell) and i >= 45:
                # This might be the target rate badge
                pass

# ── Staircase matrix update ───────────────────────────────────────────────
# Rows 24-42 contain staircase values in columns 10-12
print("\nUpdating staircase matrix...")

# The staircase values are in the rows between Section 1 bottom and Section 2
# They appear in the left portion around cols 10-12

# Parse OIL/GR/SBE counts
for i, row in enumerate(ao_rows):
    joined = ','.join(row)
    if 'OIL' in joined and i >= 30 and i <= 45:
        vals = []
        for j in range(9, min(13, len(row))):
            v = safe_int(row[j])
            if v is not None:
                vals.append(v)
        if vals:
            print(f"  OIL values (row {i}): {vals}")
    
    if i >= 30 and i <= 50 and len(row) > 10:
        if row[6] and 'SBE' in str(row[6]).upper():
            vals = []
            for j in range(8, min(13, len(row))):
                v = safe_int(row[j])
                if v is not None:
                    vals.append(v)
            if vals:
                print(f"  SBE values (row {i}): {vals}")

# ── Save updated AO data ─────────────────────────────────────────────────
print("\n\nSaving updated ao_report_data.json...")
with open(AO_JSON, 'w', encoding='utf-8') as f:
    json.dump(ao_data, f, indent=2, ensure_ascii=False)

print("AO Report sync complete.")

# Final verification
print("\n\nFinal AO Report Verification:")
with open(AO_JSON, 'r', encoding='utf-8') as f:
    final = json.load(f)

wp_final = final['section_1_target_setting']['weekly_performance']
print(f"  CPUS Actual: {wp_final['total_cpus_actual']} (total: {wp_final.get('total_cpus_actual_total')})")
print(f"  Walk-in Actual: {wp_final['walkin_actual']}")
print(f"  Booking Show Actual: {wp_final['booking_show_actual']}")
print(f"  No Show Actual: {wp_final['no_show_actual']}")
print(f"  Booking Actual: {wp_final['booking_actual']}")
print(f"  Cumulative Target: {final['section_1_target_setting']['cumulative_chart']['target']}")
print(f"  Cumulative Actual: {final['section_1_target_setting']['cumulative_chart']['actual']}")
