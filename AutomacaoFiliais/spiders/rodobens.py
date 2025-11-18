import requests
import re
import csv
import time

API_URL = "https://cms-integracao.rodobens.com.br/api/Empresa"
OUTPUT_FILE = "rodobens_filiais_nominatim.csv"

# Extract coordinates from iframe URL
def extrair_coordenadas(url):
    lon_match = re.search(r"!2d(-?\d+\.\d+)", url)
    lat_match = re.search(r"!3d(-?\d+\.\d+)", url)
    if lon_match and lat_match:
        return float(lat_match.group(1)), float(lon_match.group(1))
    return None, None

# Get structured address from OpenStreetMap Nominatim API
def obter_endereco_nominatim(lat, lon):
    try:
        url = f"https://nominatim.openstreetmap.org/reverse?format=json&lat={lat}&lon={lon}&addressdetails=1"
        headers = {"User-Agent": "RodobensDataCollector/1.0"}
        resp = requests.get(url, headers=headers)
        resp.raise_for_status()
        data = resp.json()
        endereco = data.get("display_name", "")
        address = data.get("address", {})
        cidade = address.get("city") or address.get("town") or address.get("village", "")
        estado = address.get("state", "")
        cep = address.get("postcode", "")
        return endereco, cidade, estado, cep
    except Exception as e:
        print(f"Erro ao consultar Nominatim: {e}")
        return '', '', '', ''

def main():
    try:
        response = requests.get(API_URL)
        response.raise_for_status()
        data = response.json()
    except Exception as e:
        print(f"Erro ao acessar API Rodobens: {e}")
        return

    resultados = []

    for item in data:
        descricao = item.get("descricao", "")
        cnpj = item.get("cnpj", "")
        telefones = ", ".join(item.get("telefones", []))
        coordenadas_embed = item.get("coordenadasMapa", "")

        endereco, cidade, estado, cep = '', '', '', ''
        if coordenadas_embed:
            lat, lon = extrair_coordenadas(coordenadas_embed)
            if lat and lon:
                endereco, cidade, estado, cep = obter_endereco_nominatim(lat, lon)
                time.sleep(2)  # Respect Nominatim rate limit (1 request/sec)

        resultados.append({
            "nome": descricao,
            "cnpj": cnpj,
            "telefone": telefones,
            "endereco": endereco,
            "cidade": cidade,
            "estado": estado,
            "cep": cep
        })

    if resultados:
        with open(OUTPUT_FILE, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=resultados[0].keys())
            writer.writeheader()
            writer.writerows(resultados)

    print(f"CSV completo gerado com sucesso: {OUTPUT_FILE}")

if __name__ == "__main__":
    main()
