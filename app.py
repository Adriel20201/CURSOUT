#!/usr/bin/env python3
"""Terminal UI - Painel de Cursos Gratuitos de Tecnologia"""

import json
import os
import subprocess
import sys
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

BASE_DIR = Path(__file__).parent
CURSOS_DIR = BASE_DIR / "cursos_tech"
SPIDERS = {
    "1": {"nome": "IFRS", "spider": "ifrs", "url": "estude.ifrs.edu.br"},
    "2": {"nome": "Escola Virtual (Fundação Bradesco)", "spider": "ev", "url": "ev.org.br"},
    "3": {"nome": "+IFMG", "spider": "ifmg", "url": "mais.ifmg.edu.br"},
    "4": {"nome": "Plataforma Mundi (IFSul)", "spider": "mundi", "url": "mundi.ifsul.edu.br"},
    "5": {"nome": "Escola do Trabalhador 4.0", "spider": "escola_trabalhador", "url": "ead.escoladotrabalhador40.com.br"},
    "6": {"nome": "IBM SkillsBuild", "spider": "ibm", "url": "skillsbuild.org"},
    "7": {"nome": "Coursera (USP)", "spider": "coursera_usp", "url": "coursera.org"},
    "8": {"nome": "Recode", "spider": "recode", "url": "recode.org.br"},
}

console = Console()


def cabecalho():
    return Panel(
        Text(
            "  CURSOS GRATUITOS DE TECNOLOGIA  ",
            style="bold white on blue",
        ),
        subtitle="Fontes: IFRS, EV, IFMG, IFSul, ET4.0, IBM, Coursera/USP, Recode",
        subtitle_align="center",
        box=box.ROUNDED,
    )


def menu_principal():
    console.clear()
    console.print(cabecalho())
    console.print()
    console.print("[bold cyan]MENU PRINCIPAL[/bold cyan]", justify="center")
    console.print()
    console.print("  [1] 🔍  Buscar cursos agora (rodar spiders)")
    console.print("  [2] 📋  Ver resultados salvos")
    console.print("  [3] 📊  Estatísticas")
    console.print("  [4] 🔎  Filtrar cursos por palavra-chave")
    console.print("  [5] 🚀  Sair")
    console.print()
    return Prompt.ask("[bold green]Escolha[/bold green]", choices=["1", "2", "3", "4", "5"])


def selecionar_spiders():
    console.print()
    console.print("[bold cyan]SELECIONAR PLATAFORMAS[/bold cyan]")
    console.print()
    console.print("  [0] Todas as plataformas")
    for k, v in SPIDERS.items():
        console.print(f"  [{k}] {v['nome']}")
    console.print()
    escolha = Prompt.ask(
        "[bold green]Plataforma[/bold green]",
        choices=[str(i) for i in range(9)],
    )
    if escolha == "0":
        return [v["spider"] for v in SPIDERS.values()]
    return [SPIDERS[escolha]["spider"]]


def rodar_spiders_com_progresso(spiders_para_rodar):
    arquivos_gerados = []
    resultados_por_spider = {}

    nomes = {v["spider"]: v["nome"] for v in SPIDERS.values()}

    for i, spider in enumerate(spiders_para_rodar):
        nome_exibicao = nomes.get(spider, spider)
        saida = BASE_DIR / f"{spider}_output.json"

        console.print()
        console.print(
            Panel(
                f"[bold yellow]Rodando: {nome_exibicao}[/bold yellow]",
                box=box.HORIZONTALS,
            )
        )

        progresso = Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TaskProgressColumn(),
            TimeElapsedColumn(),
            console=console,
        )

        with progresso:
            task = progresso.add_task(
                f"[cyan]{nome_exibicao}[/cyan]", total=None
            )
            result = subprocess.run(
                ["scrapy", "crawl", spider, "-o", str(saida)],
                capture_output=True,
                text=True,
                cwd=BASE_DIR,
            )
            progresso.update(task, completed=100)

        if result.returncode == 0 and saida.exists():
            with open(saida, encoding="utf-8") as f:
                dados = json.load(f)
            resultados_por_spider[spider] = dados
            arquivos_gerados.append(saida)
            console.print(
                f"  [green]✓[/green] {len(dados)} cursos encontrados"
            )
        else:
            console.print(
                f"  [red]✗[/red] Erro ao rodar {nome_exibicao}"
            )
            if result.stderr:
                console.print(f"    [dim]{result.stderr[:200]}[/dim]")

    return resultados_por_spider


def consolidar_resultados():
    todos = []
    for fname in BASE_DIR.glob("*_output.json"):
        try:
            with open(fname, encoding="utf-8") as f:
                dados = json.load(f)
            todos.extend(dados)
        except Exception:
            pass

    if todos:
        saida = CURSOS_DIR / "todos_cursos.json"
        with open(saida, "w", encoding="utf-8") as f:
            json.dump(todos, f, ensure_ascii=False, indent=2)
    return todos


def exibir_resultados(cursos):
    if not cursos:
        console.print("[yellow]Nenhum curso encontrado.[/yellow]")
        return

    tabela = Table(
        title=f"📚 CURSOS DE TECNOLOGIA ({len(cursos)})",
        box=box.ROUNDED,
        header_style="bold cyan",
        title_style="bold white on blue",
    )
    tabela.add_column("#", style="dim", width=4)
    tabela.add_column("Curso", style="white", no_wrap=False)
    tabela.add_column("Plataforma", style="yellow")
    tabela.add_column("Carga Horária", style="green", justify="center")
    tabela.add_column("Nível", style="magenta", justify="center")
    tabela.add_column("Certificado", style="blue")

    for i, c in enumerate(cursos[:50], 1):
        titulo = c.get("titulo", "")[:55]
        plataforma = c.get("plataforma", "")[:30]
        carga = c.get("carga_horaria", "") or "-"
        nivel = c.get("nivel", "") or "-"
        cert = c.get("certificado", "")[:20]
        tabela.add_row(str(i), titulo, plataforma, carga, nivel, cert)

    if len(cursos) > 50:
        tabela.add_row("...", f"[dim]mais {len(cursos)-50} cursos...[/dim]", "", "", "", "")

    console.print()
    console.print(tabela)
    console.print()


