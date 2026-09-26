"""
C2 — Top-2 de les 10 frases de data/queries.json a Chroma, amb cosinus i L2.

- Una col·lecció per mètrica (bc_cosine, bc_l2): la mètrica és de l'índex, no de la consulta.
- Els vectors de consulta es llegeixen de la col·lecció abans del cronòmetre.
- query() no pot excloure un id: es demanen 3 resultats i es descarta la pròpia frase.
- Cerca aproximada (HNSW): cal validar-la contra top2_postgres.csv (cerca exacta).
- Distàncies de Chroma: l2 = L2 al quadrat; cosine = 1 - cos. Els valors no coincideixen
  amb PostgreSQL (L2 amb arrel), però el rànquing sí.
- Per frase i mètrica: 1 escalfament (no es desa) + 5 repeticions.

Ús:  python chroma/C2_query.py [--queries F] [--db-dir D] [--out-dir D] [--tam-chunk N]
"""

import argparse
import csv
import json
import statistics
import time
from pathlib import Path

import chromadb

ROOT = Path(__file__).resolve().parent.parent
REPS = 5
METRICS = {"cosine": "bc_cosine", "l2": "bc_l2"}
db_calls = 0


def main():
    global db_calls
    parser = argparse.ArgumentParser()
    parser.add_argument("--queries", type=Path, default=ROOT / "data" / "queries.json")
    parser.add_argument("--db-dir", type=Path, default=ROOT / "chroma" / "chroma_db")
    parser.add_argument("--out-dir", type=Path, default=ROOT / "results")
    parser.add_argument("--tam-chunk", type=int, default=10000)
    args = parser.parse_args()

    qids = [str(q["id"]) for q in json.loads(args.queries.read_text(encoding="utf-8"))]

    client = chromadb.PersistentClient(path=str(args.db_dir))
    cols = {m: client.get_collection(name, embedding_function=None) for m, name in METRICS.items()}
    got = cols["cosine"].get(ids=qids, include=["embeddings"])  # fora del cronòmetre
    db_calls += 3
    vectors = dict(zip(got["ids"], got["embeddings"]))

    times, top2 = [], []
    for metric, col in cols.items():
        metric_times = []
        for qid in qids:
            col.query(query_embeddings=[vectors[qid]], n_results=3, include=["documents", "distances"])  # escalfament
            db_calls += 1
            for rep in range(1, REPS + 1):
                t0 = time.perf_counter()
                res = col.query(query_embeddings=[vectors[qid]], n_results=3, include=["documents", "distances"])
                metric_times.append(time.perf_counter() - t0)
                db_calls += 1
                times.append(["chroma", args.tam_chunk, "consulta", metric, qid, rep, f"{metric_times[-1]:.9f}"])
            hits = [h for h in zip(res["ids"][0], res["documents"][0], res["distances"][0]) if h[0] != qid][:2]
            for rank, (rid, text, d) in enumerate(hits, 1):
                top2.append(["chroma", metric, qid, rank, rid, f"{d:.9f}"])
                print(f"[{metric}] {qid} -> #{rank} {rid} d={d:.6f}  {text[:70]}")
        print(f"[{metric}] {len(metric_times)} mostres | min {min(metric_times):.6f} max {max(metric_times):.6f} "
              f"mitjana {statistics.mean(metric_times):.6f} desv {statistics.stdev(metric_times):.6f} s\n")

    args.out_dir.mkdir(parents=True, exist_ok=True)
    out_t, out_r = args.out_dir / "tiempos_c2.csv", args.out_dir / "top2_chroma.csv"
    with open(out_t, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["sistema", "tam_chunk", "operacion", "metrica", "muestra", "repeticion", "segundos"])
        w.writerows(times)
    with open(out_r, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["sistema", "metrica", "query_id", "rank", "result_id", "distancia"])
        w.writerows(top2)
    print(f"Consultes: {len(qids)} x {len(METRICS)} mètriques | crides a Chroma: {db_calls} | CSV: {out_t}, {out_r}")


if __name__ == "__main__":
    main()
