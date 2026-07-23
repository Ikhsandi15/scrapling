import json
import urllib.parse
from http.server import HTTPServer, BaseHTTPRequestHandler
from generic_scraper import fetch_api_direct, capture_network_api
from tiki_example import get_tiki_tariff

class ScraplingAPIHandler(BaseHTTPRequestHandler):
    def _send_json(self, data, status=200):
        self.send_response(status)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps(data).encode('utf-8'))

    def do_GET(self):
        parsed_path = urllib.parse.urlparse(self.path)
        query_dict = urllib.parse.parse_qs(parsed_path.query)
        params = {k: v[0] for k, v in query_dict.items()}

        if parsed_path.path == "/health":
            self._send_json({"status": "OK", "service": "Scrapling API Microservice"})
            return

        # Dedicated endpoint untuk TIKI (Otomatis handle reCAPTCHA token via StealthyFetcher)
        if parsed_path.path == "/api/scrape/tiki":
            from_name = params.get('from', 'DEPOK')
            origin_code = params.get('origin', 'DPK01.00')
            to_name = params.get('to', 'SINGAPORE')
            dest_code = params.get('dest', '173')
            
            try:
                weight = int(float(params.get('weight', 1)))
            except ValueError:
                weight = 1
            if weight < 1:
                weight = 1

            print(f"\n[Scrapling Server] Memproses request TIKI: {from_name} ({origin_code}) -> {to_name} ({dest_code}), {weight}kg")
            result = get_tiki_tariff(from_name, origin_code, to_name, dest_code, weight)
            
            if result:
                print(f"[Scrapling Server] SUCCESS MURNI! Berhasil scraping TIKI ({len(result.get('response', {}).get('data', []))} item). Mengirim data ke Golang.")
                self._send_json(result)
            else:
                self._send_json({"status": 400, "msg": "Gagal scraping TIKI", "response": None}, status=400)
            return

        if parsed_path.path == "/api/scrape/direct":
            target_url = params.pop('url', None)
            if not target_url:
                self._send_json({"error": "Parameter 'url' wajib diisi"}, status=400)
                return

            result = fetch_api_direct(target_url, method="GET", params=params)
            self._send_json(result)
            return

        if parsed_path.path == "/api/scrape/network":
            page_url = params.get('page_url')
            keyword = params.get('keyword', '/api/')
            if not page_url:
                self._send_json({"error": "Parameter 'page_url' wajib diisi"}, status=400)
                return

            results = capture_network_api(page_url, api_keyword=keyword, timeout_ms=4000)
            self._send_json({"total": len(results), "data": results})
            return

        self._send_json({"error": "Endpoint tidak ditemukan"}, status=404)

    def log_message(self, format, *args):
        print(f"[Scrapling API Server] {args[0]} - {args[1]}")

def run_server(port=5000):
    server_address = ('', port)
    httpd = HTTPServer(server_address, ScraplingAPIHandler)
    print(f"[Scrapling API] Microservice berjalan di http://localhost:{port}")
    
    # Pre-initialize browser pool untuk Sub-2 Second Mode!
    try:
        from tiki_example import tiki_pool
        tiki_pool.initialize()
    except Exception as e:
        print(f"[Warning] Inisialisasi browser pool awal terlewat: {e}")

    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n[Scrapling API] Server dihentikan.")
        httpd.server_close()

if __name__ == "__main__":
    run_server(5000)
