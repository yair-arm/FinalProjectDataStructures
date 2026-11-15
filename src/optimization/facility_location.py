"""
facility_location.py — Problema de Localización de Instalaciones (FLP).

Determina la ubicación óptima de centros de refrigeración minimizando
el número de centros necesarios, sujeto a:
  - Límite máximo de deterioro por ruta.
  - Capacidad de cada centro.
  - Cobertura de todos los puntos de pesca.

Implementa dos estrategias:
  1. Greedy (heurístico) — rápido, para primera aproximación.
  2. PuLP (óptimo)       — programación lineal entera mixta.
"""

from __future__ import annotations
from typing import Dict, List, Tuple, Optional, Set

from ..models.grafo_logistico import GrafoLogistico
from ..models.nodo import Nodo
from ..algorithms.dijkstra import dijkstra
from ..utils.constants import TIEMPO_MAX_SIN_FRIO_H
from ..utils.geo_utils import haversine, calcular_tiempo_viaje


# ═══════════════════════════════════════════════════════════════════
#  RESULTADO DE LA LOCALIZACIÓN
# ═══════════════════════════════════════════════════════════════════

class ResultadoLocalizacion:
    """Almacena y presenta los resultados de la optimización."""

    def __init__(self):
        self.centros_abiertos: List[str] = []
        self.asignaciones: Dict[str, str] = {}   # pesca → centro
        self.costo_total: float = 0.0
        self.cobertura: float = 0.0
        self.tiempo_max_sin_frio: float = 0.0
        self.detalles: List[Dict] = []

    def resumen(self) -> str:
        lineas = [
            "═" * 55,
            "  RESULTADO — LOCALIZACIÓN DE CENTROS DE FRÍO",
            "═" * 55,
            f"  Centros abiertos:       {len(self.centros_abiertos)}",
            f"  Centros:                {', '.join(self.centros_abiertos)}",
            f"  Puntos de pesca cubiertos: {len(self.asignaciones)}",
            f"  Cobertura:              {self.cobertura:.1f}%",
            f"  Tiempo máx sin frío:    {self.tiempo_max_sin_frio:.2f} h",
            f"  Costo total:            ${self.costo_total:,.0f} COP",
            "═" * 55,
        ]
        if self.asignaciones:
            lineas.append("\n  Asignaciones:")
            for pesca, centro in self.asignaciones.items():
                lineas.append(f"    {pesca} → {centro}")
        return "\n".join(lineas)


# ═══════════════════════════════════════════════════════════════════
#  ALGORITMO GREEDY
# ═══════════════════════════════════════════════════════════════════

def resolver_localizacion_greedy(
    grafo: GrafoLogistico,
    tiempo_max_h: float = TIEMPO_MAX_SIN_FRIO_H
) -> ResultadoLocalizacion:
    """
    Heurística greedy para localización de centros de frío.

    Estrategia: en cada iteración, abre el centro candidato que
    cubre más puntos de pesca aún no asignados dentro del límite
    de tiempo permitido.
    """
    resultado = ResultadoLocalizacion()

    puntos_pesca = grafo.puntos_pesca()
    candidatos = grafo.candidatos_frio()

    if not puntos_pesca or not candidatos:
        return resultado

    no_cubiertos: Set[str] = {p.id for p in puntos_pesca}

    while no_cubiertos:
        mejor_candidato = None
        mejor_cobertura: Set[str] = set()

        for candidato in candidatos:
            if candidato.id in resultado.centros_abiertos:
                continue

            cubiertos_por_este: Set[str] = set()
            for pesca_id in no_cubiertos:
                # Calcular tiempo con Dijkstra
                dist, camino = dijkstra(grafo, pesca_id, candidato.id,
                                        criterio="tiempo_h", evitar_restringidos=True)
                if dist <= tiempo_max_h:
                    cubiertos_por_este.add(pesca_id)

            if len(cubiertos_por_este) > len(mejor_cobertura):
                mejor_candidato = candidato
                mejor_cobertura = cubiertos_por_este

        if mejor_candidato is None:
            break  # No se puede cubrir más

        # Abrir el mejor centro
        resultado.centros_abiertos.append(mejor_candidato.id)
        resultado.costo_total += mejor_candidato.costo_fijo

        for pesca_id in mejor_cobertura:
            resultado.asignaciones[pesca_id] = mejor_candidato.id
            no_cubiertos.discard(pesca_id)

    # Calcular métricas
    total_pesca = len(puntos_pesca)
    resultado.cobertura = (
        len(resultado.asignaciones) / total_pesca * 100 if total_pesca > 0 else 0
    )

    # Tiempo máximo sin frío
    max_t = 0.0
    for pesca_id, centro_id in resultado.asignaciones.items():
        dist, _ = dijkstra(grafo, pesca_id, centro_id, criterio="tiempo_h", evitar_restringidos=True)
        if dist < float("inf"):
            max_t = max(max_t, dist)
    resultado.tiempo_max_sin_frio = max_t

    return resultado


