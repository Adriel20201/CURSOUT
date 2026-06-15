#!/usr/bin/env python3
"""Terminal UI - Painel de Cursos Gratuitos de Tecnologia"""
#versao com painel azul ok..FE
import json
import os
import subprocess
import sys
import re
from datetime import datetime
from pathlib import Path

from rich import box
from rich.console import Console
from rich.layout import Layout
from rich.live import Live
from rich.panel import Panel
from rich.progress import (
    BarColumn,
    Progress,
    SpinnerColumn,
    TaskProgressColumn,
    TextColumn,
    TimeElapsedColumn,
)
from rich.prompt import Confirm, Prompt
from rich.syntax import Syntax
from rich.table import Table
from rich.text import Text
from rich.columns import Columns
from rich.align import Align
from rich.rule import Rule

BASE_DIR = Path(__file__).parent
CURSOS_DIR = BASE_DIR / "cursos_tech"
SPIDERS_DIR = CURSOS_DIR / "spiders"
PLATAFORMAS_FILE = BASE_DIR / "plataformas.json"

PLATAFORMAS_PADRAO = {
    "1": {"nome": "IFRS", "spider": "ifrs", "url": "estude.ifrs.edu.br"},
    "2": {"nome": "Escola Virtual (Fundacao Bradesco)", "spider": "ev", "url": "ev.org.br"},
    "3": {"nome": "+IFMG", "spider": "ifmg", "url": "mais.ifmg.edu.br"},
    "4": {"nome": "Plataforma Mundi (IFSul)", "spider": "mundi", "url": "mundi.ifsul.edu.br"},
    "5": {"nome": "Escola do Trabalhador 4.0", "spider": "escola_trabalhador", "url": "ead.escoladotrabalhador40.com.br"},
    "6": {"nome": "IBM SkillsBuild", "spider": "ibm", "url": "skillsbuild.org"},
    "7": {"nome": "Coursera (USP)", "spider": "coursera_usp", "url": "coursera.org"},
    "8": {"nome": "Recode", "spider": "recode", "url": "recode.org.br"},
}

console = Console()


def carregar_plataformas():
    if PLATAFORMAS_FILE.exists():
        with open(PLATAFORMAS_FILE, encoding="utf-8") as f:
            return json.load(f)
    salvar_plataformas(PLATAFORMAS_PADRAO)
    return dict(PLATAFORMAS_PADRAO)


def salvar_plataformas(plataformas):
    with open(PLATAFORMAS_FILE, "w", encoding="utf-8") as f:
        json.dump(plataformas, f, ensure_ascii=False, indent=2)


def slugificar(nome):
    slug = nome.lower().strip()
    slug = re.sub(r"[^a-z0-9]+", "_", slug)
    slug = slug.strip("_")
    return slug[:30]


def gerar_spider_arquivo(plataforma):
    nome = plataforma["nome"]
    slug = plataforma["spider"]
    url = plataforma["url"]
    class_name = slug.replace("_", " ").title().replace(" ", "") + "Spider"
    caminho = SPIDERS_DIR / f"{slug}.py"

    if caminho.exists():
        console.print(Panel(f"[yellow]Spider [bold]{slug}.py[/bold] ja existe, mantendo existente.[/yellow]", box=box.ROUNDED, border_style="yellow"))
        return

    template = f'''import scrapy
from cursos_tech.items import CursoItem


class {class_name}(scrapy.Spider):
    name = "{slug}"
    allowed_domains = ["{url}"]
    start_urls = ["https://www.{url}"]

    def parse(self, response):
        yield CursoItem(
            titulo="",
            plataforma="{nome}",
            url="",
            carga_horaria="",
            nivel="",
            descricao="",
            area="",
            certificado="",
        )
'''

    with open(caminho, "w", encoding="utf-8") as f:
        f.write(template)
    console.print(Panel(f"[green]+ Spider criado: [bold]{caminho}[/bold][/green]", box=box.ROUNDED, border_style="green"))


def cabecalho():
    plataformas = carregar_plataformas()
    qtd = len(plataformas)
    return Panel(
        Text("  CURSOS GRATUITOS DE TECNOLOGIA  ", style="bold white on blue"),
        subtitle=f"[bold cyan]{qtd}[/bold cyan] Plataformas  |  [bold green]Filtro Tech[/bold green] Automatico",
        subtitle_align="center",
        box=box.ROUNDED,
        border_style="blue",
    )


