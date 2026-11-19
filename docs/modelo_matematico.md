# Modelo Matemático — Optimización de Centros de Refrigeración y Cadena Pesquera Multimodal

## 1. Formulación General del Problema

### Tipo de problema
Combinación de:
1. **Multicriteria Constrained Shortest Path Problem (MCSPP)** sobre un grafo dirigido ponderado multimodal $G = (V, E)$.
2. **Capacitated & Fixed-Charge Facility Location Problem (FLP)** acoplado a cinética de degradación térmica poscaptura (FAO).
3. **Time-Varying Graph ($G(t)$)** para conmutar entre temporada de pesca extractiva fluvial y temporada de veda (piscicultura nativa).

---

## 2. Conjuntos, Vértices y Aristas del Grafo $G = (V, E)$

El conjunto de vértices $V$ ($|V| = 25$) se particiona en **7 subconjuntos disjuntos** (`ADR-04`):

$$V = P \cup M \cup A \cup F \cup D \cup H \cup V_{\text{merc}}$$

| Subconjunto | Código | Cantidad | Rol Matemático y Operativo en el Grafo |
| :--- | :---: | :---: | :--- |
| **Puntos de Pesca / Piscicultura** | $P$ | 7 | Nodos fuente de oferta diaria $q_i > 0$ ($\sum q_i = 265.75\text{ kg/día}$). En época de veda (abril–junio) conmutan a orígenes piscícolas $P_{\text{pisc}}$. |
| **Muelles de Transbordo** | $M$ | 3 | Interfaz fluvial $\to$ terrestre; agregan tiempo de espera expuesto al sol $t_{\text{esp}}(M) = +0.25\text{ h}$ sin refrigeración. |
| **Centros de Acopio** | $A$ | 3 | Consolidación de carga; obligatorios antes del centro de frío salvo `P06` urbano (`ADR-06`). |
| **Centros de Frío Candidatos** | $F$ | 3 | Nodos con capacidad de abatimiento térmico a $0\ ^\circ\text{C}$ ($C_j = 5000\text{ kg}$, costo fijo $f_j = \$5,000,000\text{ COP/mes}$). Reinician el reloj térmico y elevan la vida útil a $360\text{ h}$. |
| **Zonas Críticas de Deterioro** | $D$ | 2 | Multiplican la tasa de degradación térmica del tramo entrante por $\phi_D = 1.5$ ($3.75\%/\text{h}$). |
| **Hábitats y Reservas Protegidas** | $H$ | 2 | Vértices con `restriccion_ambiental = True` (humedales y resguardos indígenas); excluidos como nodos intermedios cuando `evitar_restringidos = True`. |
| **Mercados de Venta Final** | $V_{\text{merc}}$ | 5 | Nodos sumidero de demanda comercial (Puerto Gaitán, Villavicencio y Bogotá). |

---

## 3. Función de Peso Multicriterio por Arista (`ADR-02`)

Cada arista dirigida $e = (i, j) \in E$ ($|E| = 41$: $10$ fluviales sobre `rios.shp`, $12$ de acceso local y $19$ terrestres OSRM) evalúa **6 factores normalizados en $[0, 1]$**:

$$w_{ij} = \alpha\,\hat{t}_{ij} + \beta\,\hat{c}_{ij} + \gamma\,r_{\text{comb},ij} + \delta\,\hat{p}_{ij} + \varepsilon\,(1 - q_{ij}) + \zeta\,P_{\text{ret},ij}$$

