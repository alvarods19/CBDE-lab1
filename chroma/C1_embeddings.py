"""
C1 — Llegeix les frases de Chroma (col·lecció de C0), en genera els embeddings i els desa.

- Generem l'embedding nosaltres (model.encode) per poder separar-ne el temps del
  d'emmagatzematge, cosa que C0 no permet. Però el registre és indivisible: cal tornar a
  passar ids + documents + embeddings en el mateix add().
- La mètrica és una propietat de l'índex HNSW i es fixa en crear la col·lecció: per a dues
  mètriques calen dues col·leccions (bc_cosine, bc_l2) i els vectors s'insereixen dues vegades.
- El vector numpy es passa directament a add(): no hi ha conversió a text ni a llista.
- Per chunk: generar_emb (encode, un cop) i insert_emb (add a cada col·lecció, amb la seva
  mètrica). Chunks > get_max_batch_size() es parteixen en diverses crides.
- Per a cada mida les col·leccions es creen de nou (buides). Cal haver executat C0.

Ús:  python chroma/C1_embeddings.py [--db-dir D] [--out-dir D] [--sizes 1 10 ...]
"""

import argparse
import csv
import statistics
import time
from pathlib import Path

import chromadb
import numpy as np
from sentence_transformers import SentenceTransformer

ROOT = Path(__file__).resolve().parent.parent
SIZES = [1, 10, 100, 500, 2000, 5000, 10000]
METRICS = {"cosine": "bc_cosine", "l2": "bc_l2"}
db_calls = 0


def main():
    global db_calls
    parser = argparse.ArgumentParser()
    parser.add_argument("--db-dir", type=Path, default=ROOT / "chroma" / "chroma_db")
    parser.add_argument("--out-dir", type=Path, default=ROOT / "results")
    parser.add_argument("--sizes", type=int, nargs="+", default=SIZES)
    args = parser.parse_args()

    model = SentenceTransformer("all-MiniLM-L6-v2", device="cpu")  # fora del cronòmetre

    client = chromadb.PersistentClient(path=str(args.db_dir))
    max_batch = client.get_max_batch_size()
    src = client.get_collection("bc_c0", embedding_function=None)
    data = src.get(include=["documents"])  # l'ordre no està garantit: s'ordena per id
    db_calls += 3
    order = sorted(range(len(data["ids"])), key=lambda i: int(data["ids"][i]))
    ids = [data["ids"][i] for i in order]
    docs = [data["documents"][i] for i in order]

    rows = []
    existing = [c.name for c in client.list_collections()]
    db_calls += 1
    for size in args.sizes:
        cols = {}
        for metric, name in METRICS.items():
            if name in existing:
                client.delete_collection(name)
                db_calls += 1
            cols[metric] = client.create_collection(name, embedding_function=None,
                                                    configuration={"hnsw": {"space": metric}})
            db_calls += 1
        existing = list(METRICS.values())
        t_gen, t_ins = [], {m: [] for m in METRICS}
        for n, start in enumerate(range(0, len(ids), size)):
            end = min(start + size, len(ids))

            t0 = time.perf_counter()
            emb = model.encode(docs[start:end])
            t_gen.append(time.perf_counter() - t0)
            rows.append(["chroma", size, "generar_emb", "-", n, 0, f"{t_gen[-1]:.9f}"])

            for metric, col in cols.items():
                t0 = time.perf_counter()
                for b in range(start, end, max_batch):
                    e = min(b + max_batch, end)
                    col.add(ids=ids[b:e], documents=docs[b:e], embeddings=emb[b - start:e - start])
                    db_calls += 1
                t_ins[metric].append(time.perf_counter() - t0)
                rows.append(["chroma", size, "insert_emb", metric, n, 0, f"{t_ins[metric][-1]:.9f}"])
        for name, t in [("generar_emb", t_gen)] + [(f"insert_emb {m}", t) for m, t in t_ins.items()]:
            std = statistics.stdev(t) if len(t) > 1 else 0.0
            print(f"chunk {size:>5} {name:<17}: {len(t):>5} chunks | total {sum(t):.4f} s | "
                  f"min {min(t):.6f} max {max(t):.6f} media {statistics.mean(t):.6f} desv {std:.6f}")

    # El model ja normalitza (capa Normalize): norma 1 => L2 i cosinus donen el mateix rànquing.
    print(f"Norma de l'últim vector: {np.linalg.norm(emb[-1]):.6f}")
    counts = {m: c.count() for m, c in cols.items()}
    db_calls += len(cols)

    args.out_dir.mkdir(parents=True, exist_ok=True)
    out = args.out_dir / "tiempos_c1.csv"
    with open(out, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["sistema", "tam_chunk", "operacion", "metrica", "muestra", "repeticion", "segundos"])
        w.writerows(rows)
    print(f"Registres: {counts} | crides a Chroma: {db_calls} | CSV: {out}")


if __name__ == "__main__":
    main()
