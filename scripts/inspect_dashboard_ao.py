import openpyxl

wb = openpyxl.load_workbook('data/ao_report.xlsx', data_only=True)
ws = wb['Dashboard AO']

print(f'Dashboard AO dimensions: {ws.dimensions}, max_row: {ws.max_row}, max_column: {ws.max_column}')

for r in range(1, min(70, ws.max_row + 1)):
    row_vals = []
    for c in range(1, min(40, ws.max_column + 1)):
        v = ws.cell(row=r, column=c).value
        if v is not None:
            # format numbers
            if isinstance(v, float):
                v_str = f"{v:.2f}" if abs(v) < 1 else f"{v:.1f}"
            else:
                v_str = str(v).strip()
            if v_str:
                row_vals.append(f"C{c}:{v_str}")
    if row_vals:
        print(f"Row {r:2d}: {' | '.join(row_vals[:12])}")
