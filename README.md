# 🐟 Optimización de Centros de Refrigeración para Pesca Artesanal

## Ubicación Estratégica de Cadenas de Frío mediante Teoría de Grafos — Puerto Gaitán, Meta, Colombia

[![Python](https://img.shields.io/badge/Python-3.10+-3776AB?logo=python&logoColor=white)](https://python.org)
[![Folium](https://img.shields.io/badge/Folium-0.20-77B829?logo=leaflet&logoColor=white)](https://python-visualization.github.io/folium/)
[![Tests](https://img.shields.io/badge/Tests-30%20passed-brightgreen)](tests/)
[![License](https://img.shields.io/badge/License-MIT-green)](LICENSE)
[![Status](https://img.shields.io/badge/Status-Funcional-brightgreen)]()

---

## 📋 Descripción

Proyecto de **Estructuras de Datos** que modela la cadena de suministro pesquera de Puerto Gaitán, Meta, como un **problema de optimización sobre grafos**. El objetivo es determinar las **ubicaciones estratégicas** de centros de refrigeración que minimicen el deterioro del pescado durante el transporte desde los sitios de captura hasta los mercados finales (Villavicencio y Bogotá).

### Problema Real

Los pescadores artesanales de Puerto Gaitán pierden hasta un **40%** del producto por falta de cadena de frío adecuada. El pescado se deteriora rápidamente desde la captura hasta los centros de comercialización, generando pérdidas económicas significativas.

### Solución Propuesta

Combinar dos problemas clásicos de optimización:
1. **Facility Location Problem (FLP):** ¿Dónde ubicar los centros de refrigeración?
2. **Shortest Path / Vehicle Routing:** ¿Qué ruta debe seguir cada lote de pescado?

---

## 🏗️ Arquitectura del Proyecto

```
Proyecto/
├── README.md                    # Este archivo
├── LICENSE                      # Licencia MIT
├── requirements.txt             # Dependencias Python
├── setup.py                     # Configuración del paquete
├── .gitignore                   # Archivos a ignorar por Git
├── main.py                      # Punto de entrada principal
│
├── src/                         # Código fuente
│   ├── __init__.py
│   ├── models/                  # Modelos de datos (nodos, aristas, grafo)
│   │   ├── __init__.py
│   │   ├── nodo.py              # Clase Nodo (pesca, acopio, muelle, etc.)
│   │   ├── arista.py            # Clase Arista (con peso multicriterio)
│   │   └── grafo_logistico.py   # Grafo dirigido de la cadena pesquera
│   │
│   ├── algorithms/              # Algoritmos de grafos
│   │   ├── __init__.py
│   │   ├── dijkstra.py          # Caminos mínimos
│   │   ├── floyd_warshall.py    # Distancias mínimas entre todos los pares
│   │   └── bellman_ford.py      # Caminos mínimos con pesos negativos
│   │
│   ├── optimization/            # Localización óptima de centros
│   │   ├── __init__.py
│   │   ├── facility_location.py # Problema de localización de instalaciones
│   │   ├── cold_chain.py        # Simulación de cadena de frío
│   │   └── scenario_evaluator.py# Comparación de escenarios
│   │
│   ├── visualization/           # Visualización de resultados
│   │   ├── __init__.py
│   │   ├── graph_plotter.py     # Dibujar grafos con matplotlib
│   │   ├── map_renderer.py      # Renderizar mapas geográficos
│   │   ├── folium_map.py        # Mapa interactivo HTML (Folium)
│   │   ├── felt_exporter.py     # Exportación GeoJSON para Felt.com
│   │   └── route_geometry.py    # Geometrías reales via OSRM
│   │
│   └── utils/                   # Utilidades
│       ├── __init__.py
│       ├── data_loader.py       # Carga de datos CSV y shapefiles
│       ├── geo_utils.py         # Funciones geográficas (Haversine, etc.)
│       └── constants.py         # Constantes del proyecto
│
├── data/                        # Datos del proyecto
│   ├── shapefiles/              # Archivos SHP de ríos
│   │   ├── rios.shp
│   │   ├── rios.dbf
│   │   ├── rios.prj
│   │   ├── rios.shx
│   │   └── rios.cst
│   ├── csv/                     # Datos tabulares
│   │   ├── nodos_pesca.csv      # Puntos de captura
│   │   ├── nodos_centros.csv    # Centros poblados candidatos
│   │   ├── nodos_destinos.csv   # Mercados de destino
│   │   └── aristas.csv          # Conexiones entre nodos
│   ├── geojson/                 # Datos georreferenciados
│   │   └── puntos_campo.geojson # 49 puntos de campo (acopio, deterioro, hábitat, muelle, venta)
│   └── output/                  # Resultados generados
│
├── tests/                       # Pruebas unitarias (30 tests)
│   ├── __init__.py
│   ├── test_grafo.py            # 7 tests — modelos de datos
│   ├── test_dijkstra.py         # 5 tests — caminos mínimos
│   ├── test_bellman_ford.py     # 5 tests — verificación cruzada
│   ├── test_floyd_warshall.py   # 5 tests — todos los pares
│   ├── test_cold_chain.py       # 5 tests — simulación de frío
│   └── test_facility_location.py# 3 tests — localización óptima
│
└── docs/                        # Documentación
    ├── modelo_matematico.md     # Formulación matemática
    └── images/                  # Imágenes para documentación
```

---

## 🗺️ Tipos de Nodos del Grafo

| Código | Tipo | Descripción |
|--------|------|-------------|
| **P** | Punto de Pesca | Sitios de captura y desembarco de pescadores |
| **A** | Centro de Acopio | Recepción, pesaje y consolidación de producto |
| **D** | Zona de Deterioro | Puntos donde se mide la pérdida de calidad |
| **H** | Hábitat Protegido | Zonas con restricción ambiental |
| **M** | Muelle | Infraestructura de desembarque fluvial |
| **F** | Red de Frío | Centros con refrigeración (candidatos o existentes) |
| **V** | Lugar de Venta | Mercados de destino (P. Gaitán, Villavicencio, Bogotá) |

---

## ⚙️ Modelo Matemático

### Función Objetivo

Minimizar el número de centros de refrigeración garantizando la conservación:

$$\min Z = \sum_{j \in J} y_j$$

Sujeto a:

$$D_{\text{ruta}} \leq D_{\max} \quad \forall \text{ ruta}$$

$$Q_j \leq \text{Cap}_j \quad \forall j \in J$$

### Peso de las Aristas

$$w_{ij} = \alpha \cdot t_{ij} + \beta \cdot c_{ij} + \gamma \cdot r_{ij} + \delta \cdot p_{ij}$$

Donde:
- $t_{ij}$: tiempo de recorrido (horas)
- $c_{ij}$: costo de transporte (COP)
- $r_{ij}$: riesgo de ruptura de cadena de frío
- $p_{ij}$: pérdida estimada de producto

---

## 🚀 Instalación y Uso

### Prerrequisitos

- Python 3.10 o superior
- pip (gestor de paquetes)

### Instalación

```bash
# Clonar el repositorio
git clone https://github.com/tu-usuario/cold-chain-optimization-puerto-gaitan.git
cd cold-chain-optimization-puerto-gaitan

# Crear entorno virtual
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # Linux/Mac

# Instalar dependencias
pip install -r requirements.txt
```

### Ejecución

```bash
# Ejecutar el programa principal (7 pasos automáticos)
python main.py

# Ejecutar pruebas unitarias
python -m pytest tests/ -v

# O individualmente
python tests/test_grafo.py
python tests/test_dijkstra.py
python tests/test_bellman_ford.py
python tests/test_floyd_warshall.py
python tests/test_cold_chain.py
python tests/test_facility_location.py
```

### Pasos del Pipeline

| Paso | Descripción | Algoritmo |
|------|-------------|-----------|
| 1 | Carga de datos CSV y construcción del grafo | — |
| 2 | Caminos mínimos desde cada punto de pesca | Dijkstra |
| 3 | Matriz de distancias entre todos los pares | Floyd-Warshall |
| 3B | Verificación cruzada y detección de ciclos | Bellman-Ford |
| 4 | Localización óptima de centros de frío | FLP Greedy |
| 5 | Simulación de deterioro del pescado | Cadena de frío |
| 6 | Comparación de escenarios (local y Bogotá) | Evaluador |
| 7 | Visualización del grafo y exportación | matplotlib |
| 8 | Exportación GeoJSON + ZIP para Felt.com | json / zipfile |
| 9 | Obtención de geometrías reales de carreteras | OSRM API |
| 10 | Mapa interactivo HTML con rutas reales | Folium |

---

## 📈 Resultados Esperados

Al ejecutar `python main.py`, el programa produce:

- **Rutas óptimas** de cada punto de pesca al mercado más cercano
- **Matriz de tiempos** entre todos los nodos del grafo
- **Validación** Bellman-Ford vs Dijkstra (detección de ciclos negativos)
- **Centro óptimo** recomendado (FLP greedy): Centro Frío Puerto Gaitán (F02) con 100% cobertura
- **Simulación** de pérdida de pescado por ruta
- **Tabla comparativa** de escenarios: sin frío vs con 1 centro vs múltiples centros
- **Gráfico** `data/output/grafo_logistico.png` con la red y ruta óptima destacada
- **Mapa interactivo** `data/output/mapa_interactivo.html` con rutas siguiendo carreteras reales (OSRM)
- **GeoJSON** `data/output/nodos_red.geojson` y `ruta_dijkstra.geojson` para visualización externa
- **CSV exportados** en `data/output/`

---

## 🗺️ Mapa Interactivo

El mapa HTML (`data/output/mapa_interactivo.html`) incluye **11 capas activables**:

| Capa | Descripción | Activa por defecto |
|------|-------------|--------------------|
| 🐟 Punto de Pesca | 7 nodos de captura del grafo | ✅ |
| 📦 Centro de Acopio | 3 nodos de acopio del grafo | ✅ |
| ❄️ Red de Frío | 3 centros candidatos del grafo | ✅ |
| 🏪 Mercados | 3 mercados destino del grafo | ✅ |
| 🔗 Conexiones | 26 aristas con geometría de carreteras reales | ✅ |
| 🛤️ Ruta Óptima | Ruta Dijkstra animada (P01 → ... → Bogotá) | ✅ |
| 📦 Acopio (campo) | 14 puntos de acopio georeferenciados | ⬜ |
| 🌡️ Deterioro (campo) | 11 zonas de deterioro identificadas | ⬜ |
| 🌿 Hábitat (campo) | 14 zonas de hábitat protegido | ⬜ |
| ⚓ Muelles (campo) | 8 puntos de infraestructura fluvial | ⬜ |
| 🏪 Venta (campo) | 2 puntos de venta adicionales | ⬜ |

Las rutas siguen **carreteras reales** obtenidas de OpenStreetMap via OSRM, no líneas rectas.

---

## 📊 Variables del Modelo

### Variables de Decisión
- Ubicación de centros de refrigeración (binaria)
- Asignación de cada punto de pesca a un centro
- Rutas utilizadas y flujos de pescado

### Parámetros de Entrada
- Producción pesquera (kg/día por punto)
- Distancia y tiempo entre nodos
- Tasa de deterioro del pescado
- Capacidad de centros y vehículos
- Costos de transporte e instalación

### Métricas de Evaluación
- Número de centros necesarios
- Tiempo promedio hasta primera refrigeración
- Porcentaje de pérdida de producto
- Costo logístico total por kg transportado

---

## 🌊 Contexto Geográfico

**Corredor principal:** Sitios de Pesca → Puerto Gaitán → Villavicencio → Bogotá

**Ríos principales:**
- Río Manacacías (ASOPESGA / Alto Neblinas)
- Río Meta (Asovida / San Miguel)
- Río Iteviare (Puerto Trujillo)

**Asociaciones de pescadores:**
- ASOPESGA — Producción histórica: 24 ton/año
- Atarraya Verde — Río Manacacías (20 personas)
- Asovida — Vereda San Miguel (11 personas)
- Asopespor — Río Meta (10 personas)

---

## 📚 Referencias Bibliográficas

1. FAO — Manual de manipulación de pescado y cadena de frío
2. Universidad de los Llanos — Proyecto piscicultura sostenible Puerto Gaitán (2026)
3. AUNAP — Resolución 2663 de 2022 (veda pesquera Orinoquía)
4. Baigún, C.R.M. (2013) — Manual gestión ambiental pesca artesanal
5. Cuan-Barrera et al. (2021) — Parámetros productivos cachama blanca

---

## 📄 Licencia

Este proyecto está bajo la [Licencia MIT](LICENSE).

---

## 👤 Autor

**Estructuras de Datos — Universidad**
Semestre 03 | 2026-II

---

> *"La mejor ubicación es la que permite enfriar el pescado lo antes posible;
> la mejor ruta es la que mantiene el producto cerca de 0 °C durante todo
> el recorrido, aunque no sea la más corta."*

