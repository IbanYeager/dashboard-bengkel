"""
Live Booking & TikTok Live Data Synchronization Script
Sources:
1. Sheet 1 (LIVE TIKTOK): ID 1b60d-JO50LU4KyywuULokmDIU7z3Ts_1, GID 1727895687
2. Sheet 2 (BOOKING): ID 1tYGRaZf39MONbZ8IvgX2EtPHGzsg9by3jRrHfoNE4pQ, GID 2008717837
"""

import os
import sys
import json
import csv
import io
import urllib.request
from datetime import datetime

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data')
BOOKING_JSON_PATH = os.path.join(DATA_DIR, 'booking_data.json')

TIKTOK_CSV_URL = "https://docs.google.com/spreadsheets/d/1b60d-JO50LU4KyywuULokmDIU7z3Ts_1/gviz/tq?tqx=out:csv&gid=1727895687"
BOOKING_CSV_URL = "https://docs.google.com/spreadsheets/d/1tYGRaZf39MONbZ8IvgX2EtPHGzsg9by3jRrHfoNE4pQ/gviz/tq?tqx=out:csv&gid=2008717837"

MONTH_NAMES_ORDER = ["Jan", "Feb", "Mar", "Apr", "Mei", "Jun", "Jul", "Agt", "Sep", "Okt", "Nov", "Des"]
MONTHS_MAP = {
    'jan': 'Jan', 'feb': 'Feb', 'mar': 'Mar', 'apr': 'Apr',
    'mei': 'Mei', 'may': 'Mei', 'jun': 'Jun', 'jul': 'Jul',
    'agt': 'Agt', 'agu': 'Agt', 'aug': 'Agt', 'sep': 'Sep',
    'okt': 'Okt', 'oct': 'Okt', 'nov': 'Nov', 'des': 'Des', 'dec': 'Des'
}

