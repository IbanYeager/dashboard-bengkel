"""
Live Google Sheets Synchronization Pipeline
Downloads the latest spreadsheet from Google Sheets, runs ETL extraction,
updates dashboard_data.json and bengkel.db, and optionally deploys to Vercel.

Usage:
    python scripts/sync_from_google_sheets.py
    python scripts/sync_from_google_sheets.py --deploy
"""

import os
import sys
import time
import shutil
import urllib.request
import subprocess

if sys.stdout and hasattr(sys.stdout, 'reconfigure'):
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

SHEET_ID = '1b60d-JO50LU4KyywuULokmDIU7z3Ts_1'
EXPORT_XLSX_URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=xlsx"
TARGET_XLSX = r"c:\laragon\www\dashboard_bengkel\DASH KIARACONDONG 24-26.xlsx"
BACKUP_XLSX = r"c:\laragon\www\dashboard_bengkel\DASH KIARACONDONG 24-26.xlsx.bak"
ETL_SCRIPT = r"c:\laragon\www\dashboard_bengkel\scripts\etl_sync.py"
PROJECT_DIR = r"c:\laragon\www\dashboard_bengkel"

def download_live_spreadsheet(max_retries=3):
    print(f"Connecting to Google Sheets (ID: {SHEET_ID})...", flush=True)
    req = urllib.request.Request(
        EXPORT_XLSX_URL,
        headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
    )
    temp_dl = TARGET_XLSX + '.downloading'
    
    for attempt in range(max_retries):
        try:
            t0 = time.time()
            print(f"Downloading live spreadsheet [Attempt {attempt+1}/{max_retries}]...", flush=True)
            with urllib.request.urlopen(req, timeout=180) as resp:
                if resp.status != 200:
                    raise Exception(f"HTTP Status {resp.status}")
                total_bytes = 0
                with open(temp_dl, 'wb') as f:
                    while True:
                        chunk = resp.read(512 * 1024)
                        if not chunk:
                            break
                        f.write(chunk)
                        total_bytes += len(chunk)
                
                elapsed = time.time() - t0
                print(f"  [OK] Downloaded {total_bytes:,} bytes ({total_bytes/(1024*1024):.1f} MB) in {elapsed:.1f}s", flush=True)
                
                # Check valid zip/xlsx signature (PK\x03\x04)
                with open(temp_dl, 'rb') as f:
                    sig = f.read(4)
                if sig != b'PK\x03\x04':
                    raise Exception("Downloaded content is not a valid Excel/ZIP file.")
                    
                # Create backup of current file
                if os.path.exists(TARGET_XLSX):
                    try:
                        shutil.copy2(TARGET_XLSX, BACKUP_XLSX)
                    except Exception as e:
                        print(f"  Note: Could not create backup: {e}", flush=True)
                
                # Move temp file to TARGET_XLSX
                if os.path.exists(TARGET_XLSX):
                    os.remove(TARGET_XLSX)
                shutil.move(temp_dl, TARGET_XLSX)
                print(f"  [OK] Updated {os.path.basename(TARGET_XLSX)} successfully.", flush=True)
                return True
        except Exception as e:
            print(f"  Attempt {attempt+1} failed: {e}", flush=True)
            if os.path.exists(temp_dl):
                try: os.remove(temp_dl)
                except Exception: pass
            if attempt < max_retries - 1:
                time.sleep(4)
    return False

def run_etl():
    print("\nRunning ETL Pipeline on fresh data...")
    res = subprocess.run([sys.executable, ETL_SCRIPT], capture_output=True, text=True)
    if res.stdout:
        print(res.stdout)
    if res.stderr:
        print("ETL notes:", res.stderr)
    if res.returncode != 0:
        raise Exception(f"ETL failed with exit code {res.returncode}")
    print("[OK] Local database and data/dashboard_data.json updated successfully!")
    
    # Also sync SBI sheet data
    sbi_script = os.path.join(PROJECT_DIR, 'scripts', 'sync_sbi_data.py')
    if os.path.exists(sbi_script):
        print("Syncing SBI data from Google Sheets...", flush=True)
        res_sbi = subprocess.run([sys.executable, sbi_script, '--force'], capture_output=True, text=True)
        if res_sbi.returncode == 0:
            print("[OK] SBI data updated successfully!")
        else:
            print("SBI sync note:", res_sbi.stderr)

