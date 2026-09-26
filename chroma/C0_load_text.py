"""
C0 — Carrega el text del corpus a Chroma, per chunks, i mesura el temps de cada chunk.

- Mateixa partició que P0: 1 línia = 1 frase, id = número de línia (Chroma exigeix str).
- A Chroma no hi ha registres sense vector: add(documents=...) crida la embedding function
  de la col·lecció (all-MiniLM-L6-v2, CPU, com P1/C1). Per això l'operació és
  "insert_fusionado": text + càlcul de l'embedding + índex HNSW, en una sola crida.
- Mida de chunk = mida de lot. Chroma limita cada add() a get_max_batch_size() elements;
  si el chunk és més gran es parteix en diverses crides dins del mateix cronòmetre.
- Per a cada mida la col·lecció es crea de nou (buida). No hi ha commit: la persistència
  és automàtica.

Ús:  python chroma/C0_load_text.py [--corpus F] [--db-dir D] [--out-dir D] [--sizes 1 10 ...]
"""

import argparse
import csv
import statistics
import time
from pathlib import Path

import chromadb
from chromadb.utils.embedding_functions import SentenceTransformerEmbeddingFunction

ROOT = Path(__file__).resolve().parent.parent
SIZES = [1, 10, 100, 500, 2000, 5000, 10000]
COLLECTION = "bc_c0"
db_calls = 0


def main():
    global db_calls
    parser = argparse.ArgumentParser()
    parser.add_argument("--corpus", type=Path, default=ROOT / "data" / "corpus_10k.txt")
    parser.add_argument("--db-dir", type=Path, default=ROOT / "chroma" / "chroma_db")
    parser.add_argument("--out-dir", type=Path, default=ROOT / "results")
    parser.add_argument("--sizes", type=int, nargs="+", default=SIZES)
    args = parser.parse_args()

    sentences = args.corpus.read_text(encoding="utf-8").splitlines()
    ids = [str(i) for i in range(len(sentences))]

    ef = SentenceTransformerEmbeddingFunction(model_name="all-MiniLM-L6-v2", device="cpu")  # carrega el model aquí
    client = chromadb.PersistentClient(path=str(args.db_dir))
    max_batch = client.get_max_batch_size()
    db_calls += 1

    rows = []
    for size in args.sizes:
        if COLLECTION in [c.name for c in client.list_collections()]:
            client.delete_collection(COLLECTION)
            db_calls += 1
        col = client.create_collection(COLLECTION, embedding_function=ef,
                                       configuration={"hnsw": {"space": "cosine"}})
        db_calls += 2
        times = []
        for n, start in enumerate(range(0, len(sentences), size)):
            end = min(start + size, len(sentences))
            t0 = time.perf_counter()
            for b in range(start, end, max_batch):
                col.add(ids=ids[b:min(b + max_batch, end)], documents=sentences[b:min(b + max_batch, end)])
                db_calls += 1
            times.append(time.perf_counter() - t0)
            rows.append(["chroma", size, "insert_fusionado", "-", n, 0, f"{times[-1]:.9f}"])
        std = statistics.stdev(times) if len(times) > 1 else 0.0
        print(f"chunk {size:>5}: {len(times):>5} chunks | total {sum(times):.4f} s | "
              f"min {min(times):.6f} max {max(times):.6f} media {statistics.mean(times):.6f} desv {std:.6f}")

    total = col.count()
    db_calls += 1

    args.out_dir.mkdir(parents=True, exist_ok=True)
    out = args.out_dir / "tiempos_c0.csv"
    with open(out, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["sistema", "tam_chunk", "operacion", "metrica", "muestra", "repeticion", "segundos"])
        w.writerows(rows)
    print(f"Registres a {COLLECTION}: {total} | max_batch_size: {max_batch} | crides a Chroma: {db_calls} | CSV: {out}")


if __name__ == "__main__":
    main()
