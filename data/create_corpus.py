"""
Genera data/corpus_10k.txt (1 frase per línia) a partir de BookCorpus (HuggingFace).

Font: rojagtap/bookcorpus (mirall en text pla, ~74M files, 1 frase per fila), en streaming
per no descarregar el corpus sencer. No s'usa bookcorpus/bookcorpus perquè depèn d'un
script de càrrega que datasets>=4.0 ja no admet.

Filtres (per aquest ordre):
    1. strip() de cada frase
    2. mostreig amb pas fix: 1 de cada PAS files (cobreix centenars de llibres, determinista)
    3. longitud entre MIN_PARAULES i MAX_PARAULES paraules, ambdós inclosos
    4. sense duplicats exactes (un duplicat d'una frase de consulta sortiria com a veí a distància 0)

Ús:  python data/create_corpus.py [--out FITXER] [--total N] [--pas P]
"""

import argparse
from pathlib import Path

import datasets
from datasets import load_dataset

DEFAULT_OUT = Path(__file__).resolve().parent / "corpus_10k.txt"
DATASET = "rojagtap/bookcorpus"
TOTAL = 10_000
PAS = 100
MIN_PARAULES = 6
MAX_PARAULES = 60


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    parser.add_argument("--total", type=int, default=TOTAL)
    parser.add_argument("--pas", type=int, default=PAS)
    args = parser.parse_args()

    stream = load_dataset(DATASET, split="train", streaming=True)

    frases: list[str] = []
    vistes: set[str] = set()
    descartades = {"longitud": 0, "duplicat": 0}
    files_recorregudes = 0

    for i, row in enumerate(stream):
        files_recorregudes = i + 1
        if i % args.pas != 0:
            continue
        frase = row["text"].strip()
        if not MIN_PARAULES <= len(frase.split()) <= MAX_PARAULES:
            descartades["longitud"] += 1
            continue
        if frase in vistes:
            descartades["duplicat"] += 1
            continue
        vistes.add(frase)
        frases.append(frase)
        if len(frases) == args.total:
            break

    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text("\n".join(frases) + "\n", encoding="utf-8", newline="\n")

    print(f"Font: {DATASET} (datasets {datasets.__version__})")
    print(f"Files recorregudes: {files_recorregudes}  (pas {args.pas})")
    print(f"Descartades: {descartades['longitud']} per longitud, {descartades['duplicat']} duplicats")
    print(f"Frases escrites: {len(frases)} -> {args.out}")


if __name__ == "__main__":
    main()
