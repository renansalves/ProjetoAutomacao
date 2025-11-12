# Como fazer a requisiçao.
# Chamar o endpoint ajax passando o form data da uf

# https://hsconsorcios.com.br/wp-admin/admin-ajax.php?action=api_ondeencontrar_cidades
# querry param action=api_ondeencontrar_cidades
# Content-Disposition: form-data; name="uf"

# A uf é um id que mapeia um label da uf ex:.. SP -> 3242 -> "uf=3242", vai listar as cidades de são paulo que possuem unidades da HS.

# curl -s -X POST \
#   -F "uf=3242" \
#   "https://hsconsorcios.com.br/wp-admin/admin-ajax.php?action=api_ondeencontrar_cidades" | jq .

#[
#  {
#    "id": 7171,
#    "label": "AMERICANA"
#  },
#  {
#    "id": 3438,
#    "label": "AMPARO"
#  },
#  {
#    "id": 3439,
#    "label": "ANDRADINA"
#  },
#  ...
#]

# O proximo passo é chamar o endpoint para encontrar as unidades daquela cidade.

# https://hsconsorcios.com.br/wp-admin/admin-ajax.php?action=api_ondeencontrar_search
# query param string action=api_ondeencontrar_search
# Content-Disposition: form-data; name="estado_id"
# Content-Disposition: form-data; name="cidade_id"

# passando os form-data "estado_id=xxxx" e "cidade_id=xxxx", onde xxxx são ambos ids da cidade e estado. 

# curl -s -X POST \
#   -F "estado_id=3242" \
#   -F "cidade_id=7171" \
#   "https://hsconsorcios.com.br/wp-admin/admin-ajax.php?action=api_ondeencontrar_search" | jq .
# saida
# [
#  {
#    "id": 400931,
#    "nome": "SANTOS E BORTOLINI LTDA",
#    "telefone": "53991016119",
#    "email": "hagaconsorcio@terra.com.br",
#    "endereco": "Rua Rio Branco, 70"
#  }
#]

# Outras considerações, as requests precisam lidar com o erro 429, por conta de receber muitas requisições seguidas nos endpoints, foram adicionados alguns parametros para lidar com isso nas requests do proprio scrapy, e adicionado um delay aleatorio de poucos segundos em cada uma das chamadas


import scrapy
import random
import time

class HSSpider(scrapy.Spider):
    name = "hs"
    allowed_domains = ["hsconsorcios.com.br"]


  # Configurações para evitar bloqueio
    custom_settings = {
        'DOWNLOAD_DELAY': 3.0,  # 2 segundos entre requisições
        'CONCURRENT_REQUESTS_PER_DOMAIN': 1,
        'AUTOTHROTTLE_ENABLED': True,
        'AUTOTHROTTLE_START_DELAY': 2.0,
        'AUTOTHROTTLE_MAX_DELAY': 10.0,
        'AUTOTHROTTLE_TARGET_CONCURRENCY': 1.0,
        'RETRY_ENABLED': True,
        'RETRY_TIMES': 5,
        'RETRY_HTTP_CODES': [429, 500, 502, 503, 504],
        'USER_AGENT': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }

    estados = {
        3340: "BA", 13863: "CE", 3194: "DF", 3358: "ES", 3318: "GO",
        12910: "MA", 3292: "MG", 3355: "MS", 3213: "MT", 13018: "PA",
        13021: "PB", 13006: "PE", 3187: "PR", 7144: "RJ", 13860: "RN",
        12898: "RO", 3184: "RS", 3191: "SC", 13869: "SE", 3242: "SP",
        3380: "TO"
    }

    def start_requests(self):
        url_cidades = "https://hsconsorcios.com.br/wp-admin/admin-ajax.php?action=api_ondeencontrar_cidades"
        for estado_id, estado_sigla in self.estados.items():
            formdata = {'uf': str(estado_id)}
            meta = {'estado': estado_sigla, 'estado_id': estado_id}
            yield self.make_request(url_cidades, formdata, self.parse_cidades, meta)

    def make_request(self, url, formdata, callback, meta):
       time.sleep(random.uniform(1.5, 3.0))
       return scrapy.FormRequest(
            url=url,
            formdata=formdata,
            callback=callback,
            meta=meta
        )

    def parse_cidades(self, response):
        estado = response.meta['estado']
        estado_id = response.meta['estado_id']

        cidades = response.json()
        for cidade in cidades:
            cidade_id = cidade.get('id')
            cidade_nome = cidade.get('label')

            url_unidades = "https://hsconsorcios.com.br/wp-admin/admin-ajax.php?action=api_ondeencontrar_search"
            formdata = {'estado_id': str(estado_id), 'cidade_id': str(cidade_id)}
            meta = {
                'estado': estado,
                'estado_id': estado_id,
                'cidade_id': cidade_id,
                'cidade_nome': cidade_nome
            }
            yield self.make_request(url_unidades, formdata, self.parse_unidades, meta)

    def parse_unidades(self, response):
        estado = response.meta['estado']
        cidade_nome = response.meta['cidade_nome']

        unidades = response.json()
        for unidade in unidades:
            yield {
                'nome': unidade.get('nome'),
                'endereco': unidade.get('endereco'),
                'cidade': cidade_nome,
                'estado': estado,
            }
