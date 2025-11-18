# 
# curl 'https://www.consorciorandon.com.br/localize/buscaunidades' --data-raw 'estado=21&cidade=14213'
#curl 'https://www.consorciorandon.com.br/localize/buscacidadesunidades'  --data-raw 'estados_id=5'
# 
# [
#   13644,
#   "Caxias Do Sul"
# ]
# [
#   13738,
#   "Ijuí"
# ]
# [
#   13842,
#   "Portão"
# ]
# [
#   13876,
#   "Santa Maria"
# ]
# [
#   14213,
#   "Canoas"
# ]
# [
#   14327,
#   "Horizontina"
# ]
# [
#   14338,
#   "Lajeado"
# ]
# [
#   14613,
#   "Passo Fundo"
# ]
# [
#   14625,
#   "Pelotas"
# ]
# 
# 
# curl 'https://www.consorciorandon.com.br/localize/buscaunidades' --data-raw 'estado=21&cidade=14213' | jq -r '.[] | [.nome,.endereco]'
# 
# [
#   "Dipesul - Canoas/RS",
#   "Avenida Getúlio Vargas, 5901"
# ]
# 
#  Montar bash script para iterar sobre o endpoint que traz as cidades por estado, e em seguida realizar a chamada para buscar a unidae com o id da cidade e do estado. Finalmente montar a estrutura do documento [nome, endereco, cidade, estado, pagina].


import requests
import csv

cabecalho_csv = ["Name", "Endereco", "Cidade", "Estado", "Pagina"]
data = []
estados = {
  'AL': 2,
  'AM': 4,
  'BA': 5,
  'CE': 6,
  'ES': 8,
  'GO': 9,
  'MA': 10,
  'MT': 11,
  'MS': 12,
  'MG': 13,
  'PA': 14,
  'PB': 15,
  'PR': 16,
  'PE': 17,
  'PI': 18,
  'RJ': 19,
  'RN': 20,
  'RS': 21,
  'RO': 22,
  'SC': 24,
  'SP': 25,
  'SE': 26,
  'TO': 27
  }

file_name = "randon.csv"
data = []
api_url=[
        "https://www.consorciorandon.com.br/localize/buscacidadesunidades",
        "https://www.consorciorandon.com.br/localize/buscaunidades"
        ]
lista_estados_cidades ={}
for key, value in estados.items():
    new_post_data = {
        'estados_id':value
    }
    response = requests.post(api_url[0],new_post_data)
    lista_estados_cidades[key] = (value,response.json())

for estados, cidades in lista_estados_cidades.items():
    for items in cidades:
        if isinstance(items, list):
            for values in items:      
                post_data = {
                    'estado':cidades[0]  ,
                    'cidade':values['cidades_id'] 
                    }
                response = requests.post(api_url[1],post_data)
                for info in response.json():
                    data.append([info['nome'], info['endereco'], cidades[1][0]['nome'] ,estados,"https://www.consorciorandon.com.br/localize-um-distribuidor"])
    

with open(file_name, 'w', newline='') as csvfile:
    writer = csv.writer(csvfile)
    writer.writerow(cabecalho_csv)
    writer.writerows(data)

print(f"CSV file '{file_name}' created successfully.")


#[
#        [{'cidades_id': 5642, 'nome': 'Messias'}], 
#        [{'cidades_id': 5828, 'nome': 'Manaus'}],
#        [{'cidades_id': 6554, 'nome': 'Simões Filho'}]
#]
