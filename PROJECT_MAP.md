# PROJECT_MAP.md — Mapa Sintáctico Automático (AST Repo-Map)

> **Generado automáticamente:** `2026-11-18 19:05` vía `scripts/generar_repo_map.py`  
> **Propósito:** Permite a cualquier agente de Antigravity navegar clases, firmas y líneas exactas sin abrir archivos completos ni desperdiciar tokens.
> **Compresión de contexto:** `13,563` líneas de código Python condensadas en `314` líneas (**97.7% de ahorro**).


## 1. Arquitectura Python (Firmas y Rangos de Línea)

### `main.py` (`632` líneas) — OPTIMIZACIÓN DE CENTROS DE REFRIGERACIÓN PARA PESCA ARTESANAL
- **Constantes:** `BASE_DIR (L32)`
- `def cargar_datos() -> GrafoLogistico` `[L56-L164]` — Construye el grafo logístico completo a partir de los CSV.
- `def _cargar_datos_ejemplo(grafo: GrafoLogistico)` `[L167-L181]` — Carga datos de ejemplo si no existen los CSV.
- `def ejecutar_dijkstra(grafo: GrafoLogistico)` `[L188-L221]` — Ejecuta Dijkstra entre puntos clave.
- `def ejecutar_bellman_ford(grafo: GrafoLogistico)` `[L224-L280]` — Ejecuta Bellman-Ford y verifica consistencia con Dijkstra.
- `def ejecutar_floyd_warshall(grafo: GrafoLogistico)` `[L283-L304]` — Ejecuta Floyd-Warshall y muestra la matriz.
- `def ejecutar_localizacion(grafo: GrafoLogistico)` `[L311-L323]` — Resuelve el problema de localización de instalaciones.
- `def ejecutar_simulacion(grafo: GrafoLogistico)` `[L330-L353]` — Simula la cadena de frío para la ruta más larga.
- `def ejecutar_itinerarios(grafo: GrafoLogistico)` `[L360-L391]` — Calcula e imprime los itinerarios por punto de pesca hacia Bogotá y V_PG1.
- `def ejecutar_comparacion(grafo: GrafoLogistico)` `[L398-L481]` — Compara escenarios con y sin centros de frío.
- `def ejecutar_soluciones_eca(grafo: GrafoLogistico)` `[L484-L488]` — Ejecuta y muestra las 6 soluciones algorítmicas de la ECA (C05-01-2026-003).
- `def ejecutar_visualizacion(grafo: GrafoLogistico)` `[L495-L524]` — Genera la visualización del grafo.
- `def main()` `[L531-L627]` — Flujo principal del programa.

### `src/algorithms/bellman_ford.py` (`104` líneas) — bellman_ford.py — Algoritmo de Bellman-Ford para caminos mínimos.
- `def bellman_ford(grafo: GrafoLogistico, origen: str, criterio: str = 'peso', evitar_restringidos: bool = False) -> Tuple[Dict[str, float], Dict[str, Optional[str]], bool]` `[L16-L87]` — Ejecuta Bellman-Ford desde un nodo origen.
- `def reconstruir_camino_bf(prev: Dict[str, Optional[str]], destino: str) -> List[str]` `[L90-L103]` — Reconstruye el camino mínimo desde el predecesor.

### `src/algorithms/bfs.py` (`173` líneas) — bfs.py — Búsqueda en Amplitud (Breadth-First Search).
- `def _restringido(grafo: GrafoLogistico, nodo_id: str) -> bool` `[L18-L21]` — Indica si el nodo tiene restricción ambiental (hábitat protegido).
- `def bfs_recorrido(grafo: GrafoLogistico, origen: str, evitar_restringidos: bool = True) -> List[str]` `[L24-L66]` — Realiza un recorrido en amplitud completo a partir del vértice origen.
- `def bfs_camino(grafo: GrafoLogistico, origen: str, destino: str, evitar_restringidos: bool = True) -> Tuple[int, List[str]]` `[L69-L125]` — Encuentra el camino con menor número de saltos (aristas) entre origen y destino.
- `def bfs_nodo_mas_cercano_por_tipo(grafo: GrafoLogistico, origen: str, tipos_objetivo: Tuple[str, ...] = ('A', 'F'), evitar_restringidos: bool = True) -> Tuple[Optional[str], int, List[str]]` `[L128-L173]` — Encuentra el nodo objetivo más próximo en número de transbordos/saltos usando BFS.

### `src/algorithms/dfs.py` (`148` líneas) — dfs.py — Búsqueda en Profundidad (Depth-First Search).
- `def _restringido(grafo: GrafoLogistico, nodo_id: str) -> bool` `[L17-L20]` — Indica si el nodo tiene restricción ambiental (hábitat protegido).
- `def dfs_recorrido(grafo: GrafoLogistico, origen: str, evitar_restringidos: bool = True) -> List[str]` `[L23-L59]` — Realiza un recorrido en profundidad completo a partir del vértice origen.
- `def dfs_todos_los_caminos(grafo: GrafoLogistico, origen: str, destino: str, max_saltos: int = 10, evitar_restringidos: bool = True) -> List[List[str]]` `[L62-L111]` — Encuentra todos los caminos simples posibles entre origen y destino mediante DFS con backtracking.
- `def dfs_resumen_rutas(grafo: GrafoLogistico, origen: str, destino: str, evitar_restringidos: bool = True) -> List[Dict[str, any]]` `[L114-L148]` — Calcula todas las rutas simples por DFS y extrae métricas de distancia y tiempo para cada una.

