Fuente: tiempos_c0.csv, tiempos_c1.csv, tiempos_c2.csv, tiempos_g0.csv, tiempos_g1.csv, tiempos_g2.csv, tiempos_p0.csv, tiempos_p1.csv, tiempos_p2.csv

## 1. Estadísticas por chunk (s)

| sistema | tam_chunk | operacion | metrica | n | total | min | max | media | desv |
|---|---|---|---|---|---|---|---|---|---|
| chroma | 1 | generar_emb | - | 10000 | 130.831441 | 0.009564 | 0.083085 | 0.013083 | 0.002092 |
| chroma | 1 | insert_emb | cosine | 10000 | 221.479754 | 0.011630 | 1.748910 | 0.022148 | 0.018584 |
| chroma | 1 | insert_emb | l2 | 10000 | 215.635828 | 0.011030 | 0.165322 | 0.021564 | 0.005836 |
| chroma | 1 | insert_fusionado | - | 10000 | 310.989266 | 0.021503 | 0.133351 | 0.031099 | 0.004661 |
| chroma | 10 | generar_emb | - | 1000 | 50.982022 | 0.023283 | 0.131446 | 0.050982 | 0.012525 |
| chroma | 10 | insert_emb | cosine | 1000 | 44.608992 | 0.020581 | 1.718814 | 0.044609 | 0.066618 |
| chroma | 10 | insert_emb | l2 | 1000 | 37.148443 | 0.016835 | 0.283262 | 0.037148 | 0.022763 |
| chroma | 10 | insert_fusionado | - | 1000 | 78.105833 | 0.051688 | 0.185217 | 0.078106 | 0.014913 |
| chroma | 100 | generar_emb | - | 100 | 37.791697 | 0.283156 | 0.518179 | 0.377917 | 0.050639 |
| chroma | 100 | insert_emb | cosine | 100 | 9.409130 | 0.065262 | 0.216850 | 0.094091 | 0.032265 |
| chroma | 100 | insert_emb | l2 | 100 | 8.687352 | 0.048536 | 0.150539 | 0.086874 | 0.020741 |
| chroma | 100 | insert_fusionado | - | 100 | 44.592770 | 0.329406 | 0.627652 | 0.445928 | 0.055835 |
| chroma | 500 | generar_emb | - | 20 | 31.418066 | 1.422033 | 1.711943 | 1.570903 | 0.082692 |
| chroma | 500 | insert_emb | cosine | 20 | 6.838989 | 0.254213 | 0.469560 | 0.341949 | 0.056711 |
| chroma | 500 | insert_emb | l2 | 20 | 5.594792 | 0.196513 | 0.768644 | 0.279740 | 0.121493 |
| chroma | 500 | insert_fusionado | - | 20 | 36.038418 | 1.623258 | 2.042620 | 1.801921 | 0.107012 |
| chroma | 2000 | generar_emb | - | 5 | 29.953349 | 5.853565 | 6.227454 | 5.990670 | 0.149284 |
| chroma | 2000 | insert_emb | cosine | 5 | 5.141001 | 0.909854 | 1.224842 | 1.028200 | 0.131963 |
| chroma | 2000 | insert_emb | l2 | 5 | 4.476345 | 0.843781 | 1.008190 | 0.895269 | 0.066664 |
| chroma | 2000 | insert_fusionado | - | 5 | 33.087219 | 6.318193 | 6.714959 | 6.617444 | 0.168243 |
| chroma | 5000 | generar_emb | - | 2 | 29.446221 | 14.483322 | 14.962898 | 14.723110 | 0.339111 |
| chroma | 5000 | insert_emb | cosine | 2 | 4.225800 | 2.054251 | 2.171549 | 2.112900 | 0.082943 |
| chroma | 5000 | insert_emb | l2 | 2 | 4.282017 | 1.873526 | 2.408491 | 2.141008 | 0.378277 |
| chroma | 5000 | insert_fusionado | - | 2 | 35.335569 | 16.771399 | 18.564170 | 17.667785 | 1.267680 |
| chroma | 10000 | generar_emb | - | 1 | 30.965322 | 30.965322 | 30.965322 | 30.965322 | – |
| chroma | 10000 | insert_emb | cosine | 1 | 4.229806 | 4.229806 | 4.229806 | 4.229806 | – |
| chroma | 10000 | insert_emb | l2 | 1 | 4.701841 | 4.701841 | 4.701841 | 4.701841 | – |
| chroma | 10000 | insert_fusionado | - | 1 | 32.761530 | 32.761530 | 32.761530 | 32.761530 | – |
| pgvector | 1 | generar_emb | - | 10000 | 127.854772 | 0.009836 | 0.083334 | 0.012785 | 0.002037 |
| pgvector | 1 | insert_emb | - | 10000 | 44.183282 | 0.003676 | 0.030846 | 0.004418 | 0.000463 |
| pgvector | 1 | insert_texto | - | 10000 | 27.810778 | 0.002037 | 0.015244 | 0.002781 | 0.000434 |
| pgvector | 10 | generar_emb | - | 1000 | 49.986700 | 0.026408 | 0.119756 | 0.049987 | 0.012471 |
| pgvector | 10 | insert_emb | - | 1000 | 56.584259 | 0.012972 | 0.473475 | 0.056584 | 0.016444 |
| pgvector | 10 | insert_texto | - | 1000 | 2.960999 | 0.002309 | 0.004677 | 0.002961 | 0.000289 |
| pgvector | 100 | generar_emb | - | 100 | 38.251969 | 0.275125 | 0.512247 | 0.382520 | 0.054255 |
| pgvector | 100 | insert_emb | - | 100 | 7.201421 | 0.045369 | 0.108116 | 0.072014 | 0.020484 |
| pgvector | 100 | insert_texto | - | 100 | 0.406842 | 0.003144 | 0.005030 | 0.004068 | 0.000344 |
| pgvector | 500 | generar_emb | - | 20 | 31.818589 | 1.486616 | 1.780536 | 1.590929 | 0.073992 |
| pgvector | 500 | insert_emb | - | 20 | 4.644010 | 0.200944 | 0.272793 | 0.232200 | 0.023709 |
| pgvector | 500 | insert_texto | - | 20 | 1.038035 | 0.050439 | 0.053047 | 0.051902 | 0.000750 |
| pgvector | 2000 | generar_emb | - | 5 | 30.217102 | 5.864693 | 6.377263 | 6.043420 | 0.206458 |
| pgvector | 2000 | insert_emb | - | 5 | 4.119462 | 0.792324 | 0.896896 | 0.823892 | 0.043080 |
| pgvector | 2000 | insert_texto | - | 5 | 0.170560 | 0.015647 | 0.060288 | 0.034112 | 0.023840 |
| pgvector | 5000 | generar_emb | - | 2 | 30.006627 | 14.627379 | 15.379248 | 15.003314 | 0.531652 |
| pgvector | 5000 | insert_emb | - | 2 | 4.191060 | 2.077271 | 2.113789 | 2.095530 | 0.025822 |
| pgvector | 5000 | insert_texto | - | 2 | 0.113739 | 0.038216 | 0.075524 | 0.056870 | 0.026381 |
| pgvector | 10000 | generar_emb | - | 1 | 30.578070 | 30.578070 | 30.578070 | 30.578070 | – |
| pgvector | 10000 | insert_emb | - | 1 | 3.884959 | 3.884959 | 3.884959 | 3.884959 | – |
| pgvector | 10000 | insert_texto | - | 1 | 0.108502 | 0.108502 | 0.108502 | 0.108502 | – |
| pgvector_hnsw | 10000 | crear_indice | cosine | 1 | 2.795388 | 2.795388 | 2.795388 | 2.795388 | – |
| pgvector_hnsw | 10000 | crear_indice | l2 | 1 | 2.537669 | 2.537669 | 2.537669 | 2.537669 | – |
| postgres | 1 | generar_emb | - | 10000 | 130.600801 | 0.009720 | 0.081323 | 0.013060 | 0.002163 |
| postgres | 1 | insert_emb | - | 10000 | 55.444613 | 0.004221 | 0.036130 | 0.005544 | 0.000566 |
| postgres | 1 | insert_texto | - | 10000 | 28.227317 | 0.002046 | 0.014078 | 0.002823 | 0.000480 |
| postgres | 10 | generar_emb | - | 1000 | 51.486145 | 0.027897 | 0.108639 | 0.051486 | 0.012063 |
| postgres | 10 | insert_emb | - | 1000 | 23.094022 | 0.019570 | 0.064726 | 0.023094 | 0.003044 |
| postgres | 10 | insert_texto | - | 1000 | 2.681904 | 0.002156 | 0.004909 | 0.002682 | 0.000271 |
| postgres | 100 | generar_emb | - | 100 | 37.710612 | 0.283874 | 0.553915 | 0.377106 | 0.056897 |
| postgres | 100 | insert_emb | - | 100 | 18.847420 | 0.148065 | 0.251293 | 0.188474 | 0.022380 |
| postgres | 100 | insert_texto | - | 100 | 0.409042 | 0.003488 | 0.005242 | 0.004090 | 0.000363 |
| postgres | 500 | generar_emb | - | 20 | 31.329691 | 1.411480 | 1.859225 | 1.566485 | 0.116682 |
| postgres | 500 | insert_emb | - | 20 | 15.086463 | 0.698816 | 0.810684 | 0.754323 | 0.029200 |
| postgres | 500 | insert_texto | - | 20 | 1.027488 | 0.048001 | 0.053130 | 0.051374 | 0.001568 |
| postgres | 2000 | generar_emb | - | 5 | 33.806630 | 6.039508 | 8.437094 | 6.761326 | 0.954208 |
| postgres | 2000 | insert_emb | - | 5 | 15.879941 | 3.069649 | 3.258503 | 3.175988 | 0.079176 |
| postgres | 2000 | insert_texto | - | 5 | 0.217159 | 0.017089 | 0.061697 | 0.043432 | 0.023465 |
| postgres | 5000 | generar_emb | - | 2 | 32.732309 | 16.287501 | 16.444809 | 16.366155 | 0.111234 |
| postgres | 5000 | insert_emb | - | 2 | 15.357623 | 7.657535 | 7.700088 | 7.678812 | 0.030090 |
| postgres | 5000 | insert_texto | - | 2 | 0.114096 | 0.034310 | 0.079785 | 0.057048 | 0.032156 |
| postgres | 10000 | generar_emb | - | 1 | 31.079177 | 31.079177 | 31.079177 | 31.079177 | – |
| postgres | 10000 | insert_emb | - | 1 | 16.065649 | 16.065649 | 16.065649 | 16.065649 | – |
| postgres | 10000 | insert_texto | - | 1 | 0.066507 | 0.066507 | 0.066507 | 0.066507 | – |

