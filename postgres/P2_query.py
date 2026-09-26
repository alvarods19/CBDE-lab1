"""
P2 — Top-2 de las 10 frases de data/queries.json con dos métricas (L2 y coseno), sin pgvector.

- PostgreSQL no sabe qué es un vector: las distancias se escriben a mano como funciones SQL
  sobre REAL[] (unnest + sum). Se acumula en float8: en float4, el cuadrado de diferencias
  muy pequeñas se redondea a 0 y PostgreSQL lanza "value out of range: underflow".
- Sin índice aplicable: cada consulta recorre las 10.000 filas.
- El vector de consulta se lee antes del cronómetro y se pasa como parámetro (igual que en
  Chroma y pgvector); la propia frase se excluye con WHERE.
- ANALYZE antes de medir (fuera del cronómetro): el plan no depende de si autovacuum ya pasó.
- Por frase y métrica: 1 calentamiento (no se guarda) + 5 repeticiones.
- Consulta el estado que dejó P1 (su último tamaño de chunk, por defecto 10000).

Uso:  python postgres/P2_query.py [--queries F] [--out-dir D] [--tam-chunk N]
"""

import argparse
import csv
import json
import os
import statistics
import time
from pathlib import Path

import psycopg2

ROOT = Path(__file__).resolve().parent.parent
REPS = 5
db_calls = 0

FUNCTIONS = """
CREATE OR REPLACE FUNCTION l2_dist(a REAL[], b REAL[]) RETURNS float8
LANGUAGE sql IMMUTABLE STRICT PARALLEL SAFE AS
$$ SELECT sqrt(sum((x::float8 - y::float8) ^ 2)) FROM unnest(a, b) AS t(x, y) $$;

CREATE OR REPLACE FUNCTION cos_dist(a REAL[], b REAL[]) RETURNS float8
LANGUAGE sql IMMUTABLE STRICT PARALLEL SAFE AS
$$ SELECT 1 - sum(x::float8 * y) / (sqrt(sum(x::float8 * x)) * sqrt(sum(y::float8 * y)))
   FROM unnest(a, b) AS t(x, y) $$;
"""

QUERY = """
SELECT s.id, s.text, {fn}(e.embedding, %(q)s::real[]) AS d
FROM sentence_embeddings e JOIN sentences s ON s.id = e.sentence_id
WHERE e.sentence_id <> %(qid)s
ORDER BY d LIMIT 2
"""
METRICS = {"cosine": "cos_dist", "l2": "l2_dist"}


def connect():
    return psycopg2.connect(
        host=os.environ.get("PGHOST", "localhost"),
        port=os.environ.get("PGPORT", "5433"),
        user=os.environ.get("PGUSER", "lab1"),
        password=os.environ.get("PGPASSWORD", "password123"),
        dbname=os.environ.get("PGDATABASE", "corpus_db"),
    )


def main():
    global db_calls
    parser = argparse.ArgumentParser()
    parser.add_argument("--queries", type=Path, default=ROOT / "data" / "queries.json")
    parser.add_argument("--out-dir", type=Path, default=ROOT / "results")
    parser.add_argument("--tam-chunk", type=int, default=10000)
    args = parser.parse_args()

    queries = json.loads(args.queries.read_text(encoding="utf-8"))
    qids = [q["id"] for q in queries]

    conn = connect()
    cur = conn.cursor()
    cur.execute(FUNCTIONS)
    # Estadísticas del planificador al día: sin esto, el plan depende de si autovacuum ya pasó.
    cur.execute("ANALYZE sentences, sentence_embeddings")
    conn.commit()
    db_calls += 3

    # Vectores de consulta, fuera del cronómetro (psycopg2 devuelve REAL[] como lista de float).
    cur.execute("SELECT sentence_id, embedding FROM sentence_embeddings WHERE sentence_id = ANY(%s)", (qids,))
    vectors = dict(cur.fetchall())
    db_calls += 1

    times, top2 = [], []
    for metric, fn in METRICS.items():
        sql = QUERY.format(fn=fn)
        metric_times = []
        for qid in qids:
            params = {"q": vectors[qid], "qid": qid}
            cur.execute(sql, params)  # calentamiento
            cur.fetchall()
            db_calls += 1
            for rep in range(1, REPS + 1):
                t0 = time.perf_counter()
                cur.execute(sql, params)
                result = cur.fetchall()
                metric_times.append(time.perf_counter() - t0)
                db_calls += 1
                times.append(["postgres", args.tam_chunk, "consulta", metric, qid, rep, f"{metric_times[-1]:.9f}"])
            for rank, (rid, text, d) in enumerate(result, 1):
                top2.append(["postgres", metric, qid, rank, rid, f"{d:.9f}"])
                print(f"[{metric}] {qid} -> #{rank} {rid} d={d:.6f}  {text[:70]}")
        print(f"[{metric}] {len(metric_times)} muestras | min {min(metric_times):.6f} max {max(metric_times):.6f} "
              f"media {statistics.mean(metric_times):.6f} desv {statistics.stdev(metric_times):.6f} s\n")
    conn.close()

    args.out_dir.mkdir(parents=True, exist_ok=True)
    out_t, out_r = args.out_dir / "tiempos_p2.csv", args.out_dir / "top2_postgres.csv"
    with open(out_t, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["sistema", "tam_chunk", "operacion", "metrica", "muestra", "repeticion", "segundos"])
        w.writerows(times)
    with open(out_r, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["sistema", "metrica", "query_id", "rank", "result_id", "distancia"])
        w.writerows(top2)
    print(f"Consultas: {len(qids)} x {len(METRICS)} métricas | llamadas a la BD: {db_calls} | CSV: {out_t}, {out_r}")


if __name__ == "__main__":
    main()
