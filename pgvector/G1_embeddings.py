"""
G1 — Lee las frases de la BD con pgvector, genera sus embeddings (all-MiniLM-L6-v2) y los guarda
en una columna de tipo vector(384).

- CREATE EXTENSION vector: añade el tipo vector, sus operadores de distancia y los índices.
- Tabla aparte sentence_embeddings, como en P1 (INSERT, no UPDATE: sin versiones MVCC muertas).
- vector(384) = float4 como el float32 del modelo, sin cabecera de array ni nulos
  (4 × 384 + 8 B). La dimensión se comprueba al insertar; en REAL[] no.
- register_vector(conn): el array de numpy se pasa tal cual, sin .tolist(). Ojo: con psycopg2
  el adaptador lo sigue enviando como texto '[0.01,-0.03,...]'; la conversión no desaparece,
  la hace la librería dentro de execute_values (y por tanto dentro del cronómetro).
- Por chunk se miden por separado:
    generar_emb: model.encode()
    insert_emb:  execute_values + commit
- Para cada tamaño la tabla se crea de nuevo (vacía). Requiere haber ejecutado G0.

Uso:  python pgvector/G1_embeddings.py [--out-dir D] [--sizes 1 10 ...]
"""

import argparse
import csv
import os
import statistics
import time
from pathlib import Path

import numpy as np
import psycopg2
from pgvector.psycopg2 import register_vector
from psycopg2.extras import execute_values
from sentence_transformers import SentenceTransformer

ROOT = Path(__file__).resolve().parent.parent
SIZES = [1, 10, 100, 500, 2000, 5000, 10000]
db_calls = 0


def connect():
    return psycopg2.connect(
        host=os.environ.get("PGHOST", "localhost"),
        port=os.environ.get("PGPORT", "5434"),
        user=os.environ.get("PGUSER", "lab1"),
        password=os.environ.get("PGPASSWORD", "password123"),
        dbname=os.environ.get("PGDATABASE", "lab_pgvector"),
    )


def create_table(conn, cur):
    global db_calls
    cur.execute("DROP TABLE IF EXISTS sentence_embeddings")
    cur.execute("""CREATE TABLE sentence_embeddings (
                       sentence_id INTEGER PRIMARY KEY REFERENCES sentences(id),
                       embedding vector(384) NOT NULL)""")
    conn.commit()
    db_calls += 3


def main():
    global db_calls
    parser = argparse.ArgumentParser()
    parser.add_argument("--out-dir", type=Path, default=ROOT / "results")
    parser.add_argument("--sizes", type=int, nargs="+", default=SIZES)
    args = parser.parse_args()

    model = SentenceTransformer("all-MiniLM-L6-v2", device="cpu")  # fuera del cronómetro

    conn = connect()
    cur = conn.cursor()
    cur.execute("CREATE EXTENSION IF NOT EXISTS vector")
    conn.commit()
    register_vector(conn)  # hace 1 SELECT a pg_type para conocer el OID del tipo vector
    cur.execute("SELECT extversion FROM pg_extension WHERE extname = 'vector'")
    print(f"pgvector {cur.fetchone()[0]}")
    cur.execute("SELECT id, text FROM sentences ORDER BY id")
    records = cur.fetchall()
    db_calls += 5

    rows = []
    for size in args.sizes:
        create_table(conn, cur)
        t_gen, t_ins = [], []
        for n, start in enumerate(range(0, len(records), size)):
            chunk = records[start:start + size]

            t0 = time.perf_counter()
            emb = model.encode([text for _, text in chunk])  # batch_size por defecto, como P1 y Chroma
            t_gen.append(time.perf_counter() - t0)

            t0 = time.perf_counter()
            values = [(sid, e) for (sid, _), e in zip(chunk, emb)]
            execute_values(cur, "INSERT INTO sentence_embeddings (sentence_id, embedding) VALUES %s",
                           values, page_size=len(values))
            conn.commit()
            t_ins.append(time.perf_counter() - t0)
            db_calls += 2

            rows.append(["pgvector", size, "generar_emb", "-", n, 0, f"{t_gen[-1]:.9f}"])
            rows.append(["pgvector", size, "insert_emb", "-", n, 0, f"{t_ins[-1]:.9f}"])
        for name, t in (("generar_emb", t_gen), ("insert_emb", t_ins)):
            std = statistics.stdev(t) if len(t) > 1 else 0.0
            print(f"chunk {size:>5} {name:<11}: {len(t):>5} chunks | total {sum(t):.4f} s | "
                  f"min {min(t):.6f} max {max(t):.6f} media {statistics.mean(t):.6f} desv {std:.6f}")

    print(f"Norma del último vector: {np.linalg.norm(emb[-1]):.6f}")

    cur.execute("SELECT count(*) FROM sentence_embeddings")
    total = cur.fetchone()[0]
    db_calls += 1
    conn.close()

    args.out_dir.mkdir(parents=True, exist_ok=True)
    out = args.out_dir / "tiempos_g1.csv"
    with open(out, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["sistema", "tam_chunk", "operacion", "metrica", "muestra", "repeticion", "segundos"])
        w.writerows(rows)
    print(f"Filas en sentence_embeddings: {total} | llamadas a la BD: {db_calls} | CSV: {out}")


if __name__ == "__main__":
    main()
