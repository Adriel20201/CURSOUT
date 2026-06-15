import scrapy
from cursos_tech.items import CursoItem


class MundiSpider(scrapy.Spider):
    name = "mundi"
    allowed_domains = ["mundi.ifsul.edu.br"]
    start_urls = ["https://mundi.ifsul.edu.br/portal/"]

    def parse(self, response):
        for curso in response.css(
            "div.curso-item, div.card, div.portfolio-item, article"
        ):
            titulo = curso.css(
                "h3::text, h4::text, .curso-titulo::text, .card-title::text"
            ).get("")
            if not titulo.strip():
                continue
            yield CursoItem(
                titulo=titulo.strip(),
                plataforma="Plataforma Mundi (IFSul)",
                url=response.urljoin(
                    curso.css("a::attr(href)").get("")
                ),
                carga_horaria=curso.css(
                    ".carga-horaria::text, .duration::text, .badge::text"
                ).get(""),
                nivel="",
                descricao=curso.css(
                    ".descricao::text, .card-text::text, p::text"
                ).get(""),
                area="",
                certificado="Gratuito (nota mínima 6)",
            )
