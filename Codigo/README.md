# Optimización de Puntos de Acopio y Red de Frío Pesquera (Puerto Gaitán, Meta)

Proyecto Final — Estructuras de Datos (Tercer Corte: Grafos)  
Universidad de los Llanos — Facultad de Ciencias Básicas e Ingeniería (Ingeniería en Sistemas)

## Estructura del Proyecto

- `include/List.h`, `src/List.cpp`: TAD `List<T>` (lista enlazada simple genérica reutilizada de las prácticas del curso).
- `include/Grafo.h`, `src/Grafo.cpp`: TAD `Graph<T>`, `Vertex<T>` y `Edge<T>` con lista de adyacencia, impresión completa, búsqueda en anchura (`bfsObjetivo`) y búsqueda en profundidad (`dfsTodasLasRutas`) con evaluación de deterioro bacteriano para cachama de río.
- `data/encuestas_pescadores.csv`: Consolidación estructurada de las 33 encuestas cartográficas reales de Puerto Gaitán y Puerto López.
- `data/red_actual.txt`: Grafo dirigido ponderado del escenario actual (sin centros de frío en subcuencas).
- `data/red_optimizada.txt`: Grafo dirigido ponderado con 3 centros estratégicos de acopio y red de frío (`P_Muco`, `D_Manacacias_Medio`, `D_Bocas_Manacacias`) + fortalecimiento en cabecera municipal.
- `main.cpp`: Interfaz de consola interactiva y modo automático (`--batch`).

## Compilación y Ejecución

Desde la carpeta `Codigo/`:

```bash
g++ -std=c++17 -Iinclude main.cpp src/Grafo.cpp src/List.cpp -o proyecto_pesca.exe
```

Ejecución interactiva (menú):

```bash
./proyecto_pesca.exe
```

Ejecución automática completa (imprime listas de adyacencia, resuelve Incógnita 1 BFS, Incógnita 2 DFS y exporta `data/comparativa_resultados.csv`):

```bash
./proyecto_pesca.exe --batch
```
