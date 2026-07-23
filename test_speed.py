import time
import json
from scrapling import Fetcher

url_page = "https://www.tiki.id/id/cek-ongkir"
url_api = "https://www.tiki.id/api/tariff"

params = {
    "from": "DEPOK",
    "origin": "DPK01.00",
    "to": "SINGAPORE",
    "dest": "173",
    "weight": "1"
}

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Referer": "https://www.tiki.id/id/cek-ongkir",
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "id-ID,id;q=0.9,en-US;q=0.8,en;q=0.7",
}

print("=== TEST 2: Session Fetcher (Cookies + Fast HTTP) ===")
start = time.time()
try:
    fetcher = Fetcher()
    # Step 1: Visit main page to get session cookies
    page_resp = fetcher.get(url_page, headers=headers)
    t1 = time.time() - start
    print(f"Step 1 (Visit Page): Status {page_resp.status}, Elapsed: {t1:.3f}s")

    # Step 2: Hit API endpoint directly using same session/cookies
    api_resp = fetcher.get(url_api, params=params, headers=headers)
    t2 = time.time() - start
    print(f"Step 2 (Hit API): Status {api_resp.status}, Total Elapsed: {t2:.3f}s")
    print("Response JSON:", api_resp.json())
except Exception as e:
    print("Session Fetcher Error:", e)