def painel_menu():
    return Panel(
        "\n".join([
            "",
            "  [1] [bold cyan]>>[/bold cyan]  [white]Buscar cursos agora (rodar spiders)[/white]",
            "  [2] [bold cyan]>>[/bold cyan]  [white]Ver resultados salvos[/white]",
            "  [3] [bold cyan]>>[/bold cyan]  [white]Estatisticas[/white]",
            "  [4] [bold cyan]>>[/bold cyan]  [white]Filtrar cursos por palavra-chave[/white]",
            "  [5] [bold cyan]>>[/bold cyan]  [white]Gerenciar arquivos salvos[/white]",
            "  [6] [bold cyan]>>[/bold cyan]  [white]Gerenciar plataformas[/white]",
            "  [7] [bold cyan]>>[/bold cyan]  [white]Sair[/white]",
            "",
        ]),
        title="[bold white]MENU PRINCIPAL[/bold white]",
        title_align="center",
        box=box.DOUBLE_EDGE,
        border_style="cyan",
        padding=(0, 2),
    )


def menu_principal():
    console.clear()
    console.print(cabecalho())
    console.print()
    console.print(painel_menu())
    console.print()
    return Prompt.ask("[bold green]Escolha[/bold green]", choices=["1", "2", "3", "4", "5", "6", "7"])


def painel_selecao(plataformas):
    linhas = ["", "  [0] [bold green]Todas as plataformas[/bold green]"]
    for k, v in plataformas.items():
        linhas.append(f"  [{k}] [yellow]{v['nome']}[/yellow]")
    linhas.append("")
    return Panel(
        "\n".join(linhas),
        title="[bold white]SELECIONAR PLATAFORMAS[/bold white]",
        title_align="center",
        box=box.DOUBLE_EDGE,
        border_style="cyan",
    )


def selecionar_spiders(plataformas):
    console.print()
    console.print(painel_selecao(plataformas))
    console.print()
    max_key = max(int(k) for k in plataformas.keys())
    escolha = Prompt.ask(
        "[bold green]Plataforma[/bold green]",
        choices=[str(i) for i in range(max_key + 1)],
    )
    if escolha == "0":
        return [v["spider"] for v in plataformas.values()]
    return [plataformas[escolha]["spider"]]


def rodar_spiders_com_progresso(spiders_para_rodar):
    plataformas = carregar_plataformas()
    arquivos_gerados = []
    resultados_por_spider = {}

    nomes = {v["spider"]: v["nome"] for v in plataformas.values()}

    for i, spider in enumerate(spiders_para_rodar):
        nome_exibicao = nomes.get(spider, spider)
        saida = BASE_DIR / f"{spider}_output.json"

        console.print()
        console.print(
            Panel(
                f"[bold yellow]Rodando: {nome_exibicao}[/bold yellow]",
                box=box.HORIZONTALS,
                border_style="yellow",
            )
        )

        progresso = Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(bar_width=40),
            TaskProgressColumn(),
            TimeElapsedColumn(),
            console=console,
        )

        with progresso:
            task = progresso.add_task(
                f"[cyan]{nome_exibicao}[/cyan]", total=None
            )
            if saida.exists():
                saida.unlink()
            result = subprocess.run(
                ["scrapy", "crawl", spider, "-o", str(saida)],
                capture_output=True,
                text=True,
                cwd=BASE_DIR,
            )
            progresso.update(task, completed=100)

        if result.returncode == 0 and saida.exists():
            raw = saida.read_text(encoding="utf-8").strip()
            try:
                dados = json.loads(raw)
            except json.JSONDecodeError:
                dados = []
                for line in raw.splitlines():
                    line = line.strip().rstrip(",")
                    if line in ("[", "]", "", "[", "]"):
                        continue
                    try:
                        dados.append(json.loads(line))
                    except json.JSONDecodeError:
                        pass
            resultados_por_spider[spider] = dados
            arquivos_gerados.append(saida)
            console.print(
                f"  [green]+[/green] [bold]{len(dados)}[/bold] cursos encontrados"
            )
        else:
            console.print(
                f"  [red]-[/red] Erro ao rodar [bold]{nome_exibicao}[/bold]"
            )
            if result.stderr:
                console.print(f"    [dim]{result.stderr[:250]}[/dim]")

    return resultados_por_spider


