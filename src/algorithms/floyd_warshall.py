"""
floyd_warshall.py — Algoritmo de Floyd-Warshall.

Calcula las distancias mínimas entre TODOS los pares de nodos.
Útil para construir la matriz completa de costos logísticos.

Complejidad: O(V³)
"""

from __future__ import annotations
from typing import Dict, List, Optional, Tuple

from ..models.grafo_logistico import GrafoLogistico


def floyd_warshall(
    grafo: GrafoLogistico,
    criterio: str = "peso",
    evitar_restringidos: bool = False
) -> Tuple[Dict[str, Dict[str, float]], Dict[str, Dict[str, Optional[str]]]]:
    """
    Ejecuta Floyd-Warshall sobre el grafo logístico.

    Parameters
    ----------
    grafo : GrafoLogistico
    criterio : str
        'peso', 'distancia_km', 'tiempo_h', 'costo_cop'.
    evitar_restringidos : bool
        Si es True, los nodos con restricción ambiental no actúan como
        intermedios (k) en ningún camino.

    Returns
    -------
    tuple (dist, siguiente)
        dist : dict[str, dict[str, float]]
            Matriz de distancias mínimas.
        siguiente : dict[str, dict[str, str | None]]
            Matriz de nodos siguientes para reconstruir caminos.
    """
    ids = [n.id for n in grafo.nodos]
    INF = float("inf")

    # Inicializar matrices
    dist: Dict[str, Dict[str, float]] = {
        i: {j: INF for j in ids} for i in ids
    }
    siguiente: Dict[str, Dict[str, Optional[str]]] = {
        i: {j: None for j in ids} for i in ids
    }

    # Diagonal = 0
    for i in ids:
        dist[i][i] = 0.0

    # Cargar aristas
    for arista in grafo.aristas:
        if criterio == "peso":
            peso = arista.peso_default
        else:
            peso = getattr(arista, criterio, arista.peso_default)

        if peso < dist[arista.origen][arista.destino]:
            dist[arista.origen][arista.destino] = peso
            siguiente[arista.origen][arista.destino] = arista.destino

    # Algoritmo principal: triple bucle
    restringidos = {n.id for n in grafo.nodos if n.restriccion_ambiental}
    for k in ids:
        if evitar_restringidos and k in restringidos:
            continue
        for i in ids:
            for j in ids:
                if dist[i][k] + dist[k][j] < dist[i][j]:
                    dist[i][j] = dist[i][k] + dist[k][j]
                    siguiente[i][j] = siguiente[i][k]

    return dist, siguiente


def reconstruir_camino(
    siguiente: Dict[str, Dict[str, Optional[str]]],
    origen: str,
    destino: str
) -> List[str]:
    """
    Reconstruye el camino mínimo usando la matriz 'siguiente'
    obtenida de Floyd-Warshall.

    Returns
    -------
    list[str] : secuencia de IDs de nodos, o lista vacía si no hay camino.
    """
    if siguiente[origen][destino] is None:
        return []

    camino = [origen]
    actual = origen
    while actual != destino:
        actual = siguiente[actual][destino]
        if actual is None:
            return []
        camino.append(actual)

    return camino


def matriz_a_tabla(
    dist: Dict[str, Dict[str, float]],
    ids: Optional[List[str]] = None
) -> str:
    """
    Formatea la matriz de distancias como tabla legible.
    """
    if ids is None:
        ids = sorted(dist.keys())

    # Encabezado
    ancho = 12
    header = " " * ancho + "".join(f"{i:>{ancho}}" for i in ids)
    lineas = [header, "─" * len(header)]

    for i in ids:
        fila = f"{i:<{ancho}}"
        for j in ids:
            val = dist[i][j]
            if val == float("inf"):
                fila += f"{'∞':>{ancho}}"
            else:
                fila += f"{val:>{ancho}.4f}"
        lineas.append(fila)

    return "\n".join(lineas)

