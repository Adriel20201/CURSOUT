import re
from scrapy.exceptions import DropItem


TECH_KEYWORDS = [
    "programação", "programador", "software", "desenvolvimento", "sistemas",
    "web", "mobile", "aplicativos", "dados", "data", "inteligência artificial",
    "inteligencia artificial", "ia", "machine learning", "aprendizado de máquina",
    "redes", "computadores", "segurança", "cibersegurança", "cloud", "nuvem",
    "devops", "python", "java", "javascript", "typescript", "react", "node",
    "angular", "html", "css", "sql", "banco de dados", "git", "linux",
    "windows server", "iot", "raspberry", "blockchain", "análise de dados",
    "análise de dados", "ciência de dados", "ciencia de dados", "power bi",
    "informática", "informatica", "tecnologia", "sistemas operacionais",
    "php", "docker", "kubernetes", "api", "rest", "graphql", "mongodb",
    "postgresql", "mysql", "front-end", "frontend", "back-end", "backend",
    "full stack", "fullstack", "data science", "data analyst", "data engineer",
    "engenharia de dados", "business intelligence", "bi", "big data",
    "computação em nuvem", "computacao em nuvem", "aws", "azure",
    "google cloud", "metodologias ágeis", "metodologias ageis", "scrum",
    "testes", "qualidade de software", "automação", "automação",
    "robótica", "robotica", "ciência da computação", "ciencia da computacao",
    "engenharia da computação", "engenharia da computacao", "analista de sistemas",
    "suporte técnico", "suporte tecnico", "manutenção de computadores",
    "manutencao de computadores", "excel", "word", "powerpoint",
    "pacs", "office", "algoritmos", "logica de programacao",
    "lógica de programação", "servidores", "active directory",
    "redes de computadores", "windows", "react native", "flutter",
    "framework", "api rest", "api restful", "design", "ux", "ui",
    "experiência do usuário", "experiencia do usuario", "produto digital",
    "transformação digital", "transformacao digital", "cybersecurity",
    "segurança da informação", "seguranca da informacao", "governança",
    "ti", "tecnologia da informação", "tecnologia da informacao",
    "aplicacoes web", "desenvolvimento web", "páginas web", "paginas web",
    "site", "sites", "e-commerce", "marketing digital",
    "redes sociais", "wordpress", "gestão de projetos", "gestao de projetos",
    "empreendedorismo digital", "cloud computing", "computação",
    "computacao", "programador web", "projeto de sistemas",
    "softwares de segurança", "seguranca"
]


class FiltroTechPipeline:
    def process_item(self, item, spider):
        titulo = (item.get("titulo", "") or "").lower()
        descricao = (item.get("descricao", "") or "").lower()
        area = (item.get("area", "") or "").lower()
        texto = f"{titulo} {descricao} {area}"
        if any(kw in texto for kw in TECH_KEYWORDS):
            return item
        raise DropItem(f"Curso não relacionado a tecnologia: {titulo[:50]}")
