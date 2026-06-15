import scrapy
from cursos_tech.items import CursoItem


class IfmgSpider(scrapy.Spider):
    name = "ifmg"
    allowed_domains = ["mais.ifmg.edu.br"]
    start_urls = ["https://mais.ifmg.edu.br/"]

    def parse(self, response):
        for curso in response.css("div.course-item, div.card, article"):
            titulo = curso.css(
                "h3::text, h4::text, .course-title::text, .card-title::text"
            ).get("")
            if not titulo.strip():
                continue
            yield CursoItem(
                titulo=titulo.strip(),
                plataforma="+IFMG (IFMG)",
                url=response.urljoin(
                    curso.css("a::attr(href)").get("")
                ),
                carga_horaria=curso.css(
                    ".course-hours::text, .duration::text, .carga-horaria::text"
                ).get(""),
                nivel="",
                descricao=curso.css(
                    ".course-description::text, .card-text::text"
                ).get(""),
                area="",
                certificado="Gratuito (MEC)",
            )