def consolidar_resultados():
    todos = []
    for fname in BASE_DIR.glob("*_output.json"):
        try:
            raw = fname.read_text(encoding="utf-8").strip()
            dados = json.loads(raw)
            todos.extend(dados)
        except json.JSONDecodeError:
            try:
                dados = json.loads("[" + raw.replace("}{", "},{") + "]")
                todos.extend(dados)
            except Exception:
                pass
        except Exception:
            pass

    if todos:
        saida = CURSOS_DIR / "todos_cursos.json"
        with open(saida, "w", encoding="utf-8") as f:
            json.dump(todos, f, ensure_ascii=False, indent=2)
    return todos


def exibir_resultados(cursos, pagina=1, por_pagina=30):
    if not cursos:
        console.print(Panel("[yellow]Nenhum curso encontrado.[/yellow]", border_style="yellow", box=box.ROUNDED))
        return

    total = len(cursos)
    total_paginas = (total + por_pagina - 1) // por_pagina
    inicio = (pagina - 1) * por_pagina
    fim = min(inicio + por_pagina, total)
    fatia = cursos[inicio:fim]

    subtitulo = ""
    if total_paginas > 1:
        subtitulo = f"Pagina [bold]{pagina}[/bold]/{total_paginas}  |  [dim]linhas {inicio+1}-{fim}[/dim]"

    tabela = Table(
        title=f"[bold white]CURSOS DE TECNOLOGIA[/bold white]  [green]({total})[/green]",
        caption=subtitulo,
        box=box.HEAVY_EDGE,
        header_style="bold white on #0055aa",
        title_style="bold white on blue",
        padding=(0, 1),
        collapse_padding=True,
        show_edge=True,
    )
    tabela.add_column("#", style="dim", width=3, no_wrap=True)
    tabela.add_column("Curso", style="white", no_wrap=False, ratio=3)
    tabela.add_column("Plataforma", style="yellow", no_wrap=False, ratio=1)
    tabela.add_column("Link", style="blue", no_wrap=False, ratio=2)
    tabela.add_column("Carga", style="green", justify="center", width=6)
    tabela.add_column("Nivel", style="magenta", justify="center", width=10)
    tabela.add_column("Area", style="cyan", no_wrap=False, ratio=1)
    tabela.add_column("Descricao", style="white", no_wrap=False, ratio=1)
    tabela.add_column("Cert.", style="blue", justify="center", width=6)

    for i, c in enumerate(fatia, inicio + 1):
        url_raw = c.get("url", "")
        link_text = url_raw[:55] if url_raw else "-"
        link_col = f"[link={url_raw}]{link_text}[/link]" if url_raw else "[dim]-[/dim]"
        tabela.add_row(
            str(i),
            c.get("titulo", "")[:60],
            c.get("plataforma", "")[:22],
            link_col,
            c.get("carga_horaria", "") or "-",
            c.get("nivel", "") or "-",
            c.get("area", "")[:22] or "-",
            c.get("descricao", "")[:40] or "-",
            "Sim" if "grat" in c.get("certificado", "").lower() else c.get("certificado", "")[:8] or "-",
        )

    console.print()
    console.print(tabela)
    console.print()

    opcoes_validas = ["n", "p", "q"]
    if total_paginas > 1:
        hint = "  [green][n][/green] proxima  |  [green][p][/green] anterior  |  [green][q][/green] sair  |  [cyan][numero][/cyan] abrir link  "
    else:
        hint = "  [green][q][/green] sair  |  [cyan][numero][/cyan] abrir link  "
    console.print(Panel(hint, box=box.HORIZONTALS, border_style="cyan"))

    while True:
        cmd = Prompt.ask("[bold green]Opcao[/bold green]", default="q")
        if cmd == "n" and pagina < total_paginas:
            return exibir_resultados(cursos, pagina + 1, por_pagina)
        elif cmd == "p" and pagina > 1:
            return exibir_resultados(cursos, pagina - 1, por_pagina)
        elif cmd == "q":
            break
        elif cmd.isdigit():
            idx = int(cmd) - 1
            if 0 <= idx < total:
                url = cursos[idx].get("url", "")
                if url:
                    import webbrowser
                    webbrowser.open(url)
                    console.print(f"  [green]+ Link aberto:[/green] [dim]{url[:70]}[/dim]")
                else:
                    console.print("  [yellow]Este curso nao possui link.[/yellow]")
            else:
                console.print(f"  [yellow]Numero invalido (1-{total}).[/yellow]")