### `src/algorithms/dijkstra.py` (`271` líneas) — dijkstra.py — Algoritmo de Dijkstra para caminos mínimos.
- `def _restringido(grafo: GrafoLogistico, nodo_id: str) -> bool` `[L18-L21]` — Indica si el nodo tiene restricción ambiental (hábitat protegido).
- `def _tiene_refrigeracion(grafo: GrafoLogistico, nodo_id: str) -> bool` `[L24-L31]` — Indica si el nodo abate temperatura (centro de frío F o acopio con frío).
- `def dijkstra_con_cota_inocuidad(grafo: GrafoLogistico, origen: str, destino: str, tiempo_limite_h: float = TIEMPO_MAX_SIN_FRIO_H, criterio: str = 'peso', evitar_restringidos: bool = True) -> Tuple[float, List[str], float, bool]` `[L34-L117]` — Camino Más Corto Restringido por Tiempo de Inocuidad FAO (Constrained Shortest Path).
- `def dijkstra(grafo: GrafoLogistico, origen: str, destino: str, criterio: str = 'peso', evitar_restringidos: bool = False) -> Tuple[float, List[str]]` `[L120-L208]` — Encuentra el camino mínimo entre dos nodos usando Dijkstra.
- `def dijkstra_completo(grafo: GrafoLogistico, origen: str, criterio: str = 'peso', evitar_restringidos: bool = False) -> Dict[str, Tuple[float, List[str]]]` `[L211-L270]` — Ejecuta Dijkstra desde un origen hacia TODOS los nodos alcanzables.

### `src/algorithms/floyd_warshall.py` (`134` líneas) — floyd_warshall.py — Algoritmo de Floyd-Warshall.
- `def floyd_warshall(grafo: GrafoLogistico, criterio: str = 'peso', evitar_restringidos: bool = False) -> Tuple[Dict[str, Dict[str, float]], Dict[str, Dict[str, Optional[str]]]]` `[L16-L78]` — Ejecuta Floyd-Warshall sobre el grafo logístico.
- `def reconstruir_camino(siguiente: Dict[str, Dict[str, Optional[str]]], origen: str, destino: str) -> List[str]` `[L81-L105]` — Reconstruye el camino mínimo usando la matriz 'siguiente'
- `def matriz_a_tabla(dist: Dict[str, Dict[str, float]], ids: Optional[List[str]] = None) -> str` `[L108-L133]` — Formatea la matriz de distancias como tabla legible.

### `src/models/arista.py` (`212` líneas) — arista.py — Modelo de datos para las aristas del grafo logístico.
- `class Arista` `[L27-L212]` — Representa una conexión dirigida entre dos nodos del grafo.
  - `def __post_init__(self)` `[L84-L89]` — Calcula costos por defecto si no fueron provistos.
  - `def factor_estado_via(self) -> float` `[L94-L97]` — Multiplicador de penalización por estado de la vía.
  - `def factor_flujo(self) -> float` `[L100-L103]` — Multiplicador por nivel de flujo vehicular.
  - `def riesgo_combinado(self) -> float` `[L106-L111]` — Riesgo combinado: térmico + accidente + derrumbe (0–1).
  - `def tiempo_efectivo_h(self) -> float` `[L114-L116]` — Tiempo total incluyendo espera y factor de flujo.
  - `def costo_total_cop(self) -> float` `[L119-L121]` — Costo total del tramo: transporte + peajes.
  - `def perdida_esperada(self) -> float` `[L124-L135]` — Porcentaje de pérdida estimada en el tramo (0–100).
  - `def peso(self, alpha: float = ALPHA, beta: float = BETA, gamma: float = GAMMA, delta: float = DELTA, epsilon: float = EPSILON, zeta: float = ZETA) -> float` `[L139-L168]` — Calcula el peso combinado multicriterio de la arista.
  - `def peso_default(self) -> float` `[L171-L173]` — Peso con coeficientes por defecto.
  - `def to_dict(self) -> Dict[str, Any]` `[L177-L205]` — Convierte la arista a diccionario serializable.
  - `def __repr__(self) -> str` `[L207-L212]`

### `src/models/grafo_logistico.py` (`262` líneas) — grafo_logistico.py — Grafo dirigido multicriterio para la cadena pesquera.
- `class GrafoLogistico` `[L20-L261]` — Grafo dirigido ponderado para modelar la cadena de suministro
  - `def __init__(self)` `[L29-L32]`
  - `def agregar_nodo(self, nodo: Nodo) -> None` `[L38-L42]` — Agrega un nodo al grafo. Si ya existe, lo reemplaza.
  - `def obtener_nodo(self, id_nodo: str) -> Optional[Nodo]` `[L44-L46]` — Devuelve el nodo con el ID dado, o None.
  - `def eliminar_nodo(self, id_nodo: str) -> bool` `[L48-L64]` — Elimina un nodo y todas sus aristas asociadas.
  - `def nodos(self) -> List[Nodo]` `[L67-L69]` — Lista de todos los nodos.
  - `def num_nodos(self) -> int` `[L72-L73]`
  - `def nodos_por_tipo(self, tipo: str) -> List[Nodo]` `[L75-L77]` — Filtra nodos por código de tipo (P, A, D, H, M, F, V).
  - `def agregar_arista(self, arista: Arista) -> None` `[L83-L90]` — Agrega una arista dirigida al grafo.
  - `def agregar_arista_auto(self, id_origen: str, id_destino: str, estado_via: str = 'buena', tipo_via: str = 'terrestre', **kwargs) -> Arista` `[L92-L119]` — Crea y agrega una arista calculando automáticamente la distancia
  - `def obtener_aristas(self, id_origen: str) -> List[Arista]` `[L121-L123]` — Devuelve todas las aristas que salen de un nodo.
  - `def obtener_arista(self, id_origen: str, id_destino: str) -> Optional[Arista]` `[L125-L131]` — Devuelve la arista entre dos nodos, o None.
  - `def aristas(self) -> List[Arista]` `[L134-L140]` — Lista de todas las aristas del grafo.
  - `def num_aristas(self) -> int` `[L143-L144]`
  - `def vecinos(self, id_nodo: str) -> List[str]` `[L146-L148]` — IDs de los nodos adyacentes (sucesores).
  - `def puntos_pesca(self) -> List[Nodo]` `[L154-L155]`
  - `def centros_frio(self) -> List[Nodo]` `[L157-L158]`
  - `def centros_acopio(self) -> List[Nodo]` `[L160-L161]`
  - `def mercados(self) -> List[Nodo]` `[L163-L164]`
  - `def candidatos_frio(self) -> List[Nodo]` `[L166-L168]` — Nodos que podrían albergar un centro de frío.
  - `def produccion_total_kg(self) -> float` `[L170-L172]` — Suma de producción diaria de todos los puntos de pesca.
  - `def matriz_adyacencia(self, criterio: str = 'peso') -> Dict[str, Dict[str, float]]` `[L178-L209]` — Construye la matriz de adyacencia como diccionario de diccionarios.
  - `def to_networkx(self)` `[L215-L231]` — Convierte el grafo a un objeto networkx.DiGraph.
  - `def resumen(self) -> str` `[L237-L252]` — Resumen textual del grafo.
  - `def __repr__(self) -> str` `[L254-L255]`
  - `def __contains__(self, id_nodo: str) -> bool` `[L257-L258]`
  - `def __len__(self) -> int` `[L260-L261]`

