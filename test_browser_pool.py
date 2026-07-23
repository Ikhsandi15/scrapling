import time
import json
from playwright.sync_api import sync_playwright

print("=== TESTING PRE-LOADED PAGE REUSE (SUB-SECOND SPEED) ===")
p = sync_playwright().start()
browser = p.chromium.launch(headless=True)
context = browser.new_context()

# Pre-load page ONCE at startup
page = context.new_page()
page.route("**/*.{png,jpg,jpeg,gif,svg,css,woff,woff2,ttf}", lambda route: route.abort())
page.goto("https://www.tiki.id/id/cek-ongkir", wait_until="domcontentloaded")
page.wait_for_timeout(1000) # Ensure recaptcha script loaded

def get_tariff_preloaded(from_name, origin_code, to_name, dest_code, weight):
    t0 = time.time()
    captured_json = []

    def handle_response(response):
        if "/api/tariff" in response.url:
            try:
                captured_json.append(response.json())
            except Exception:
                pass

    listener = page.on("response", handle_response)

    page.evaluate("""
        (args) => {
            const orig = document.querySelector('#origin');
            if (orig) orig.value = args.origin_code;
            
            const dest = document.querySelector('#dest');
            if (dest) dest.value = args.dest_code;

            const fromInput = document.querySelector('#from_');
            if (fromInput) fromInput.value = args.from_name;

            const toInput = document.querySelector('#to_');
            if (toInput) toInput.value = args.to_name;

            const beratInput = document.querySelector('#berat_');
            if (beratInput) beratInput.value = args.weight;

            const btn = document.querySelector('.tracking-btn-cek-ongkir');
            if (btn) btn.click();
        }
    """, {
        "from_name": from_name,
        "origin_code": origin_code,
        "to_name": to_name,
        "dest_code": dest_code,
        "weight": str(weight)
    })

    for _ in range(30):
        if captured_json:
            break
        page.wait_for_timeout(50)

    page.remove_listener("response", handle_response)
    elapsed = time.time() - t0
    print(f"[ULTRA FAST PRE-LOADED] Response received in: {elapsed:.3f}s")
    return captured_json[0] if captured_json else None

print("\nRequest 1:")
get_tariff_preloaded("DEPOK", "DPK01.00", "SINGAPORE", "173", 1)

print("\nRequest 2:")
get_tariff_preloaded("JAKARTA", "CGK01.00", "MALAYSIA", "174", 2)

browser.close()
p.stop()
