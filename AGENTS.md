# AGENTS.md — Reglas del proyecto y sistema de orquestación multiagente

Este archivo lo carga Antigravity automáticamente para TODO agente que trabaje en este
repositorio (coordinador y workers). Lee la sección que te corresponde.

---

## 1. Proyecto (contexto mínimo para cualquier agente)

**Optimización de centros de refrigeración para pesca artesanal — Puerto Gaitán, Meta (Colombia).**
Curso Estructuras de Datos (603301). La cadena pesquera se modela como **grafo dirigido ponderado**
con algoritmos **implementados desde cero** (no NetworkX para cálculo).

```
PROJECT_MAP.md                  Mapa AST automático (~270 líneas = 97% ahorro de contexto) — LEER PRIMERO
scripts/generar_repo_map.py     Generador AST del mapa (auto-ejecutado por .agents/hooks.json)
main.py                         Pipeline de 10 pasos (punto de entrada)
src/models/                     nodo.py, arista.py (19 campos, peso multicriterio 6 factores), grafo_logistico.py (lista de adyacencia)
src/algorithms/                 dijkstra.py (heap), floyd_warshall.py, bellman_ford.py
src/optimization/               facility_location.py (greedy + PuLP opcional), cold_chain.py, scenario_evaluator.py
src/visualization/              folium_map.py (mapa HTML), route_geometry.py (OSRM + ríos), felt_exporter.py, graph_plotter.py, graph_slides.py
src/utils/                      constants.py, geo_utils.py, data_loader.py
data/csv/                       nodos_pesca.csv (P), nodos_centros.csv (F,A,M,D,H), nodos_destinos.csv (V), aristas.csv
data/shapefiles/rios.*          Red fluvial real
data/geojson/puntos_campo.geojson  49 puntos de campo (A,D,H,M,V)
data/output/rutas_cache.json    Caché de geometrías OSRM — NO borrar
tests/                          pytest (debe quedar 100 % verde)
```

**Tipos de nodo:** P pesca · A acopio · F frío · M muelle (transbordo fluvial→terrestre) ·
D zona de deterioro (penaliza pérdida) · H hábitat protegido (restricción ambiental, se evita) · V venta.
**Tipos de vía:** `fluvial`, `acceso_local`, `terrestre`.
**Flujo real:** `P ─río→ M ─acceso→ A ─carretera→ F ─carretera→ V`.

### Protocolo Automático de Contexto Eficiente (AST Repo-Map — OBLIGATORIO)
Para reducir el consumo de tokens (~97% menos) y acelerar cada respuesta **sin que el usuario deba pedirlo**:
1. **Mapa primero:** Antes de explorar `src/`, `main.py` o `tests/`, lee `PROJECT_MAP.md` (índice AST con todas las clases, firmas con tipos, rangos `[Lstart-Lend]` y esquemas CSV).
2. **Lectura quirúrgica:** Usa `read_file` con `StartLine` y `EndLine` exactos según `PROJECT_MAP.md`. Nunca cargues archivos completos (especialmente `graph_slides.py`) salvo que sea estrictamente necesario.
3. **Prohibido abrir archivos pesados completos:** Nunca leas enteros `data/output/*.html`, `data/output/rutas_cache.json`, `data/geojson/*.geojson` ni `data/shapefiles/*`; inspecciónalos vía comandos/scripts o `Select-String`.
4. **Auto-actualización:** `.agents/hooks.json` ejecuta `scripts/generar_repo_map.py --hook` automáticamente al iniciar sesión (`SessionStart`) y tras editar/escribir archivos (`PostToolUse`). Si alteras código desde terminal, corre `python scripts/generar_repo_map.py --if-stale`.

### Convenciones obligatorias
- Todo texto visible, docstrings y comentarios **en español**. Type hints y docstrings en funciones públicas.
- Algoritmos de grafos **propios**; prohibido reemplazarlos por librerías.
- Solo servicios **gratuitos/locales** (Folium, OSRM público). Nada de pago (Felt.com rechazado).
- Datos con base **real** (asociaciones, tiendas y coordenadas verificables). No inventar cifras sin marcarlas como estimación.
- Shell: **PowerShell** → separar comandos con `;` (no `&&`).
- `main.py` fija `OPENBLAS_NUM_THREADS=1` (Python 3.14). El exit code 1 de `python main.py` es un falso positivo por un
  `UserWarning` de Folium en stderr: usar `python main.py 2>$null` y verificar el mensaje “✅ Ejecución completada exitosamente.”