def exibir_estatisticas(cursos):
    if not cursos:
        console.print(Panel("[yellow]Nenhum dado disponivel. Busque cursos primeiro.[/yellow]", border_style="yellow", box=box.ROUNDED))
        return

    por_plataforma = {}
    areas = {}
    niveis = {}
    total_carga = 0
    com_cert = 0
    for c in cursos:
        p = c.get("plataforma", "Desconhecida")
        por_plataforma[p] = por_plataforma.get(p, 0) + 1
        a = c.get("area", "") or "Nao definida"
        areas[a] = areas.get(a, 0) + 1
        n = c.get("nivel", "") or "Nao definido"
        niveis[n] = niveis.get(n, 0) + 1
        if c.get("carga_horaria", ""):
            try:
                total_carga += int(re.sub(r"\D", "", c["carga_horaria"]))
            except ValueError:
                pass
        if c.get("certificado", ""):
            com_cert += 1

    console.print()
    console.print(Rule(style="blue"))
    console.print(Align.center("[bold white on blue]  ESTATISTICAS  [/bold white on blue]"))
    console.print(Rule(style="blue"))
    console.print()

    grid = Table.grid(padding=(0, 4))
    grid.add_column(justify="center", style="bold")
    grid.add_column(justify="center")
    grid.add_row(
        Panel(f"[bold green]{len(cursos)}[/bold green]\n[dim]CURSOS[/dim]", box=box.ROUNDED, border_style="green"),
        Panel(f"[bold cyan]{len(por_plataforma)}[/bold cyan]\n[dim]PLATAFORMAS[/dim]", box=box.ROUNDED, border_style="cyan"),
        Panel(f"[bold magenta]{len(areas)}[/bold magenta]\n[dim]AREAS[/dim]", box=box.ROUNDED, border_style="magenta"),
        Panel(f"[bold blue]{com_cert}[/bold blue]\n[dim]COM CERTIFICADO[/dim]", box=box.ROUNDED, border_style="blue"),
    )
    console.print(Align.center(grid))
    console.print()

    console.print(Rule(style="dim"))
    console.print(Align.center("[bold]CURSOS POR PLATAFORMA[/bold]"))
    console.print()

    tabela = Table(box=box.SIMPLE_HEAD, header_style="bold cyan", show_lines=False)
    tabela.add_column("Plataforma", style="yellow", ratio=3)
    tabela.add_column("Cursos", style="green", justify="right", width=8)
    tabela.add_column("%", style="blue", justify="right", width=6)
    barra_max = 30

    for p, count in sorted(por_plataforma.items(), key=lambda x: -x[1]):
        pct = count / len(cursos) * 100
        barras = "|" * int(pct / 100 * barra_max)
        label = f"[green]{barras}[/green]" if barras else ""
        tabela.add_row(p[:35], str(count), f"{pct:.1f}%")

    console.print(tabela)
    console.print()


