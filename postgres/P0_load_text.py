"""
P0 — Carga el texto del corpus en PostgreSQL, por chunks, y mide el tiempo de cada chunk.

- El corpus ya viene segmentado: 1 línea = 1 frase. El id de cada frase es su número de
  línea (desde 0), el mismo en PostgreSQL, Chroma y pgvector.
- Tamaño de chunk = tamaño de lote: 1 execute_values + 1 commit por chunk.
- Para cada tamaño la tabla se crea de nuevo (vacía).

Conexión: variables PGHOST, PGPORT, PGUSER, PGPASSWORD, PGDATABASE (por defecto, las de
docker-compose.yml).

Uso:  python postgres/P0_load_text.py [--corpus F] [--out-dir D] [--sizes 1 10 ...]
"""

import argparse
import csv
import os
import statistics
import time
from pathlib import Path

import psycopg2
from psycopg2.extras import execute_values

ROOT = Path(__file__).resolve().parent.parent
SIZES = [1, 10, 100, 500, 2000, 5000, 10000]
db_calls = 0


def connect():
    return psycopg2.connect(
        host=os.environ.get("PGHOST", "localhost"),
        port=os.environ.get("PGPORT", "5433"),
        user=os.environ.get("PGUSER", "lab1"),
        password=os.environ.get("PGPASSWORD", "password123"),
        dbname=os.environ.get("PGDATABASE", "corpus_db"),
    )


def create_table(conn, cur):
    global db_calls
    # TEXT: mismo tipo interno (varlena) que VARCHAR, sin límite ni comprobación de longitud.
    # id INTEGER (no SERIAL): el id lo fija el corpus, no el orden de inserción.
    cur.execute("DROP TABLE IF EXISTS sentences CASCADE")
    cur.execute("CREATE TABLE sentences (id INTEGER PRIMARY KEY, text TEXT NOT NULL)")
    conn.commit()
    db_calls += 3


def main():
    global db_calls
    parser = argparse.ArgumentParser()
    parser.add_argument("--corpus", type=Path, default=ROOT / "data" / "corpus_10k.txt")
    parser.add_argument("--out-dir", type=Path, default=ROOT / "results")
    parser.add_argument("--sizes", type=int, nargs="+", default=SIZES)
    args = parser.parse_args()

    sentences = args.corpus.read_text(encoding="utf-8").splitlines()
    records = list(enumerate(sentences))  # [(id, text), ...]

    conn = connect()
    cur = conn.cursor()
    rows = []
    for size in args.sizes:
        create_table(conn, cur)
        times = []
        for n, start in enumerate(range(0, len(records), size)):
            chunk = records[start:start + size]
            t0 = time.perf_counter()
            execute_values(cur, "INSERT INTO sentences (id, text) VALUES %s", chunk, page_size=len(chunk))
            conn.commit()
            times.append(time.perf_counter() - t0)
            db_calls += 2
            rows.append(["postgres", size, "insert_texto", "-", n, 0, f"{times[-1]:.9f}"])
        std = statistics.stdev(times) if len(times) > 1 else 0.0
        print(f"chunk {size:>5}: {len(times):>5} chunks | total {sum(times):.4f} s | "
              f"min {min(times):.6f} max {max(times):.6f} media {statistics.mean(times):.6f} desv {std:.6f}")

    cur.execute("SELECT count(*) FROM sentences")
    total = cur.fetchone()[0]
    db_calls += 1
    conn.close()

    args.out_dir.mkdir(parents=True, exist_ok=True)
    out = args.out_dir / "tiempos_p0.csv"
    with open(out, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["sistema", "tam_chunk", "operacion", "metrica", "muestra", "repeticion", "segundos"])
        w.writerows(rows)
    print(f"Filas en sentences: {total} | llamadas a la BD: {db_calls} | CSV: {out}")


if __name__ == "__main__":
    main()