- Verificación mínima antes de reportar “hecho”: `python -m pytest tests/ -q` verde y `main.py` completo.
- Los workers **no hacen commits** ni push; el coordinador integra y hace commit.

---

## 2. Si eres un WORKER (agente secundario)

1. Modifica **solo** los archivos que tu brief te asigna. Si necesitas cambiar otro, pídelo en el board al dueño o al coordinador.
2. No inventes resultados: reporta salidas reales de comandos (tests, ejecuciones).
3. Informe final **breve y estructurado**: archivos cambiados, interfaz pública nueva, salida de tests, problemas abiertos.
4. Menciona (`@nombre`) solo al siguiente agente que debe actuar; `@coordinator` solo para entregable final o bloqueo.

---

## 3. Si eres el COORDINADOR (director técnico)

### 3.1 Capacidades reales verificadas del entorno (2026-11-15)
| Mecanismo | Selección de modelo | Uso |
|---|---|---|
| `swarm add` (workers con board compartido) | **Cualquier modelo listado** por `swarm models` | Trabajo paralelo con dueño por archivo |
| `invoke_subagent` | Solo `inherit`, `flash_lite`, `flash`, `pro` (familia Gemini) | Investigación/lectura aislada |
| Subagentes `research` (solo lectura) y `browser` | según `Model` | Exploración, web |

### 3.2 Niveles de modelo
| Nivel | Modelos (IDs reales) | Para qué |
|---|---|---|
| Económico | `gemini-3.8-flash-low/medium`, `gpt-oss-120b-medium`, subagente `flash`/`flash_lite` | Inventarios, lectura, verificación mecánica (tests, grep), docs, informes |
| Intermedio | `claude-sonnet-5-5-medium/high` | Implementación de módulos con interfaz definida, refactors delimitados, bugs medios, tests de integración |
| Avanzado | `claude-opus-5-5-*` (coordinador) | Arquitectura, diseño de interfaces y estructuras de datos, decisiones algorítmicas, integración final, revisión de calidad |

> Los modelos Gemini 4 Argon/Hydrogen existen en la lista, pero su capacidad relativa no está verificada: no asignarlos sin probar.

### 3.3 Protocolo
1. Clasificar la tarea (económica / intermedia / avanzada) **antes** de ejecutar.
2. Opus diseña: interfaces públicas, estructuras de datos, reglas del modelo, reparto de archivos.
3. Un archivo = un dueño. Nunca dos workers sobre el mismo archivo.
4. Brief = objetivo + contexto mínimo + archivos permitidos + interfaz exacta + criterios de aceptación.
5. Paralelizar lo independiente; un verificador económico por cada 2–4 autores.
6. Revisar con `git diff`, no releyendo archivos completos; confiar en pruebas automáticas.
7. Pedir autorización al usuario antes de operaciones destructivas (borrar datos, migraciones, reescrituras masivas).
8. No afirmar ahorro de Opus si la subtarea corre en Opus.

### 3.4 Registro de decisiones (ADR breve)
- **ADR-01** Algoritmos propios (Dijkstra/Floyd/Bellman-Ford); NetworkX solo para exportar.
- **ADR-02** Peso multicriterio: `w = 0.25·t + 0.20·c + 0.20·r + 0.10·p + 0.10·(1-conf) + 0.05·retraso`.
- **ADR-03** Visualización gratuita con Folium; geometría vial vía OSRM con caché en `rutas_cache.json`.
- **ADR-04** Nodos M, D, H son vértices reales del grafo (no solo marcadores). Efectos:
  M = transbordo (espera + sin frío) · D = multiplica deterioro del tramo entrante ·
  H = `restriccion_ambiental`; los algoritmos con `evitar_restringidos=True` no lo usan como nodo intermedio.
- **ADR-05** Rutas fluviales trazadas sobre la red real de `rios.shp` (grafo de segmentos + Dijkstra propio).
- **ADR-06** Todo punto de pesca debe pasar por un acopio (A) o muelle (M) antes del centro de frío (salvo P06, que está en el casco urbano junto a F02).
