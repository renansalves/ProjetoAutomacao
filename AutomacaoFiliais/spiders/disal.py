# URL
# https://disalconsorcio.com.br/rede-autorizadahttps://disalconsorcio.com.br/rede-autorizada

#https://disalconsorcio.com.br/cms/Principal/simularconsorcio/CarregarMapa?criterio=&codigo=

import scrapy
import json

class disal(scrapy.Spider):
    name = "disal"
    start_urls = [
        "https://disalconsorcio.com.br/cms/Principal/simularconsorcio/CarregarMapa?criterio=&codigo="
    ]

#    def parse(self, response):
        # Carrega JSON
#        data = json.loads(response.text)


#        for filial in data:
#        for filial in data:
#            yield {
#                "Nome": filial.get("RazaoSocial"),
#                "Endereco": filial.get("Endereco"),
#                "Cidade": filial.get("Cidade"),
#                "Estado": filial.get("Uf"),
#                "Pagina": "https://disalconsorcio.com.br"  # padrão
#            }

 # Solução rapida, fazer o curl do endpoint para retornar toda a informação das filiais e depois usar o jq para fazer o parser dos dados e salvar em um arquivo .csv

## curl -s "https://disalconsorcio.com.br/cms/Principal/simularconsorcio/CarregarMapa?criterio=&codigo=" -o req.json

## (echo "Nome,Endereco,Cidade,Estado,Pagina" &&
## cat req.json | jq -r '.LstRevendas | select(type=="array")[] | [.RazaoSocial, .Endereco, .Cidade, .Uf, "https://disalconsorcio.com.br"] | @csv'
## ) > disal.csv

