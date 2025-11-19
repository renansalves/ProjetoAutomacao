import time
import json
import csv
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

options = Options()
# options.add_argument("--headless=new")
options.add_argument("--start-maximized")
options.add_argument("--disable-blink-features=AutomationControlled")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
wait = WebDriverWait(driver, 25)

URL = "https://www.consorcioservopa.com.br/onde-encontrar#PA"

def clicar_svg_element(el):
    """
    Tenta clicar de forma segura em elementos <a class="estado"> / <path> do SVG.
    Primeiro tenta el.click() (quando possível), senão dispara um MouseEvent via JS.
    """
    try:
        el.click()
        return
    except Exception:
        pass

    # fallback: dispatchEvent no próprio elemento
    driver.execute_script("""
        const el = arguments[0];
        const evt = new MouseEvent('click', {bubbles: true, cancelable: true, view: window});
        el.dispatchEvent(evt);
    """, el)

def extrair_parceiros_para_estado(uf, nome_estado):
    """
    Aguarda .results aparecer e coleta .results .item h5 -> retorna lista de nomes
    """
    try:
        # espera até aparecer pelo menos um item (timeout reduzido para não travar)
        wait_local = WebDriverWait(driver, 8)
        wait_local.until(EC.presence_of_element_located((By.CSS_SELECTOR, ".results .item h5")))
        itens = driver.find_elements(By.CSS_SELECTOR, ".results .item h5")
        nomes = [i.text.strip() for i in itens if i.text.strip()]
        return nomes
    except Exception:
        # nenhum parceiro encontrado / timeout
        return []

def main():
    print("🚀 Abrindo página:", URL)
    driver.get(URL)

    # aguarda SVG do mapa carregar
    wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "svg#svg-map, svg")))
    time.sleep(1.0)  # deixa scripts da página estabilizarem

    estados = driver.find_elements(By.CSS_SELECTOR, "a.estado")
    print(f"🔎 {len(estados)} elementos <a.estado> encontrados no mapa")

    resultados = []
    vistos = set()

    for idx, estado in enumerate(estados, start=1):
        uf = estado.get_attribute("uf") or ""
        nome_estado = estado.get_attribute("name") or ""
        print(f"\n[{idx}/{len(estados)}] ▶ Clicando em {uf} ({nome_estado.strip()}) ...")

        # rolagem para o elemento ficar visível (ajuda em alguns casos)
        try:
            driver.execute_script("arguments[0].scrollIntoView({block:'center', inline:'center'});", estado)
        except Exception:
            pass

        # primeiro tentar clicar no <a> diretamente; se não, pegar o path interno e dispatch
        try:
            clicar_svg_element(estado)
        except Exception as e:
            print("⚠ Erro ao clicar no <a> do estado:", e)
            # tenta clicar no path interno
            try:
                path = estado.find_element(By.TAG_NAME, "path")
                clicar_svg_element(path)
            except Exception as ex:
                print("⚠ Também falhou ao clicar no path:", ex)
                continue

        # pequena espera para a lista carregar (a página pode atualizar via JS)
        time.sleep(1.2)

        nomes = extrair_parceiros_para_estado(uf, nome_estado)
        if not nomes:
            # tenta esperar um pouco mais se inicialmente vazio
            time.sleep(1.5)
            nomes = extrair_parceiros_para_estado(uf, nome_estado)

        if nomes:
            print(f"✔ Extraídos {len(nomes)} parceiros de {uf}")
            for n in nomes:
                key = (uf, n)
                if key not in vistos:
                    vistos.add(key)
                    resultados.append({"estado": uf, "nome": n})
        else:
            print(f"⚠ Nenhum parceiro encontrado para {uf}")

    # salvar resultados
    if resultados:
        csv_file = "servopa_parceiros.csv"
        json_file = "servopa_parceiros.json"

        # CSV
        with open(csv_file, "w", encoding="utf-8", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=["estado", "nome"])
            writer.writeheader()
            writer.writerows(resultados)

        # JSON
        with open(json_file, "w", encoding="utf-8") as f:
            json.dump(resultados, f, ensure_ascii=False, indent=2)

        print("\n✅ Finalizado! Arquivos gerados:")
        print(" -", csv_file)
        print(" -", json_file)
        print("Total de parceiros únicos extraídos:", len(resultados))
    else:
        print("\n⚠ Não foram extraídos parceiros.")

    driver.quit()

if __name__ == "__main__":
    main()