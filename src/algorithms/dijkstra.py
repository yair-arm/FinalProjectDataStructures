"""
dijkstra.py — Algoritmo de Dijkstra para caminos mínimos.

Implementación propia con cola de prioridad (heap), sin depender
de NetworkX, para demostrar dominio de estructuras de datos.

Complejidad: O((V + E) log V)
"""

from __future__ import annotations
import heapq
from typing import Dict, List, Optional, Tuple

from ..models.grafo_logistico import GrafoLogistico
from ..utils.constants import TIEMPO_MAX_SIN_FRIO_H, TIEMPO_TRANSBORDO_MUELLE_H


def _restringido(grafo: GrafoLogistico, nodo_id: str) -> bool:
    """Indica si el nodo tiene restricción ambiental (hábitat protegido)."""
    nodo = grafo.obtener_nodo(nodo_id)
    return bool(nodo is not None and nodo.restriccion_ambiental)


def _tiene_refrigeracion(grafo: GrafoLogistico, nodo_id: str) -> bool:
    """Indica si el nodo abate temperatura (centro de frío F o acopio con frío)."""
    nodo = grafo.obtener_nodo(nodo_id)
    return bool(
        nodo is not None
        and nodo.tipo in ("F", "A")
        and nodo.capacidad_frio_kg > 0
    )


def dijkstra_con_cota_inocuidad(
    grafo: GrafoLogistico,
    origen: str,
    destino: str,
    tiempo_limite_h: float = TIEMPO_MAX_SIN_FRIO_H,
    criterio: str = "peso",
    evitar_restringidos: bool = True,
) -> Tuple[float, List[str], float, bool]:
    """
    Camino Más Corto Restringido por Tiempo de Inocuidad FAO (Constrained Shortest Path).

    Poda directamente dentro del montículo binario (`heapq`) cualquier rama cuyo
    tiempo acumulado sin refrigeración (incluyendo +0.25 h en muelles M) supere
    `tiempo_limite_h` (4.0 h = 240 min) antes de alcanzar un nodo frigorífico (F),
    mitigando el riesgo biológico de formación de histamina.

    Returns
    -------
    tuple (costo_total, camino, max_tiempo_sin_frio_h, cumple_inocuidad)
    """
    if origen not in grafo or destino not in grafo:
        raise KeyError(f"Nodo '{origen}' o '{destino}' no existe en el grafo.")

    # Cola de prioridad: (costo_acum, t_sin_frio_actual, max_t_sin_frio, nodo_actual, camino)
    heap: List[Tuple[float, float, float, str, List[str]]] = [
        (0.0, 0.0, 0.0, origen, [origen])
    ]
    mejor_estado: Dict[str, Tuple[float, float]] = {}

    while heap:
        costo_act, t_sin_frio, max_t_sf, u, camino = heapq.heappop(heap)

        if u == destino:
            return costo_act, camino, max_t_sf, (max_t_sf <= tiempo_limite_h)

        prev_mejor = mejor_estado.get(u)
        if (
            prev_mejor is not None
            and costo_act >= prev_mejor[0]
            and t_sin_frio >= prev_mejor[1]
        ):
            continue
        mejor_estado[u] = (costo_act, t_sin_frio)

        for arista in grafo.obtener_aristas(u):
            v = arista.destino
            if v in camino:
                continue
            if evitar_restringidos and v != destino and _restringido(grafo, v):
                continue

            nodo_v = grafo.obtener_nodo(v)
            espera_muelle = (
                TIEMPO_TRANSBORDO_MUELLE_H
                if (nodo_v is not None and nodo_v.tipo == "M")
                else 0.0
            )
            nuevo_t_sin_frio = t_sin_frio + arista.tiempo_h + espera_muelle

            # Poda dura de inocuidad FAO en el montículo binario
            if nuevo_t_sin_frio > tiempo_limite_h:
                continue

            nuevo_max_sf = max(max_t_sf, nuevo_t_sin_frio)
            if _tiene_refrigeracion(grafo, v):
                nuevo_t_sin_frio = 0.0

            peso_arista = (
                arista.peso_default
                if criterio == "peso"
                else getattr(arista, criterio, arista.peso_default)
            )
            heapq.heappush(
                heap,
                (
                    costo_act + peso_arista,
                    nuevo_t_sin_frio,
                    nuevo_max_sf,
                    v,
                    camino + [v],
                ),
            )

    return float("inf"), [], float("inf"), False