# ═══════════════════════════════════════════════════════════════════
#  PROGRAMACIÓN LINEAL ENTERA (PuLP)
# ═══════════════════════════════════════════════════════════════════

def resolver_localizacion_pulp(
    grafo: GrafoLogistico,
    tiempo_max_h: float = TIEMPO_MAX_SIN_FRIO_H,
    max_centros: Optional[int] = None
) -> ResultadoLocalizacion:
    """
    Resuelve el FLP con programación lineal entera usando PuLP.

    Minimiza: Σ y_j  (número de centros abiertos)
    Sujeto a:
      - Cada punto de pesca asignado a exactamente un centro.
      - Solo asignar a centros abiertos.
      - Tiempo de viaje ≤ tiempo_max_h.
      - Capacidad de centros.
    """
    try:
        import pulp
    except ImportError:
        raise ImportError("Se necesita PuLP: pip install pulp")

    resultado = ResultadoLocalizacion()
    puntos_pesca = grafo.puntos_pesca()
    candidatos = grafo.candidatos_frio()

    if not puntos_pesca or not candidatos:
        return resultado

    I = [p.id for p in puntos_pesca]    # Puntos de pesca
    J = [c.id for c in candidatos]      # Candidatos a centro

    # Precalcular tiempos
    tiempos: Dict[Tuple[str, str], float] = {}
    for i in I:
        for j in J:
            dist, _ = dijkstra(grafo, i, j, criterio="tiempo_h", evitar_restringidos=True)
            tiempos[(i, j)] = dist

    # Variables de decisión
    y = pulp.LpVariable.dicts("y", J, cat="Binary")       # Abrir centro j
    x = pulp.LpVariable.dicts("x", [(i, j) for i in I for j in J],
                               cat="Binary")                # Asignar i → j

    # Modelo
    prob = pulp.LpProblem("Localizacion_Centros_Frio", pulp.LpMinimize)

    # Objetivo: minimizar centros abiertos
    prob += pulp.lpSum(y[j] for j in J), "Min_Centros"

    # Restricción: cada pesca asignada a exactamente un centro
    for i in I:
        prob += (
            pulp.lpSum(x[(i, j)] for j in J) == 1,
            f"Asignacion_{i}"
        )

    # Restricción: solo asignar a centros abiertos
    for i in I:
        for j in J:
            prob += x[(i, j)] <= y[j], f"Abierto_{i}_{j}"

    # Restricción: tiempo máximo
    for i in I:
        for j in J:
            if tiempos[(i, j)] > tiempo_max_h:
                prob += x[(i, j)] == 0, f"Tiempo_{i}_{j}"

    # Restricción: máximo de centros (opcional)
    if max_centros is not None:
        prob += (
            pulp.lpSum(y[j] for j in J) <= max_centros,
            "Max_Centros"
        )

    # Resolver
    prob.solve(pulp.PULP_CBC_CMD(msg=0))

    if prob.status != pulp.constants.LpStatusOptimal:
        return resultado

    # Extraer solución
    for j in J:
        if y[j].varValue and y[j].varValue > 0.5:
            resultado.centros_abiertos.append(j)
            nodo = grafo.obtener_nodo(j)
            if nodo:
                resultado.costo_total += nodo.costo_fijo

    for i in I:
        for j in J:
            if x[(i, j)].varValue and x[(i, j)].varValue > 0.5:
                resultado.asignaciones[i] = j
                break

    total = len(I)
    resultado.cobertura = len(resultado.asignaciones) / total * 100 if total > 0 else 0

    max_t = 0.0
    for i, j in resultado.asignaciones.items():
        max_t = max(max_t, tiempos.get((i, j), 0))
    resultado.tiempo_max_sin_frio = max_t

    return resultado


# ═══════════════════════════════════════════════════════════════════
#  FUNCIÓN PRINCIPAL
# ═══════════════════════════════════════════════════════════════════

def resolver_localizacion(
    grafo: GrafoLogistico,
    metodo: str = "greedy",
    tiempo_max_h: float = TIEMPO_MAX_SIN_FRIO_H,
    max_centros: Optional[int] = None
) -> ResultadoLocalizacion:
    """
    Resuelve el problema de localización de centros de frío.

    Parameters
    ----------
    grafo : GrafoLogistico
    metodo : str — 'greedy' o 'pulp'.
    tiempo_max_h : float — tiempo máximo sin refrigeración.
    max_centros : int | None — límite de centros a abrir.
    """
    if metodo == "pulp":
        return resolver_localizacion_pulp(grafo, tiempo_max_h, max_centros)
    else:
        return resolver_localizacion_greedy(grafo, tiempo_max_h)

