"""
bellman_ford.py — Algoritmo de Bellman-Ford para caminos mínimos.

A diferencia de Dijkstra, soporta aristas con peso negativo
y detecta ciclos negativos. Útil como verificación.

Complejidad: O(V × E)
"""

from __future__ import annotations
from typing import Dict, List, Optional, Tuple

from ..models.grafo_logistico import GrafoLogistico


def bellman_ford(
    grafo: GrafoLogistico,
    origen: str,
    criterio: str = "peso",
    evitar_restringidos: bool = False
) -> Tuple[Dict[str, float], Dict[str, Optional[str]], bool]:
    """
    Ejecuta Bellman-Ford desde un nodo origen.

    Parameters
    ----------
    grafo : GrafoLogistico
    origen : str — ID del nodo de partida.
    criterio : str — atributo de peso a usar.
    evitar_restringidos : bool — si es True, los nodos con restricción
        ambiental no se usan como intermedios (sí como origen/destino).

    Returns
    -------
    tuple (dist, prev, tiene_ciclo_negativo)
        dist : dict[str, float] — distancia mínima a cada nodo.
        prev : dict[str, str|None] — predecesor en el camino mínimo.
        tiene_ciclo_negativo : bool — True si existe un ciclo negativo.
    """
    if origen not in grafo:
        raise KeyError(f"Nodo '{origen}' no existe en el grafo.")

    ids = [n.id for n in grafo.nodos]
    INF = float("inf")

    dist: Dict[str, float] = {i: INF for i in ids}
    prev: Dict[str, Optional[str]] = {i: None for i in ids}
    dist[origen] = 0.0

    todas_aristas = grafo.aristas
    if evitar_restringidos:
        restringidos = {
            n.id for n in grafo.nodos
            if n.restriccion_ambiental and n.id != origen
        }
        # No se puede salir de un nodo restringido (sería intermedio)
        todas_aristas = [a for a in todas_aristas
                         if a.origen not in restringidos]

    # Relajar |V| - 1 veces
    for _ in range(len(ids) - 1):
        actualizo = False
        for arista in todas_aristas:
            if criterio == "peso":
                peso = arista.peso_default
            else:
                peso = getattr(arista, criterio, arista.peso_default)

            if dist[arista.origen] + peso < dist[arista.destino]:
                dist[arista.destino] = dist[arista.origen] + peso
                prev[arista.destino] = arista.origen
                actualizo = True

        if not actualizo:
            break  # Optimización: si no hubo cambios, terminar

    # Detectar ciclos negativos
    tiene_ciclo = False
    for arista in todas_aristas:
        peso = arista.peso_default if criterio == "peso" else getattr(
            arista, criterio, arista.peso_default
        )
        if dist[arista.origen] + peso < dist[arista.destino]:
            tiene_ciclo = True
            break

    return dist, prev, tiene_ciclo


def reconstruir_camino_bf(
    prev: Dict[str, Optional[str]],
    destino: str
) -> List[str]:
    """Reconstruye el camino mínimo desde el predecesor."""
    camino = []
    actual = destino
    visitados = set()
    while actual is not None and actual not in visitados:
        visitados.add(actual)
        camino.append(actual)
        actual = prev.get(actual)
    camino.reverse()
    return camino