### `src/models/nodo.py` (`137` líneas) — nodo.py — Modelo de datos para los nodos del grafo logístico.
- `class Nodo` `[L22-L136]` — Representa un nodo dentro del grafo de la cadena pesquera.
  - `def __post_init__(self)` `[L70-L75]`
  - `def coordenadas(self) -> tuple` `[L78-L80]` — Devuelve (latitud, longitud).
  - `def tipo_descripcion(self) -> str` `[L83-L85]` — Descripción legible del tipo de nodo.
  - `def es_candidato_frio(self) -> bool` `[L88-L94]` — Indica si el nodo podría albergar un centro de frío.
  - `def es_origen(self) -> bool` `[L97-L99]` — Indica si es un nodo de producción (origen de flujo).
  - `def es_destino(self) -> bool` `[L102-L104]` — Indica si es un nodo de mercado (destino de flujo).
  - `def to_dict(self) -> Dict[str, Any]` `[L106-L122]` — Convierte el nodo a diccionario serializable.
  - `def __repr__(self) -> str` `[L124-L128]`
  - `def __hash__(self) -> int` `[L130-L131]`
  - `def __eq__(self, other) -> bool` `[L133-L136]`

### `src/optimization/cold_chain.py` (`221` líneas) — cold_chain.py — Simulador de cadena de frío.
- `class EstadoProducto` `[L28-L38]` — Estado del pescado en un punto de la ruta.
- `class ResultadoSimulacion` `[L42-L74]` — Resultado completo de la simulación de una ruta.
  - `def resumen(self) -> str` `[L57-L74]`
- `class SimuladorCadenaFrio` `[L77-L220]` — Simula el recorrido de un lote de pescado a lo largo de una ruta
  - `def __init__(self, grafo: GrafoLogistico, temp_ambiente: float = TEMP_AMBIENTE_LLANOS_C, tiempo_limite_h: float = 4.0)` `[L83-L88]`
  - `def simular_ruta(self, ruta: List[str], kg_pescado: float) -> ResultadoSimulacion` `[L90-L208]` — Simula el transporte de pescado a lo largo de una ruta.
  - `def simular_todas_rutas(self, rutas: Dict[str, List[str]], kg_por_punto: Dict[str, float]) -> List[ResultadoSimulacion]` `[L210-L220]` — Simula múltiples rutas y devuelve todos los resultados.

### `src/optimization/eca_solutions.py` (`785` líneas) — eca_solutions.py — Soluciones Algorítmicas y de Estructuras de Datos para la ECA
- **Constantes:** `NODOS_PISCICULTURA_VEDA (L42)`
- `def construir_grafo_veda_bitemporal(grafo_pesca: GrafoLogistico) -> Tuple[GrafoLogistico, Dict[str, Any]]` `[L82-L238]` — Construye el grafo del Régimen 2 (Época de Veda Abril–Junio, `G_veda`) a partir
- `def evaluar_inocuidad_histamina_red(grafo: GrafoLogistico, centro_frio_id: str = 'F02', tiempo_limite_h: float = TIEMPO_MAX_SIN_FRIO_H) -> Dict[str, Any]` `[L246-L294]` — Ejecuta `dijkstra_con_cota_inocuidad` desde cada punto de pesca hacia `centro_frio_id`
- `class BalanceCargaHielo` `[L303-L316]` — Resultado del dimensionamiento 1:1 de hielo y capacidad por punto de pesca.
- `def calcular_dimensionamiento_hielo_red(grafo: GrafoLogistico, centro_frio_id: str = 'F02', proporcion_hielo: float = RELACION_HIELO_PESCADO) -> Dict[str, Any]` `[L319-L386]` — Calcula para las 7 asociaciones el requerimiento de hielo en proporción 1:1
- `def evaluar_flp_hielo_muelles_vs_central(grafo: GrafoLogistico) -> Dict[str, Any]` `[L394-L424]` — Evalúa matemáticamente la propuesta de la Diapositiva 30 de la ECA:
- `def auditar_proteccion_habitats_y_resguardos(grafo: GrafoLogistico, destino_id: str = 'F02') -> Dict[str, Any]` `[L432-L475]` — Compara para cada origen las rutas sin filtro ambiental (`evitar_restringidos=False`)
- `class NodoEventoDAG` `[L484-L494]` — Vértice de una etapa sanitaria/logística dentro del DAG de trazabilidad.
- `class LoteTrazabilidadDAG` `[L497-L575]` — Grafo Acíclico Dirigido (DAG) implementado desde cero mediante lista de adyacencia
  - `def __init__(self, codigo_lote: str, asociacion: str, especie: str = …)` `[L505-L511]`
  - `def agregar_evento(self, evento: NodoEventoDAG) -> None` `[L513-L517]` — Inserta un vértice de etapa sanitaria en O(1).
  - `def conectar_etapas(self, etapa_origen: str, etapa_destino: str) -> None` `[L519-L525]` — Agrega una transición dirigida entre dos etapas del lote.
  - `def orden_topologico_kahn(self) -> Tuple[bool, List[str]]` `[L527-L548]` — Algoritmo de Kahn implementado desde cero con cola FIFO (`deque`) en O(V + E).
  - `def exposicion_grado_hora(self) -> float` `[L550-L561]` — Calcula la integral discreta térmica Sum(Delta_T * Delta_t) en °C·h.
  - `def to_dict(self) -> Dict[str, Any]` `[L563-L575]`
