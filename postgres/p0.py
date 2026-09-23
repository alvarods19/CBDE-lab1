import time
import statistics
import psycopg2
from psycopg2.extras import execute_values
import nltk

# Aseguramos que el tokenizador de frases esté descargado
nltk.download('punkt', quiet=True)
nltk.download('punkt_tab', quiet=True) # Necesario en versiones recientes de nltk

DB_CONFIG = {
    "dbname": "corpus_db",
    "user": "lab1",
    "password": "password123",
    "host": "localhost",
    "port": 5433
}

def init_table(conn):
    with conn.cursor() as cur:
        # Usamos REAL[] como tipo óptimo para PostgreSQL sin Pgvector
        cur.execute("""
            CREATE TABLE IF NOT EXISTS sentences (
                id SERIAL PRIMARY KEY,
                text TEXT NOT NULL,
                embedding REAL[]
            );
        """)
        cur.execute("TRUNCATE TABLE sentences RESTART IDENTITY;")
        conn.commit()

def load_data_in_chunks(conn, file_path, chunk_size):
    # 1. Lectura y separación rigurosa por frases según el enunciado
    with open(file_path, "r", encoding="utf-8") as f:
        raw_text = f.read()
    
    # nltk.sent_tokenize divide el texto masivo en frases reales
    all_sentences = nltk.sent_tokenize(raw_text)
    
    # Preparamos los registros para PostgreSQL: [(linea1,), (linea2,), ...]
    records = [(s.strip(),) for s in all_sentences if s.strip()]
    
    times = []
    
    with conn.cursor() as cur:
        for i in range(0, len(records), chunk_size):
            chunk = records[i:i + chunk_size]
            
            # Medimos estrictamente el tiempo de almacenamiento
            start_time = time.time()
            execute_values(
                cur,
                "INSERT INTO sentences (text) VALUES %s",
                chunk,
                page_size=chunk_size
            )
            conn.commit()
            
            # Guardamos el tiempo parcial de este bloque
            times.append(time.time() - start_time)
            
    # 2. Computamos las estadísticas exigidas por P0
    print(f"\n--- Métricas de inserción de texto (Chunk Size: {chunk_size}) ---")
    print(f"Total frases procesadas: {len(records)}")
    print(f"Bloques (chunks) insertados: {len(times)}")
    print(f"Tiempo Mínimo: {min(times):.6f} s")
    print(f"Tiempo Máximo: {max(times):.6f} s")
    print(f"Tiempo Medio (Avg): {statistics.mean(times):.6f} s")
    if len(times) > 1:
        print(f"Desviación Estándar (Std Dev): {statistics.stdev(times):.6f} s")
    else:
        print("Desviación Estándar (Std Dev): N/A (solo hay un bloque)")

def main():
    # Parámetros de prueba
    test_chunk_sizes = [500, 1000, 5000]
    file_path = "corpus_10k.txt"

    for size in test_chunk_sizes:
        conn = psycopg2.connect(**DB_CONFIG)
        init_table(conn)
        load_data_in_chunks(conn, file_path, chunk_size=size)
        conn.close()

if __name__ == "__main__":
    main()