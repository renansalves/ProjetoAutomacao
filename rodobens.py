import requests
import re
import csv
import time
import json

API_FILE = "/home/renanalves/Downloads/Empresa.json"  # Local file with API response
OUTPUT_FILE = "rodobens_all_filiais_complete.csv"
REPORT_FILE = "rodobens_missing_report.csv"
LOCATIONIQ_API_KEY = "YOUR_LOCATIONIQ_API_KEY"  # Replace with your actual key

# Extract coordinates from iframe URL
def extrair_coordenadas(url):
    lon_match = re.search(r"!2d(-?\d+\.\d+)", url)
    lat_match = re.search(r"!3d(-?\d+\.\d+)", url)
    if lon_match and lat_match:
        return float(lat_match.group(1)), float(lon_match.group(1))
    return None, None

# Resolve short Google Maps URLs
def resolver_url_curta(url):
    try:
        if "goo.gl/maps" in url or "maps.app.goo.gl" in url:
            resp = requests.get(url, allow_redirects=True, timeout=10)
            return resp.url
    except Exception as e:
        print(f"[WARN] Failed to resolve short URL: {e}")
    return url

# Nominatim reverse geocoding with retry
def obter_endereco_nominatim(lat, lon, max_retries=3):
    attempt = 0
    while attempt < max_retries:
        try:
            url = f"https://nominatim.openstreetmap.org/reverse?format=json&lat={lat}&lon={lon}&addressdetails=1"
            headers = {"User-Agent": "RodobensDataCollector/1.0"}
            print(f"[INFO] Nominatim request for lat={lat}, lon={lon} (Attempt {attempt+1})")
            resp = requests.get(url, headers=headers, timeout=10)
            resp.raise_for_status()
            data = resp.json()
            endereco = data.get("display_name", "")
            address = data.get("address", {})
            cidade = address.get("city") or address.get("town") or address.get("village", "")
            estado = address.get("state", "")
            cep = address.get("postcode", "")
            if endereco:
                print(f"[SUCCESS] Nominatim found: {endereco}")
                return endereco, cidade, estado, cep
        except Exception as e:
            print(f"[ERROR] Nominatim failed (Attempt {attempt+1}): {e}")
        attempt += 1
        if attempt < max_retries:
            wait_time = 2 ** attempt
            print(f"[INFO] Retrying Nominatim in {wait_time}s...")
            time.sleep(wait_time)
    return None, None, None, None

# LocationIQ fallback
def obter_endereco_locationiq(lat, lon):
    try:
        url = f"https://us1.locationiq.com/v1/reverse.php?key={LOCATIONIQ_API_KEY}&lat={lat}&lon={lon}&format=json"
        print(f"[INFO] LocationIQ fallback request for lat={lat}, lon={lon}")
        resp = requests.get(url, timeout=10)
        resp.raise_for_status()
        data = resp.json()
        endereco = data.get("display_name", "")
        address = data.get("address", {})
        cidade = address.get("city") or address.get("town") or address.get("village", "")
        estado = address.get("state", "")
        cep = address.get("postcode", "")
        print(f"[SUCCESS] LocationIQ found: {endereco}")
        return endereco, cidade, estado, cep
    except Exception as e:
        print(f"[ERROR] LocationIQ failed: {e}")
        return '', '', '', ''

# Fallback search by name + city
def buscar_por_nome(nome, cidade):
    try:
        query = f"{nome} {cidade}".strip()
        url = f"https://nominatim.openstreetmap.org/search?format=json&q={query}&addressdetails=1&limit=1"
        headers = {"User-Agent": "RodobensDataCollector/1.0"}
        print(f"[INFO] Searching by name: {query}")
        resp = requests.get(url, headers=headers, timeout=10)
        resp.raise_for_status()
        results = resp.json()
        if results:
            lat = float(results[0]["lat"])
            lon = float(results[0]["lon"])
            return obter_endereco_nominatim(lat, lon)
    except Exception as e:
        print(f"[ERROR] Name-based search failed: {e}")
    return '', '', '', ''

def limpar_telefone(telefone):
    return "" if "S/N" in telefone else telefone

def processar_empresa(nome, cnpj, telefones, coordenadas, cidade_hint=""):
    endereco, cidade, estado, cep = '', '', '', ''
    if coordenadas:
        url_resolvida = resolver_url_curta(coordenadas)
        lat, lon = extrair_coordenadas(url_resolvida)
        if lat and lon:
            endereco, cidade, estado, cep = obter_endereco_nominatim(lat, lon)
            if endereco is None:
                endereco, cidade, estado, cep = obter_endereco_locationiq(lat, lon)
            time.sleep(1)
        else:
            print("[WARN] Coordinates not found, trying name-based search...")
            endereco, cidade, estado, cep = buscar_por_nome(nome, cidade_hint)
    else:
        print("[WARN] No iframe URL provided, trying name-based search...")
        endereco, cidade, estado, cep = buscar_por_nome(nome, cidade_hint)

    return {
        "nome": nome,
        "cnpj": cnpj,
        "telefone": ", ".join([limpar_telefone(t) for t in telefones]),
        "endereco": endereco,
        "cidade": cidade,
        "estado": estado,
        "cep": cep
    }

def main():
    with open(API_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)

    resultados = []
    faltantes = []

    for item in data:
        if "descricao" in item:
            empresa = processar_empresa(item.get("descricao", ""), item.get("cnpj", ""), item.get("telefones", []), item.get("coordenadasMapa", ""))
            resultados.append(empresa)
            if not empresa["endereco"]:
                faltantes.append(empresa)

        if "empresas" in item:
            for empresa_data in item["empresas"]:
                nome = empresa_data.get("razaoSocial", "")
                cnpj = empresa_data.get("cnpj", "")
                telefones = empresa_data.get("telefones", [])
                coordenadas = empresa_data.get("coordenadasMapa", "")
                empresa = processar_empresa(nome, cnpj, telefones, coordenadas)
                resultados.append(empresa)
                if not empresa["endereco"]:
                    faltantes.append(empresa)

    # Save main CSV
    with open(OUTPUT_FILE, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=resultados[0].keys())
        writer.writeheader()
        writer.writerows(resultados)

    # Save missing report
    with open(REPORT_FILE, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=faltantes[0].keys())
        writer.writeheader()
        writer.writerows(faltantes)

    print(f"[INFO] CSV generated: {OUTPUT_FILE}")
    print(f"[INFO] Missing report generated: {REPORT_FILE}")
    print(f"[SUMMARY] Total: {len(resultados)}, Missing: {len(faltantes)}")

if __name__ == "__main__":
    main()

