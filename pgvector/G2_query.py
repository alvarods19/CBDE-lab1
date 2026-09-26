"""
G2 — Top-2 de las 10 frases de data/queries.json con pgvector, en dos escenarios:

  1. sistema=pgvector       sin índice: recorrido completo, pero la distancia es un operador
                            nativo en C (<-> L2, <=> 1 - coseno). Búsqueda exacta.
  2. sistema=pgvector_hnsw  con un índice HNSW por métrica (su operator class): búsqueda
                            aproximada. Se mide crear_indice.

- Sin funciones de distancia escritas a mano (P2 las necesita). Mismo SQL que P2 con otro
  operador: la métrica la elige la consulta; el índice, en cambio, sirve para una sola métrica.
- <-> es L2 con raíz y <=> es 1 - coseno, como l2_dist y cos_dist de P2: las distancias deben
  coincidir con top2_postgres.csv (salvo redondeo: pgvector acumula en float4).
- Parámetros HNSW iguales a los de Chroma (m = max_neighbors = 16, ef_construction = 100,
  ef_search = 100) para comparar sistemas, no configuraciones. Defaults de pgvector: 16, 64, 40.
- ANALYZE antes de medir (como en P2): el plan no depende de si autovacuum ya pasó.
- EXPLAIN ANALYZE (fuera del cronómetro) de cada escenario y métrica: con HNSW, el plan tiene
  que usar el índice; si no, el script se para.
- El vector de consulta se lee antes del cronómetro y se pasa como parámetro; la propia frase
  se excluye con WHERE. Por frase y métrica: 1 calentamiento (no se guarda) + 5 repeticiones.
- Consulta el estado que dejó G1 (su último tamaño de chunk, por defecto 10000).

Uso:  python pgvector/G2_query.py [--queries F] [--out-dir D] [--tam-chunk N]
                                  [--m 16] [--ef-construction 100] [--ef-search 100]
"""

import argparse
import csv
import json
import os
import re
import statistics
import time
from pathlib import Path

import psycopg2
from pgvector.psycopg2 import register_vector

ROOT = Path(__file__).resolve().parent.parent
REPS = 5
db_calls = 0

QUERY = """
SELECT s.id, s.text, e.embedding {op} %(q)s AS d
FROM sentence_embeddings e JOIN sentences s ON s.id = e.sentence_id
WHERE e.sentence_id <> %(qid)s
ORDER BY d LIMIT 2
"""
METRICS = {"cosine": ("<=>", "vector_cosine_ops"), "l2": ("<->", "vector_l2_ops")}


def connect():
    return psycopg2.connect(
        host=os.environ.get("PGHOST", "localhost"),
        port=os.environ.get("PGPORT", "5434"),
        user=os.environ.get("PGUSER", "lab1"),
        password=os.environ.get("PGPASSWORD", "password123"),
        dbname=os.environ.get("PGDATABASE", "lab_pgvector"),
    )


def explain(cur, sql, params, index=None):
    global db_calls
    cur.execute("EXPLAIN (ANALYZE, BUFFERS) " + sql, params)
    plan = re.sub(r"'\[[^\]]*\]'", "'[...]'", "\n".join(r[0] for r in cur.fetchall()))  # sin el literal
    db_calls += 1
    print(plan + "\n")
    if index and index not in plan:
        raise SystemExit(f"El plan no usa {index}: la medición con HNSW no sería válida.")


def run_queries(cur, sistema, vectors, tam_chunk, times, top2):
    global db_calls
    for metric, (op, _) in METRICS.items():
        sql = QUERY.format(op=op)
        metric_times = []
        for qid, q in vectors.items():
            params = {"q": q, "qid": qid}
            cur.execute(sql, params)  # calentamiento
            cur.fetchall()
            db_calls += 1
            for rep in range(1, REPS + 1):
                t0 = time.perf_counter()
                cur.execute(sql, params)
                result = cur.fetchall()
                metric_times.append(time.perf_counter() - t0)
                db_calls += 1
                times.append([sistema, tam_chunk, "consulta", metric, qid, rep, f"{metric_times[-1]:.9f}"])
            for rank, (rid, text, d) in enumerate(result, 1):
                top2.append([sistema, metric, qid, rank, rid, f"{d:.9f}"])
                print(f"[{sistema} {metric}] {qid} -> #{rank} {rid} d={d:.6f}  {text[:60]}")
        print(f"[{sistema} {metric}] {len(metric_times)} muestras | min {min(metric_times):.6f} "
              f"max {max(metric_times):.6f} media {statistics.mean(metric_times):.6f} "
              f"desv {statistics.stdev(metric_times):.6f} s\n")