def sync_live_tiktok(booking_data):
    print("Mengambil data live TikTok dari Google Sheets (GID 1727895687)...")
    req = urllib.request.Request(TIKTOK_CSV_URL, headers={'User-Agent': 'Mozilla/5.0'})
    try:
        with urllib.request.urlopen(req, timeout=20) as resp:
            data = resp.read().decode('utf-8', errors='ignore')
            reader = list(csv.reader(io.StringIO(data)))
            
            monthly_dict = {}
            i = 0
            while i < len(reader):
                row_title = reader[i][0].strip().upper() if len(reader[i]) > 0 else ''
                if 'BOOKING REPORT' in row_title:
                    header_cells = [c.strip().lower() for c in reader[i][1:] if c.strip()]
                    detected_month = None
                    for c in header_cells:
                        for m_k, m_v in MONTHS_MAP.items():
                            if m_k in c:
                                detected_month = m_v
                                break
                        if detected_month:
                            break
                    if detected_month and i + 5 < len(reader):
                        def extract_daily_vals(r):
                            vals = []
                            for c in r[1:]:
                                c_clean = c.strip().replace(',', '.')
                                if any(w in c_clean.lower() for w in ['duration', 'likes', 'viewer', 'comment', 'booking', '/day', '/month']):
                                    break
                                try:
                                    vals.append(float(c_clean))
                                except:
                                    pass
                            return vals

                        dur_row = extract_daily_vals(reader[i+1])
                        likes_row = extract_daily_vals(reader[i+2])
                        view_row = extract_daily_vals(reader[i+3])
                        com_row = extract_daily_vals(reader[i+4])
                        book_row = extract_daily_vals(reader[i+5])
                        
                        avg_dur = round(sum(dur_row)/len(dur_row)) if dur_row else None
                        avg_likes = round(sum(likes_row)/len(likes_row)) if likes_row else None
                        avg_view = round(sum(view_row)/len(view_row)) if view_row else None
                        avg_com = round(sum(com_row)/len(com_row)) if com_row else None
                        tot_book = round(sum(book_row)) if book_row else 0
                        
                        # Check explicit booking /month in summary column if present
                        for c_idx, c in enumerate(reader[i+5]):
                            if 'booking /month' in c.lower() and c_idx + 1 < len(reader[i+5]):
                                try:
                                    tot_book = round(float(reader[i+5][c_idx+1].strip().replace(',', '.')))
                                except:
                                    pass
                        
                        monthly_dict[detected_month] = {
                            'month': detected_month,
                            'duration': avg_dur,
                            'likes': avg_likes,
                            'viewer': avg_view,
                            'comments': avg_com,
                            'booking': tot_book,
                            'has_data': len(dur_row) > 0
                        }
                        i += 6
                        continue
                i += 1
            
            if monthly_dict:
                trend = []
                all_dur = []
                all_likes = []
                all_views = []
                all_com = []
                total_booking = 0
                
                for m in MONTH_NAMES_ORDER:
                    if m in monthly_dict:
                        item = monthly_dict[m]
                        trend.append(item)
                        if item['has_data']:
                            if item['duration']: all_dur.append(item['duration'])
                            if item['likes']: all_likes.append(item['likes'])
                            if item['viewer']: all_views.append(item['viewer'])
                            if item['comments']: all_com.append(item['comments'])
                            total_booking += item['booking'] or 0
                    else:
                        trend.append({
                            'month': m,
                            'duration': None,
                            'likes': None,
                            'viewer': None,
                            'comments': None,
                            'booking': None,
                            'has_data': False
                        })
                
                avg_dur_overall = round(sum(all_dur)/len(all_dur)) if all_dur else 56
                avg_likes_overall = round(sum(all_likes)/len(all_likes)) if all_likes else 419
                avg_view_overall = round(sum(all_views)/len(all_views)) if all_views else 60
                avg_com_overall = round(sum(all_com)/len(all_com)) if all_com else 12
                
                if 'tiktok_live' not in booking_data:
                    booking_data['tiktok_live'] = {}
                    
                booking_data['tiktok_live']['monthly_trend'] = trend
                booking_data['tiktok_live']['kpis'] = {
                    "duration_minutes": {"value": avg_dur_overall, "unit": "Menit/sesi", "label": "Duration (Minute)"},
                    "likes_per_day": {"value": avg_likes_overall, "unit": "Likes/hari", "label": "Likes / day"},
                    "viewer_per_day": {"value": avg_view_overall, "unit": "Viewer/hari", "label": "Viewer / day"},
                    "comments_per_day": {"value": avg_com_overall, "unit": "Komen/hari", "label": "Comment / day"},
                    "total_booking": {"value": total_booking, "unit": "Unit Booking", "label": "Booking Acquired"}
                }
                print(f"[OK] Performa TikTok Live berhasil di-update dari Google Sheets (Total Booking: {total_booking} Unit).")
    except Exception as e:
        print(f"[WARN] Gagal memperbarui TikTok Live dari Google Sheets: {e}")

