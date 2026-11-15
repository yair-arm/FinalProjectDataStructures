"""
dfs.py — Búsqueda en Profundidad (Depth-First Search).

Algoritmo fundamental de recorrido de grafos del curso de Estructuras de Datos.
Utiliza retroceso (backtracking) para explorar exhaustivamente ramas del grafo
y encontrar todos los caminos simples entre puntos de captura y mercados.

Complejidad temporal: O(V + E) para recorrido simple; O(V!) para enumeración exhaustiva de caminos.
"""

from __future__ import annotations
from typing import Dict, List, Set, Tuple

from ..models.grafo_logistico import GrafoLogistico


def _restringido(grafo: GrafoLogistico, nodo_id: str) -> bool:
    """Indica si el nodo tiene restricción ambiental (hábitat protegido)."""
    nodo = grafo.obtener_nodo(nodo_id)
    return bool(nodo is not None and nodo.restriccion_ambiental)


def dfs_recorrido(
    grafo: GrafoLogistico,
    origen: str,
    evitar_restringidos: bool = True,
) -> List[str]:
    """
    Realiza un recorrido en profundidad completo a partir del vértice origen.

    Parameters
    ----------
    grafo : GrafoLogistico
    origen : str
    evitar_restringidos : bool

    Returns
    -------
    list[str]
        Lista de IDs de nodos en el orden en que fueron descubiertos por DFS.
    """
    if origen not in grafo:
        raise KeyError(f"Nodo '{origen}' no existe en el grafo.")

    visitados: Set[str] = set()
    orden_visita: List[str] = []

    def _dfs_visitar(u: str) -> None:
        visitados.add(u)
        orden_visita.append(u)
        for arista in grafo.obtener_aristas(u):
            v = arista.destino
            if v not in visitados:
                if evitar_restringidos and _restringido(grafo, v):
                    continue
                _dfs_visitar(v)

    _dfs_visitar(origen)
    return orden_visita


def dfs_todos_los_caminos(
    grafo: GrafoLogistico,
    origen: str,
    destino: str,
    max_saltos: int = 10,
    evitar_restringidos: bool = True,
) -> List[List[str]]:
    """
    Encuentra todos los caminos simples posibles entre origen y destino mediante DFS con backtracking.

    Parameters
    ----------
    grafo : GrafoLogistico
    origen : str
    destino : str
    max_saltos : int
        Límite de profundidad para evitar explosión combinatoria.
    evitar_restringidos : bool

    Returns
    -------
    list[list[str]]
        Lista con todas las secuencias de caminos válidos.
    """
    if origen not in grafo or destino not in grafo:
        raise KeyError(f"Nodo '{origen}' o '{destino}' no existe en el grafo.")

    caminos: List[List[str]] = []

    def _backtrack(u: str, camino_actual: List[str], visitados: Set[str]) -> None:
        if len(camino_actual) > max_saltos:
            return

        if u == destino:
            caminos.append(list(camino_actual))
            return

        for arista in grafo.obtener_aristas(u):
            v = arista.destino
            if v not in visitados:
                if evitar_restringidos and _restringido(grafo, v) and v != destino:
                    continue
                visitados.add(v)
                camino_actual.append(v)
                _backtrack(v, camino_actual, visitados)
                camino_actual.pop()
                visitados.remove(v)

    _backtrack(origen, [origen], {origen})
    return caminos


def dfs_resumen_rutas(
    grafo: GrafoLogistico,
    origen: str,
    destino: str,
    evitar_restringidos: bool = True,
) -> List[Dict[str, any]]:
    """
    Calcula todas las rutas simples por DFS y extrae métricas de distancia y tiempo para cada una.
    """
    caminos = dfs_todos_los_caminos(grafo, origen, destino, evitar_restringidos=evitar_restringidos)
    resumen = []

    for cam in caminos:
        dist_total = 0.0
        tiempo_total = 0.0
        valido = True
        for i in range(len(cam) - 1):
            arista = grafo.obtener_arista(cam[i], cam[i + 1])
            if arista:
                dist_total += arista.distancia_km
                tiempo_total += arista.tiempo_h
            else:
                valido = False
                break
        if valido:
            resumen.append({
                "camino": cam,
                "saltos": len(cam) - 1,
                "distancia_km": round(dist_total, 2),
                "tiempo_h": round(tiempo_total, 2),
            })

    # Ordenar por tiempo total ascendente
    resumen.sort(key=lambda x: x["tiempo_h"])
    return resumen
