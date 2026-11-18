with open('index.html', 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Update select-ai-advisor-period: add Nov and Des
old_ai = '''                  <option value="Sep">September</option>
                  <option value="Okt" selected>Oktober</option>
                </select>'''

new_ai = '''                  <option value="Sep">September</option>
                  <option value="Okt" selected>Oktober</option>
                  <option value="Nov">November</option>
                  <option value="Des">Desember</option>
                </select>'''

# 2. Update select-potensi-month: add Nov and Des
old_pot = '''                  <option value="Sep">September</option>
                  <option value="Okt">Oktober</option>
                </select>'''

new_pot = '''                  <option value="Sep">September</option>
                  <option value="Okt">Oktober</option>
                  <option value="Nov">November</option>
                  <option value="Des">Desember</option>
                </select>'''

# 3. Update select-funnel-module-period: add Nov and Des
old_mod = '''                <option value="Sep">September</option>
                <option value="Okt">Oktober</option>
              </select>'''

new_mod = '''                <option value="Sep">September</option>
                <option value="Okt">Oktober</option>
                <option value="Nov">November</option>
                <option value="Des">Desember</option>
              </select>'''

assert old_ai in content, "old_ai not found in index.html"
assert old_pot in content, "old_pot not found in index.html"
assert old_mod in content, "old_mod not found in index.html"

content = content.replace(old_ai, new_ai)
content = content.replace(old_pot, new_pot)
content = content.replace(old_mod, new_mod)

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(content)

print("index.html updated with November & Desember in all period selects!")
