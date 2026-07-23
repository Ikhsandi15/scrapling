import json
from typing import Dict, Any, List, Optional
from scrapling import Fetcher, StealthyFetcher

def fetch_api_direct(url: str, method: str = "GET", headers: Optional[Dict[str, str]] = None, params: Optional[Dict[str, Any]] = None) -> Any:
    """
    1. Direct API Fetcher:
       Menembak endpoint API APA SAJA secara langsung tanpa terikat situs tertentu.
       
       :param url: Full URL endpoint target (contoh: "https://api.example.com/v1/tariff")
       :param method: HTTP Method ("GET" atau "POST")
       :param headers: Dictionary HTTP Headers opsional
       :param params: Dictionary Query Params / Body JSON opsional
    """
    fetcher = Fetcher()
    method_upper = method.upper()
    
    if method_upper == "POST":
        response = fetcher.post(url, headers=headers, json=params)
    else:
        response = fetcher.get(url, headers=headers, params=params)
        
    if response.status == 200:
        try:
            return response.json()
        except Exception:
            return response.text
    return {"status": response.status, "text": response.text[:300]}


def capture_network_api(target_page_url: str, api_keyword: str, timeout_ms: int = 5000) -> List[Any]:
    """
    2. Generic Page Interceptor:
       Membuka halaman web APA SAJA di latar belakang, dan otomatis menangkap 
       semua respon JSON dari API yang mengandung `api_keyword`.
       
       :param target_page_url: URL web tempat form berada (contoh: "https://example.com/cek-ongkir")
       :param api_keyword: Kata kunci endpoint yang ingin ditangkap (contoh: "/tariff" atau "/cek")
       :param timeout_ms: Berapa milidetik peramban menunggu aktivitas jaringan
    """
    captured_data = []

    def page_listener(page):
        def on_response(response):
            if api_keyword in response.url and response.status == 200:
                print(f"[+] Response API Ditangkap dari: {response.url[:80]}...")
                try:
                    data = response.json()
                    captured_data.append(data)
                except Exception:
                    pass

        page.on("response", on_response)
        page.wait_for_timeout(timeout_ms)

    StealthyFetcher.fetch(
        target_page_url,
        page_action=page_listener,
        headless=True  # 100% Otomatis di latar belakang
    )

    return captured_data


if __name__ == "__main__":
    print("=== DEMO GENERIC SCRAPER (BISA UNTUK ENDPOINT APA SAJA) ===")
    
    # -------------------------------------------------------------------
    # Contoh 1: Direct API Request ke Endpoint Publik Mana Pun
    # -------------------------------------------------------------------
    endpoint_target = "https://httpbin.org/get"
    print(f"\n[1] Menembak API Direct: {endpoint_target}")
    
    res1 = fetch_api_direct(
        url=endpoint_target,
        method="GET",
        params={"origin": "DEPOK", "destination": "SINGAPORE"}
    )
    print(json.dumps(res1, indent=2))
    
    # -------------------------------------------------------------------
    # Contoh 2: Capture Network dari Web Mana Pun yang Mengandung /api/
    # -------------------------------------------------------------------
    web_target = "https://www.tiki.id/id/cek-ongkir"
    print(f"\n[2] Membuka web '{web_target}' & menangkap API ber-keyword '/api/tariff'...")
    
    res2 = capture_network_api(
        target_page_url=web_target,
        api_keyword="/api/tariff",
        timeout_ms=3000
    )
    if res2:
        print(json.dumps(res2[0], indent=2))
