import scrapy

class RepresentantesSpider(scrapy.Spider):
    name = "representantes"
    allowed_domains = ["unifisa.com.br"]
    start_urls = [
        "https://www.unifisa.com.br/representantes/"
    ]

    def parse(self, response):
        representantes = response.css("div.search-filter-results")

        for rep in representantes:
            yield {
                "nome": rep.css("div.card_representante h3::text").get(),
                "endereco": rep.css("div.card_representante p.endereco::text").get(),
            }

        # Paginação
        next_page = response.css("a.nextpostslink::attr(href)").get()
        if next_page:
            yield response.follow(next_page, callback=self.parse)

