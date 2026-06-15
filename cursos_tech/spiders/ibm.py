import scrapy
from cursos_tech.items import CursoItem


class IbmSpider(scrapy.Spider):
    name = "ibm"
    allowed_domains = ["skillsbuild.org"]
    start_urls = ["https://skillsbuild.org/pt-br/students/catalog"]

    def parse(self, response):
        for curso in response.css(
            ".catalog-card, .card, .learning-path-item, article, .course-card"
        ):
            titulo = curso.css(
                "h3::text, h4::text, .card-title::text, .title::text"
            ).get("")
            if not titulo.strip():
                continue
            yield CursoItem(
                titulo=titulo.strip(),
                plataforma="IBM SkillsBuild",
                url=response.urljoin(
                    curso.css("a::attr(href)").get("")
                ),
                carga_horaria=curso.css(
                    ".duration::text, .hours::text, .badge::text"
                ).get(""),
                nivel=curso.css(".level::text, .nivel::text").get(""),
                descricao=curso.css(
                    ".description::text, .card-text::text, p::text"
                ).get(""),
                area=curso.css(
                    ".category::text, .topic::text, .badge-category::text"
                ).get(""),
                certificado="Badge digital IBM (gratuito)",
            )
