import scrapy
from cursos_tech.items import CursoItem


class EvSpider(scrapy.Spider):
    name = "ev"
    allowed_domains = ["ev.org.br"]
    start_urls = ["https://www.ev.org.br/api/busca-curso"]

    def parse(self, response):
        data = response.json()
        for curso in data.get("Data", []):
            yield CursoItem(
                titulo=curso.get("Nome", ""),
                plataforma="Escola Virtual (Fundação Bradesco)",
                url=response.urljoin(curso.get("Url", "")),
                carga_horaria="",
                nivel="",
                descricao="",
                area="",
                certificado="Gratuito",
            )
