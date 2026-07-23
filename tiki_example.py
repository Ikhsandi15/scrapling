import json
import time
from playwright.sync_api import sync_playwright

class TikiScraperPool:
    def __init__(self):
        self.playwright = None
        self.browser = None
        self.context = None
        self.page = None

    def initialize(self):
        if not self.page or self.page.is_closed():
            print("[TikiScraperPool] Inisialisasi Pre-loaded Playwright Browser...")
            self.playwright = sync_playwright().start()
            self.browser = self.playwright.chromium.launch(
                headless=True,
                args=["--no-sandbox", "--disable-setuid-sandbox", "--disable-dev-shm-usage"]
            )
            self.context = self.browser.new_context()
            self.page = self.context.new_page()
            
            # Block resource berat (gambar, font, css, media)
            self.page.route("**/*.{png,jpg,jpeg,gif,svg,css,woff2,ttf}", lambda route: route.abort())
            
            # Pre-load halaman TIKI
            self.page.goto("https://www.tiki.id/id/cek-ongkir", wait_until="domcontentloaded")
            self.page.wait_for_timeout(1000)
            print("[TikiScraperPool] Pre-loaded Browser SIAP (Sub-2 Second Mode)!")

    def get_tariff(self, from_name: str, origin_code: str, to_name: str, dest_code: str, weight: int = 1):
        start_time = time.time()
        
        # MENGGUNAKAN MODE DINAMIS (NGETIK): tidak perlu mapping lagi
        # Script akan mengetik to_name di kolom input, lalu TIKI akan memunculkan dropdown
        # yang berisi kode rahasianya (dest_code)

        try:
            self.initialize()
        except Exception as e:
            print(f"[TikiScraperPool Error] Gagal init browser: {e}")
            return None

        captured_json = []

        def handle_response(response):
            if "/api/tariff" in response.url:
                try:
                    captured_json.append(response.json())
                except Exception:
                    pass

        # Pasang listener respons
        self.page.on("response", handle_response)

        # Execute DOM Injection untuk Origin dan Weight
        try:
            self.page.evaluate("""
                (args) => {
                    const orig = document.querySelector('#origin');
                    if (orig) orig.value = args.origin_code;

                    const fromInput = document.querySelector('#from_');
                    if (fromInput) fromInput.value = args.from_name;

                    const beratInput = document.querySelector('#berat_');
                    if (beratInput) beratInput.value = args.weight;
                }
            """, {
                "from_name": from_name,
                "origin_code": origin_code,
                "weight": str(weight)
            })

            # Eksekusi Dinamis untuk Destination (Ngetik & Klik Autocomplete)
            self.page.fill('#to_', to_name)
            self.page.wait_for_selector('.tt-suggestion', timeout=4000)
            self.page.click('.tt-suggestion:first-child')
            
            # Klik tombol cek ongkir
            self.page.click('.tracking-btn-cek-ongkir')

        except Exception as e:
            print(f"[TikiScraperPool Error] Evaluate DOM error: {e}")

        # Polling respons API TIKI secara instan (max 5 detik, break langsung saat data tertangkap)
        for _ in range(100):
            if captured_json:
                break
            self.page.wait_for_timeout(50)

        # Lepas listener agar tidak menumpuk
        try:
            self.page.remove_listener("response", handle_response)
        except Exception:
            pass

        elapsed = time.time() - start_time
        print(f"[FAST SCRAPLING] Response TIKI selesai dalam: {elapsed:.2f} detik")

        if captured_json:
            return captured_json[0]
        
        # Jika gagal/timeout, coba reload halaman background untuk request berikutnya
        print("[TikiScraperPool] Refreshing preloaded page background...")
        try:
            self.page.reload(wait_until="domcontentloaded")
        except Exception:
            pass
        return None

# Singleton Instance
tiki_pool = TikiScraperPool()

def get_tiki_tariff(from_name: str, origin_code: str, to_name: str, dest_code: str, weight: int = 1):
    return tiki_pool.get_tariff(from_name, origin_code, to_name, dest_code, weight)

if __name__ == "__main__":
    tiki_pool.initialize()
    print("Testing Run 1:")
    get_tiki_tariff("DEPOK", "DPK01.00", "SINGAPORE", "173", 1)
    print("Testing Run 2:")
    get_tiki_tariff("JAKARTA", "CGK01.00", "MALAYSIA", "174", 2)
