import json
import string
import requests
import time
import subprocess

def generate_mapping():
    print("Mulai proses scraping ID Negara dari TIKI...")
    
    # Ambil list country dari MySQL Komerce
    print("Mengambil daftar negara dari database...")
    cmd = 'mysql -u root -e "SELECT country FROM dev_openapi_tariff.international_destination;"'
    try:
        output = subprocess.check_output(cmd, shell=True, text=True)
        countries = [line.strip() for line in output.split('\\n') if line.strip() and line.strip() != 'country']
    except Exception as e:
        print("Gagal connect DB:", e)
        # Fallback list manual aja
        countries = ["SINGAPORE", "MALAYSIA", "TAIWAN", "HONG KONG", "JAPAN", "SOUTH KOREA", "CHINA", "UNITED STATES", "UNITED KINGDOM", "AUSTRALIA", "SAUDI ARABIA", "UNITED ARAB EMIRATES", "THAILAND", "VIETNAM", "PHILIPPINES", "INDIA"]

    results = {}
    
    print(f"Mulai fetching ID dari {len(countries)} negara...")
    
    for country in countries:
        try:
            r = requests.get(f'https://www.tiki.id/api/area-tariff?term={country}', timeout=10)
            if r.status_code == 200:
                data = r.json()
                # Kadang ada banyak hasil, cari yang persis match namanya
                for item in data:
                    name = str(item.get('name', '')).strip().upper()
                    code = str(item.get('code', '')).strip()
                    
                    if '.' not in code and not any(char.isdigit() for char in name):
                        results[name] = code
                        # Jika sudah ketemu match, gak perlu loop lagi
                        break
        except Exception as e:
            pass
            
        time.sleep(0.1) # Jangan nge-spam
            
    # Simpan ke JSON
    with open("tiki_country_map.json", "w") as f:
        json.dump(results, f, indent=4)
        
    print(f"Selesai! Ditemukan {len(results)} negara internasional.")

if __name__ == "__main__":
    generate_mapping()