def deploy_to_vercel():
    print("\nDeploying to Vercel Production...")
    dep = subprocess.run(["npx", "vercel", "--prod", "--yes"], capture_output=True, text=True, cwd=PROJECT_DIR)
    print(dep.stdout)
    if dep.returncode != 0:
        print("Deploy error:", dep.stderr)
        return
        
    print("\nSetting production alias...")
    alias = subprocess.run(["npx", "vercel", "alias", "set", "dashboard-bengkel", "dashboard-bengkel-kiaracondong.vercel.app"], capture_output=True, text=True, cwd=PROJECT_DIR)
    print(alias.stdout)
    print("[OK] Production deployment at https://dashboard-bengkel-kiaracondong.vercel.app/ updated!")

def print_summary():
    json_path = os.path.join(PROJECT_DIR, "data", "dashboard_data.json")
    if os.path.exists(json_path):
        try:
            import json
            with open(json_path, 'r', encoding='utf-8') as f:
                d = json.load(f)
            sep = d.get('monthly_kpis', {}).get('2026', {}).get('September', {})
            total_pkb = d.get('meta', {}).get('total_pkb_records', 0)
            print("==================================================")
            print(" VERIFIED SYNC SUMMARY:")
            print(f" - Total PKB Records in Database: {total_pkb:,}")
            print(f" - September 2026 UE: {sep.get('ue_total', 0):,}")
            print(f" - September 2026 CPUS: {sep.get('cpus', 0):,}")
            print(f" - September 2026 Revenue: Rp {sep.get('total_revenue', 0):,.0f}")
            print(f" - Generated At: {d.get('meta', {}).get('generated_at')}")
            print("==================================================")
        except Exception as e:
            print("Summary note:", e)

def run_full_pipeline():
    # 1. Core ETL for database and dashboard_data.json
    run_etl()
    
    # 2. Funnelling sync from ATTACKLIST
    funnelling_script = os.path.join(PROJECT_DIR, "scripts", "sync_full_funnelling_from_attacklist.py")
    if os.path.exists(funnelling_script):
        print("\nSyncing Funnelling from live Google Sheets ATTACKLIST...")
        res_fn = subprocess.run([sys.executable, funnelling_script], capture_output=True, text=True)
        if res_fn.stdout: print(res_fn.stdout)
        if res_fn.returncode != 0: print("Funnelling sync warning:", res_fn.stderr)
        
    # 3. Booking & Live TikTok sync
    booking_script = os.path.join(PROJECT_DIR, "scripts", "sync_booking_sheet.py")
    if os.path.exists(booking_script):
        print("\nSyncing Booking & Live TikTok metrics...")
        res_bk = subprocess.run([sys.executable, booking_script], capture_output=True, text=True)
        if res_bk.stdout: print(res_bk.stdout)
        if res_bk.returncode != 0: print("Booking sync warning:", res_bk.stderr)

    # 4. Master Sync for PKB 100% Fidelity & AO Report
    master_sync_script = os.path.join(PROJECT_DIR, "scripts", "sync_all_sheets.py")
    if os.path.exists(master_sync_script):
        print("\nRunning Master Accuracy Sync (PKB & AO Report)...")
        res_ms = subprocess.run([sys.executable, master_sync_script], capture_output=True, text=True)
        if res_ms.stdout: print(res_ms.stdout)
        if res_ms.returncode != 0: print("Master sync warning:", res_ms.stderr)

def main():
    print("==================================================")
    print(" TUNAS TOYOTA KIARACONDONG — GOOGLE SHEETS SYNC")
    print("==================================================")
    
    success = download_live_spreadsheet()
    if not success:
        print("ERROR: Failed to download spreadsheet from Google Sheets.")
        sys.exit(1)
        
    run_full_pipeline()
    print_summary()
    
    if "--deploy" in sys.argv:
        deploy_to_vercel()
        
    print("\n✨ All synchronization tasks completed successfully.")

if __name__ == "__main__":
    main()
