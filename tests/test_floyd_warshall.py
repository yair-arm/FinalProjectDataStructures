"""
test_floyd_warshall.py — Pruebas unitarias para Floyd-Warshall.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.models.nodo import Nodo
from src.models.arista import Arista
from src.models.grafo_logistico import GrafoLogistico
from src.algorithms.floyd_warshall import floyd_warshall, reconstruir_camino, matriz_a_tabla


def _crear_grafo_prueba() -> GrafoLogistico:
    """Crea un grafo de prueba con 4 nodos."""
    g = GrafoLogistico()

    g.agregar_nodo(Nodo("P01", "Pesca A", "P"))
    g.agregar_nodo(Nodo("F01", "Centro Frío", "F", capacidad_frio_kg=2000))
    g.agregar_nodo(Nodo("A01", "Acopio", "A"))
    g.agregar_nodo(Nodo("V01", "Mercado", "V"))

    g.agregar_arista(Arista("P01", "F01", distancia_km=10, tiempo_h=0.5))
    g.agregar_arista(Arista("P01", "A01", distancia_km=15, tiempo_h=0.8))
    g.agregar_arista(Arista("A01", "F01", distancia_km=5, tiempo_h=0.2))
    g.agregar_arista(Arista("F01", "V01", distancia_km=200, tiempo_h=4.0))
    g.agregar_arista(Arista("A01", "V01", distancia_km=210, tiempo_h=4.5))

    return g


def test_floyd_warshall_diagonal_cero():
    """Verifica que la diagonal de la matriz es cero."""
    g = _crear_grafo_prueba()
    dist, _ = floyd_warshall(g, criterio="tiempo_h")
    for nodo in g.nodos:
        assert dist[nodo.id][nodo.id] == 0.0, \
            f"dist[{nodo.id}][{nodo.id}] debería ser 0"
    print("  [✓] test_floyd_warshall_diagonal_cero")


def test_floyd_warshall_camino_intermedio():
    """Verifica que encuentra rutas pasando por nodos intermedios."""
    g = _crear_grafo_prueba()
    dist, _ = floyd_warshall(g, criterio="tiempo_h")

    # P01 → A01 → F01 = 0.8 + 0.2 = 1.0h  vs  P01 → F01 = 0.5h
    # El directo es mejor, así que dist[P01][F01] = 0.5
    assert abs(dist["P01"]["F01"] - 0.5) < 0.001

    # P01 → V01 vía F01 = 0.5 + 4.0 = 4.5h  (óptimo)
    assert abs(dist["P01"]["V01"] - 4.5) < 0.001

    print(f"  [✓] test_floyd_warshall_camino_intermedio (P01→V01={dist['P01']['V01']:.2f}h)")


def test_reconstruir_camino_fw():
    """Verifica la reconstrucción del camino."""
    g = _crear_grafo_prueba()
    _, sig = floyd_warshall(g, criterio="tiempo_h")
    camino = reconstruir_camino(sig, "P01", "V01")
    assert camino[0] == "P01"
    assert camino[-1] == "V01"
    assert len(camino) >= 2
    print(f"  [✓] test_reconstruir_camino_fw: {' → '.join(camino)}")


def test_reconstruir_camino_sin_ruta():
    """Verifica camino vacío para nodos no conectados."""
    g = _crear_grafo_prueba()
    _, sig = floyd_warshall(g, criterio="tiempo_h")
    # V01 → P01 no tiene camino (grafo dirigido)
    camino = reconstruir_camino(sig, "V01", "P01")
    assert camino == []
    print("  [✓] test_reconstruir_camino_sin_ruta")


def test_matriz_a_tabla():
    """Verifica que la tabla se genera sin errores."""
    g = _crear_grafo_prueba()
    dist, _ = floyd_warshall(g, criterio="tiempo_h")
    tabla = matriz_a_tabla(dist, ["P01", "F01", "V01"])
    assert "P01" in tabla
    assert "V01" in tabla
    assert len(tabla) > 0
    print("  [✓] test_matriz_a_tabla")


if __name__ == "__main__":
    print("\n═══ PRUEBAS DE FLOYD-WARSHALL ═══\n")
    test_floyd_warshall_diagonal_cero()
    test_floyd_warshall_camino_intermedio()
    test_reconstruir_camino_fw()
    test_reconstruir_camino_sin_ruta()
    test_matriz_a_tabla()
    print("\n  ✅ Todas las pruebas pasaron.\n")
