import scrapy
import re
import unicodedata


def tratar_acentos(texto):
    """Normaliza acentos e caracteres especiais."""
    if not texto:
        return ""
    # Normaliza para decompor acentos e caracteres especiais
    texto_normalizado = unicodedata.normalize('NFKC', texto)
    return texto_normalizado.strip()


class UnifisaSpider(scrapy.Spider):
    name = "unifisa_representantes"
    allowed_domains = ["unifisa.com.br"]
    start_urls = ["https://www.unifisa.com.br/representantes/"]

    def parse(self, response):
        representantes = response.css("div.search-filter-results div.card_representante")

        for rep in representantes:
            nome = tratar_acentos(rep.css("h3.titulo_representante::text").get(default=""))
            endereco_completo = tratar_acentos(rep.css("p.endereco::text").get(default=""))

            cidade = None
            estado = None

            # Detecta estado (ex: SP, RJ)
            estado_match = re.search(r"\b([A-Z]{2})\b$", endereco_completo)
            if estado_match:
                estado = estado_match.group(1)
                endereco_sem_estado = endereco_completo[:estado_match.start()].strip()
                # Detecta cidade antes do estado
                cidade_match = re.search(r"[-–]\s*([\w\s'çãáâéêíóôúü\-]+)$", endereco_sem_estado)
                if cidade_match:
                    cidade = tratar_acentos(cidade_match.group(1))

            yield {
                "nome": nome,
                "endereco": endereco_completo,
                "cidade": cidade,
                "estado": estado,
                "pagina": response.url,
            }

        # Paginacao
        next_page = response.css("a.nextpostslink::attr(href)").get()
        if next_page:
            yield response.follow(next_page, callback=self.parse)
