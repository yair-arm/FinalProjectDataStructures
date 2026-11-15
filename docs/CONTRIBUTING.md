# 🤝 Guía de Contribución

Gracias por tu interés en contribuir al proyecto de **Optimización de Centros de Refrigeración para Pesca Artesanal**.

---

## 🛠️ Configuración del Entorno

### Prerrequisitos

- Python 3.10 o superior
- Git

### Instalación

```bash
# Clonar el repositorio
git clone <url-del-repositorio>
cd Proyecto

# Crear entorno virtual
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # Linux/Mac

# Instalar dependencias
pip install -r requirements.txt
```

---

## 📏 Convenciones de Código

### Estilo

- Seguimos **PEP 8** para todo el código Python.
- Usar **type hints** en todas las funciones y métodos.
- Documentar con **docstrings** estilo NumPy/Google en todas las funciones públicas.

### Ejemplo

```python
def calcular_ruta(grafo: GrafoLogistico,
                  origen: str,
                  destino: str) -> Tuple[float, List[str]]:
    """
    Calcula la ruta óptima entre dos nodos.

    Parameters
    ----------
    grafo : GrafoLogistico
        Grafo dirigido ponderado.
    origen : str
        ID del nodo de partida.
    destino : str
        ID del nodo de llegada.

    Returns
    -------
    tuple (distancia, camino)
        distancia : float — distancia total.
        camino : list[str] — secuencia de IDs.
    """
```

### Nombres

| Elemento | Convención | Ejemplo |
|----------|-----------|---------|
| Variables | `snake_case` | `tiempo_total_h` |
| Funciones | `snake_case` | `calcular_deterioro()` |
| Clases | `PascalCase` | `GrafoLogistico` |
| Constantes | `UPPER_SNAKE_CASE` | `TIEMPO_MAX_SIN_FRIO_H` |
| IDs de nodo | Prefijo tipo + número | `P01`, `F02`, `V_BOG` |

---

## 🧪 Pruebas

### Ejecutar todas las pruebas

```bash
# Con pytest (recomendado)
python -m pytest tests/ -v

# Individualmente
python tests/test_grafo.py
python tests/test_dijkstra.py
python tests/test_bellman_ford.py
python tests/test_floyd_warshall.py
python tests/test_cold_chain.py
python tests/test_facility_location.py
```

### Escribir pruebas nuevas

Sigue el patrón existente en `tests/`:

```python
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.models.nodo import Nodo
# ... más imports

def test_mi_funcionalidad():
    """Descripción clara de lo que se prueba."""
    # Arrange
    grafo = _crear_grafo_prueba()

    # Act
    resultado = mi_funcion(grafo)

    # Assert
    assert resultado.es_valido
    print("  [✓] test_mi_funcionalidad")

if __name__ == "__main__":
    print("\n═══ PRUEBAS DE MI MÓDULO ═══\n")
    test_mi_funcionalidad()
    print("\n  ✅ Todas las pruebas pasaron.\n")
```

---

## 📊 Agregar Datos

### Nuevo punto de pesca

1. Agregar una fila en `data/csv/nodos_pesca.csv`:
   ```csv
   P08,Nombre del Punto,P,4.XXXX,-72.XXXX,produccion_kg_dia,rio,num_pescadores,observacion
   ```

2. Agregar conexiones en `data/csv/aristas.csv`:
   ```csv
   P08,F02,distancia_km,tiempo_h,costo_cop,riesgo_termico,estado_via,tipo_via,capacidad_kg
   ```

### Nuevo centro de frío/acopio

1. Agregar en `data/csv/nodos_centros.csv`:
   ```csv
   F04,Nombre Centro,F,lat,lon,capacidad_frio_kg,costo_fijo,tiene_energia,tiene_agua,tiene_muelle,restriccion_ambiental,observacion
   ```

2. Agregar las aristas correspondientes de conexión.

### Nuevo mercado de destino

1. Agregar en `data/csv/nodos_destinos.csv`:
   ```csv
   V_XXX,Nombre Mercado,V,lat,lon,demanda_kg_dia,observacion
   ```

---

## 🏗️ Estructura de Módulos

| Módulo | Responsabilidad |
|--------|----------------|
| `src/models/` | Estructuras de datos: Nodo, Arista, GrafoLogistico |
| `src/algorithms/` | Algoritmos de grafos: Dijkstra, Floyd-Warshall, Bellman-Ford |
| `src/optimization/` | FLP, simulación de cadena de frío, evaluación de escenarios |
| `src/visualization/` | Generación de gráficos y mapas |
| `src/utils/` | Carga de datos, funciones geográficas, constantes |

---

## 📝 Commits

Usar mensajes descriptivos con prefijos:

```
feat: agregar nuevo algoritmo de clustering
fix: corregir cálculo de distancia en Haversine
docs: actualizar README con resultados
test: agregar pruebas para Floyd-Warshall
refactor: optimizar función de deterioro
data: actualizar coordenadas de nodos de pesca
```

---

## ❓ ¿Preguntas?

Si tienes dudas sobre el proyecto, abre un Issue en el repositorio o consulta la documentación en `docs/`.