- `class TablaHashTrazabilidad` `[L578-L599]` — Índice en memoria basado en Tabla Hash O(1) para consulta instantánea de lotes
  - `def __init__(self) -> None` `[L584-L585]`
  - `def registrar_lote(self, lote: LoteTrazabilidadDAG) -> None` `[L587-L589]` — Inserción en tiempo constante O(1).
  - `def consultar_lote(self, codigo_lote: str) -> Optional[LoteTrazabilidadDAG]` `[L591-L593]` — Búsqueda en tiempo constante O(1) por código de lote.
  - `def codigos(self) -> List[str]` `[L595-L596]`
  - `def __len__(self) -> int` `[L598-L599]`
- `def construir_trazabilidad_lotes_red(grafo: GrafoLogistico, destino_final: str = 'V_PG1') -> Tuple[TablaHashTrazabilidad, Dict[str, Any]]` `[L602-L681]` — Construye y registra en una `TablaHashTrazabilidad` los DAGs de trazabilidad
- `def ejecutar_suite_eca(grafo: GrafoLogistico) -> Dict[str, Any]` `[L689-L705]` — Ejecuta los 6 módulos algorítmicos de la ECA y devuelve el diccionario consolidado.
- `def formatear_reporte_eca(datos_eca: Dict[str, Any]) -> str` `[L708-L785]` — Genera el reporte de consola para `main.py` con los 6 resultados de la ECA.

### `src/optimization/facility_location.py` (`265` líneas) — facility_location.py — Problema de Localización de Instalaciones (FLP).
- `class ResultadoLocalizacion` `[L29-L57]` — Almacena y presenta los resultados de la optimización.
  - `def __init__(self)` `[L32-L38]`
  - `def resumen(self) -> str` `[L40-L57]`
- `def resolver_localizacion_greedy(grafo: GrafoLogistico, tiempo_max_h: float = TIEMPO_MAX_SIN_FRIO_H) -> ResultadoLocalizacion` `[L64-L130]` — Heurística greedy para localización de centros de frío.
- `def resolver_localizacion_pulp(grafo: GrafoLogistico, tiempo_max_h: float = TIEMPO_MAX_SIN_FRIO_H, max_centros: Optional[int] = None) -> ResultadoLocalizacion` `[L137-L238]` — Resuelve el FLP con programación lineal entera usando PuLP.
- `def resolver_localizacion(grafo: GrafoLogistico, metodo: str = 'greedy', tiempo_max_h: float = TIEMPO_MAX_SIN_FRIO_H, max_centros: Optional[int] = None) -> ResultadoLocalizacion` `[L245-L264]` — Resuelve el problema de localización de centros de frío.

### `src/optimization/itinerarios.py` (`213` líneas) — itinerarios.py — Itinerarios completos por punto de pesca.
- **Constantes:** `INF (L22)`
- `class Tramo` `[L26-L34]` — Un tramo (arista) del itinerario.
- `class Itinerario` `[L38-L68]` — Itinerario completo de un punto de pesca hasta el destino.
  - `def resumen(self) -> str` `[L53-L68]` — Texto legible de una línea con el recorrido y sus métricas.
- `def _unir(*segmentos: List[str]) -> List[str]` `[L71-L76]` — Concatena caminos que comparten nodo de empalme.
- `def _camino(grafo: GrafoLogistico, a: str, b: str, evitar: bool) -> Tuple[float, List[str]]` `[L79-L84]`
- `def _mejor_ruta(grafo: GrafoLogistico, origen: str, destino: str, acopios: List[str], centros: List[str]) -> Tuple[List[str], Optional[str], Optional[str]]` `[L87-L127]` — Elige la combinación (A, F) de menor tiempo total evitando H.
- `def _restringidos_en(grafo: GrafoLogistico, ruta: List[str]) -> List[str]` `[L130-L133]`
- `def _evitados(grafo: GrafoLogistico, origen: str, destino: str, acopio: Optional[str], centro: Optional[str], ruta: List[str]) -> List[str]` `[L136-L153]` — Nodos H que aparecerían en el mismo recorrido sin la restricción.
- `def calcular_itinerarios(grafo: GrafoLogistico, destino_id: str, centros_frio: Optional[List[str]] = None) -> List[Itinerario]` `[L156-L213]` — Calcula un itinerario por cada punto de pesca hacia ``destino_id``.

### `src/optimization/scenario_evaluator.py` (`257` líneas) — scenario_evaluator.py — Evaluador y comparador de escenarios logísticos.
- `class MetricasEscenario` `[L24-L67]` — Métricas cuantitativas para un escenario logístico.
  - `def resumen(self) -> str` `[L44-L67]`
- `class EvaluadorEscenarios` `[L70-L256]` — Evalúa y compara múltiples escenarios logísticos.
  - `def __init__(self, grafo: GrafoLogistico, temp_ambiente: float = 30.0, tiempo_limite_h: float = TIEMPO_MAX_SIN_FRIO_H)` `[L81-L87]`
  - `def evaluar_escenario(self, nombre: str, centros_activos: List[str], destino_final: str = 'V_Bogota') -> MetricasEscenario` `[L89-L207]` — Evalúa un escenario específico con los centros dados.
  - `def comparar_escenarios(self, escenarios: List[Dict], destino_final: str = 'V_Bogota') -> List[MetricasEscenario]` `[L209-L232]` — Compara múltiples escenarios.
  - `def tabla_comparativa(metricas_lista: List[MetricasEscenario]) -> str` `[L235-L256]` — Genera una tabla comparativa de escenarios.

