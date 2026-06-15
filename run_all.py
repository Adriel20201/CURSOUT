"""Run all spiders and merge results into a single JSON + CSV."""

import subprocess
import json
import os


def run_spider(name):
    print(f"\n=== Executando spider: {name} ===")
    saida = os.path.join(os.path.dirname(__file__), f"{name}_output.json")
    if os.path.exists(saida):
        os.remove(saida)
    result = subprocess.run(
        ["scrapy", "crawl", name, "-o", saida],
        capture_output=True, text=True, cwd=os.path.dirname(__file__)
    )
    if result.returncode == 0:
        print(f"  OK - {name} finalizado")
    else:
        print(f"  ERRO - {name}: {result.stderr[:200]}")


def merge_results():
    all_courses = []
    for fname in os.listdir(os.path.dirname(__file__)):
        if fname.endswith("_output.json"):
            path = os.path.join(os.path.dirname(__file__), fname)
            try:
                raw = open(path, encoding="utf-8").read().strip()
                data = json.loads(raw)
                all_courses.extend(data)
            except json.JSONDecodeError:
                try:
                    data = json.loads("[" + raw.replace("}{", "},{") + "]")
                    all_courses.extend(data)
                except Exception:
                    print(f"  Erro ao ler {fname} (formato inválido)")
            except Exception as e:
                print(f"  Erro ao ler {fname}: {e}")

    output = os.path.join(os.path.dirname(__file__), "cursos_tech", "todos_cursos.json")
    with open(output, "w", encoding="utf-8") as f:
        json.dump(all_courses, f, ensure_ascii=False, indent=2)

    csv_path = os.path.join(os.path.dirname(__file__), "cursos_tech", "todos_cursos.csv")
    if all_courses:
        import csv
        with open(csv_path, "w", encoding="utf-8-sig", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=all_courses[0].keys())
            writer.writeheader()
            writer.writerows(all_courses)

    print(f"\n=== Resumo Final ===")
    print(f"Total de cursos de tecnologia: {len(all_courses)}")
    by_platform = {}
    for c in all_courses:
        p = c["plataforma"]
        by_platform[p] = by_platform.get(p, 0) + 1
    for p, count in sorted(by_platform.items()):
        print(f"  {p}: {count}")
    print(f"\nArquivos salvos:")
    print(f"  - {output}")
    print(f"  - {csv_path}")


if __name__ == "__main__":
    spiders = ["ifrs", "ev", "ifmg", "mundi", "escola_trabalhador", "ibm", "coursera_usp", "recode"]
    for s in spiders:
        run_spider(s)
    merge_results()