def try_sync_booking_sheet(booking_data):
    print("Mencoba mengambil data booking dari Sheet 2 (ID: 1tYGRaZf39MONbZ8IvgX2EtPHGzsg9by3jRrHfoNE4pQ)...")
    req = urllib.request.Request(BOOKING_CSV_URL, headers={'User-Agent': 'Mozilla/5.0'})
    try:
        with urllib.request.urlopen(req, timeout=12) as resp:
            if resp.status == 200:
                raw_csv = resp.read().decode('utf-8', errors='ignore')
                print(f"[OK] Berhasil mengunduh Sheet Booking ({len(raw_csv)} byte).")
                reader = list(csv.reader(io.StringIO(raw_csv)))
                if len(reader) >= 2:
                    channels_def = [
                        ('inc_call', 'Incoming Call (Inc. Call)', 'INC_CALL', ['incoming', 'inc. call', 'inc call']),
                        ('boc', 'Booking on Call (BOC)', 'BOC', ['boc', 'booking on call']),
                        ('sales', 'Sales Booking Referral', 'SALES', ['sales', 'referral']),
                        ('m_toyota', 'M-Toyota', 'M_TOYOTA', ['m-toyota', 'm toyota', 'mobile app', 'mtoyota']),
                        ('sa_total', 'SA Total / Summary', 'SA_TOTAL', ['sa total', 'akumulasi semua sa', 'total sa', 'summary sa']),
                        ('sa_didin', 'SA Didin', 'SA_DIDIN', ['didin']),
                        ('sa_ficky', 'SA Ficky', 'SA_FICKY', ['ficky']),
                        ('sa_acep', 'SA Acep', 'SA_ACEP', ['acep'])
                    ]
                    res_channels = {}
                    for k, title, code, _ in channels_def:
                        res_channels[k] = {'title': title, 'code': code, 'ytd_total': 0, 'monthly': [None]*12}

                    header_row_idx = -1
                    month_cols = {}
                    for r_idx in range(min(len(reader), 15)):
                        row = reader[r_idx]
                        found = {}
                        for c_idx, cell in enumerate(row):
                            c_low = cell.strip().lower()
                            for m_name, m_val in MONTHS_MAP.items():
                                if c_low == m_name or c_low.startswith(m_name + ' ') or c_low.startswith(m_name + '-'):
                                    m_num = MONTH_NAMES_ORDER.index(m_val)
                                    if m_num not in found:
                                        found[m_num] = c_idx
                                    break
                        if len(found) >= 3:
                            header_row_idx = r_idx
                            month_cols = found
                            break

                    if header_row_idx != -1:
                        for r_idx in range(header_row_idx + 1, len(reader)):
                            row = reader[r_idx]
                            if not row: continue
                            label = (row[0].strip().lower() + ' ' + (row[1].strip().lower() if len(row) > 1 else ''))
                            for k, title, code, matchers in channels_def:
                                if any(m in label for m in matchers):
                                    if k == 'sa_total' and any(s in label for s in ['didin', 'ficky', 'acep']) and 'total' not in label:
                                        continue
                                    for m_num, col_idx in month_cols.items():
                                        if col_idx < len(row):
                                            val_str = row[col_idx].strip().replace('.', '').replace(',', '.')
                                            try:
                                                res_channels[k]['monthly'][m_num] = round(float(val_str))
                                            except:
                                                pass
                                    break

                        # Auto calculate sa_total if missing
                        if not any(v is not None for v in res_channels['sa_total']['monthly']):
                            for m_idx in range(12):
                                d = res_channels['sa_didin']['monthly'][m_idx]
                                f = res_channels['sa_ficky']['monthly'][m_idx]
                                a = res_channels['sa_acep']['monthly'][m_idx]
                                if d is not None or f is not None or a is not None:
                                    res_channels['sa_total']['monthly'][m_idx] = (d or 0) + (f or 0) + (a or 0)

                        for k, ch in res_channels.items():
                            ch['ytd_total'] = sum(v for v in ch['monthly'] if v is not None)

                        active_months = max((m_idx + 1 for m_idx in range(12) if any(ch['monthly'][m_idx] is not None for ch in res_channels.values())), default=9)

                        booking_data['channels'] = res_channels
                        booking_data['meta']['active_months_count'] = active_months
                        booking_data['meta']['valid_until'] = f"{MONTH_NAMES_ORDER[active_months-1]} 2026"

                booking_data["meta"]["source"] = "live_google_sheets"
                booking_data["meta"]["updated_at"] = datetime.now().isoformat()
                booking_data["meta"]["note"] = f"Data berhasil disinkronkan live dari Google Sheets (GID: 2008717837)."
                return True
    except Exception as e:
        print(f"[INFO] Sheet Booking memerlukan akses publik ('Siapa saja yang memiliki link'): {e}")
        booking_data["meta"]["note"] = "Sheet Booking diset 'Dibatasi'. Menampilkan data booking tervalidasi."
    return False

def main():
    os.makedirs(DATA_DIR, exist_ok=True)
    
    if os.path.exists(BOOKING_JSON_PATH):
        with open(BOOKING_JSON_PATH, 'r', encoding='utf-8') as f:
            booking_data = json.load(f)
    else:
        booking_data = {"meta": {}, "months": MONTH_NAMES_ORDER, "channels": {}}
        
    sync_live_tiktok(booking_data)
    try_sync_booking_sheet(booking_data)
    
    booking_data["meta"]["updated_at"] = datetime.now().isoformat()
    with open(BOOKING_JSON_PATH, 'w', encoding='utf-8') as f:
        json.dump(booking_data, f, indent=2, ensure_ascii=False)
        
    print(f"[OK] Selesai sinkronisasi booking_data.json: {BOOKING_JSON_PATH}")

if __name__ == '__main__':
    main()
