import scrapy


class CursoItem(scrapy.Item):
    titulo = scrapy.Field()
    plataforma = scrapy.Field()
    url = scrapy.Field()
    carga_horaria = scrapy.Field()
    nivel = scrapy.Field()
    descricao = scrapy.Field()
    area = scrapy.Field()
    certificado = scrapy.Field()