def main():
    global db_calls
    parser = argparse.ArgumentParser()
    parser.add_argument("--queries", type=Path, default=ROOT / "data" / "queries.json")
    parser.add_argument("--out-dir", type=Path, default=ROOT / "results")
    parser.add_argument("--tam-chunk", type=int, default=10000)
    parser.add_argument("--m", type=int, default=16)
    parser.add_argument("--ef-construction", type=int, default=100)
    parser.add_argument("--ef-search", type=int, default=100)
    args = parser.parse_args()

    qids = [q["id"] for q in json.loads(args.queries.read_text(encoding="utf-8"))]

    conn = connect()
    cur = conn.cursor()
    register_vector(conn)  # 1 SELECT a pg_type; devuelve los vector como pgvector.Vector
    for _, opclass in METRICS.values():
        cur.execute(f"DROP INDEX IF EXISTS emb_hnsw_{opclass}")
    # Estadísticas del planificador al día: sin esto, el plan depende de si autovacuum ya pasó.
    cur.execute("ANALYZE sentences, sentence_embeddings")
    conn.commit()
    # Vectores de consulta, fuera del cronómetro.
    cur.execute("SELECT sentence_id, embedding FROM sentence_embeddings WHERE sentence_id = ANY(%s)", (qids,))
    vectors = dict(sorted(cur.fetchall()))
    db_calls += 6

    times, top2 = [], []

    # Escenario 1: sin índice (exacto).
    for op, _ in METRICS.values():
        explain(cur, QUERY.format(op=op), {"q": vectors[qids[0]], "qid": qids[0]})
    run_queries(cur, "pgvector", vectors, args.tam_chunk, times, top2)

    # Escenario 2: un índice HNSW por métrica.
    for metric, (op, opclass) in METRICS.items():
        t0 = time.perf_counter()
        cur.execute(f"CREATE INDEX emb_hnsw_{opclass} ON sentence_embeddings USING hnsw "
                    f"(embedding {opclass}) WITH (m = {args.m}, ef_construction = {args.ef_construction})")
        conn.commit()
        t = time.perf_counter() - t0
        db_calls += 2
        times.append(["pgvector_hnsw", args.tam_chunk, "crear_indice", metric, 0, 0, f"{t:.9f}"])
        cur.execute(f"SELECT pg_size_pretty(pg_relation_size('emb_hnsw_{opclass}'))")
        db_calls += 1
        print(f"CREATE INDEX hnsw {opclass}: {t:.4f} s | tamaño {cur.fetchone()[0]}")
    cur.execute(f"SET hnsw.ef_search = {args.ef_search}")
    db_calls += 1
    for op, opclass in METRICS.values():
        explain(cur, QUERY.format(op=op), {"q": vectors[qids[0]], "qid": qids[0]}, f"emb_hnsw_{opclass}")
    run_queries(cur, "pgvector_hnsw", vectors, args.tam_chunk, times, top2)
    conn.close()

    args.out_dir.mkdir(parents=True, exist_ok=True)
    out_t, out_r = args.out_dir / "tiempos_g2.csv", args.out_dir / "top2_pgvector.csv"
    with open(out_t, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["sistema", "tam_chunk", "operacion", "metrica", "muestra", "repeticion", "segundos"])
        w.writerows(times)
    with open(out_r, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["sistema", "metrica", "query_id", "rank", "result_id", "distancia"])
        w.writerows(top2)
    print(f"Consultas: {len(qids)} x {len(METRICS)} métricas x 2 escenarios | llamadas a la BD: {db_calls} | "
          f"CSV: {out_t}, {out_r}")


if __name__ == "__main__":
    main()
