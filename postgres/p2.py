import psycopg2
import time
import statistics

DB_CONFIG = {
    "dbname": "corpus_db",
    "user": "lab1",
    "password": "password123",
    "host": "localhost",
    "port": 5433
}

def crear_funciones_matematicas(cur):
    print("-> Inyectando funciones matemáticas en PostgreSQL...")
    
    # 1. Función para Distancia Euclídea usando DOUBLE PRECISION internamente
    cur.execute("""
        CREATE OR REPLACE FUNCTION euclidean_distance(a REAL[], b REAL[])
        RETURNS REAL AS $$
        DECLARE
            dist DOUBLE PRECISION := 0;
            diff DOUBLE PRECISION;
        BEGIN
            FOR i IN 1 .. array_length(a, 1) LOOP
                -- Convertimos a double para evitar el underflow al restar y multiplicar
                diff := a[i]::DOUBLE PRECISION - b[i]::DOUBLE PRECISION;
                dist := dist + (diff * diff);
            END LOOP;
            RETURN sqrt(dist)::REAL;
        END;
        $$ LANGUAGE plpgsql IMMUTABLE;
    """)

    # 2. Función para Similitud Coseno usando DOUBLE PRECISION internamente
    cur.execute("""
        CREATE OR REPLACE FUNCTION cosine_similarity(a REAL[], b REAL[])
        RETURNS REAL AS $$
        DECLARE
            dot_product DOUBLE PRECISION := 0;
            norm_a DOUBLE PRECISION := 0;
            norm_b DOUBLE PRECISION := 0;
            val_a DOUBLE PRECISION;
            val_b DOUBLE PRECISION;
        BEGIN
            FOR i IN 1 .. array_length(a, 1) LOOP
                val_a := a[i]::DOUBLE PRECISION;
                val_b := b[i]::DOUBLE PRECISION;
                dot_product := dot_product + (val_a * val_b);
                norm_a := norm_a + (val_a * val_a);
                norm_b := norm_b + (val_b * val_b);
            END LOOP;
            IF norm_a = 0 OR norm_b = 0 THEN RETURN 0; END IF;
            RETURN (dot_product / (sqrt(norm_a) * sqrt(norm_b)))::REAL;
        END;
        $$ LANGUAGE plpgsql IMMUTABLE;
    """)

def buscar_similares(conn, metric_name, query_template, order_desc, target_ids):
    cur = conn.cursor()
    tiempos = []
    
    print(f"\n=== Evaluando métrica: {metric_name} ===")
    
    for target_id in target_ids:
        # Recuperar el texto original para mostrarlo por consola
        cur.execute("SELECT text FROM sentences WHERE id = %s;", (target_id,))
        frase_original = cur.fetchone()[0]
        
        # INICIO DEL CRONÓMETRO
        start_time = time.time()
        
        # Ejecutar la búsqueda de los 2 más similares (excluyendo la propia frase)
        cur.execute(query_template, (target_id, target_id))
        resultados = cur.fetchall()
        
        # FIN DEL CRONÓMETRO
        end_time = time.time()
        tiempos.append(end_time - start_time)
        
        print(f"\nFrase objetivo [{target_id}]: '{frase_original[:80]}...'")
        for i, row in enumerate(resultados):
            print(f"  Top {i+1} (Score: {row[2]:.4f}): '{row[1][:80]}...'")

    cur.close()
    
    # Calcular estadísticas
    print(f"\n--- ESTADÍSTICAS PARA {metric_name.upper()} ---")
    print(f"Mínimo:             {min(tiempos):.4f} segundos")
    print(f"Máximo:             {max(tiempos):.4f} segundos")
    print(f"Media (Average):    {statistics.mean(tiempos):.4f} segundos")
    print(f"Desviación Estándar:{statistics.stdev(tiempos):.4f} segundos")


def main():
    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()
    
    crear_funciones_matematicas(cur)
    conn.commit()
    
    # Elegimos 10 frases específicas (puedes cambiar los IDs por los que quieras)
    target_sentences = [1, 100, 500, 1000, 2500, 4000, 5500, 7000, 8500, 9999]
    
    # Query para Euclídea: Ordenamos ASCENDENTE (distancia menor es mejor)
    query_euclidean = """
        SELECT b.id, b.text, euclidean_distance(a.embedding, b.embedding) AS score
        FROM sentences a, sentences b
        WHERE a.id = %s AND b.id != %s
        ORDER BY score ASC 
        LIMIT 2;
    """
    
    # Query para Coseno: Ordenamos DESCENDENTE (similitud mayor es mejor)
    query_cosine = """
        SELECT b.id, b.text, cosine_similarity(a.embedding, b.embedding) AS score
        FROM sentences a, sentences b
        WHERE a.id = %s AND b.id != %s
        ORDER BY score DESC 
        LIMIT 2;
    """
    
    buscar_similares(conn, "Distancia Euclídea", query_euclidean, order_desc=False, target_ids=target_sentences)
    buscar_similares(conn, "Similitud Coseno", query_cosine, order_desc=True, target_ids=target_sentences)

    conn.close()

if __name__ == "__main__":
    main()