def filtrar_cursos(cursos):
    if not cursos:
        console.print(Panel("[yellow]Nenhum dado disponivel. Busque cursos primeiro.[/yellow]", border_style="yellow", box=box.ROUNDED))
        return None

    console.print()
    console.print(Rule(style="cyan"))
    console.print(Align.center("[bold white on cyan]  FILTRAR CURSOS  [/bold white on cyan]"))
    console.print(Rule(style="cyan"))
    console.print()

    termo = Prompt.ask("[bold green]Palavra-chave[/bold green]").lower().strip()
    if not termo:
        return None

    resultados = [
        c for c in cursos
        if termo in c.get("titulo", "").lower()
        or termo in c.get("descricao", "").lower()
        or termo in c.get("area", "").lower()
        or termo in c.get("plataforma", "").lower()
    ]

    if not resultados:
        console.print(Panel(f"[yellow]Nenhum curso encontrado com '[bold]{termo}[/bold]'[/yellow]", border_style="yellow", box=box.ROUNDED))
        return None

    console.print(Panel(
        f"[bold green]{len(resultados)}[/bold green] curso(s) encontrado(s) para '[bold]{termo}[/bold]'",
        border_style="green",
        box=box.ROUNDED,
    ))
    console.print()
    console.print("  [1] [bold]Ver amostra[/bold] (50 cursos)")
    console.print("  [2] [bold]Ver completo[/bold] (navegavel)")
    console.print("  [3] [bold]Exportar filtro[/bold] para JSON")
    console.print("  [Enter] Voltar")
    console.print()
    op = Prompt.ask("[bold green]Opcao[/bold green]", choices=["1", "2", "3"], default="1")
    if op == "1":
        exibir_resultados(resultados, por_pagina=50)
    elif op == "2":
        exibir_resultados(resultados, por_pagina=30)
    elif op == "3":
        saida = BASE_DIR / f"filtro_{termo.replace(' ', '_')}.json"
        with open(saida, "w", encoding="utf-8") as f:
            json.dump(resultados, f, ensure_ascii=False, indent=2)
        console.print(Panel(f"[green]Filtro salvo: [bold]{saida}[/bold][/green]", border_style="green", box=box.ROUNDED))

    return resultados


def inicializar_projeto():
    if not (CURSOS_DIR / "todos_cursos.json").exists():
        console.print()
        if Confirm.ask("[yellow]Nenhum dado salvo. Deseja buscar cursos agora?[/yellow]"):
            plataformas = carregar_plataformas()
            spiders = selecionar_spiders(plataformas)
            console.print(Panel(f"[cyan]Iniciando busca em [bold]{len(spiders)}[/bold] plataforma(s)...[/cyan]", border_style="cyan", box=box.ROUNDED))
            resultados = rodar_spiders_com_progresso(spiders)
            cursos = consolidar_resultados()
            if cursos:
                console.print(Rule(style="green"))
                exibir_resultados(cursos)
                return cursos
        return []
    with open(CURSOS_DIR / "todos_cursos.json", encoding="utf-8") as f:
        return json.load(f)


