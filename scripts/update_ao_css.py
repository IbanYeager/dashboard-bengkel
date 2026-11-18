import re

css_code = '''
/* ==========================================================================
   FAITHFUL SPREADSHEET VIEW: DASHBOARD AO REPORT
   100% Pixel-Accurate Google Spreadsheet Aesthetic & Layout
   ========================================================================== */
.ao-sheet-wrapper {
  background: #ffffff;
  padding: 16px 20px 40px 20px;
  font-family: "Segoe UI", -apple-system, BlinkMacSystemFont, Arial, sans-serif;
  color: #000000;
  box-sizing: border-box;
  overflow-x: auto;
}

.ao-sheet-topbar {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 16px;
  padding-bottom: 12px;
  border-bottom: 2px solid #000000;
  gap: 16px;
}

.ao-sheet-title-col {
  display: flex;
  flex-direction: column;
}

.ao-title-row {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 8px;
}

.ao-label-bold {
  font-size: 17px;
  font-weight: 900;
  color: #000000;
  letter-spacing: 0.5px;
}

.ao-colon {
  font-size: 17px;
  font-weight: 900;
  color: #000000;
  margin: 0 4px;
}

.ao-select-pill {
  background: #ffff00;
  border: 1.5px solid #000000;
  padding: 1px 6px;
  display: inline-flex;
  align-items: center;
}

.ao-native-select {
  background: transparent;
  border: none;
  font-size: 13.5px;
  font-weight: 800;
  color: #000000;
  outline: none;
  cursor: pointer;
  padding: 2px;
  font-family: inherit;
}

.ao-callout-yellow {
  background: #ffff00;
  border: 1.5px solid #000000;
  padding: 3px 12px;
  font-size: 12.5px;
  font-weight: 800;
  color: #000000;
  white-space: nowrap;
}

.ao-sync-btn {
  background: #f0fdf4;
  border: 1.5px solid #16a34a;
  color: #166534;
  font-size: 11.5px;
  font-weight: 800;
  padding: 3px 10px;
  cursor: pointer;
  border-radius: 4px;
  display: inline-flex;
  align-items: center;
  gap: 4px;
  transition: all 0.15s;
}

.ao-sync-btn:hover {
  background: #dcfce7;
}

.ao-outlet-name {
  font-size: 16px;
  font-weight: 800;
  color: #000000;
  margin-right: 14px;
}

.ao-year-badge {
  background: #ffff00;
  border: 1.5px solid #000000;
  padding: 2px 12px;
  font-size: 14px;
  font-weight: 800;
  color: #000000;
}

/* CLOSING ESTIMATION BOX (Top Right) */
.ao-closing-est-box {
  border: 2px solid #000000;
  background: #ffffff;
  min-width: 270px;
  box-sizing: border-box;
}

.ao-closing-est-header {
  border-bottom: 1.5px solid #000000;
  padding: 4px 10px;
  font-size: 11px;
  font-weight: 900;
  text-align: center;
  text-transform: uppercase;
  background: #ffffff;
}

.ao-closing-est-body {
  display: flex;
}

.ao-closing-est-col {
  flex: 1;
  padding: 6px 14px;
  text-align: center;
  border-right: 1.5px solid #000000;
}

.ao-closing-est-col.green-bg {
  background: #84e291 !important;
  border-right: none;
}

.ao-closing-est-sub {
  font-size: 9.5px;
  font-weight: 800;
  color: #334155;
  margin-bottom: 2px;
}

.ao-closing-est-val {
  font-size: 24px;
  font-weight: 900;
  line-height: 1.1;
  color: #000000;
}

/* MASTER SPREADSHEET 3-COLUMN GRID */
.ao-sheet-grid {
  display: grid;
  grid-template-columns: 53.5% 8.5% 38%;
  gap: 10px;
  align-items: start;
}

@media (max-width: 1250px) {
  .ao-sheet-grid {
    grid-template-columns: 1fr;
  }
}

.ao-section-title {
  font-size: 12.5px;
  font-weight: 900;
  color: #000000;
  text-transform: uppercase;
  margin-bottom: 6px;
  letter-spacing: 0.3px;
}

.ao-sec1-container {
  display: grid;
  grid-template-columns: 46% 54%;
  gap: 8px;
  align-items: start;
}

/* GENERIC SPREADSHEET TABLE GRID */
.ao-grid-tbl {
  width: 100%;
  border-collapse: collapse;
  border: 1.5px solid #000000;
  font-size: 11px;
  background: #ffffff;
}

.ao-grid-tbl th {
  border: 1px solid #000000;
  padding: 3.5px 5px;
  font-weight: 800;
  color: #000000;
  font-size: 10.5px;
}

.ao-grid-tbl td {
  border: 1px solid #000000;
  padding: 3px 5px;
  color: #000000;
  font-size: 11px;
  font-variant-numeric: tabular-nums;
  text-align: right;
}

.ao-tree-root-val {
  background: #ffffff;
  font-size: 19px;
  font-weight: 900;
  vertical-align: middle;
  text-align: center;
}

.ao-cell-center {
  text-align: center !important;
  vertical-align: middle !important;
}

.ao-tree-blue-pct {
  color: #0070c0;
  font-style: italic;
  font-weight: 700;
  font-size: 10.5px;
  margin-top: 1px;
}

/* AUTHENTIC SPREADSHEET CELL COLORS */
.ao-salmon-cell {
  background: #fae2d6 !important;
  color: #ff0000 !important;
  font-weight: 800 !important;
  text-align: center !important;
}

.ao-green-cell {
  background: #84e291 !important;
  color: #000000 !important;
  font-weight: 800 !important;
  text-align: center !important;
}

.ao-yellow-cell {
  background: #ffff00 !important;
  color: #000000 !important;
  font-weight: 800 !important;
  text-align: center !important;
}

/* CENTER STRIP: VERTICAL KPI COLUMN (COLUMN O) */
.ao-vertical-kpi-tbl {
  border: 2px solid #000000;
  width: 100%;
}

.ao-vkpi-th {
  background: #ffffff;
  border: 1px solid #000000;
  font-size: 9px;
  font-weight: 800;
  padding: 5px 2px;
  text-align: center;
  text-transform: uppercase;
  line-height: 1.2;
}

.ao-vkpi-td {
  border: 1px solid #000000;
  font-size: 16px;
  font-weight: 900;
  padding: 7px 2px;
  text-align: center;
}

.ao-vkpi-td.white-cell {
  background: #ffffff;
  color: #000000;
}

.ao-vkpi-td.salmon-cell {
  background: #fae2d6;
  color: #ff0000;
}

.ao-vkpi-td.blue-cell {
  background: #caedfb;
  color: #000000;
}

/* ACTION PLAN STATUS BADGE */
.ao-status-pill {
  padding: 2px 6px;
  border-radius: 4px;
  font-size: 9.5px;
  font-weight: 800;
  display: inline-block;
  background: #fef3c7;
  color: #b45309;
  border: 1px solid #fde68a;
  text-transform: lowercase;
}
'''

with open('assets/css/style.css', 'r', encoding='utf-8') as f:
    orig_css = f.read()

# Replace previous ao styling or append
ao_css_pattern = re.compile(r'/\* ==========================================================================\s+AO REPORT GR.*?(\Z)', re.DOTALL)
if ao_css_pattern.search(orig_css):
    new_css = ao_css_pattern.sub(css_code, orig_css)
else:
    new_css = orig_css + '\n' + css_code

with open('assets/css/style.css', 'w', encoding='utf-8') as f:
    f.write(new_css)

print("Updated assets/css/style.css with authentic spreadsheet styles!")
