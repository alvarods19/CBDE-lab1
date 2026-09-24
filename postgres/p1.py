import psycopg2
from psycopg2.extras import execute_values
from sentence_transformers import SentenceTransformer
import time
import statistics

# Configuración de tu base de datos
DB_CONFIG = {
    "dbname": "corpus_db",
    "user": "lab1",
    "password": "password123",
    "host": "localhost",
    "port": 5433
}

def main():
    print("1. Cargando el modelo de IA (all-MiniLM-L6-v2)...")
    model = SentenceTransformer('all-MiniLM-L6-v2')
    
    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()

    print("2. Recuperando los textos de la BD...")
    cur.execute("SELECT id, text FROM sentences ORDER BY id;")
    rows = cur.fetchall()
    
    if not rows:
        print("No hay frases para procesar. Ejecuta P0 primero.")
        return

    print(f"Se van a procesar {len(rows)} frases.\n")

    # Tamaños de lote (chunks) que queremos probar
    test_batch_sizes = [100, 500, 1000]

    for b_size in test_batch_sizes:
        print(f"=== INICIANDO PRUEBA CON BATCH SIZE = {b_size} ===")
        
        # 3. Limpiar los embeddings antes de cada prueba para que sea justo
        cur.execute("UPDATE sentences SET embedding = NULL;")
        conn.commit()
        
        storage_times = [] # Aquí guardaremos los tiempos de cada bloque
        
        # 4. Procesamiento por bloques
        for i in range(0, len(rows), b_size):
            batch = rows[i:i+b_size]
            batch_ids = [row[0] for row in batch]
            batch_texts = [row[1] for row in batch]
            
            # -- FASE DE IA (NO se cuenta en el tiempo de almacenamiento) --
            embeddings = model.encode(batch_texts)
            
            # Preparar datos para Postgres: (id, [0.1, -0.4, ...])
            update_data = [(d_id, emb.tolist()) for d_id, emb in zip(batch_ids, embeddings)]
                
            update_query = """
                UPDATE sentences AS s
                SET embedding = v.embedding::REAL[]
                FROM (VALUES %s) AS v(id, embedding)
                WHERE s.id = v.id;
            """
            
            # -- FASE DE ALMACENAMIENTO (INICIO DEL CRONÓMETRO) --
            start_store_time = time.time()
            
            execute_values(cur, update_query, update_data, page_size=b_size)
            conn.commit()
            
            end_store_time = time.time()
            # -- FASE DE ALMACENAMIENTO (FIN DEL CRONÓMETRO) --
            
            # Guardamos el tiempo de este bloque en particular
            storage_times.append(end_store_time - start_store_time)
            
        # 5. Calcular e imprimir métricas para este tamaño de lote
        total_time = sum(storage_times)
        min_time = min(storage_times)
        max_time = max(storage_times)
        avg_time = statistics.mean(storage_times)
        std_dev = statistics.stdev(storage_times) if len(storage_times) > 1 else 0.0
        
        print(f"Resultados para Batch Size {b_size}:")
        print(f"  - Tiempo TOTAL de guardado: {total_time:.4f} seg")
        print(f"  - Mínimo por bloque:        {min_time:.4f} seg")
        print(f"  - Máximo por bloque:        {max_time:.4f} seg")
        print(f"  - Media por bloque:         {avg_time:.4f} seg")
        print(f"  - Desviación estándar:      {std_dev:.4f} seg\n")

    cur.close()
    conn.close()
    print("Pruebas finalizadas correctamente.")

if __name__ == "__main__":
    main()