def dijkstra(grafo: GrafoLogistico,
             origen: str,
             destino: str,
             criterio: str = "peso",
             evitar_restringidos: bool = False) -> Tuple[float, List[str]]:
    """
    Encuentra el camino mínimo entre dos nodos usando Dijkstra.

    Parameters
    ----------
    grafo : GrafoLogistico
        Grafo dirigido ponderado.
    origen : str
        ID del nodo de inicio.
    destino : str
        ID del nodo de llegada.
    criterio : str
        Atributo de la arista a minimizar:
        'peso' (multicriterio), 'distancia_km', 'tiempo_h', 'costo_cop'.

    Returns
    -------
    tuple (distancia_total, camino)
        distancia_total : float — peso total del camino.
        camino : list[str]     — secuencia de IDs de nodos.
        Si no hay camino, devuelve (inf, []).
    """
    if origen not in grafo or destino not in grafo:
        raise KeyError(f"Nodo '{origen}' o '{destino}' no existe en el grafo.")

    # Distancias mínimas conocidas
    dist: Dict[str, float] = {nodo.id: float("inf") for nodo in grafo.nodos}
    dist[origen] = 0.0

    # Predecesores para reconstruir el camino
    prev: Dict[str, Optional[str]] = {nodo.id: None for nodo in grafo.nodos}

    # Nodos ya procesados
    visitados: set = set()

    # Cola de prioridad: (distancia_acumulada, id_nodo)
    heap: List[Tuple[float, str]] = [(0.0, origen)]

    while heap:
        dist_actual, nodo_actual = heapq.heappop(heap)

        if nodo_actual in visitados:
            continue
        visitados.add(nodo_actual)

        # Si llegamos al destino, cortamos
        if nodo_actual == destino:
            break

        # Explorar vecinos
        for arista in grafo.obtener_aristas(nodo_actual):
            vecino = arista.destino

            if vecino in visitados:
                continue
            if (evitar_restringidos and vecino != destino
                    and _restringido(grafo, vecino)):
                continue

            # Obtener el peso según el criterio
            if criterio == "peso":
                peso_arista = arista.peso_default
            else:
                peso_arista = getattr(arista, criterio, arista.peso_default)

            nueva_dist = dist_actual + peso_arista

            if nueva_dist < dist[vecino]:
                dist[vecino] = nueva_dist
                prev[vecino] = nodo_actual
                heapq.heappush(heap, (nueva_dist, vecino))

    # Reconstruir camino
    if dist[destino] == float("inf"):
        return float("inf"), []

    camino = []
    nodo = destino
    while nodo is not None:
        camino.append(nodo)
        nodo = prev[nodo]
    camino.reverse()

    return dist[destino], camino


def dijkstra_completo(grafo: GrafoLogistico,
                      origen: str,
                      criterio: str = "peso",
                      evitar_restringidos: bool = False
                      ) -> Dict[str, Tuple[float, List[str]]]:
    """
    Ejecuta Dijkstra desde un origen hacia TODOS los nodos alcanzables.

    Returns
    -------
    dict[str, tuple(float, list[str])]
        Diccionario {id_nodo: (distancia, camino)}.
    """
    dist: Dict[str, float] = {n.id: float("inf") for n in grafo.nodos}
    dist[origen] = 0.0
    prev: Dict[str, Optional[str]] = {n.id: None for n in grafo.nodos}
    visitados: set = set()
    heap: List[Tuple[float, str]] = [(0.0, origen)]

    while heap:
        dist_actual, nodo_actual = heapq.heappop(heap)

        if nodo_actual in visitados:
            continue
        visitados.add(nodo_actual)

        # Un nodo restringido puede alcanzarse, pero no se expande
        if (evitar_restringidos and nodo_actual != origen
                and _restringido(grafo, nodo_actual)):
            continue

        for arista in grafo.obtener_aristas(nodo_actual):
            vecino = arista.destino
            if vecino in visitados:
                continue

            peso = arista.peso_default if criterio == "peso" else getattr(
                arista, criterio, arista.peso_default
            )
            nueva_dist = dist_actual + peso
            if nueva_dist < dist[vecino]:
                dist[vecino] = nueva_dist
                prev[vecino] = nodo_actual
                heapq.heappush(heap, (nueva_dist, vecino))

    # Reconstruir todos los caminos
    resultado: Dict[str, Tuple[float, List[str]]] = {}
    for nodo_id in dist:
        if dist[nodo_id] == float("inf"):
            resultado[nodo_id] = (float("inf"), [])
        else:
            camino = []
            actual = nodo_id
            while actual is not None:
                camino.append(actual)
                actual = prev[actual]
            camino.reverse()
            resultado[nodo_id] = (dist[nodo_id], camino)

    return resultado

