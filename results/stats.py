"""
Genera les taules del document a partir dels CSV de temps (tiempos_*.csv) i compta les
línies de codi de cada script.

Taules (desviació estàndard mostral, ddof=1):
  1. Per sistema × mida de chunk × operació × mètrica: n, total, mín, màx, mitjana, desv.
  2. Càrrega completa per mida de chunk: temps total i temps per frase.
  3. Consultes per sistema × mètrica.
  4. Línies de codi (sense comentaris, docstrings ni línies en blanc).

Ús:  python results/stats.py [--results-dir D] [--out F]
"""

import argparse
import io
import tokenize
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
SCRIPTS = ["postgres", "chroma", "pgvector"]


def markdown(df, floats="{:.6f}"):
    cols = list(df.columns)
    lines = ["| " + " | ".join(map(str, cols)) + " |", "|" + "---|" * len(cols)]
    for row in df.itertuples(index=False):
        cells = ["–" if pd.isna(v) else floats.format(v) if isinstance(v, float) else str(v) for v in row]
        lines.append("| " + " | ".join(cells) + " |")
    return "\n".join(lines)


def code_lines(path):
    """Línies amb algun token de codi: sense comentaris, docstrings ni línies en blanc."""
    lines, prev = set(), tokenize.INDENT
    for tok in tokenize.generate_tokens(io.StringIO(path.read_text(encoding="utf-8")).readline):
        ignore = (tokenize.COMMENT, tokenize.NL, tokenize.NEWLINE, tokenize.INDENT,
                  tokenize.DEDENT, tokenize.ENDMARKER)
        is_docstring = tok.type == tokenize.STRING and prev in (tokenize.INDENT, tokenize.NEWLINE, tokenize.DEDENT)
        if tok.type not in ignore and not is_docstring:
            lines.update(range(tok.start[0], tok.end[0] + 1))
        if tok.type not in (tokenize.COMMENT, tokenize.NL):
            prev = tok.type
    return len(lines)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--results-dir", type=Path, default=ROOT / "results")
    parser.add_argument("--out", type=Path)
    args = parser.parse_args()
    out = args.out or args.results_dir / "tablas.md"

    files = sorted(args.results_dir.glob("tiempos_*.csv"))
    df = pd.concat([pd.read_csv(f) for f in files], ignore_index=True)
    keys = ["sistema", "tam_chunk", "operacion", "metrica"]
    stats = (df.groupby(keys)["segundos"]
               .agg(n="count", total="sum", min="min", max="max", media="mean", desv=lambda s: s.std(ddof=1))
               .reset_index())  # desv = NaN si n = 1 (no definida)

    ins = stats[stats.operacion != "consulta"].copy()
    ins["por_frase"] = ins.total / 10000
    load = ins[["sistema", "operacion", "metrica", "tam_chunk", "n", "total", "por_frase"]]
    queries = (df[df.operacion == "consulta"].groupby(["sistema", "metrica"])["segundos"]
                 .agg(n="count", min="min", max="max", media="mean", desv=lambda s: s.std(ddof=1))
                 .reset_index())

    loc = pd.DataFrame([{"script": f"{d}/{p.name}", "lineas": code_lines(p)}
                        for d in SCRIPTS for p in sorted((ROOT / d).glob("*.py"))])

    text = "\n\n".join([
        f"Fuente: {', '.join(f.name for f in files)}",
        "## 1. Estadísticas por chunk (s)\n\n" + markdown(ins.drop(columns="por_frase")),
        "## 2. Carga completa por tamaño de chunk (s)\n\n" + markdown(load),
        "## 3. Consultas top-2 (s)\n\n" + markdown(queries),
        "## 4. Líneas de código\n\n" + markdown(loc),
    ]) + "\n"
    out.write_text(text, encoding="utf-8", newline="\n")
    print(text)
    print(f"-> {out}")


if __name__ == "__main__":
    main()
