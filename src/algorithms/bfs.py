"""
bfs.py — Búsqueda en Amplitud (Breadth-First Search).

Algoritmo fundamental de recorrido de grafos del curso de Estructuras de Datos.
Utiliza una cola FIFO para explorar los vértices nivel por nivel.

Complejidad temporal: O(V + E)
Complejidad espacial: O(V)
"""

from __future__ import annotations
from collections import deque
from typing import Dict, List, Optional, Set, Tuple

from ..models.grafo_logistico import GrafoLogistico


def _restringido(grafo: GrafoLogistico, nodo_id: str) -> bool:
    """Indica si el nodo tiene restricción ambiental (hábitat protegido)."""
    nodo = grafo.obtener_nodo(nodo_id)
    return bool(nodo is not None and nodo.restriccion_ambiental)


def bfs_recorrido(
    grafo: GrafoLogistico,
    origen: str,
    evitar_restringidos: bool = True,
) -> List[str]:
    """
    Realiza un recorrido en amplitud completo a partir del vértice origen.

    Parameters
    ----------
    grafo : GrafoLogistico
        Grafo dirigido.
    origen : str
        ID del nodo inicial.
    evitar_restringidos : bool
        Si es True, no visita nodos con restricción ambiental.

    Returns
    -------
    list[str]
        Lista de IDs de nodos en el orden en que fueron visitados.
    """
    if origen not in grafo:
        raise KeyError(f"Nodo '{origen}' no existe en el grafo.")

    visitados: Set[str] = set()
    orden_visita: List[str] = []
    cola: deque[str] = deque([origen])
    visitados.add(origen)

    while cola:
        actual = cola.popleft()
        orden_visita.append(actual)

        for arista in grafo.obtener_aristas(actual):
            vecino = arista.destino
            if vecino not in visitados:
                if evitar_restringidos and _restringido(grafo, vecino):
                    continue
                visitados.add(vecino)
                cola.append(vecino)

    return orden_visita


def bfs_camino(
    grafo: GrafoLogistico,
    origen: str,
    destino: str,
    evitar_restringidos: bool = True,
) -> Tuple[int, List[str]]:
    """
    Encuentra el camino con menor número de saltos (aristas) entre origen y destino.

    Parameters
    ----------
    grafo : GrafoLogistico
    origen : str
    destino : str
    evitar_restringidos : bool

    Returns
    -------
    tuple (num_saltos, camino)
        Si no hay camino, devuelve (-1, []).
    """
    if origen not in grafo or destino not in grafo:
        raise KeyError(f"Nodo '{origen}' o '{destino}' no existe en el grafo.")

    if origen == destino:
        return 0, [origen]

    cola: deque[str] = deque([origen])
    padre: Dict[str, Optional[str]] = {origen: None}
    distancia: Dict[str, int] = {origen: 0}

    while cola:
        actual = cola.popleft()
        if actual == destino:
            break

        for arista in grafo.obtener_aristas(actual):
            vecino = arista.destino
            if vecino not in padre:
                if evitar_restringidos and _restringido(grafo, vecino) and vecino != destino:
                    continue
                padre[vecino] = actual
                distancia[vecino] = distancia[actual] + 1
                cola.append(vecino)

    if destino not in padre:
        return -1, []

    # Reconstruir camino
    camino = []
    curr: Optional[str] = destino
    while curr is not None:
        camino.append(curr)
        curr = padre[curr]
    camino.reverse()

    return distancia[destino], camino


def bfs_nodo_mas_cercano_por_tipo(
    grafo: GrafoLogistico,
    origen: str,
    tipos_objetivo: Tuple[str, ...] = ("A", "F"),
    evitar_restringidos: bool = True,
) -> Tuple[Optional[str], int, List[str]]:
    """
    Encuentra el nodo objetivo más próximo en número de transbordos/saltos usando BFS.
    Ideal para resolver: ¿Cuál es el acopio o cuarto frío más inmediato desde un punto de pesca?

    Returns
    -------
    tuple (nodo_id, saltos, camino)
        Si no encuentra ninguno, retorna (None, -1, []).
    """
    if origen not in grafo:
        raise KeyError(f"Nodo '{origen}' no existe en el grafo.")

    cola: deque[str] = deque([origen])
    padre: Dict[str, Optional[str]] = {origen: None}
    distancia: Dict[str, int] = {origen: 0}

    while cola:
        actual = cola.popleft()
        nodo_obj = grafo.obtener_nodo(actual)

        if actual != origen and nodo_obj and nodo_obj.tipo in tipos_objetivo:
            # Encontrado el primer objetivo por BFS (garantiza menor número de saltos)
            camino = []
            curr: Optional[str] = actual
            while curr is not None:
                camino.append(curr)
                curr = padre[curr]
            camino.reverse()
            return actual, distancia[actual], camino

        for arista in grafo.obtener_aristas(actual):
            vecino = arista.destino
            if vecino not in padre:
                if evitar_restringidos and _restringido(grafo, vecino):
                    continue
                padre[vecino] = actual
                distancia[vecino] = distancia[actual] + 1
                cola.append(vecino)

    return None, -1, []
