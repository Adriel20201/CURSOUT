import scrapy
from cursos_tech.items import CursoItem

TRILHAS_TECH = [
    "programação",
    "programacao",
    "letramento digital",
    "produtividade",
    "avançado ti",
    "avancado ti",
    "tecnologia",
    "dados",
    "cloud",
    "nuvem",
]


class EscolaTrabalhadorSpider(scrapy.Spider):
    name = "escola_trabalhador"
    allowed_domains = ["ead.escoladotrabalhador40.com.br"]
    start_urls = ["https://ead.escoladotrabalhador40.com.br/"]

    def parse(self, response):
        for curso in response.css(
            ".course-item, .card, .trilha-item, article, .curso-card"
        ):
            titulo = curso.css(
                "h3::text, h4::text, .card-title::text, .course-title::text"
            ).get("")
            if not titulo.strip():
                continue
            yield CursoItem(
                titulo=titulo.strip(),
                plataforma="Escola do Trabalhador 4.0 (MTE/Microsoft)",
                url=response.urljoin(
                    curso.css("a::attr(href)").get("")
                ),
                carga_horaria=curso.css(
                    ".carga-horaria::text, .duration::text, .badge::text"
                ).get(""),
                nivel="",
                descricao=curso.css(
                    ".description::text, .card-text::text, p::text"
                ).get(""),
                area=curso.css(".trilha-tag::text, .categoria::text").get(""),
                certificado="Gratuito (MTE/Microsoft)",
            )
