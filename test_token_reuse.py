import time
import json
from scrapling import Fetcher, StealthyFetcher

print("=== TESTING TOKEN REUSE FOR 100-200ms SPEED ===")

captured_url = []

def script_action(page):
    def handle_request(request):
        if "/api/tariff" in request.url:
            captured_url.append(request.url)

    page.on("request", handle_request)
    page.evaluate("""
        () => {
            document.querySelector('#origin').value = 'DPK01.00';
            document.querySelector('#dest').value = '173';
            document.querySelector('#from_').value = 'DEPOK';
            document.querySelector('#to_').value = 'SINGAPORE';
            document.querySelector('#berat_').value = '1';
            document.querySelector('.tracking-btn-cek-ongkir').click();
        }
    """)
    page.wait_for_timeout(2000)

StealthyFetcher.fetch("https://www.tiki.id/id/cek-ongkir", page_action=script_action, headless=True)

if captured_url:
    full_url = captured_url[0]
    print("\nCaptured API URL with Token:")
    print(full_url[:100] + "...")

    # Now test reusing this URL/token with fast HTTP Fetcher for DIFFERENT destinations!
    # Replace dest/to in the URL with MALAYSIA (174)
    fast_url = full_url.replace("SINGAPORE", "MALAYSIA").replace("dest=173", "dest=174")

    print("\nExecuting Direct HTTP Fetch with reused Token...")
    t0 = time.time()
    fetcher = Fetcher()
    resp = fetcher.get(fast_url, headers={
        "Referer": "https://www.tiki.id/id/cek-ongkir",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/124.0.0.0 Safari/537.36"
    })
    elapsed = time.time() - t0
    print(f"[FAST HTTP RESPONSE TIME]: {elapsed:.3f} seconds ({elapsed*1000:.0f} ms)!")
    print("Status:", resp.status)
    if resp.status == 200:
        print("Data received:", resp.json())