def gerenciar_arquivos():
    console.print()
    console.print(Rule(style="cyan"))
    console.print(Align.center("[bold white on cyan]  GERENCIAR ARQUIVOS SALVOS  [/bold white on cyan]"))
    console.print(Rule(style="cyan"))
    console.print()

    arquivos = []
    for ext in ("*.json", "*.csv"):
        for f in BASE_DIR.glob(f"*{ext[1:]}"):
            if "output" in f.stem or "filtro" in f.stem or "todos" in f.stem:
                tamanho = f.stat().st_size
                arquivos.append((f, tamanho))
        for f in CURSOS_DIR.glob(f"*{ext[1:]}"):
            if "todos" in f.stem:
                tamanho = f.stat().st_size
                arquivos.append((f, tamanho))

    if not arquivos:
        console.print(Panel("[yellow]Nenhum arquivo salvo encontrado. Busque cursos primeiro (opcao 1).[/yellow]", border_style="yellow", box=box.ROUNDED))
        input("\nPressione Enter para continuar...")
        return

    arquivos.sort(key=lambda x: x[1], reverse=True)

    tabela = Table(box=box.HEAVY_EDGE, header_style="bold white on #0055aa")
    tabela.add_column("#", style="dim", width=4)
    tabela.add_column("Arquivo", style="white", ratio=3)
    tabela.add_column("Tamanho", style="green", justify="right", width=10)
    tabela.add_column("Acoes", style="blue", width=14)

    opcoes = {}
    for i, (path, size) in enumerate(arquivos, 1):
        kb = size / 1024
        tamanho_str = f"{kb:.1f} KB" if kb < 1024 else f"{kb/1024:.1f} MB"
        nome = str(path.relative_to(BASE_DIR))
        if "todos_cursos" in nome:
            acoes = "[yellow]Ver[/yellow] | [green]Exportar[/green]"
        elif "filtro" in nome:
            acoes = "[cyan]Ver[/cyan]"
        else:
            acoes = "[cyan]Ver[/cyan]"
        tabela.add_row(str(i), nome, tamanho_str, acoes)
        opcoes[str(i)] = path

    console.print(tabela)
    console.print()
    console.print(Panel(
        "  [bold][numero][/bold] para ver  |  [bold]d[/bold]eletar arquivo  |  [bold]a[/bold]brir pasta  |  [bold]v[/bold]er JSON principal  |  [Enter] voltar  ",
        box=box.HORIZONTALS,
        border_style="cyan",
    ))
    console.print()

    escolha = Prompt.ask("[bold green]Escolha[/bold green]", default="")
    if not escolha:
        return

    if escolha == "a":
        import subprocess as sp
        sp.run(["explorer", str(BASE_DIR)])
        return

    if escolha.startswith("d"):
        partes = escolha.split()
        num_del = partes[1] if len(partes) > 1 else Prompt.ask("[bold red]Numero do arquivo para deletar[/bold red]")
        if num_del in opcoes and not isinstance(opcoes[num_del], str):
            path_del = opcoes[num_del]
            console.print(Panel(f"[red]Deletar: [bold]{path_del.name}[/bold][/red]", border_style="red", box=box.ROUNDED))
            if Confirm.ask("[red]Tem certeza?[/red]"):
                path_del.unlink()
                console.print(Panel(f"[green]+ Arquivo deletado: [bold]{path_del.name}[/bold][/green]", border_style="green", box=box.ROUNDED))
        else:
            console.print("[yellow]Numero invalido.[/yellow]")
        input("\nPressione Enter para continuar...")
        return

    if escolha == "v":
        json_path = CURSOS_DIR / "todos_cursos.json"
        if json_path.exists():
            with open(json_path, encoding="utf-8") as f:
                dados = json.load(f)
            if isinstance(dados, list) and len(dados) > 0:
                console.print(Panel(f"[green][bold]{json_path.name}[/bold] - {len(dados)} cursos[/green]", border_style="green", box=box.ROUNDED))
                console.print()
                console.print("  [1] [bold]Ver amostra[/bold] (50 cursos)")
                console.print("  [2] [bold]Ver completo[/bold] (navegavel)")
                console.print("  [Enter] Voltar")
                console.print()
                op = Prompt.ask("[bold green]Opcao[/bold green]", choices=["1", "2"], default="1")
                if op == "1":
                    exibir_resultados(dados, por_pagina=50)
                elif op == "2":
                    exibir_resultados(dados, por_pagina=30)
            else:
                console.print(Panel("[yellow]Nenhum curso encontrado no JSON principal.[/yellow]", border_style="yellow", box=box.ROUNDED))
        else:
            console.print(Panel("[yellow]Arquivo todos_cursos.json nao encontrado.[/yellow]", border_style="yellow", box=box.ROUNDED))
        input("\nPressione Enter para continuar...")
        return

    path = opcoes.get(escolha)
    if not path:
        return

    raw = path.read_text(encoding="utf-8").strip()
    try:
        dados = json.loads(raw)
    except json.JSONDecodeError:
        dados = None

    if isinstance(dados, list) and len(dados) > 0:
        console.print(Panel(f"[green][bold]{path.name}[/bold] - {len(dados)} cursos[/green]", border_style="green", box=box.ROUNDED))
        console.print()
        console.print("  [1] [bold]Ver amostra[/bold] (50 cursos)")
        console.print("  [2] [bold]Ver completo[/bold] (navegavel)")
        console.print("  [3] [bold]Exportar[/bold] para CSV")
        console.print("  [Enter] Voltar")
        console.print()
        op = Prompt.ask("[bold green]Opcao[/bold green]", choices=["1", "2", "3"], default="1")
        if op == "1":
            exibir_resultados(dados, por_pagina=50)
        elif op == "2":
            exibir_resultados(dados, por_pagina=30)
        elif op == "3":
            csv_path = path.with_suffix(".csv")
            import csv as csv_mod
            with open(csv_path, "w", encoding="utf-8-sig", newline="") as f:
                writer = csv_mod.writer(f)
                writer.writerow(dados[0].keys())
                for row in dados:
                    writer.writerow(row.values())
            console.print(Panel(f"[green]+ CSV salvo: [bold]{csv_path}[/bold][/green]", border_style="green", box=box.ROUNDED))
    else:
        console.print()
        linhas = raw.splitlines()
        max_linhas = console.height - 6
        for linha in linhas[:max_linhas]:
            console.print(f"  [dim]{linha[:130]}[/dim]")
        if len(linhas) > max_linhas:
            console.print(f"  [dim]... mais {len(linhas) - max_linhas} linhas[/dim]")

    input("\nPressione Enter para continuar...")