| Coeficiente | Valor | Variable Normalizada | Expresión Matemática | Prioridad |
| :---: | :---: | :--- | :--- | :---: |
| $\alpha$ | $0.25$ | Tiempo efectivo ($\hat{t}_{ij}$) | $\min\!\left(\dfrac{t_{ij}\cdot \phi_{\text{flujo}} + t_{\text{esp},ij}}{48.0},\,1\right)$ | **1.ª (Máxima — Inocuidad)** |
| $\beta$ | $0.20$ | Costo total ($\hat{c}_{ij}$) | $\min\!\left(\dfrac{c_{\text{transp},ij} + c_{\text{peajes},ij}}{5,000,000},\,1\right)$ | **2.ª (Rentabilidad)** |
| $\gamma$ | $0.20$ | Riesgo combinado ($r_{\text{comb},ij}$) | $\min\!\Big(1.0,\; 0.50\,r_{\text{térm}} + 0.30\,r_{\text{acc}} + 0.20\,r_{\text{derr}}\Big)$ | **3.ª (Seguridad física/térmica)** |
| $\delta$ | $0.10$ | Pérdida esperada ($\hat{p}_{ij}$) | $\dfrac{\min(100,\; 2.5 \cdot t_{\text{ef},ij} \cdot \phi_{\text{vía}} \cdot (1 + r_{\text{térm}}))}{100}$ | **4.ª (Merma directa)** |
| $\varepsilon$ | $0.10$ | Inestabilidad vial ($1 - q_{ij}$) | $1 - \text{confiabilidad\_via}_{ij}$ | **5.ª (Confiabilidad)** |
| $\zeta$ | $0.05$ | Probabilidad de retraso ($P_{\text{ret},ij}$) | $\text{prob\_retraso}_{ij} \in [0, 1]$ | **6.ª (Puntualidad)** |

---

## 4. Modelado Matemático de las Problemáticas Reales (ECA `C05-01-2026-003`)

### 4.1. Grafos Bitemporales para Época de Pesca vs. Época de Veda ($G_{\text{pesca}}$ y $G_{\text{veda}}$)
Para modelar la prohibición extractiva de abril–junio y la transición a piscicultura de especies nativas:

$$G(\tau) = \big(V,\; E(\tau)\big), \qquad \tau \in \{\text{pesca (jul–mar)},\; \text{veda (abr–jun)}\}$$

- **En $\tau = \text{pesca}$:** vector de oferta activo $q_i(\tau) > 0$ para $i \in P_{\text{río}} = \{\text{P01},\dots,\text{P07}\}$.
- **En $\tau = \text{veda}$:** $q_i(\text{veda}) = 0$ para captura fluvial extractiva y se activan los nodos productivos de piscicultura en tierra firme $P_{\text{pisc}}$, desplazando el flujo óptimo hacia subgrafos de acceso local y acopios terrestres ($A$).

### 4.2. Cota Dura Sanitaria FAO y Control de Histamina ($t \le 4.0\text{ h}$)
Sea $\pi(P_i, F_j) = (v_0, v_1, \dots, v_k)$ el camino óptimo desde un origen $P_i$ hasta un centro de frío $F_j$. La condición necesaria de inocuidad (prevención de histamina a $T_{\text{amb}} = 30\ ^\circ\text{C}$) es:

$$T_{\text{sin frío}}\big(\pi(P_i, F_j)\big) = \sum_{e \in \pi} t_{\text{ef}}(e) + \sum_{v \in \pi \cap M} t_{\text{esp}}(v) \;\le\; T_{\max\text{ FAO}} = 4.0\text{ h} \;\;(240\text{ min})$$

La pérdida porcentual acumulada a lo largo del camino antes de tocar frío se modela recursivamente como:

$$D_{\text{acum}}(v_m) = D_{\text{acum}}(v_{m-1}) + r_{\text{base}}(T_m)\cdot \phi_D(v_m)\cdot \Delta t_m, \qquad \phi_D(v_m) = \begin{cases} 1.5 & \text{si } v_m \in D \\ 1.0 & \text{en otro caso} \end{cases}$$

Una vez alcanzado $F_j$, la temperatura cae a $0\ ^\circ\text{C}$ y la tasa de deterioro se reduce en un $90\%$ ($r_{\text{frío}} = 0.10\,r_{\text{base}}$), extendiendo la vida útil de $6\text{ h}$ a $360\text{ h}$.

### 4.3. Proporción Hielo-Pescado ($1:1$) y Balance de Carga
Siguiendo el estándar BPP/FAO ($\rho_{\text{hielo}} = 1.0\text{ kg hielo / kg pescado}$):

$$M_{\text{bruta}}(i) = q_i\,(1 + \rho_{\text{hielo}}) = 2\,q_i, \qquad C_{\text{hielo}}(i) = c_{\text{hielo/kg}}\cdot \rho_{\text{hielo}}\cdot q_i \quad (\$800\text{ COP/kg})$$

Toda arista $e \in E$ en la ruta asignada debe verificar $M_{\text{bruta}}(i) \le \text{capacidad\_kg}(e)$.

