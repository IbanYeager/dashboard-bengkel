with open('index.html', 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Update select-ai-advisor-period
old_ai = '''                <select id="select-ai-advisor-period" class="mini-potensi-month-select" title="Pilih Bulan Analisis AI" style="font-weight: 700; background: #ffffff; border: 1.5px solid #6366f1; color: #4338ca; border-radius: 6px; padding: 3px 8px; font-size: 11px; cursor: pointer;">
                  <option value="all">Semua Periode (YTD)</option>
                  <option value="Q1">Kuartal 1 (Jan-Mar)</option>
                  <option value="Q2">Kuartal 2 (Apr-Jun)</option>
                  <option value="Q3">Kuartal 3 (Jul-Sep)</option>
                  <option value="Jan">Januari</option>
                  <option value="Feb">Februari</option>
                  <option value="Mar">Maret</option>
                  <option value="Apr">April</option>
                  <option value="Mei">Mei</option>
                  <option value="Jun">Juni</option>
                  <option value="Jul">Juli</option>
                  <option value="Agt">Agustus</option>
                  <option value="Sep" selected>September</option>
                </select>'''

new_ai = '''                <select id="select-ai-advisor-period" class="mini-potensi-month-select" title="Pilih Bulan Analisis AI" style="font-weight: 700; background: #ffffff; border: 1.5px solid #6366f1; color: #4338ca; border-radius: 6px; padding: 3px 8px; font-size: 11px; cursor: pointer;">
                  <option value="all">Semua Periode (YTD)</option>
                  <option value="Q1">Kuartal 1 (Jan-Mar)</option>
                  <option value="Q2">Kuartal 2 (Apr-Jun)</option>
                  <option value="Q3">Kuartal 3 (Jul-Sep)</option>
                  <option value="Q4">Kuartal 4 (Okt-Des)</option>
                  <option value="Jan">Januari</option>
                  <option value="Feb">Februari</option>
                  <option value="Mar">Maret</option>
                  <option value="Apr">April</option>
                  <option value="Mei">Mei</option>
                  <option value="Jun">Juni</option>
                  <option value="Jul">Juli</option>
                  <option value="Agt">Agustus</option>
                  <option value="Sep">September</option>
                  <option value="Okt" selected>Oktober</option>
                </select>'''

# 2. Update select-potensi-month
old_pot = '''                <select id="select-potensi-month" class="mini-potensi-month-select" title="Pilih Periode Potensi">
                  <option value="all" selected>Semua Periode (YTD)</option>
                  <option value="Q1">Kuartal 1 (Jan-Mar)</option>
                  <option value="Q2">Kuartal 2 (Apr-Jun)</option>
                  <option value="Q3">Kuartal 3 (Jul-Sep)</option>
                  <option value="Jan">Januari</option>
                  <option value="Feb">Februari</option>
                  <option value="Mar">Maret</option>
                  <option value="Apr">April</option>
                  <option value="Mei">Mei</option>
                  <option value="Jun">Juni</option>
                  <option value="Jul">Juli</option>
                  <option value="Agt">Agustus</option>
                  <option value="Sep">September</option>
                </select>'''

new_pot = '''                <select id="select-potensi-month" class="mini-potensi-month-select" title="Pilih Periode Potensi">
                  <option value="all" selected>Semua Periode (YTD)</option>
                  <option value="Q1">Kuartal 1 (Jan-Mar)</option>
                  <option value="Q2">Kuartal 2 (Apr-Jun)</option>
                  <option value="Q3">Kuartal 3 (Jul-Sep)</option>
                  <option value="Q4">Kuartal 4 (Okt-Des)</option>
                  <option value="Jan">Januari</option>
                  <option value="Feb">Februari</option>
                  <option value="Mar">Maret</option>
                  <option value="Apr">April</option>
                  <option value="Mei">Mei</option>
                  <option value="Jun">Juni</option>
                  <option value="Jul">Juli</option>
                  <option value="Agt">Agustus</option>
                  <option value="Sep">September</option>
                  <option value="Okt">Oktober</option>
                </select>'''

# 3. Update select-funnel-module-period
old_mod = '''              <select id="select-funnel-module-period" class="mini-potensi-month-select" title="Pilih Periode Funneling">
                <option value="all" selected>Semua Periode (YTD)</option>
                <option value="Q1">Kuartal 1 (Jan-Mar)</option>
                <option value="Q2">Kuartal 2 (Apr-Jun)</option>
                <option value="Q3">Kuartal 3 (Jul-Sep)</option>
                <option value="Jan">Januari</option>
                <option value="Feb">Februari</option>
                <option value="Mar">Maret</option>
                <option value="Apr">April</option>
                <option value="Mei">Mei</option>
                <option value="Jun">Juni</option>
                <option value="Jul">Juli</option>
                <option value="Agt">Agustus</option>
                <option value="Sep">September</option>
              </select>'''

new_mod = '''              <select id="select-funnel-module-period" class="mini-potensi-month-select" title="Pilih Periode Funneling">
                <option value="all" selected>Semua Periode (YTD)</option>
                <option value="Q1">Kuartal 1 (Jan-Mar)</option>
                <option value="Q2">Kuartal 2 (Apr-Jun)</option>
                <option value="Q3">Kuartal 3 (Jul-Sep)</option>
                <option value="Q4">Kuartal 4 (Okt-Des)</option>
                <option value="Jan">Januari</option>
                <option value="Feb">Februari</option>
                <option value="Mar">Maret</option>
                <option value="Apr">April</option>
                <option value="Mei">Mei</option>
                <option value="Jun">Juni</option>
                <option value="Jul">Juli</option>
                <option value="Agt">Agustus</option>
                <option value="Sep">September</option>
                <option value="Okt">Oktober</option>
              </select>'''

# 4. Update sbi-compare-month-filter
old_sbi = '''              <select id="sbi-compare-month-filter" class="sbi-compare-select">
                <option value="all" selected>Semua Bulan (Setahun)</option>
                <option value="ytd">Januari - September (YTD)</option>
                <option value="Q1">Kuartal 1 (Jan - Mar)</option>
                <option value="Q2">Kuartal 2 (Apr - Jun)</option>
                <option value="Q3">Kuartal 3 (Jul - Sep)</option>
                <option value="H1">Semester 1 (Jan - Jun)</option>
              </select>'''

new_sbi = '''              <select id="sbi-compare-month-filter" class="sbi-compare-select">
                <option value="all" selected>Semua Bulan (Setahun)</option>
                <option value="ytd">Januari - Oktober (YTD)</option>
                <option value="Q1">Kuartal 1 (Jan - Mar)</option>
                <option value="Q2">Kuartal 2 (Apr - Jun)</option>
                <option value="Q3">Kuartal 3 (Jul - Sep)</option>
                <option value="Q4">Kuartal 4 (Okt - Des)</option>
                <option value="H1">Semester 1 (Jan - Jun)</option>
              </select>'''

assert old_ai in content, "old_ai not found in index.html"
assert old_pot in content, "old_pot not found in index.html"
assert old_mod in content, "old_mod not found in index.html"
assert old_sbi in content, "old_sbi not found in index.html"

content = content.replace(old_ai, new_ai)
content = content.replace(old_pot, new_pot)
content = content.replace(old_mod, new_mod)
content = content.replace(old_sbi, new_sbi)

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(content)

print("index.html dropdowns updated successfully!")
