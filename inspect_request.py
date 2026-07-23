from scrapling import StealthyFetcher

def script_action(page):
    def handle_request(request):
        if "/api/tariff" in request.url:
            print("\n=== CAPTURED REQUEST DETAILS ===")
            print("URL:", request.url)
            print("Headers:", json.dumps(request.headers, indent=2))
            print("================================\n")

    import json
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
