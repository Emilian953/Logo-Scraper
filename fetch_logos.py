import warnings
warnings.filterwarnings("ignore")

import pandas as pd
from concurrent.futures import ThreadPoolExecutor, as_completed
from tqdm import tqdm
import json

from utils import extract_hostname, try_fetch_base, safe_request_once, is_valid_image, hash_and_store_image, hashes
from logo_discovery import (
    find_logo_url,
    try_clearbit_logo,
    try_direct_favicon,
    try_duckduckgo_favicon,
    try_fallback_favicon
)

# ========== CONFIG ==========
MAX_WORKERS = 40
# ============================

df = pd.read_csv('data.csv')
domains = df['domain'].dropna().unique()

def process_site(domain):
    error_log = [f"\n🔎 Fetching {domain}..."]
    base_url, response = try_fetch_base(domain, error_log)
    hostname = extract_hostname(base_url if base_url else domain)

    if not response:
        error_log.append(f"❌ Failed to connect to {hostname}")
        error_log.append("⚠️ Proceeding with fallback methods...")

    if response:
        logo_url = find_logo_url(response.text, base_url, error_log, hostname)
        if logo_url:
            res, error = safe_request_once(logo_url)
            if error:
                error_log.append(error)
            elif res and res.status_code == 200:
                if is_valid_image(res, hostname, error_log):
                    error_log.append(f"✅ Saved logo for {hostname}")
                    return None, error_log

    if try_clearbit_logo(hostname, error_log): return None, error_log
    if try_direct_favicon(hostname, hostname, error_log): return None, error_log
    if try_fallback_favicon(domain, hostname, error_log): return None, error_log
    if try_duckduckgo_favicon(hostname, error_log): return None, error_log

    error_log.append(f"❌ Could not fetch favicon for {hostname}")
    return hostname, error_log

# --- PARALLEL EXECUTION ---
print(f"🔍Checking {len(domains)} sites...\n")
success_count = 0
failed = []
error_logs = []

with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
    futures = {executor.submit(process_site, domain): domain for domain in domains}
    progress_bar = tqdm(total=len(futures), desc="🔍 Scraping Logos", unit="site", dynamic_ncols=True)

    for future in as_completed(futures):
        result, errors = future.result()
        if result:
            failed.append(result)
        else:
            success_count += 1
        error_logs.extend(errors)
        progress_bar.update(1)
        progress_bar.set_postfix(success=success_count, failed=len(failed))

    progress_bar.close()

# --- STATS ---
failed = sorted(set(failed))
total = len(domains)

print("\n" + "=" * 50)
print("📦 LOGO SCRAPING COMPLETE — SUMMARY BELOW")
print("=" * 50)

print("\n📊 Statistics:")
print(f"🔢 Total domains:       {total}")
print(f"✅ Logos retrieved:     {success_count}")
print(f"❌ Logos failed:        {len(failed)}")

with open("logo_hashes.json", "w") as f:
    json.dump({k: str(v) for k, v in hashes.items()}, f)
print(f"💾 Saved {len(hashes)} hashes to logo_hashes.json")

if failed:
    with open("failed_logos.txt", "w") as f:
        for site in failed:
            f.write(site + "\n")
    print("💾 failed_logos.txt written.")

if error_logs:
    with open("logo_scraping_results.txt", "w", encoding='utf-8') as ef:
        for line in error_logs:
            ef.write(line + "\n")
    print("📄 logo_scraping_results.txt written.")