### `src/utils/constants.py` (`124` líneas) — constants.py — Constantes globales del proyecto.
- **Constantes:** `COORDENADAS (L12), TEMP_OBJETIVO_C (L24), TEMP_AMBIENTE_LLANOS_C (L27), TIEMPO_MAX_SIN_FRIO_H (L30), VIDA_UTIL_HORAS (L33), RELACION_HIELO_PESCADO (L43), TASA_DETERIORO_BASE (L46), COSTO_TRANSPORTE_KM (L52), COSTO_HIELO_KG (L53), COSTO_PERDIDA_KG (L54), PRECIO_VENTA_KG (L55), COSTO_FIJO_CENTRO_FRIO (L56) (+12 más)`
- `class TipoNodo` `[L70-L96]` — Códigos de categoría para los nodos del grafo.
  - `def descripcion(cls, codigo: str) -> str` `[L91-L92]`
  - `def es_valido(cls, codigo: str) -> bool` `[L95-L96]`

### `src/utils/data_loader.py` (`118` líneas) — data_loader.py — Carga y exportación de datos del proyecto.
- **Constantes:** `DATA_DIR (L15), CSV_DIR (L16), SHP_DIR (L17), OUTPUT_DIR (L18)`
- `def cargar_nodos_csv(nombre_archivo: str) -> List[Dict[str, Any]]` `[L21-L40]` — Lee un CSV de nodos y devuelve una lista de diccionarios.
- `def cargar_aristas_csv(nombre_archivo: str = 'aristas.csv') -> List[Dict[str, Any]]` `[L43-L50]` — Lee un CSV de aristas y devuelve una lista de diccionarios.
- `def guardar_resultados_csv(datos: List[Dict[str, Any]], nombre_archivo: str) -> str` `[L53-L68]` — Escribe una lista de diccionarios como CSV en data/output/.
- `def cargar_shapefile_rios() -> Any` `[L71-L89]` — Carga el shapefile de ríos como GeoDataFrame.
- `def listar_archivos_datos() -> Dict[str, List[str]]` `[L92-L99]` — Lista todos los archivos disponibles en data/.
- `def _convertir_valor(valor: str) -> Any` `[L104-L117]` — Intenta convertir un string a int, float o lo deja como str.

### `src/utils/geo_utils.py` (`117` líneas) — geo_utils.py — Funciones geográficas y cálculos de distancia.
- `def haversine(coord1: Tuple[float, float], coord2: Tuple[float, float]) -> float` `[L18-L43]` — Calcula la distancia en km entre dos puntos geográficos
- `def calcular_tiempo_viaje(distancia_km: float, velocidad_kmh: float = VELOCIDAD_PROMEDIO_KMH, factor_estado_via: float = 1.0) -> float` `[L46-L69]` — Estima el tiempo de viaje en horas.
- `def calcular_deterioro(tiempo_sin_frio_h: float, temp_ambiente_c: float = 30.0) -> float` `[L72-L96]` — Estima el porcentaje de deterioro del pescado según el tiempo
- `def dms_a_decimal(grados: float, minutos: float, segundos: float, direccion: str = 'N') -> float` `[L99-L116]` — Convierte coordenadas de grados/minutos/segundos a decimal.

### `src/visualization/felt_exporter.py` (`353` líneas) — felt_exporter.py — Exportador de datos geográficos para Felt.com.
- `def exportar_nodos_geojson(grafo: GrafoLogistico, nombre_archivo: str = 'nodos_red.geojson') -> str` `[L31-L118]` — Exporta todos los nodos del grafo como GeoJSON FeatureCollection
- `def exportar_ruta_geojson(grafo: GrafoLogistico, ruta: List[str], nombre_archivo: str = 'ruta_dijkstra.geojson', nombre_ruta: str = 'Ruta Óptima Dijkstra') -> str` `[L125-L257]` — Exporta una ruta (lista de IDs de nodos) como GeoJSON LineString
- `def empaquetar_rios_zip(nombre_archivo: str = 'rios.zip') -> str` `[L264-L304]` — Comprime todos los archivos del shapefile de ríos en un ZIP
- `def exportar_para_felt(grafo: GrafoLogistico, ruta_optima: Optional[List[str]] = None, nombre_ruta: str = 'Ruta Óptima Dijkstra') -> Dict[str, str]` `[L311-L352]` — Ejecuta las tres exportaciones para Felt.com en un solo paso.