## 2. Carga completa por tamaño de chunk (s)

| sistema | operacion | metrica | tam_chunk | n | total | por_frase |
|---|---|---|---|---|---|---|
| chroma | generar_emb | - | 1 | 10000 | 130.831441 | 0.013083 |
| chroma | insert_emb | cosine | 1 | 10000 | 221.479754 | 0.022148 |
| chroma | insert_emb | l2 | 1 | 10000 | 215.635828 | 0.021564 |
| chroma | insert_fusionado | - | 1 | 10000 | 310.989266 | 0.031099 |
| chroma | generar_emb | - | 10 | 1000 | 50.982022 | 0.005098 |
| chroma | insert_emb | cosine | 10 | 1000 | 44.608992 | 0.004461 |
| chroma | insert_emb | l2 | 10 | 1000 | 37.148443 | 0.003715 |
| chroma | insert_fusionado | - | 10 | 1000 | 78.105833 | 0.007811 |
| chroma | generar_emb | - | 100 | 100 | 37.791697 | 0.003779 |
| chroma | insert_emb | cosine | 100 | 100 | 9.409130 | 0.000941 |
| chroma | insert_emb | l2 | 100 | 100 | 8.687352 | 0.000869 |
| chroma | insert_fusionado | - | 100 | 100 | 44.592770 | 0.004459 |
| chroma | generar_emb | - | 500 | 20 | 31.418066 | 0.003142 |
| chroma | insert_emb | cosine | 500 | 20 | 6.838989 | 0.000684 |
| chroma | insert_emb | l2 | 500 | 20 | 5.594792 | 0.000559 |
| chroma | insert_fusionado | - | 500 | 20 | 36.038418 | 0.003604 |
| chroma | generar_emb | - | 2000 | 5 | 29.953349 | 0.002995 |
| chroma | insert_emb | cosine | 2000 | 5 | 5.141001 | 0.000514 |
| chroma | insert_emb | l2 | 2000 | 5 | 4.476345 | 0.000448 |
| chroma | insert_fusionado | - | 2000 | 5 | 33.087219 | 0.003309 |
| chroma | generar_emb | - | 5000 | 2 | 29.446221 | 0.002945 |
| chroma | insert_emb | cosine | 5000 | 2 | 4.225800 | 0.000423 |
| chroma | insert_emb | l2 | 5000 | 2 | 4.282017 | 0.000428 |
| chroma | insert_fusionado | - | 5000 | 2 | 35.335569 | 0.003534 |
| chroma | generar_emb | - | 10000 | 1 | 30.965322 | 0.003097 |
| chroma | insert_emb | cosine | 10000 | 1 | 4.229806 | 0.000423 |
| chroma | insert_emb | l2 | 10000 | 1 | 4.701841 | 0.000470 |
| chroma | insert_fusionado | - | 10000 | 1 | 32.761530 | 0.003276 |
| pgvector | generar_emb | - | 1 | 10000 | 127.854772 | 0.012785 |
| pgvector | insert_emb | - | 1 | 10000 | 44.183282 | 0.004418 |
| pgvector | insert_texto | - | 1 | 10000 | 27.810778 | 0.002781 |
| pgvector | generar_emb | - | 10 | 1000 | 49.986700 | 0.004999 |
| pgvector | insert_emb | - | 10 | 1000 | 56.584259 | 0.005658 |
| pgvector | insert_texto | - | 10 | 1000 | 2.960999 | 0.000296 |
| pgvector | generar_emb | - | 100 | 100 | 38.251969 | 0.003825 |
| pgvector | insert_emb | - | 100 | 100 | 7.201421 | 0.000720 |
| pgvector | insert_texto | - | 100 | 100 | 0.406842 | 0.000041 |
| pgvector | generar_emb | - | 500 | 20 | 31.818589 | 0.003182 |
| pgvector | insert_emb | - | 500 | 20 | 4.644010 | 0.000464 |
| pgvector | insert_texto | - | 500 | 20 | 1.038035 | 0.000104 |
| pgvector | generar_emb | - | 2000 | 5 | 30.217102 | 0.003022 |
| pgvector | insert_emb | - | 2000 | 5 | 4.119462 | 0.000412 |
| pgvector | insert_texto | - | 2000 | 5 | 0.170560 | 0.000017 |
| pgvector | generar_emb | - | 5000 | 2 | 30.006627 | 0.003001 |
| pgvector | insert_emb | - | 5000 | 2 | 4.191060 | 0.000419 |
| pgvector | insert_texto | - | 5000 | 2 | 0.113739 | 0.000011 |
| pgvector | generar_emb | - | 10000 | 1 | 30.578070 | 0.003058 |
| pgvector | insert_emb | - | 10000 | 1 | 3.884959 | 0.000388 |
| pgvector | insert_texto | - | 10000 | 1 | 0.108502 | 0.000011 |
| pgvector_hnsw | crear_indice | cosine | 10000 | 1 | 2.795388 | 0.000280 |
| pgvector_hnsw | crear_indice | l2 | 10000 | 1 | 2.537669 | 0.000254 |
| postgres | generar_emb | - | 1 | 10000 | 130.600801 | 0.013060 |
| postgres | insert_emb | - | 1 | 10000 | 55.444613 | 0.005544 |
| postgres | insert_texto | - | 1 | 10000 | 28.227317 | 0.002823 |
| postgres | generar_emb | - | 10 | 1000 | 51.486145 | 0.005149 |
| postgres | insert_emb | - | 10 | 1000 | 23.094022 | 0.002309 |
| postgres | insert_texto | - | 10 | 1000 | 2.681904 | 0.000268 |
| postgres | generar_emb | - | 100 | 100 | 37.710612 | 0.003771 |
| postgres | insert_emb | - | 100 | 100 | 18.847420 | 0.001885 |
| postgres | insert_texto | - | 100 | 100 | 0.409042 | 0.000041 |
| postgres | generar_emb | - | 500 | 20 | 31.329691 | 0.003133 |
| postgres | insert_emb | - | 500 | 20 | 15.086463 | 0.001509 |
| postgres | insert_texto | - | 500 | 20 | 1.027488 | 0.000103 |
| postgres | generar_emb | - | 2000 | 5 | 33.806630 | 0.003381 |
| postgres | insert_emb | - | 2000 | 5 | 15.879941 | 0.001588 |
| postgres | insert_texto | - | 2000 | 5 | 0.217159 | 0.000022 |
| postgres | generar_emb | - | 5000 | 2 | 32.732309 | 0.003273 |
| postgres | insert_emb | - | 5000 | 2 | 15.357623 | 0.001536 |
| postgres | insert_texto | - | 5000 | 2 | 0.114096 | 0.000011 |
| postgres | generar_emb | - | 10000 | 1 | 31.079177 | 0.003108 |
| postgres | insert_emb | - | 10000 | 1 | 16.065649 | 0.001607 |
| postgres | insert_texto | - | 10000 | 1 | 0.066507 | 0.000007 |

