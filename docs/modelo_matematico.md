# Modelo Matemático — Localización de Centros de Refrigeración

## Formulación del Problema

### Tipo de problema
**Facility Location Problem (FLP)** combinado con **Shortest Path Problem**.

### Conjuntos
- $I$: Conjunto de puntos de pesca $\{P_1, P_2, \ldots, P_n\}$
- $J$: Conjunto de centros candidatos $\{F_1, F_2, \ldots, F_m\}$
- $V$: Conjunto de mercados de destino

### Variables de Decisión
- $y_j \in \{0, 1\}$: 1 si se abre un centro de frío en $j$, 0 si no
- $x_{ij} \in \{0, 1\}$: 1 si el punto de pesca $i$ se asigna al centro $j$

### Parámetros
| Símbolo | Descripción | Unidad |
|---------|-------------|--------|
| $d_{ij}$ | Distancia del punto $i$ al centro $j$ | km |
| $t_{ij}$ | Tiempo de viaje | horas |
| $q_i$ | Producción diaria del punto $i$ | kg/día |
| $C_j$ | Capacidad del centro $j$ | kg |
| $F_j$ | Costo fijo de operar el centro $j$ | COP |
| $T_{\max}$ | Tiempo máximo permitido sin frío | horas |
| $D_{\max}$ | Deterioro máximo aceptable | % |

### Función Objetivo

$$\min Z = \sum_{j \in J} y_j$$

Minimizar el número de centros de refrigeración necesarios.

### Restricciones

**1. Asignación completa:** cada punto de pesca asignado a exactamente un centro.

$$\sum_{j \in J} x_{ij} = 1 \quad \forall i \in I$$

**2. Solo centros abiertos:** no se puede asignar a un centro cerrado.

$$x_{ij} \leq y_j \quad \forall i \in I, \, j \in J$$

**3. Límite de tiempo sin frío:**

$$t_{ij} \cdot x_{ij} \leq T_{\max} \quad \forall i \in I, \, j \in J$$

**4. Capacidad de centros:**

$$\sum_{i \in I} q_i \cdot x_{ij} \leq C_j \cdot y_j \quad \forall j \in J$$

**5. Deterioro máximo:**

$$D_{\text{ruta}_p} \leq D_{\max} \quad \forall p$$

### Peso Multicriterio de las Aristas

$$w_{ij} = \alpha \cdot \frac{t_{ij}}{48} + \beta \cdot \frac{c_{ij}}{5\,000\,000} + \gamma \cdot r_{ij} + \delta \cdot \frac{p_{ij}}{100}$$

Donde:
- $\alpha = 0.35$ (tiempo)
- $\beta = 0.25$ (costo)
- $\gamma = 0.25$ (riesgo térmico)
- $\delta = 0.15$ (pérdida esperada)

## Algoritmos Implementados

| Algoritmo | Uso | Complejidad |
|-----------|-----|-------------|
| Dijkstra | Ruta mínima origen → destino | $O((V+E) \log V)$ |
| Floyd-Warshall | Todas las distancias mínimas | $O(V^3)$ |
| Bellman-Ford | Verificación con pesos negativos | $O(V \cdot E)$ |
| Greedy FLP | Localización heurística de centros | $O(|I| \cdot |J|^2)$ |
| PuLP (MIP) | Localización óptima exacta | Variable |

