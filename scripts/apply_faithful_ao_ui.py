import re

# 1. READ INDEX.HTML
with open('index.html', 'r', encoding='utf-8') as f:
    html = f.read()

# Define faithful pane-ao markup
faithful_pane_ao = '''  <!-- TAB: AO REPORT GR (EXACT GOOGLE SPREADSHEET LAYOUT) -->
  <div id="pane-ao" class="tab-pane-container">
    <div class="ao-sheet-wrapper">
      <!-- 1. Header Top Bar matching Spreadsheet Rows 1-3 -->
      <div class="ao-sheet-topbar">
        <div class="ao-sheet-title-col">
          <div class="ao-title-row">
            <span class="ao-label-bold">AO REPORT GR</span>
            <span class="ao-colon">:</span>
            <div class="ao-select-pill">
              <select id="ao-week-select" class="ao-native-select">
                <option value="all">All</option>
                <option value="W1" selected>W1</option>
                <option value="W2">W2</option>
                <option value="W3">W3</option>
                <option value="W4">W4</option>
                <option value="W5">W5</option>
              </select>
            </div>
            <div class="ao-select-pill">
              <select id="ao-month-select" class="ao-native-select">
                <option value="January">January</option>
                <option value="February">February</option>
                <option value="March">March</option>
                <option value="April">April</option>
                <option value="May">May</option>
                <option value="June">June</option>
                <option value="July">July</option>
                <option value="August">August</option>
                <option value="September">September</option>
                <option value="October" selected>October</option>
                <option value="November">November</option>
                <option value="December">December</option>
              </select>
            </div>
            <div class="ao-callout-yellow">
              ⇨ Pilih Week dan Bulan ya
            </div>
            <button type="button" id="btn-sync-ao-sheet" class="ao-sync-btn" title="Sinkronkan data dari sheet">
              🔄 Sinkronkan Data
            </button>
          </div>

          <div class="ao-title-row" style="margin-top: 8px;">
            <span class="ao-label-bold">OUTLET</span>
            <span class="ao-colon">:</span>
            <span class="ao-outlet-name">TUNAS TOYOTA KIARA CONDONG</span>
            <span class="ao-year-badge">2026</span>
          </div>
        </div>

        <!-- Right Side: THIS MONTH CLOSING ESTIMATION Box -->
        <div class="ao-closing-est-box">
          <div class="ao-closing-est-header">THIS MONTH CLOSING ESTIMATION</div>
          <div class="ao-closing-est-body">
            <div class="ao-closing-est-col">
              <div class="ao-closing-est-sub">CPUS</div>
              <div class="ao-closing-est-val" id="ao-est-cpus-val">714</div>
            </div>
            <div class="ao-closing-est-col green-bg">
              <div class="ao-closing-est-sub" style="color: #064e3b;">VS TAR</div>
              <div class="ao-closing-est-val" id="ao-est-pct-val" style="color: #064e3b;">105%</div>
            </div>
          </div>
        </div>
      </div>

      <!-- 2. Master Spreadsheet 3-Column Layout -->
      <div class="ao-sheet-grid">
        <!-- ZONE 1 (LEFT): I. TARGET SETTING AND WEEKLY PERFORMANCE -->
        <div class="ao-left-zone">
          <div class="ao-section-title">I. TARGET SETTING AND WEEKLY PERFORMANCE</div>

          <div class="ao-sec1-container">
            <!-- Sub-col A: KPI Tree Table (Excel Merged Cells) -->
            <div class="ao-kpi-tree-table-wrap">
              <table class="ao-grid-tbl ao-tree-table">
                <thead>
                  <tr>
                    <th style="min-width: 60px;">CPUS TARGET</th>
                    <th style="min-width: 60px;">WALK-IN</th>
                    <th style="min-width: 72px;">BOOKING SHOW</th>
                    <th colspan="3" style="min-width: 140px;">BREAKDOWN</th>
                  </tr>
                </thead>
                <tbody>
                  <tr>
                    <!-- CPUS Root -->
                    <td rowspan="4" class="ao-cell-center ao-tree-root-val">
                      <div id="ao-tree-cpus" style="font-size: 19px; font-weight: 900;">714</div>
                    </td>
                    <!-- WALK-IN -->
                    <td rowspan="4" class="ao-cell-center">
                      <div id="ao-tree-walkin" style="font-size: 14px; font-weight: 800;">268</div>
                      <div id="ao-tree-walkin-pct" class="ao-tree-blue-pct">38%</div>
                    </td>
                    <!-- BOOKING SHOW -->
                    <td rowspan="4" class="ao-cell-center">
                      <div id="ao-tree-booking" style="font-size: 14px; font-weight: 800;">446</div>
                      <div id="ao-tree-booking-pct" class="ao-tree-blue-pct">62%</div>
                    </td>
                    <!-- TCARE -->
                    <td colspan="3" class="ao-cell-center" style="background: #ffffff; padding: 4px;">
                      <div style="font-size: 10px; font-weight: 800;">TCARE</div>
                      <div id="ao-tree-tcare" style="font-size: 13px; font-weight: 800;">229</div>
                      <div id="ao-tree-tcare-pct" class="ao-tree-blue-pct">51%</div>
                    </td>
                  </tr>
                  <tr>
                    <!-- NON TCARE Header -->
                    <td colspan="3" class="ao-cell-center" style="background: #ffffff; border-top: 1px solid #000; padding: 4px;">
                      <div style="font-size: 10px; font-weight: 800;">NON TCARE</div>
                      <div id="ao-tree-nontcare" style="font-size: 13px; font-weight: 800;">217</div>
                      <div id="ao-tree-nontcare-pct" class="ao-tree-blue-pct">49%</div>
                    </td>
                  </tr>
                  <!-- NON TCARE Sub-headers: OIL, GR, SBE -->
                  <tr style="font-size: 9.5px; font-weight: 800; background: #ffffff; text-align: center;">
                    <td style="border: 1px solid #000; padding: 2px;">OIL</td>
                    <td style="border: 1px solid #000; padding: 2px;">GR</td>
                    <td style="border: 1px solid #000; padding: 2px;">SBE</td>
                  </tr>
                  <tr style="text-align: center;">
                    <td style="border: 1px solid #000; padding: 3px;">
                      <div id="ao-tree-oil" style="font-size: 12px; font-weight: 800;">26</div>
                      <div id="ao-tree-oil-pct" class="ao-tree-blue-pct">12%</div>
                    </td>
                    <td style="border: 1px solid #000; padding: 3px;">
                      <div id="ao-tree-gr" style="font-size: 12px; font-weight: 800;">140</div>
                      <div id="ao-tree-gr-pct" class="ao-tree-blue-pct">65%</div>
                    </td>
                    <td style="border: 1px solid #000; padding: 3px;">
                      <div id="ao-tree-sbe" style="font-size: 12px; font-weight: 800;">50</div>
                      <div id="ao-tree-sbe-pct" class="ao-tree-blue-pct">23%</div>
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>

            <!-- Sub-col B: Mini W1 Badge & Weekly CPUS Table -->
            <div class="ao-weekly-table-wrap">
              <!-- Mini W1 Badge (Right aligned above table) -->
              <div class="ao-mini-w1-box">
                <table class="ao-grid-tbl" style="width: 140px; margin-left: auto; margin-bottom: 4px;">
                  <thead>
                    <tr><th colspan="2" style="background: #ffffff; text-align: center; font-size: 10px; padding: 2px;" id="ao-mini-week-label">W1</th></tr>
                  </thead>
                  <tbody>
                    <tr>
                      <td style="font-size: 9.5px; padding: 2px; text-align: center;">Actual</td>
                      <td style="font-size: 9.5px; padding: 2px; text-align: center; background: #84e291; font-weight: 800;">VS TAR</td>
                    </tr>
                    <tr>
                      <td style="font-size: 13px; font-weight: 900; text-align: center; padding: 3px;" id="ao-mini-w1-act">95</td>
                      <td style="font-size: 13px; font-weight: 900; text-align: center; padding: 3px; background: #84e291; color: #064e3b;" id="ao-mini-w1-pct">130%</td>
                    </tr>
                  </tbody>
                </table>
              </div>

              <!-- Weekly CPUS Matrix Table -->
              <table class="ao-grid-tbl" id="ao-tbl-sec1-cpus">
                <thead>
                  <tr>
                    <th style="text-align: left; min-width: 145px;">TOTAL CPUS PLAN</th>
                    <th colspan="5" style="text-align: center; background: #ffffff;" id="ao-sec1-target-total">714</th>
                  </tr>
                  <tr style="background: #ffffff;">
                    <th style="text-align: left;">Indikator</th>
                    <th style="width: 44px; text-align: center;">W1</th>
                    <th style="width: 44px; text-align: center;">W2</th>
                    <th style="width: 44px; text-align: center;">W3</th>
                    <th style="width: 44px; text-align: center;">W4</th>
                    <th style="width: 44px; text-align: center;">W5</th>
                  </tr>
                </thead>
                <tbody id="ao-tbody-sec1-cpus">
                  <!-- Dynamically populated -->
                </tbody>
              </table>
            </div>
          </div>

          <!-- Staircase Waterfall Matrix (Rows 26-41) -->
          <div class="ao-staircase-wrap" style="margin-top: 10px;">
            <table class="ao-grid-tbl" style="width: 100%; font-size: 10px;">
              <tbody>
                <tr>
                  <td style="width: 16.6%;" class="ao-salmon-cell">-49</td>
                  <td style="width: 16.6%;" class="ao-green-cell">49</td>
                  <td style="width: 16.6%;" class="ao-salmon-cell">-167</td>
                  <td style="width: 16.6%;"></td><td style="width: 16.6%;"></td><td style="width: 16.6%;"></td>
                </tr>
                <tr>
                  <td class="ao-salmon-cell">-51</td>
                  <td class="ao-green-cell">51</td>
                  <td class="ao-salmon-cell">-162</td>
                  <td></td><td></td><td></td>
                </tr>
                <tr>
                  <td></td>
                  <td class="ao-salmon-cell">-49</td>
                  <td class="ao-green-cell">49</td>
                  <td class="ao-salmon-cell">-118</td>
                  <td></td><td></td>
                </tr>
                <tr>
                  <td></td>
                  <td class="ao-salmon-cell">-51</td>
                  <td class="ao-green-cell">51</td>
                  <td class="ao-salmon-cell">-111</td>
                  <td></td><td></td>
                </tr>
                <tr>
                  <td></td><td></td>
                  <td class="ao-salmon-cell">-49</td>
                  <td class="ao-green-cell">49</td>
                  <td class="ao-salmon-cell">-69</td>
                  <td></td>
                </tr>
                <tr>
                  <td></td><td></td>
                  <td class="ao-salmon-cell">-51</td>
                  <td class="ao-green-cell">51</td>
                  <td class="ao-salmon-cell">-59</td>
                  <td></td>
                </tr>
                <tr>
                  <td></td><td></td><td></td>
                  <td class="ao-salmon-cell">-24</td>
                  <td class="ao-green-cell">49</td>
                  <td class="ao-salmon-cell">-21</td>
                </tr>
                <tr>
                  <td></td><td></td><td></td>
                  <td class="ao-salmon-cell">-12</td>
                  <td class="ao-green-cell">51</td>
                  <td class="ao-salmon-cell">-8</td>
                </tr>
              </tbody>
            </table>
          </div>

          <!-- Booking & No-Show Monitoring Table (Rows 47-66) -->
          <div style="margin-top: 10px;">
            <table class="ao-grid-tbl" id="ao-tbl-sec1-booking" style="width: 100%;">
              <thead>
                <tr style="background: #ffffff;">
                  <th style="text-align: left; min-width: 170px;">MRA EFFORT &amp; BOOKING MONITORING</th>
                  <th style="width: 44px; text-align: center;">W1</th>
                  <th style="width: 44px; text-align: center;">W2</th>
                  <th style="width: 44px; text-align: center;">W3</th>
                  <th style="width: 44px; text-align: center;">W4</th>
                  <th style="width: 44px; text-align: center;">W5</th>
                  <th style="width: 52px; text-align: center; background: #e2e8f0;">TOTAL</th>
                </tr>
              </thead>
              <tbody id="ao-tbody-sec1-booking">
                <!-- Dynamically populated -->
              </tbody>
            </table>
          </div>

          <!-- Trajectory Chart (Rows 72-73) -->
          <div style="margin-top: 12px; border: 1.5px solid #000; background: #fff; padding: 10px;">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px;">
              <span style="font-size: 11px; font-weight: 800;">📈 CPUS COMMULATIVE TRAJECTORY (TARGET VS AKTUAL)</span>
              <span style="font-size: 10px; color: #475569;">Target Akhir: 714 Unit</span>
            </div>
            <div style="height: 180px; position: relative;">
              <canvas id="chart-ao-cumulative"></canvas>
            </div>
          </div>
        </div>

        <!-- ZONE 2 (CENTER STRIP): VERTICAL KPI COLUMN (Column O) -->
        <div class="ao-center-strip">
          <table class="ao-grid-tbl ao-vertical-kpi-tbl">
            <tbody>
              <tr>
                <th class="ao-vkpi-th">CLOSING COMMITMENT</th>
              </tr>
              <tr>
                <td class="ao-vkpi-td white-cell" id="ao-vkpi-closing-comm">714</td>
              </tr>
              <tr>
                <th class="ao-vkpi-th">TOTAL CPUS GAP (FM)</th>
              </tr>
              <tr>
                <td class="ao-vkpi-td salmon-cell" id="ao-vkpi-total-gap">-619</td>
              </tr>
              <tr>
                <th class="ao-vkpi-th">GAP CPUS WALK-IN (FM)</th>
              </tr>
              <tr>
                <td class="ao-vkpi-td salmon-cell" id="ao-vkpi-walkin-gap">-226</td>
              </tr>
              <tr>
                <th class="ao-vkpi-th">ACT. CPUS WALK-IN (FM)</th>
              </tr>
              <tr>
                <td class="ao-vkpi-td blue-cell" id="ao-vkpi-walkin-act">42</td>
              </tr>
              <tr>
                <th class="ao-vkpi-th">GAP CPUS BOOKING (FM)</th>
              </tr>
              <tr>
                <td class="ao-vkpi-td salmon-cell" id="ao-vkpi-booking-gap">-393</td>
              </tr>
              <tr>
                <th class="ao-vkpi-th">ACT. CPUS BOOKING (FM)</th>
              </tr>
              <tr>
                <td class="ao-vkpi-td blue-cell" id="ao-vkpi-booking-act">53</td>
              </tr>
            </tbody>
          </table>
        </div>

        <!-- ZONE 3 (RIGHT): SECTION II, III, IV -->
        <div class="ao-right-zone">
          <div class="ao-section-title">II. SERVICE PROSPECTING MANAGEMENT</div>

          <!-- T-CARE Table (Rows 5-20) -->
          <div class="ao-funnel-block" style="margin-bottom: 12px;">
            <table class="ao-grid-tbl ao-funnel-tbl" id="ao-tbl-funnel-tcare">
              <thead>
                <tr style="background: #ffffff;">
                  <th colspan="2" style="text-align: left; font-size: 11px; font-weight: 800; border-bottom: 2px solid #000;">TCARE</th>
                  <th style="width: 40px; text-align: center;">W1</th>
                  <th style="width: 40px; text-align: center;">W2</th>
                  <th style="width: 40px; text-align: center;">W3</th>
                  <th style="width: 40px; text-align: center;">W4</th>
                  <th style="width: 40px; text-align: center;">W5</th>
                  <th style="width: 48px; text-align: center; background: #e2e8f0;">TOTAL</th>
                </tr>
              </thead>
              <tbody id="ao-tbody-funnel-tcare">
                <!-- Dynamically populated with yellow actuals and green % vs tar -->
              </tbody>
            </table>
          </div>

          <!-- NON T-CARE Table (Rows 26-41) - DIRECTLY STACKED -->
          <div class="ao-funnel-block" style="margin-bottom: 14px;">
            <table class="ao-grid-tbl ao-funnel-tbl" id="ao-tbl-funnel-nontcare">
              <thead>
                <tr style="background: #ffffff;">
                  <th colspan="2" style="text-align: left; font-size: 11px; font-weight: 800; border-bottom: 2px solid #000;">NON TCARE</th>
                  <th style="width: 40px; text-align: center;">W1</th>
                  <th style="width: 40px; text-align: center;">W2</th>
                  <th style="width: 40px; text-align: center;">W3</th>
                  <th style="width: 40px; text-align: center;">W4</th>
                  <th style="width: 40px; text-align: center;">W5</th>
                  <th style="width: 48px; text-align: center; background: #e2e8f0;">TOTAL</th>
                </tr>
              </thead>
              <tbody id="ao-tbody-funnel-nontcare">
                <!-- Dynamically populated with yellow actuals and green % vs tar -->
              </tbody>
            </table>
          </div>

          <!-- SECTION III: SBI TCARE / TCARE LIGHT (Rows 43-53) -->
          <div class="ao-section-title" style="margin-top: 14px;">III. SBI TCARE/TCARE LIGHT</div>
          <div style="margin-bottom: 14px;">
            <table class="ao-grid-tbl" id="ao-tbl-sbi-matrix" style="width: 100%;">
              <thead>
                <tr style="background: #ffffff;">
                  <th style="text-align: left; min-width: 110px;">Kategori</th>
                  <th style="width: 40px; text-align: center;">W1</th>
                  <th style="width: 40px; text-align: center;">W2</th>
                  <th style="width: 40px; text-align: center;">W3</th>
                  <th style="width: 40px; text-align: center;">W4</th>
                  <th style="width: 40px; text-align: center;">W5</th>
                  <th style="width: 48px; text-align: center; background: #e2e8f0;">TOTAL</th>
                </tr>
              </thead>
              <tbody id="ao-tbody-sbi-matrix">
                <!-- Dynamically populated -->
              </tbody>
            </table>
          </div>

          <!-- SECTION IV: ACTION PLAN (Rows 54-68) -->
          <div class="ao-section-title" style="margin-top: 14px;">IV. ACTION PLAN</div>
          <div>
            <table class="ao-grid-tbl ao-action-plan-tbl" id="ao-tbl-action-plan" style="width: 100%;">
              <thead>
                <tr style="background: #ffffff;">
                  <th style="width: 75px; text-align: left;">PROGRAM</th>
                  <th style="text-align: left;">PLAN</th>
                  <th style="width: 60px; text-align: center;">PIC</th>
                  <th style="width: 80px; text-align: center;">STATUS</th>
                </tr>
              </thead>
              <tbody id="ao-tbody-action-plan">
                <!-- Dynamically populated -->
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  </div>
'''

# Replace <div id="pane-ao" ...></div> in index.html
pane_pattern = re.compile(r'  <!-- TAB: AO REPORT.*?<div id="pane-ao".*?  </div>\s*(?=  <!-- DEDICATED MODAL: IMPOR EXCEL WS)', re.DOTALL)
new_html = pane_pattern.sub(faithful_pane_ao, html)

if new_html != html:
    with open('index.html', 'w', encoding='utf-8') as f:
        f.write(new_html)
    print("Successfully updated index.html with faithful AO sheet markup!")
else:
    print("Could not match pane-ao in index.html")
