import scrapy
from cursos_tech.items import CursoItem


class IfrsSpider(scrapy.Spider):
    name = "ifrs"
    allowed_domains = ["estude.ifrs.edu.br"]
    start_urls = [
        "https://estude.ifrs.edu.br/cursos/?busca=bW9kYWxpZGFkZSU1QiU1RD1lYWQmdW5pZGFkZSU1QiU1RD12aXJ0dWFs"
    ]

    def parse(self, response):
        for curso in response.css("article.curso-item"):
            yield CursoItem(
                titulo=curso.css("h4.curso-item__title a::text").get("").strip(),
                plataforma="IFRS",
                url=response.url,
                carga_horaria=curso.css(
                    "span.curso-item__meta--cargahoraria::text"
                ).get("").strip(),
                nivel=curso.css("p.curso-item__nivel::text").get("").strip(),
                descricao="",
                area="",
                certificado="Gratuito (MEC)",
            )

        next_page = response.css("a.next::attr(href)").get()
        if next_page:
            yield response.follow(next_page, callback=self.parse)