### `src/visualization/folium_map.py` (`842` líneas) — folium_map.py — Mapa interactivo HTML con Folium.
- **Constantes:** `COLORES_FELT (L38), ICONOS_FOLIUM (L48)`
- `def generar_mapa_interactivo(grafo: GrafoLogistico, ruta_optima: Optional[List[str]] = None, nombre_ruta: str = 'Ruta Óptima Dijkstra', nombre_archivo: str = 'mapa_interactivo.html', abrir_navegador: bool = False, geometrias_reales: Optional[Dict[str, list]] = None, itinerarios: Optional[list] = None) -> str` `[L63-L406]` — Genera un mapa HTML interactivo con Folium.
- `def _agregar_capa_rios(mapa: folium.Map) -> None` `[L426-L452]` — Agrega la capa de ríos reales (siempre visible) con tooltip del nombre.
- `def _tiene_propiedad(datos: dict, clave: str) -> bool` `[L455-L460]` — Indica si todas las features del GeoJSON tienen la propiedad dada.
- `def _locs_tramo(grafo: GrafoLogistico, geo_cache: dict, o: str, d: str) -> list` `[L463-L471]` — Coordenadas [[lat, lon], ...] de un tramo (geometría real o recta).
- `def _paradas(it) -> list` `[L474-L479]` — Lista ordenada de IDs de parada de un itinerario.
- `def _resumen_acopios(itinerarios: list) -> Dict[str, dict]` `[L482-L491]` — Por acopio: puntos de pesca que recibe y kg/día totales.
- `def _tramo_popup(grafo: GrafoLogistico, t) -> str` `[L494-L505]` — HTML del popup de un tramo.
- `def _icono_numerado(num: int, color: str) -> folium.DivIcon` `[L508-L516]` — Marca circular numerada para una parada.
- `def _agregar_itinerarios(mapa, grafo, itinerarios, geo_cache) -> None` `[L519-L564]` — Una capa por itinerario + capa resumen 'Flujo de acopio'.
- `def _agregar_nodos_especiales(mapa, grafo, itinerarios) -> None` `[L567-L617]` — Capas de muelles (M), zonas de deterioro (D) y hábitats (H).
- `def _agregar_leyenda(mapa: folium.Map) -> None` `[L620-L655]` — Leyenda: tipos de nodo, tipos de vía y círculos D/H.
- `def _agregar_panel_itinerarios(mapa, grafo, itinerarios) -> None` `[L658-L680]` — Panel lateral con la tabla resumen de itinerarios.
- `def _agregar_puntos_campo(mapa: folium.Map) -> None` `[L683-L841]` — Carga los 49 puntos de campo desde data/geojson/puntos_campo.geojson,

### `src/visualization/graph_plotter.py` (`184` líneas) — graph_plotter.py — Visualización de grafos con matplotlib.
- **Constantes:** `COLORES_NODO (L20), SIMBOLOS_NODO (L30)`
- `def graficar_grafo(grafo: GrafoLogistico, titulo: str = …, ruta_destacada: Optional[List[str]] = None, guardar_como: Optional[str] = None, mostrar: bool = True, figsize: tuple = (14, 10)) -> None` `[L41-L167]` — Dibuja el grafo completo con posiciones geográficas.
- `def graficar_ruta(grafo: GrafoLogistico, ruta: List[str], titulo: str = 'Ruta Óptima', guardar_como: Optional[str] = None) -> None` `[L170-L183]` — Atajo para graficar el grafo con una ruta destacada.