### 4.4. Problema de Localización de Instalaciones (FLP) de Costo Total Mínimo
Con variables binarias de apertura $y_j \in \{0, 1\}$ ($\forall j \in F$) y asignación $x_{ij} \in \{0, 1\}$ ($\forall i \in P, j \in F$):

$$\min_{y,\,x} \; Z = \sum_{j \in F} f_j\,y_j + 30 \sum_{i \in P} \sum_{j \in F} \Big(c_{\text{transp}}(i,j) + c_{\text{hielo}}(i) + p_{\text{venta}}\cdot q_i \cdot \frac{D_{\text{acum}}(i,j)}{100}\Big) x_{ij}$$

Sujeto a:
1. **Asignación única:** $\sum_{j \in F} x_{ij} = 1 \quad \forall i \in P$
2. **Apertura previa:** $x_{ij} \le y_j \quad \forall i \in P, j \in F$
3. **Inocuidad FAO obligatoria:** $T_{\text{sin frío}}(i, j)\cdot x_{ij} \le 4.0\text{ h} \quad \forall i \in P, j \in F$
4. **Capacidad frigorífica:** $\sum_{i \in P} q_i\,x_{ij} \le C_j\,y_j \quad \forall j \in F$
5. **Flujo por acopio/muelle (`ADR-06`):** toda ruta $\pi(P_i, F_j)$ con $P_i \ne \text{P06}$ verifica $\pi(P_i, F_j) \cap (A \cup M) \ne \emptyset$.

### 4.5. Exclusión de Hábitats y Reservas Indígenas (`evitar_restringidos = True`)
En los algoritmos de caminos mínimos, el conjunto de aristas admisibles desde un nodo actual $u$ hacia un vecino $v$ hacia el destino final $d$ se filtra mediante:

$$E_{\text{adm}}(u, d) = \big\{(u, v) \in E \;:\; \neg\,\text{restringido}(v) \;\lor\; v = d\big\}$$

donde $\text{restringido}(v) = \text{True} \iff v \in H$ (`H01`, `H02`).

### 4.6. Trazabilidad Sanitaria mediante DAG y Tablas Hash $O(1)$
Cada lote procesado genera una secuencia acíclica dirigida de estados $\mathcal{T}_i = \langle s_0, s_1, \dots, s_k \rangle$ indexada en memoria mediante tablas hash (`Dict[str, Nodo]`, `Dict[str, List[Arista]]`) con complejidad de acceso $O(1)$, almacenando la tupla auditable $(\text{id\_tramo}, \Delta d, \Delta t, T_m, D_{\text{tramo}}, D_{\text{acum}}, \text{kg\_útiles})$ exigida por las normas de trazabilidad ICA/INVIMA.

---

## 5. Complejidad Computacional de los Algoritmos Propios

| Algoritmo | Módulo | Uso en el Proyecto | Complejidad Temporal | Complejidad Espacial |
| :--- | :--- | :--- | :---: | :---: |
| **Dijkstra (Montículo Binario)** | `src/algorithms/dijkstra.py` | Camino mínimo origen $\to$ destino y árbol completo | $O((|V| + |E|)\log |V|)$ | $O(|V|)$ |
| **Bellman-Ford** | `src/algorithms/bellman_ford.py` | Verificación cruzada y detección de ciclos negativos | $O(|V| \cdot |E|)$ | $O(|V|)$ |
| **Floyd-Warshall** | `src/algorithms/floyd_warshall.py` | Matriz de distancias y tiempos entre todos los pares | $O(|V|^3)$ | $O(|V|^2)$ |
| **BFS / DFS Propios** | `src/visualization/graph_slides.py` | Saltos topológicos mínimos y exploración de rutas con backtracking | $O(|V| + |E|)$ | $O(|V|)$ |
| **Greedy FLP + Evaluador** | `src/optimization/facility_location.py` | Selección heurística y evaluación exhaustiva de escenarios | $O(|P| \cdot |F|^2)$ | $O(|P| \cdot |F|)$ |
| **Dijkstra Fluvial Espacial** | `src/visualization/river_network.py` | Trazado sobre cauce real `rios.shp` ($12,413$ vértices) | $O((|V_r| + |E_r|)\log |V_r|)$ | $O(|V_r|)$ |
