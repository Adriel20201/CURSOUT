import scrapy
from cursos_tech.items import CursoItem


class CourseraUspSpider(scrapy.Spider):
    name = "coursera_usp"
    allowed_domains = ["coursera.org"]
    start_urls = [
        "https://www.coursera.org/partners/usp",
        "https://www.coursera.org/programs/universidade-de-sao-paulo-br-on-coursera-mvxtw",
    ]

    def parse(self, response):
        for curso in response.css(
            ".cds-ProductCard, .cds-Card, .card-item, .course-card, .Card"
        ):
            titulo = curso.css(
                "h3::text, h2::text, .card-title::text, .cds-ProductCard-title::text"
            ).get("")
            if not titulo or not titulo.strip():
                continue
            yield CursoItem(
                titulo=titulo.strip(),
                plataforma="Coursera (USP)",
                url=response.urljoin(
                    curso.css("a::attr(href)").get("")
                ),
                carga_horaria=curso.css(
                    ".duration::text, .hours::text"
                ).get(""),
                nivel=curso.css(".level::text").get(""),
                descricao=curso.css(
                    ".description::text, .cds-ProductCard-description::text, p::text"
                ).get(""),
                area="",
                certificado="Certificado pagos (US$29) / Gratuito modo ouvinte",
            )
