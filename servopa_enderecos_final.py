import pandas as pd
import re
import os

# Caminho base que você informou
BASE = r"C:\Users\yasmin.ribeiro\Documents\Python\ProjetoAutomacao\AutomacaoFiliais\AutomacaoFiliais\spiders\servopa"

# Arquivo de entrada
import os

input_file = os.path.join(os.path.dirname(__file__), "servopa_enderecos_robusto.csv")

# Arquivo de saída
output_file = os.path.join(BASE, "servopa_enderecos_processado.csv")

# ----------- CARREGA CSV -----------
df = pd.read_csv(input_file, dtype=str).fillna("")

# ----------- FUNÇÕES AUXILIARES -----------

def extrair_cep(endereco):
    cep = re.search(r"\b\d{5}-?\d{3}\b", endereco)
    return cep.group(0) if cep else ""

def extrair_estado_do_endereco(endereco):
    # Estados brasileiros (siglas)
    estados = [
        "AC","AL","AP","AM","BA","CE","DF","ES","GO","MA",
        "MT","MS","MG","PA","PB","PR","PE","PI","RJ","RN",
        "RS","RO","RR","SC","SP","SE","TO"
    ]
    for uf in estados:
        if re.search(rf"\b{uf}\b", endereco):
            return uf
    return ""

def extrair_cidade(endereco):
    """
    Padrão mais forte:
    ' - Cidade - UF'
    Ex: 'Rua X, 123 - Centro, Cuiabá - MT'
    """
    padrao1 = re.search(r"-\s*([^-,]+)\s*-\s*[A-Z]{2}", endereco)
    if padrao1:
        cidade = padrao1.group(1).strip()
        return cidade

    # Padrão alternativo: "Cidade - UF" sem vírgula antes
    padrao2 = re.search(r"([^,]+)\s*-\s*[A-Z]{2}", endereco)
    if padrao2:
        cidade = padrao2.group(1).strip()
        return cidade

    # Última tentativa: pegar algo depois da última vírgula
    if "," in endereco:
        possivel = endereco.split(",")[-1].strip()
        if len(possivel.split()) >= 1 and not re.search(r"\d", possivel):
            return possivel

    return ""

# ----------- PROCESSAMENTO -----------

df["cep"] = df["endereco"].apply(extrair_cep)
df["estado_endereco"] = df["endereco"].apply(extrair_estado_do_endereco)
df["cidade"] = df["endereco"].apply(extrair_cidade)

# Criar coluna de divergência
df["estado_divergente"] = df.apply(
    lambda x: "SIM" if x["estado_endereco"] not in ["", x["estado"]] else "NAO",
    axis=1
)

# ----------- REORDENAR COLUNAS -----------
df_final = df[[
    "nome",
    "estado",
    "cnpj",
    "endereco",
    "cidade",
    "cep",
    "estado_divergente"
]]

# ----------- SALVAR CSV -----------
df_final.to_csv(output_file, index=False, encoding="utf-8-sig")

print("✔ Arquivo processado salvo em:")
print(output_file)