def gerenciar_plataformas():
    plataformas = carregar_plataformas()

    while True:
        console.print()
        console.print(Rule(style="cyan"))
        console.print(Align.center("[bold white on cyan]  GERENCIAR PLATAFORMAS  [/bold white on cyan]"))
        console.print(Rule(style="cyan"))
        console.print()

        tabela = Table(box=box.HEAVY_EDGE, header_style="bold white on #0055aa")
        tabela.add_column("#", style="dim", width=4)
        tabela.add_column("Plataforma", style="white", ratio=3)
        tabela.add_column("Spider", style="yellow", ratio=2)
        tabela.add_column("URL", style="blue", ratio=3)
        for k, v in plataformas.items():
            tabela.add_row(k, v["nome"], v["spider"], v["url"])

        console.print(tabela)
        console.print()
        console.print(Panel(
            "  [green][a][/green]dicionar  |  [yellow][e][/yellow]ditar  |  [red][r][/red]emover  |  [cyan][Enter][/cyan] voltar  ",
            box=box.HORIZONTALS,
            border_style="cyan",
        ))
        console.print()

        escolha = Prompt.ask("[bold green]Opcao[/bold green]", default="")
        if not escolha:
            return

        if escolha == "a":
            adicionar_plataforma(plataformas)
        elif escolha == "e":
            editar_plataforma(plataformas)
        elif escolha == "r":
            remover_plataforma(plataformas)


def adicionar_plataforma(plataformas):
    console.print()
    console.print(Rule(style="green"))
    console.print(Align.center("[bold white on green]  ADICIONAR PLATAFORMA  [/bold white on green]"))
    console.print(Rule(style="green"))
    console.print()

    nome = Prompt.ask("[bold green]Nome da plataforma[/bold green]").strip()
    if not nome:
        return

    url = Prompt.ask("[bold green]URL do site[/bold green]").strip()
    if not url:
        return

    slug = slugificar(nome)

    prox_num = str(max(int(k) for k in plataformas.keys()) + 1)
    plataformas[prox_num] = {
        "nome": nome,
        "spider": slug,
        "url": url,
    }

    salvar_plataformas(plataformas)
    gerar_spider_arquivo(plataformas[prox_num])
    console.print(Panel(f"[green]+ Plataforma '[bold]{nome}[/bold]' adicionada![/green]\n[dim]  Spider: {slug}.py[/dim]", border_style="green", box=box.ROUNDED))
    input("\nPressione Enter para continuar...")


def editar_plataforma(plataformas):
    console.print()
    console.print(Rule(style="yellow"))
    console.print(Align.center("[bold white on yellow]  EDITAR PLATAFORMA  [/bold white on yellow]"))
    console.print(Rule(style="yellow"))
    console.print()

    max_key = max(int(k) for k in plataformas.keys())
    num = Prompt.ask("[bold green]Numero da plataforma[/bold green]")
    if num not in plataformas:
        return

    p = plataformas[num]
    console.print(Panel(f"Editando: [bold]{p['nome']}[/bold]", border_style="yellow", box=box.ROUNDED))
    console.print()

    novo_nome = Prompt.ask("Nome", default=p["nome"]).strip()
    nova_url = Prompt.ask("URL", default=p["url"]).strip()
    novo_slug = slugificar(novo_nome)

    p["nome"] = novo_nome or p["nome"]
    p["url"] = nova_url or p["url"]
    p["spider"] = novo_slug

    salvar_plataformas(plataformas)
    console.print(Panel(f"[green]+ Plataforma atualizada![/green]", border_style="green", box=box.ROUNDED))
    input("\nPressione Enter para continuar...")


