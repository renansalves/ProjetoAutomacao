import csv
import json
import re
import time
import random
import requests
from urllib.parse import quote
from concurrent.futures import ThreadPoolExecutor, as_completed

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager

# ------------------ FUNÇÕES AUXILIARES ------------------ #
def delay():
    time.sleep(random.uniform(4, 7))

def extrair_cnpj(texto):
    match = re.search(r"\d{2}\.\d{3}\.\d{3}/\d{4}-\d{2}", texto)
    return match.group(0) if match else None

def extrair_endereco_google_texto(texto):
    match = re.search(r"(\bRua\b|\bAv\b|\bAvenida\b|\bR\b\.)[^,\n]+(?:,.*\d+)?", texto)
    return match.group(0) if match else None

def buscar_google(nome, estado, driver, cnpj=None):
    query = f"endereco {nome} {cnpj or ''} {estado}"
    driver.get(f"https://www.google.com/search?q={quote(query)}")
    delay()
    texto = driver.find_element(By.TAG_NAME, "body").text
    endereco = extrair_endereco_google_texto(texto)
    cnpj_encontrado = extrair_cnpj(texto)
    return endereco, cnpj_encontrado, texto

def buscar_brasilapi(cnpj):
    try:
        r = requests.get(f"https://brasilapi.com.br/api/cnpj/v1/{cnpj}")
        if r.status_code == 200:
            data = r.json()
            endereco = f"{data.get('logradouro','')}, {data.get('numero','')} - {data.get('municipio','')} - {data.get('uf','')}, {data.get('cep','')}"
            return endereco
    except:
        pass
    return None

def buscar_nominatim(nome, estado):
    try:
        query = f"{nome}, {estado}, Brasil"
        r = requests.get(f"https://nominatim.openstreetmap.org/search/{quote(query)}?format=json&addressdetails=1&limit=1")
        data = r.json()
        if data:
            return data[0].get('display_name')
    except:
        pass
    return None

def buscar_google_maps(nome, estado, driver):
    try:
        query = f"{nome}, {estado}, Brasil"
        driver.get(f"https://www.google.com/maps/search/{quote(query)}")
        delay()
        texto = driver.find_element(By.TAG_NAME, "body").text
        endereco = extrair_endereco_google_texto(texto)
        return endereco
    except:
        return None

def processar_empresa(row):
    # Cada thread cria seu próprio driver
    chrome_options = Options()
    chrome_options.add_argument("--headless=new")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

    nome = row["nome"].strip()
    estado = row.get("estado","").strip()
    cnpj = extrair_cnpj(nome)

    print(f"endereco {nome} ({estado})")

    endereco = None

    try:
        # 1️⃣ Google Nome + CNPJ
        endereco_google, cnpj_google, texto_google = buscar_google(nome, estado, driver, cnpj)
        if cnpj_google and not cnpj:
            cnpj = cnpj_google
        if endereco_google:
            endereco = endereco_google

        # 2️⃣ BrasilAPI
        if not endereco:
            if cnpj:
                endereco_brasilapi = buscar_brasilapi(cnpj)
                if endereco_brasilapi:
                    endereco = endereco_brasilapi
            # Se ainda não encontrou, tenta extrair CNPJ do texto do Google e consultar BrasilAPI
            if not endereco:
                cnpj_texto = extrair_cnpj(texto_google)
                if cnpj_texto:
                    endereco_brasilapi = buscar_brasilapi(cnpj_texto)
                    if endereco_brasilapi:
                        endereco = endereco_brasilapi
                        if not cnpj:
                            cnpj = cnpj_texto

        # 3️⃣ Nominatim
        if not endereco:
            endereco = buscar_nominatim(nome, estado)

        # 4️⃣ Google Maps
        if not endereco:
            endereco = buscar_google_maps(nome, estado, driver)

        if endereco:
            print(f"✔ Endereço encontrado: {endereco}")
        else:
            print("❌ Nenhuma fonte conseguiu encontrar endereço.")

    except Exception as e:
        print("❌ Erro ao processar:", e)
        endereco = ""
    finally:
        driver.quit()

    delay()
    return {
        "nome": nome,
        "estado": estado,
        "cnpj": cnpj or "",
        "endereco": endereco or ""
    }

# ------------------ LENDO CSV ------------------ #
input_file = "servopa_parceiros.csv"
rows = []
with open(input_file, newline="", encoding="utf-8") as f:
    reader = csv.DictReader(f)
    rows = list(reader)

# ------------------ EXECUÇÃO PARALLELA ------------------ #
results = []
with ThreadPoolExecutor(max_workers=3) as executor:
    future_to_row = {executor.submit(processar_empresa, row): row for row in rows}
    for future in as_completed(future_to_row):
        results.append(future.result())

# ------------------ SALVANDO ARQUIVOS ------------------ #
with open("servopa_enderecos_robusto.csv", "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=["nome","estado","cnpj","endereco"])
    writer.writeheader()
    writer.writerows(results)

with open("servopa_enderecos_robusto.json", "w", encoding="utf-8") as f:
    json.dump(results, f, ensure_ascii=False, indent=2)

print("✅ Processo finalizado. Arquivos gerados: servopa_enderecos_robusto.csv, servopa_enderecos_robusto.json")
