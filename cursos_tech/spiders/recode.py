import scrapy
from cursos_tech.items import CursoItem


class RecodeSpider(scrapy.Spider):
    name = "recode"
    allowed_domains = ["recode.org.br"]
    start_urls = ["https://recode.org.br/formacoes/"]

    def parse(self, response):
        for curso in response.css(
            ".formation-item, .card, .curso-card, article, .post-item"
        ):
            titulo = curso.css(
                "h3::text, h4::text, .card-title::text, .title::text, .entry-title::text"
            ).get("")
            if not titulo.strip():
                continue
            yield CursoItem(
                titulo=titulo.strip(),
                plataforma="Recode (CDI/Microsoft)",
                url=response.urljoin(
                    curso.css("a::attr(href)").get("")
                ),
                carga_horaria=curso.css(
                    ".duration::text, .carga-horaria::text, .badge::text"
                ).get(""),
                nivel="",
                descricao=curso.css(
                    ".description::text, .card-text::text, p::text"
                ).get(""),
                area=curso.css(
                    ".category::text, .tag::text, .area::text"
                ).get(""),
                certificado="Gratuito (Microsoft/PMI)",
            )