def remover_plataforma(plataformas):
    console.print()
    console.print(Rule(style="red"))
    console.print(Align.center("[bold white on red]  REMOVER PLATAFORMA  [/bold white on red]"))
    console.print(Rule(style="red"))
    console.print()

    max_key = max(int(k) for k in plataformas.keys())
    num = Prompt.ask("[bold green]Numero da plataforma[/bold green]")
    if num not in plataformas:
        return

    p = plataformas[num]
    console.print(Panel(f"Remover: [bold red]{p['nome']}[/bold red]", border_style="red", box=box.ROUNDED))
    if not Confirm.ask("[red]Tem certeza?[/red]"):
        return

    spider_path = SPIDERS_DIR / f"{p['spider']}.py"
    del plataformas[num]
    salvar_plataformas(plataformas)

    if spider_path.exists():
        spider_path.unlink()
        console.print(Panel(f"[yellow]Spider removido: [bold]{spider_path.name}[/bold][/yellow]", border_style="yellow", box=box.ROUNDED))

    console.print(Panel(f"[green]+ Plataforma removida![/green]", border_style="green", box=box.ROUNDED))
    input("\nPressione Enter para continuar...")


def main():
    console.clear()
    console.print()
    console.print(Align.center(Text("""
  ____ _   _ ____  ____   ___  _   _ _____
 / ___| | | |  _ \\/ ___| / _ \\| | | |_   _|
| |   | | | | |_) \\___ \\| | | | | | | | |
| |___| |_| |  _ < ___) | |_| | |_| | | |
 \\____|\\___/|_| \\_\\____/ \\___/ \\___/  |_|
    """, style="bold cyan")))
    console.print(Align.center("[dim]Scraper de Cursos Gratuitos de Tecnologia[/dim]"))
    console.print()

    cursos = inicializar_projeto()

    while True:
        opcao = menu_principal()

        if opcao == "1":
            plataformas = carregar_plataformas()
            spiders = selecionar_spiders(plataformas)
            if not spiders:
                continue
            console.print(Rule(style="cyan"))
            console.print(Align.center(f"[cyan]Iniciando busca em [bold]{len(spiders)}[/bold] plataforma(s)...[/cyan]"))
            console.print(Rule(style="cyan"))
            resultados = rodar_spiders_com_progresso(spiders)

            todos = []
            for dados in resultados.values():
                todos.extend(dados)

            if todos:
                saida = CURSOS_DIR / "todos_cursos.json"
                with open(saida, "w", encoding="utf-8") as f:
                    json.dump(todos, f, ensure_ascii=False, indent=2)
                console.print(Rule(style="green"))
                console.print(Align.center(f"[bold green]+ Dados consolidados![/bold green]"))
                console.print(Rule(style="green"))
                exibir_resultados(todos)
                cursos = todos
            else:
                console.print(Panel("[yellow]Nenhum curso encontrado.[/yellow]", border_style="yellow", box=box.ROUNDED))

            input("\nPressione Enter para continuar...")

        elif opcao == "2":
            if cursos:
                exibir_resultados(cursos)
            else:
                console.print(Panel("[yellow]Nenhum dado disponivel.[/yellow]", border_style="yellow", box=box.ROUNDED))
            input("\nPressione Enter para continuar...")

        elif opcao == "3":
            exibir_estatisticas(cursos)
            input("\nPressione Enter para continuar...")

        elif opcao == "4":
            filtrar_cursos(cursos)
            input("\nPressione Enter para continuar...")

        elif opcao == "5":
            gerenciar_arquivos()

        elif opcao == "6":
            gerenciar_plataformas()

        elif opcao == "7":
            usuario = os.getenv("USERNAME", "Usuario")
            console.print()
            console.print(Panel(
                f"[bold green]Obrigado por utilizar o programa, [cyan]{usuario}[/cyan]![/bold green]\n\n"
                "[dim]Cursos salvos em[/dim] [cyan]cursos_tech/todos_cursos.json[/cyan]\n"
                "[dim]GitHub do criador:[/dim] [cyan]https://github.com/Adriel20201[/cyan]\n"
                "[dim]Projeto:[/dim] [cyan]https://github.com/Adriel20201/CURSOUT[/cyan]",
                box=box.DOUBLE_EDGE,
                border_style="green",
            ))
            console.print()
            sys.exit(0)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        console.print(Panel("\n[yellow]Programa encerrado.[/yellow]\n", border_style="yellow", box=box.ROUNDED))
        sys.exit(0)