def exibir_estatisticas(cursos):
    if not cursos:
        console.print("[yellow]Nenhum dado disponível. Busque cursos primeiro.[/yellow]")
        return

    por_plataforma = {}
    for c in cursos:
        p = c.get("plataforma", "Desconhecida")
        por_plataforma[p] = por_plataforma.get(p, 0) + 1

    console.print()
    console.print(
        Panel(
            f"[bold white on blue]📊 ESTATÍSTICAS[/bold white on blue]",
            box=box.ROUNDED,
        )
    )
    console.print()
    console.print(f"  [bold]Total de cursos:[/bold green] {len(cursos)}[/green]")
    console.print(f"  [bold]Plataformas:[/bold] {len(por_plataforma)}")
    console.print()

    tabela = Table(box=box.SIMPLE, header_style="bold cyan")
    tabela.add_column("Plataforma", style="yellow")
    tabela.add_column("Cursos", style="green", justify="right")
    tabela.add_column("%", style="blue", justify="right")

    for p, count in sorted(por_plataforma.items(), key=lambda x: -x[1]):
        pct = count / len(cursos) * 100
        tabela.add_row(p[:40], str(count), f"{pct:.1f}%")

    console.print(tabela)
    console.print()


def filtrar_cursos(cursos):
    if not cursos:
        console.print("[yellow]Nenhum dado disponível. Busque cursos primeiro.[/yellow]")
        return None

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
        console.print(f"[yellow]Nenhum curso encontrado com '{termo}'[/yellow]")
        return None

    exibir_resultados(resultados)
    console.print(
        f"  [bold green]{len(resultados)}[/bold green] curso(s) encontrado(s) para '[bold]{termo}[/bold]'"
    )
    console.print()

    exportar = Confirm.ask("Exportar este filtro para JSON?")
    if exportar:
        saida = BASE_DIR / f"filtro_{termo.replace(' ', '_')}.json"
        with open(saida, "w", encoding="utf-8") as f:
            json.dump(resultados, f, ensure_ascii=False, indent=2)
        console.print(f"  [green]Salvo em:[/green] {saida}")

    return resultados


def inicializar_projeto():
    if not (CURSOS_DIR / "todos_cursos.json").exists():
        if Confirm.ask("Nenhum dado salvo. Deseja buscar cursos agora?"):
            spiders = selecionar_spiders()
            console.print(f"\n[cyan]Iniciando busca em {len(spiders)} plataforma(s)...[/cyan]")
            resultados = rodar_spiders_com_progresso(spiders)
            cursos = consolidar_resultados()
            if cursos:
                exibir_resultados(cursos)
                return cursos
        return []
    with open(CURSOS_DIR / "todos_cursos.json", encoding="utf-8") as f:
        return json.load(f)


def main():
    console.clear()
    console.print(
        """
[bold blue]╔══════════════════════════════════════════════════╗
║     CURSOS TECH - SCRAPER DE CURSOS GRATUITOS     ║
║     Área de Tecnologia - 8 Plataformas            ║
╚══════════════════════════════════════════════════╝[/bold blue]
        """
    )
    console.print("[dim]Carregando dados...[/dim]")

    cursos = inicializar_projeto()

    while True:
        opcao = menu_principal()

        if opcao == "1":
            spiders = selecionar_spiders()
            if not spiders:
                continue
            console.print(
                f"\n[cyan]Iniciando busca em {len(spiders)} plataforma(s)...[/cyan]"
            )
            resultados = rodar_spiders_com_progresso(spiders)

            todos = []
            for dados in resultados.values():
                todos.extend(dados)

            if todos:
                saida = CURSOS_DIR / "todos_cursos.json"
                with open(saida, "w", encoding="utf-8") as f:
                    json.dump(todos, f, ensure_ascii=False, indent=2)
                console.print(f"\n[green]✓ Dados consolidados![/green]")
                exibir_resultados(todos)
                cursos = todos
            else:
                console.print("[yellow]Nenhum curso encontrado.[/yellow]")

            input("\nPressione Enter para continuar...")

        elif opcao == "2":
            if cursos:
                exibir_resultados(cursos)
            else:
                console.print("[yellow]Nenhum dado disponível.[/yellow]")
            input("\nPressione Enter para continuar...")

        elif opcao == "3":
            exibir_estatisticas(cursos)
            input("\nPressione Enter para continuar...")

        elif opcao == "4":
            filtrar_cursos(cursos)
            input("\nPressione Enter para continuar...")

        elif opcao == "5":
            console.print()
            console.print(
                Panel(
                    "[bold green]Até logo! 🚀[/bold green]\n\n"
                    "[dim]Cursos salvos em[/dim] [cyan]cursos_tech/todos_cursos.json[/cyan]\n"
                    "[dim]GitHub:[/dim] [cyan]git push origin main[/cyan]",
                    box=box.ROUNDED,
                )
            )
            console.print()
            sys.exit(0)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        console.print("\n[yellow]Programa encerrado.[/yellow]")
        sys.exit(0)
