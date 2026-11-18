import urllib.request
import time
import sys
import os

if sys.stdout and hasattr(sys.stdout, 'reconfigure'):
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

SHEET_ID = '1b60d-JO50LU4KyywuULokmDIU7z3Ts_1'
EXPORT_XLSX_URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=xlsx"
TEMP_FILE = r"c:\laragon\www\dashboard_bengkel\scripts\live_download_temp.xlsx"

print("Connecting to Google Sheets export URL...", flush=True)
req = urllib.request.Request(
    EXPORT_XLSX_URL,
    headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
)

t0 = time.time()
try:
    with urllib.request.urlopen(req, timeout=120) as resp:
        print(f"Connected! HTTP Status: {resp.status}. Starting download...", flush=True)
        total_downloaded = 0
        with open(TEMP_FILE, 'wb') as f:
            while True:
                chunk = resp.read(1024 * 512) # 512 KB
                if not chunk:
                    break
                f.write(chunk)
                total_downloaded += len(chunk)
                print(f"Downloaded: {total_downloaded / (1024*1024):.2f} MB in {time.time() - t0:.1f}s", flush=True)
    print(f"Download complete: {total_downloaded:,} bytes ({total_downloaded / (1024*1024):.2f} MB) in {time.time() - t0:.1f}s", flush=True)
except Exception as e:
    print(f"Download failed: {e}", flush=True)
    sys.exit(1)
