"""
test_bellman_ford.py — Pruebas unitarias para Bellman-Ford.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.models.nodo import Nodo
from src.models.arista import Arista
from src.models.grafo_logistico import GrafoLogistico
from src.algorithms.bellman_ford import bellman_ford, reconstruir_camino_bf
from src.algorithms.dijkstra import dijkstra


def _crear_grafo_prueba() -> GrafoLogistico:
    """Crea un grafo de prueba con 5 nodos."""
    g = GrafoLogistico()

    g.agregar_nodo(Nodo("P01", "Pesca A", "P"))
    g.agregar_nodo(Nodo("P02", "Pesca B", "P"))
    g.agregar_nodo(Nodo("F01", "Centro Frío", "F", capacidad_frio_kg=2000))
    g.agregar_nodo(Nodo("A01", "Acopio", "A"))
    g.agregar_nodo(Nodo("V01", "Mercado", "V"))

    g.agregar_arista(Arista("P01", "F01", distancia_km=10, tiempo_h=0.5, costo_cop=35000))
    g.agregar_arista(Arista("P01", "A01", distancia_km=15, tiempo_h=0.8, costo_cop=52500))
    g.agregar_arista(Arista("P02", "F01", distancia_km=8, tiempo_h=0.3, costo_cop=28000))
    g.agregar_arista(Arista("F01", "V01", distancia_km=200, tiempo_h=4.0, costo_cop=700000))
    g.agregar_arista(Arista("A01", "F01", distancia_km=5, tiempo_h=0.2, costo_cop=17500))
    g.agregar_arista(Arista("A01", "V01", distancia_km=210, tiempo_h=4.5, costo_cop=735000))

    return g


def test_bellman_ford_camino_basico():
    """Verifica que BF encuentra distancias correctas."""
    g = _crear_grafo_prueba()
    dist, prev, ciclo = bellman_ford(g, "P01", criterio="tiempo_h")
    assert dist["P01"] == 0.0
    assert dist["F01"] == 0.5  # P01 → F01 directo
    assert dist["V01"] < float("inf")
    print(f"  [✓] test_bellman_ford_camino_basico (V01={dist['V01']:.2f}h)")


def test_bellman_ford_sin_ciclo_negativo():
    """Verifica que no detecta ciclos negativos en un grafo normal."""
    g = _crear_grafo_prueba()
    _, _, ciclo = bellman_ford(g, "P01", criterio="tiempo_h")
    assert ciclo is False
    print("  [✓] test_bellman_ford_sin_ciclo_negativo")


def test_bellman_ford_consistencia_dijkstra():
    """Verifica que BF y Dijkstra dan los mismos resultados."""
    g = _crear_grafo_prueba()
    dist_bf, _, _ = bellman_ford(g, "P01", criterio="tiempo_h")

    for nodo in g.nodos:
        t_dj, _ = dijkstra(g, "P01", nodo.id, criterio="tiempo_h")
        t_bf = dist_bf[nodo.id]
        # Ambos infinitos = nodo inalcanzable → ok
        if t_bf == float("inf") and t_dj == float("inf"):
            continue
        assert abs(t_bf - t_dj) < 0.0001, \
            f"Inconsistencia en {nodo.id}: BF={t_bf} vs DJ={t_dj}"

    print("  [✓] test_bellman_ford_consistencia_dijkstra")


def test_reconstruir_camino_bf():
    """Verifica la reconstrucción del camino."""
    g = _crear_grafo_prueba()
    _, prev, _ = bellman_ford(g, "P01", criterio="tiempo_h")
    camino = reconstruir_camino_bf(prev, "V01")
    assert camino[0] == "P01"
    assert camino[-1] == "V01"
    assert len(camino) >= 2
    print(f"  [✓] test_reconstruir_camino_bf: {' → '.join(camino)}")


def test_bellman_ford_nodo_inexistente():
    """Verifica que lanza KeyError con nodo inexistente."""
    g = _crear_grafo_prueba()
    try:
        bellman_ford(g, "INEXISTENTE")
        assert False, "Debería haber lanzado KeyError"
    except KeyError:
        pass
    print("  [✓] test_bellman_ford_nodo_inexistente")


def test_bellman_ford_evitar_restringidos():
    """Verifica que Bellman-Ford evita nodos con restricción ambiental como intermedios."""
    g = GrafoLogistico()
    g.agregar_nodo(Nodo("P01", "Pesca", "P"))
    g.agregar_nodo(Nodo("H01", "Hábitat", "H", restriccion_ambiental=True))
    g.agregar_nodo(Nodo("A01", "Acopio", "A"))
    g.agregar_nodo(Nodo("V01", "Mercado", "V"))

    g.agregar_arista(Arista("P01", "H01", distancia_km=2, tiempo_h=0.1))
    g.agregar_arista(Arista("H01", "V01", distancia_km=2, tiempo_h=0.1))
    g.agregar_arista(Arista("P01", "A01", distancia_km=5, tiempo_h=0.3))
    g.agregar_arista(Arista("A01", "V01", distancia_km=5, tiempo_h=0.3))

    dist_libre, prev_libre, _ = bellman_ford(
        g, "P01", criterio="tiempo_h", evitar_restringidos=False
    )
    assert "H01" in reconstruir_camino_bf(prev_libre, "V01")
    assert abs(dist_libre["V01"] - 0.2) < 1e-6

    dist_ev, prev_ev, _ = bellman_ford(
        g, "P01", criterio="tiempo_h", evitar_restringidos=True
    )
    camino_ev = reconstruir_camino_bf(prev_ev, "V01")
    assert "H01" not in camino_ev
    assert camino_ev == ["P01", "A01", "V01"]
    assert abs(dist_ev["V01"] - 0.6) < 1e-6
    assert abs(dist_ev["H01"] - 0.1) < 1e-6
    print("  [✓] test_bellman_ford_evitar_restringidos")


if __name__ == "__main__":
    print("\n═══ PRUEBAS DE BELLMAN-FORD ═══\n")
    test_bellman_ford_camino_basico()
    test_bellman_ford_sin_ciclo_negativo()
    test_bellman_ford_consistencia_dijkstra()
    test_reconstruir_camino_bf()
    test_bellman_ford_nodo_inexistente()
    test_bellman_ford_evitar_restringidos()
    print("\n  ✅ Todas las pruebas pasaron.\n")
