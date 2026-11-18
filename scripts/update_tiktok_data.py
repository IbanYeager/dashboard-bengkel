import json
import csv

with open('data/live_tiktok_from_sheet.csv', encoding='utf-8') as f:
    rows = list(csv.reader(f))

months = ['Jan', 'Feb', 'Mar', 'Apr', 'Mei', 'Jun', 'Jul', 'Agt', 'Sep']
data_by_month = {}

i = 0
while i < len(rows):
    r0 = rows[i][0].strip().upper() if rows[i] else ''
    if 'BOOKING REPORT' in r0:
        header_row = rows[i]
        m_name = None
        for c in header_row[1:]:
            c_clean = c.strip()
            for m in months:
                if m.lower() in c_clean.lower() or (m == 'Agt' and 'agu' in c_clean.lower()):
                    m_name = m
                    break
            if m_name: break
        
        if m_name:
            dur_row = rows[i+1]
            likes_row = rows[i+2]
            view_row = rows[i+3]
            comm_row = rows[i+4]
            book_row = rows[i+5]

            def extract_daily(row):
                vals = []
                for c in row[1:]:
                    c_clean = c.strip().replace(',', '.')
                    if any(w in c_clean.lower() for w in ['duration', 'likes', 'viewer', 'comment', 'booking', '/day', '/month']):
                        break
                    try:
                        vals.append(float(c_clean))
                    except:
                        pass
                return vals

            durs = extract_daily(dur_row)
            likes = extract_daily(likes_row)
            views = extract_daily(view_row)
            comms = extract_daily(comm_row)
            books = extract_daily(book_row)

            avg_dur = round(sum(durs)/len(durs)) if durs else 0
            avg_likes = round(sum(likes)/len(likes)) if likes else 0
            avg_view = round(sum(views)/len(views)) if views else 0
            avg_comm = round(sum(comms)/len(comms)) if comms else 0
            tot_book = int(sum(books)) if books else 0

            for c_idx, c in enumerate(book_row):
                if 'booking /month' in c.lower() and c_idx + 1 < len(book_row):
                    try:
                        tot_book = int(float(book_row[c_idx+1].strip().replace(',', '.')))
                    except:
                        pass

            data_by_month[m_name] = {
                'month': m_name,
                'duration': avg_dur,
                'likes': avg_likes,
                'viewer': avg_view,
                'comments': avg_comm,
                'booking': tot_book,
                'has_data': True
            }
            i += 6
            continue
    i += 1

all_months = ["Jan", "Feb", "Mar", "Apr", "Mei", "Jun", "Jul", "Agt", "Sep", "Okt", "Nov", "Des"]
monthly_trend = []
active_durs, active_likes, active_views, active_comms = [], [], [], []
total_booking = 0

for m in all_months:
    if m in data_by_month:
        d = data_by_month[m]
        monthly_trend.append(d)
        active_durs.append(d['duration'])
        active_likes.append(d['likes'])
        active_views.append(d['viewer'])
        active_comms.append(d['comments'])
        total_booking += d['booking']
    else:
        monthly_trend.append({
            'month': m,
            'duration': None,
            'likes': None,
            'viewer': None,
            'comments': None,
            'booking': None,
            'has_data': False
        })

n = len(active_durs) or 1
kpis = {
    "duration_minutes": { "value": round(sum(active_durs)/n), "unit": "Menit/sesi", "label": "Duration (Minute)" },
    "likes_per_day": { "value": round(sum(active_likes)/n), "unit": "Likes/hari", "label": "Likes / day" },
    "viewer_per_day": { "value": round(sum(active_views)/n), "unit": "Viewer/hari", "label": "Viewer / day" },
    "comments_per_day": { "value": round(sum(active_comms)/n), "unit": "Komen/hari", "label": "Comment / day" },
    "total_booking": { "value": total_booking, "unit": "Unit Booking", "label": "Booking Acquired" }
}

with open('data/booking_data.json', 'r', encoding='utf-8') as f:
    bk = json.load(f)

bk['tiktok_live'] = {
    "title": "Performa Live TikTok Bengkel",
    "source": "Google Sheets (LIVE TIKTOK - GID 1727895687)",
    "kpis": kpis,
    "monthly_trend": monthly_trend
}

with open('data/booking_data.json', 'w', encoding='utf-8') as f:
    json.dump(bk, f, ensure_ascii=False, indent=2)

print("Updated data/booking_data.json with accurate TikTok Live values!")
print(f"Total Booking: {total_booking} Unit")
print(f"Average Duration: {round(sum(active_durs)/n)} Menit")
print(f"Average Likes: {round(sum(active_likes)/n)} Likes/hari")
print(f"Average Viewer: {round(sum(active_views)/n)} Viewer/hari")
print(f"Average Comments: {round(sum(active_comms)/n)} Komen/hari")
