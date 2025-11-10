import scrapy
import json

class ademicon(scrapy.Spider):
    name = "ademicon"
    start_urls = [
        "https://unidades.ademicon.com.br/api/json"
    ]

    def parse(self, response):
        data = json.loads(response.text)
        for estado, cidades in data.items():
            for cidade, unidades in cidades.items():
                for u in unidades:
                    yield {
                        'estado': estado,
                        'cidade': cidade,
                        'title': u.get('title'),
                        'endereco': u.get('endereco'),
                    }
