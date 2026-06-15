# Scrapy settings for cursos_tech project
#
# For simplicity, this file contains only settings considered important or
# commonly used. You can find more settings consulting the documentation:
#
#     https://docs.scrapy.org/en/latest/topics/settings.html
#     https://docs.scrapy.org/en/latest/topics/downloader-middleware.html
#     https://docs.scrapy.org/en/latest/topics/spider-middleware.html

BOT_NAME = "cursos_tech"

SPIDER_MODULES = ["cursos_tech.spiders"]
NEWSPIDER_MODULE = "cursos_tech.spiders"

ADDONS = {}

TWISTED_REACTOR = "twisted.internet.asyncioreactor.AsyncioSelectorReactor"

USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/120.0.0.0 Safari/537.36"
)

ROBOTSTXT_OBEY = False

CONCURRENT_REQUESTS_PER_DOMAIN = 2
DOWNLOAD_DELAY = 1.5

FEED_EXPORT_ENCODING = "utf-8"
FEEDS = {
    "cursos_tech.json": {
        "format": "json",
        "encoding": "utf-8",
        "store_empty": False,
        "fields": [
            "titulo", "plataforma", "area", "nivel",
            "carga_horaria", "url", "certificado"
        ],
        "overwrite": True,
    },
    "cursos_tech.csv": {
        "format": "csv",
        "encoding": "utf-8-sig",
        "store_empty": False,
        "fields": [
            "titulo", "plataforma", "area", "carga_horaria",
            "nivel", "url", "certificado"
        ],
        "overwrite": True,
    },
}

ITEM_PIPELINES = {
    "cursos_tech.pipelines.FiltroTechPipeline": 300,
}
