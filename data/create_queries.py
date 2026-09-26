"""
Genera data/queries.json: 10 frases de consulta triades a l'atzar de corpus_10k.txt.

Llavor fixa (SEED) perquè la tria sigui reproduïble. Les mateixes 10 frases s'usen a P2, C2 i G2.
id = número de línia al corpus (des de 0).

Ús:  python data/create_queries.py [--n N] [--seed S]
"""

import argparse
import json
import random
from pathlib import Path

DATA = Path(__file__).resolve().parent
SEED = 2026
N = 10


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--n", type=int, default=N)
    parser.add_argument("--seed", type=int, default=SEED)
    args = parser.parse_args()

    sentences = (DATA / "corpus_10k.txt").read_text(encoding="utf-8").splitlines()
    ids = sorted(random.Random(args.seed).sample(range(len(sentences)), args.n))
    queries = [{"id": i, "text": sentences[i]} for i in ids]

    out = DATA / "queries.json"
    out.write_text(json.dumps(queries, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
    for q in queries:
        print(f"{q['id']:>5}  {q['text']}")
    print(f"-> {out} (llavor {args.seed})")


if __name__ == "__main__":
    main()
