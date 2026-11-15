"""
test_bfs_dfs.py — Pruebas unitarias para algoritmos BFS y DFS.
"""

import pytest
from src.models.nodo import Nodo
from src.models.arista import Arista
from src.models.grafo_logistico import GrafoLogistico
from src.algorithms.bfs import bfs_recorrido, bfs_camino, bfs_nodo_mas_cercano_por_tipo
from src.algorithms.dfs import dfs_recorrido, dfs_todos_los_caminos, dfs_resumen_rutas


@pytest.fixture
def grafo_prueba():
    g = GrafoLogistico()
    # Nodos
    g.agregar_nodo(Nodo(id="P01", nombre="Pesca 1", tipo="P"))
    g.agregar_nodo(Nodo(id="M01", nombre="Muelle 1", tipo="M"))
    g.agregar_nodo(Nodo(id="A01", nombre="Acopio 1", tipo="A"))
    g.agregar_nodo(Nodo(id="F01", nombre="Frío 1", tipo="F"))
    g.agregar_nodo(Nodo(id="H01", nombre="Hábitat 1", tipo="H", restriccion_ambiental=True))
    g.agregar_nodo(Nodo(id="V01", nombre="Venta 1", tipo="V"))

    # Aristas
    g.agregar_arista(Arista(origen="P01", destino="M01", distancia_km=5.0, tiempo_h=0.3))
    g.agregar_arista(Arista(origen="M01", destino="A01", distancia_km=10.0, tiempo_h=0.5))
    g.agregar_arista(Arista(origen="P01", destino="H01", distancia_km=2.0, tiempo_h=0.1))
    g.agregar_arista(Arista(origen="H01", destino="A01", distancia_km=2.0, tiempo_h=0.1))
    g.agregar_arista(Arista(origen="A01", destino="F01", distancia_km=8.0, tiempo_h=0.4))
    g.agregar_arista(Arista(origen="F01", destino="V01", distancia_km=50.0, tiempo_h=1.0))
    return g


def test_bfs_recorrido_basico(grafo_prueba):
    orden = bfs_recorrido(grafo_prueba, "P01", evitar_restringidos=True)
    assert "P01" in orden
    assert "M01" in orden
    assert "H01" not in orden  # Debe excluir el hábitat protegido
    assert orden[0] == "P01"


def test_bfs_camino_minimo_saltos(grafo_prueba):
    saltos, camino = bfs_camino(grafo_prueba, "P01", "F01", evitar_restringidos=True)
    assert saltos == 3
    assert camino == ["P01", "M01", "A01", "F01"]


def test_bfs_nodo_mas_cercano(grafo_prueba):
    nodo_id, saltos, camino = bfs_nodo_mas_cercano_por_tipo(grafo_prueba, "P01", tipos_objetivo=("A", "F"))
    assert nodo_id == "A01"
    assert saltos == 2
    assert camino == ["P01", "M01", "A01"]


def test_dfs_recorrido_basico(grafo_prueba):
    orden = dfs_recorrido(grafo_prueba, "P01", evitar_restringidos=True)
    assert orden[0] == "P01"
    assert "H01" not in orden
    assert "V01" in orden


def test_dfs_todos_los_caminos(grafo_prueba):
    caminos = dfs_todos_los_caminos(grafo_prueba, "P01", "V01", evitar_restringidos=True)
    assert len(caminos) == 1
    assert caminos[0] == ["P01", "M01", "A01", "F01", "V01"]


def test_dfs_con_atajo_restringido(grafo_prueba):
    # Si permitimos restringidos, debe hallar 2 caminos
    caminos_todos = dfs_todos_los_caminos(grafo_prueba, "P01", "V01", evitar_restringidos=False)
    assert len(caminos_todos) == 2