### `src/visualization/graph_slides.py` (`5647` líneas) — graph_slides.py — Experiencia Interactiva de Visualización Logística y Presentación Magistral
- **Constantes:** `GEOJSON_DIR (L43)`
- `def _cargar_puntos_campo_reales() -> List[Dict[str, Any]]` `[L46-L85]` — Carga los 49 puntos de campo reales desde `data/geojson/puntos_campo.geojson`
- `def _calcular_bfs_saltos(grafo: GrafoLogistico, destino_frio: str = 'F02') -> List[Dict[str, Any]]` `[L88-L123]` — Implementación propia de Búsqueda en Amplitud (BFS) con cola FIFO (collections.deque)
- `def _calcular_dfs_rutas_alternativas(grafo: GrafoLogistico, destino_frio: str = 'F02', max_profundidad: int = 7) -> List[Dict[str, Any]]` `[L126-L176]` — Implementación propia de Búsqueda en Profundidad (DFS) con retroceso (backtracking)
- `def construir_datos_slides(grafo: GrafoLogistico, geo_cache: Optional[Dict[str, list]] = None, itinerarios: Optional[list] = None) -> Dict[str, Any]` `[L179-L533]` — Extrae y serializa todos los datos reales del repositorio (nodos, aristas, geometrías OSRM,
- `def _construir_bloque_ui_interactiva(json_payload: str, modo_autonomo: bool = True) -> str` `[L536-L5580]` — Construye el sistema completo de 8 diapositivas interactivas combinando:
- `def generar_html_slides(grafo: GrafoLogistico, geo_cache: Optional[Dict[str, list]] = None, itinerarios: Optional[list] = None) -> str` `[L5583-L5593]` — Devuelve el bloque HTML + CSS + JS para inyectar sobre `folium_map.py`.
- `def generar_presentacion_html_autonoma(grafo: GrafoLogistico, geo_cache: Optional[Dict[str, list]] = None, itinerarios: Optional[list] = None, ruta_salida: Optional[str] = None) -> str` `[L5596-L5647]` — Genera el archivo HTML autónomo y 100% offline en:

### `src/visualization/map_renderer.py` (`96` líneas) — map_renderer.py — Renderizado de mapas geográficos.
- `def renderizar_mapa(grafo: GrafoLogistico, ruta: Optional[List[str]] = None, titulo: str = …, mostrar_rios: bool = True, guardar_como: Optional[str] = None, mostrar: bool = True) -> None` `[L19-L95]` — Renderiza un mapa geográfico con los nodos y rutas del grafo.

### `src/visualization/river_network.py` (`578` líneas) — river_network.py — Red fluvial real a partir de data/shapefiles/rios.shp.
- **Constantes:** `BBOX_DEFECTO (L19), DISTANCIA_MAX_ENLACE_KM (L20)`
- `def cargar_rios(bbox: Tuple[float, float, float, float] = BBOX_DEFECTO)` `[L28-L59]` — Carga el shapefile de ríos en EPSG:4326, recortado al bbox
- `class RedFluvial` `[L62-L248]` — Grafo no dirigido de la red fluvial (los botes navegan en ambos sentidos).
  - `def __init__(self, bbox: Tuple[float, float, float, float] = BBOX_DEFECTO) -> None` `[L65-L82]`
  - `def _conectar_confluencias_afluentes(self) -> None` `[L84-L146]` — Une micro-discontinuidades de digitalización entre afluentes secundarios
  - `def _ij(self, lon: float, lat: float) -> Tuple[int, int]` `[L148-L149]`
  - `def nodo_mas_cercano(self, lat: float, lon: float) -> Tuple[Optional[Vertice], float]` `[L151-L172]` — Vértice fluvial más cercano: (clave_vertice (lon, lat), distancia_km).
  - `def enlace_al_cauce(self, lat: float, lon: float) -> Tuple[Optional[List[float]], Optional[Vertice], float]` `[L174-L199]` — Proyecta el punto sobre el tramo de río más cercano (no solo el vértice).
  - `def _dijkstra(self, origen: Vertice, destino: Vertice) -> Optional[Tuple[List[Vertice], float]]` `[L201-L223]`
  - `def ruta(self, lat1: float, lon1: float, lat2: float, lon2: float) -> Optional[Tuple[List[List[float]], float]]` `[L225-L248]` — Ruta por el río entre dos puntos: ([[lon, lat], ...], km).
- `def obtener_red_fluvial() -> RedFluvial` `[L251-L256]` — Singleton de la red fluvial.
- `def obtener_capa_rios_geojson(bbox: Optional[Tuple[float, float, float, float]] = None, tolerancia: float = 0.0005) -> Optional[dict]` `[L259-L283]` — FeatureCollection simplificada de los ríos para el mapa; None si falla.
- `def estimar_cota_cauce_msnm(lat: float, lon: float) -> float` `[L293-L305]` — Estima la cota hidrométrica del cauce fluvial (m s.n.m.) en la cuenca de los Llanos
- `def calcular_corredor_fluvial_puntos_campo() -> Dict[str, object]` `[L308-L578]` — Conecta los 49 puntos reales de campo (`data/geojson/puntos_campo.geojson`)

### `src/visualization/route_geometry.py` (`260` líneas) — route_geometry.py — Obtención de geometrías reales de carreteras.
- `def obtener_geometria_carretera(lat1: float, lon1: float, lat2: float, lon2: float) -> Optional[List[List[float]]]` `[L27-L70]` — Consulta OSRM para obtener la geometría real de la carretera
- `def obtener_geometrias_grafo(grafo: GrafoLogistico, usar_cache: bool = True) -> Dict[str, List[List[float]]]` `[L73-L179]` — Obtiene las geometrías reales de TODAS las aristas del grafo.
- `def obtener_geometria_ruta(grafo: GrafoLogistico, ruta: List[str], cache: Dict[str, List[List[float]]]) -> List[List[float]]` `[L182-L223]` — Construye la geometría completa de una ruta concatenando
- `def _geometria_valida(coords: List[List[float]]) -> bool` `[L226-L230]` — True si la geometría tiene al menos 3 puntos distintos (no es una recta).
- `def _anclar_extremos(coords: List[List[float]], n_o, n_d) -> List[List[float]]` `[L233-L247]` — Une la geometría real a las coordenadas exactas de los nodos.
- `def _ruta_fluvial_real(lat1: float, lon1: float, lat2: float, lon2: float) -> Optional[List[List[float]]]` `[L250-L260]` — Ruta sobre el cauce real (RedFluvial); None si no hay geopandas o conexión.

### `scripts/generar_repo_map.py` (`414` líneas) — Generador automático del Mapa Sintáctico del Proyecto (AST Repo-Map).
- **Constantes:** `ROOT_DIR (L28), OUTPUT_PATH (L29), SOURCE_DIRS (L31), TEST_DIR (L32), CSV_DIR (L33), HEAVY_DIRS (L34)`
- `def _primera_linea_doc(nodo: ast.AST) -> str` `[L41-L51]` — Extrae la primera línea útil del docstring de un nodo AST.
- `def _formatear_firma(nodo: ast.FunctionDef | ast.AsyncFunctionDef) -> str` `[L54-L100]` — Construye la firma compacta de una función o método con type hints.
- `def _extraer_constantes(arbol: ast.Module) -> List[str]` `[L103-L115]` — Extrae nombres de constantes top-level en MAYÚSCULAS.
- `def _analizar_archivo_python(ruta: Path) -> Tuple[int, List[str]]` `[L118-L174]` — Parsea un archivo Python y devuelve (total_lineas, lineas_markdown).
- `def _analizar_tests() -> Tuple[int, List[str]]` `[L177-L213]` — Genera un índice compacto de la suite de pruebas.
- `def _analizar_csvs() -> List[str]` `[L216-L235]` — Resume los esquemas (columnas y número de filas) de `data/csv/*.csv`.
- `def _formato_tamano(n_bytes: int) -> str` `[L238-L242]` — Formatea bytes a KB o MB legibles.
- `def _analizar_activos_pesados() -> List[str]` `[L245-L281]` — Lista archivos pesados/generados para prevenir lecturas accidentales.
- `def _archivos_monitoreados() -> List[Path]` `[L284-L298]` — Devuelve la lista de archivos fuente que invalidan el mapa si cambian.
- `def esta_desactualizado() -> bool` `[L301-L312]` — Retorna True si `PROJECT_MAP.md` no existe o algún archivo fuente es más reciente.
- `def generar_mapa() -> Tuple[int, int]` `[L315-L383]` — Genera `PROJECT_MAP.md` y devuelve (lineas_codigo_indexadas, lineas_mapa).
- `def main(argv: Optional[List[str]] = None) -> int` `[L386-L410]` — Punto de entrada CLI y soporte para hooks de Antigravity.

## 2. Esquema de Datos CSV (`data/csv/`)

| Archivo | Filas | Columnas |
| :--- | ---: | :--- |
| `data/csv/aristas.csv` | 41 | `origen`, `destino`, `distancia_km`, `tiempo_h`, `costo_cop`, `riesgo_termico`, `estado_via`, `tipo_via`, `capacidad_kg`, `prob_retraso`, `riesgo_accidente`, `riesgo_derrumbe`, `restriccion_peso_ton`, `peajes`, `costo_peajes_cop`, `horario_restriccion`, `flujo_vehicular`, `tiempo_espera_h`, `confiabilidad_via` |
| `data/csv/nodos_centros.csv` | 13 | `id`, `nombre`, `tipo`, `latitud`, `longitud`, `capacidad_frio_kg`, `costo_fijo`, `tiene_energia`, `tiene_agua`, `tiene_muelle`, `restriccion_ambiental`, `observacion` |
| `data/csv/nodos_destinos.csv` | 5 | `id`, `nombre`, `tipo`, `latitud`, `longitud`, `demanda_kg_dia`, `observacion` |
| `data/csv/nodos_pesca.csv` | 8 | `id`, `nombre`, `tipo`, `latitud`, `longitud`, `produccion_kg_dia`, `rio_asociado`, `num_pescadores`, `observacion` |

## 3. Suite de Pruebas (`tests/`)

- `tests/test_bellman_ford.py` (`131` L): test_bellman_ford_camino_basico (L36), test_bellman_ford_sin_ciclo_negativo (L46), test_bellman_ford_consistencia_dijkstra (L54), test_reconstruir_camino_bf (L71), test_bellman_ford_nodo_inexistente (L82), test_bellman_ford_evitar_restringidos (L93)
- `tests/test_bfs_dfs.py` (`71` L): test_bfs_recorrido_basico (L34), test_bfs_camino_minimo_saltos (L42), test_bfs_nodo_mas_cercano (L48), test_dfs_recorrido_basico (L55), test_dfs_todos_los_caminos (L62), test_dfs_con_atajo_restringido (L68)
- `tests/test_cold_chain.py` (`172` L): test_simulacion_con_frio (L34), test_simulacion_sin_frio (L49), test_simulacion_deterioro_mayor_sin_frio (L62), test_simulacion_ruta_corta (L76), test_simulacion_resumen (L90), test_efecto_zona_deterioro_y_muelle (L101), test_itinerario_pasa_por_acopio (L133)
- `tests/test_dijkstra.py` (`136` L): test_dijkstra_camino_existe (L35), test_dijkstra_camino_optimo (L46), test_dijkstra_sin_camino (L58), test_dijkstra_completo (L70), test_dijkstra_nodo_inexistente (L80), test_dijkstra_evitar_restringidos (L91)
- `tests/test_eca_solutions.py` (`95` L): test_grafo_bitemporal_veda (L18), test_dijkstra_con_cota_inocuidad_histamina (L29), test_evaluacion_inocuidad_todas_asociaciones (L47), test_dimensionamiento_hielo_1a1 (L56), test_auditoria_habitats_y_resguardos (L65), test_dag_y_tabla_hash_trazabilidad (L74)
- `tests/test_facility_location.py` (`88` L): test_localizacion_greedy (L54), test_localizacion_cobertura_total (L65), test_localizacion_sin_candidatos (L73)
- `tests/test_floyd_warshall.py` (`97` L): test_floyd_warshall_diagonal_cero (L33), test_floyd_warshall_camino_intermedio (L43), test_reconstruir_camino_fw (L58), test_reconstruir_camino_sin_ruta (L69), test_matriz_a_tabla (L79)
- `tests/test_grafo.py` (`124` L): test_crear_nodo (L14), test_crear_arista (L32), test_grafo_agregar_nodos (L50), test_grafo_agregar_aristas (L64), test_grafo_arista_auto (L81), test_grafo_resumen (L93), test_nodo_tipo_invalido (L104)
- `tests/test_repo_map.py` (`41` L): test_generacion_project_map (L13), test_modo_hook_retorna_json_valido (L29)
- `tests/test_river_network.py` (`61` L): test_carga_no_vacia (L14), test_ruta_mismo_rio (L20), test_punto_lejano_none (L39), test_capa_geojson (L43), test_corredor_fluvial_49_puntos_campo (L48)

## 4. Activos Pesados y Salidas Generadas (NO leer completos)

| Archivo | Tamaño | Nota |
| :--- | ---: | :--- |
| `data/geojson/puntos_campo.geojson` | 16.7 KB | GeoJSON (49 features) — consultar vía script |
| `data/shapefiles/rios.cst` | 0.0 KB | Archivo binario/generado — no leer completo |
| `data/shapefiles/rios.dbf` | 1.11 MB | Geometría SIG fluvial — procesar vía `route_geometry.py` |
| `data/shapefiles/rios.prj` | 0.3 KB | Geometría SIG fluvial — procesar vía `route_geometry.py` |
| `data/shapefiles/rios.shp` | 3.62 MB | Geometría SIG fluvial — procesar vía `route_geometry.py` |
| `data/shapefiles/rios.shx` | 33.2 KB | Geometría SIG fluvial — procesar vía `route_geometry.py` |
| `data/output/aristas_resultado.csv` | 6.6 KB | Archivo binario/generado — no leer completo |
| `data/output/grafo_logistico.png` | 191.0 KB | Archivo binario/generado — no leer completo |
| `data/output/mapa_interactivo.html` | 3.56 MB | HTML generado por pipeline — editar en `src/visualization/` |
| `data/output/nodos_red.geojson` | 13.8 KB | GeoJSON (25 features) — consultar vía script |
| `data/output/nodos_resultado.csv` | 2.4 KB | Archivo binario/generado — no leer completo |
| `data/output/presentacion_red_logistica.html` | 787.1 KB | HTML generado por pipeline — editar en `src/visualization/` |
| `data/output/rios.zip` | 3.15 MB | Geometría SIG fluvial — procesar vía `route_geometry.py` |
| `data/output/ruta_dijkstra.geojson` | 4.2 KB | GeoJSON (5 features) — consultar vía script |
| `data/output/rutas_cache.json` | 1.14 MB | Caché OSRM/ríos (48 rutas) — NO borrar ni leer entero |