## 3. Consultas top-2 (s)

| sistema | metrica | n | min | max | media | desv |
|---|---|---|---|---|---|---|
| chroma | cosine | 50 | 0.001483 | 0.002704 | 0.001925 | 0.000305 |
| chroma | l2 | 50 | 0.001400 | 0.002733 | 0.001802 | 0.000333 |
| pgvector | cosine | 50 | 0.008958 | 0.013163 | 0.009824 | 0.000725 |
| pgvector | l2 | 50 | 0.008811 | 0.010375 | 0.009352 | 0.000307 |
| pgvector_hnsw | cosine | 50 | 0.002954 | 0.004098 | 0.003428 | 0.000282 |
| pgvector_hnsw | l2 | 50 | 0.002907 | 0.004512 | 0.003486 | 0.000322 |
| postgres | cosine | 50 | 0.518922 | 0.702493 | 0.557772 | 0.029047 |
| postgres | l2 | 50 | 0.505187 | 0.612301 | 0.531341 | 0.023167 |

## 4. Líneas de código

| script | lineas |
|---|---|
| postgres/P0_load_text.py | 64 |
| postgres/P1_embeddings.py | 77 |
| postgres/P2_query.py | 89 |
| chroma/C0_load_text.py | 56 |
| chroma/C1_embeddings.py | 72 |
| chroma/C2_query.py | 56 |
| pgvector/G0_load_text.py | 64 |
| pgvector/G1_embeddings.py | 83 |
| pgvector/G2_query.py | 115 |
