import scrapy
import json

class embracon(scrapy.Spider):
    name = "embracon"

    allowed_domains = ["www.embracon.com.br"]

    # Lista de estados brasileiros
    estados = [
        "AC","AL","AM","AP","BA","CE","DF","ES","GO","MA","MG","MS","MT",
        "PA","PB","PE","PI","PR","RJ","RN","RO","RR","RS","SC","SE","SP","TO"
    ]
   
    def start_requests(self):
        for estado in self.estados:
            url = f"https://www.embracon.com.br/api/filiais/cities?state={estado}"
            yield scrapy.Request(url, callback=self.parse_cities, meta={"estado": estado})

    def parse_cities(self, response):
        estado = response.meta["estado"]
        data = json.loads(response.text)
        cidades = data.get("result").get("data")
        for cidade in cidades:
            url_filiais = f"https://www.embracon.com.br/api/filiais?state={estado}&city={cidade}"
            yield scrapy.Request(url_filiais, callback=self.parse_filiais, meta={"estado": estado, "cidade": cidade})

    def parse_filiais(self, response):
        estado = response.meta["estado"]
        cidade = response.meta["cidade"]
        data = json.loads(response.text)
        for filial in data.get("result").get("data"):
            yield {
                "Nome": filial.get("title"),
                "Endereco": filial.get("address"),
                "Cidade": cidade,
                "Estado": estado,
                "Pagina": 'https://www.embracon.com.br/filiais'
            }
