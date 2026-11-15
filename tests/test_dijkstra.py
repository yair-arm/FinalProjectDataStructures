"""
test_dijkstra.py — Pruebas unitarias para el algoritmo de Dijkstra.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.models.nodo import Nodo
from src.models.arista import Arista
from src.models.grafo_logistico import GrafoLogistico
from src.algorithms.dijkstra import dijkstra, dijkstra_completo


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


def test_dijkstra_camino_existe():
    """Verifica que Dijkstra encuentra un camino válido."""
    g = _crear_grafo_prueba()
    dist, camino = dijkstra(g, "P01", "V01", criterio="tiempo_h")
    assert dist < float("inf")
    assert camino[0] == "P01"
    assert camino[-1] == "V01"
    assert len(camino) >= 2
    print(f"  [✓] test_dijkstra_camino_existe: {' → '.join(camino)} (t={dist:.2f}h)")


def test_dijkstra_camino_optimo():
    """Verifica que la ruta más rápida pasa por F01."""
    g = _crear_grafo_prueba()
    dist, camino = dijkstra(g, "P01", "V01", criterio="tiempo_h")
    # P01 → F01 → V01 = 0.5 + 4.0 = 4.5h
    # P01 → A01 → V01 = 0.8 + 4.5 = 5.3h
    # P01 → A01 → F01 → V01 = 0.8 + 0.2 + 4.0 = 5.0h
    assert "F01" in camino
    assert dist <= 4.5 + 0.01
    print(f"  [✓] test_dijkstra_camino_optimo: dist={dist:.2f}h")


def test_dijkstra_sin_camino():
    """Verifica el manejo de nodos sin camino."""
    g = GrafoLogistico()
    g.agregar_nodo(Nodo("A", "Nodo A", "P"))
    g.agregar_nodo(Nodo("B", "Nodo B", "V"))
    # Sin aristas
    dist, camino = dijkstra(g, "A", "B")
    assert dist == float("inf")
    assert camino == []
    print("  [✓] test_dijkstra_sin_camino")


def test_dijkstra_completo():
    """Verifica Dijkstra desde un origen a todos los nodos."""
    g = _crear_grafo_prueba()
    resultados = dijkstra_completo(g, "P01", criterio="tiempo_h")
    assert resultados["P01"][0] == 0.0
    assert resultados["V01"][0] < float("inf")
    assert resultados["F01"][0] < float("inf")
    print(f"  [✓] test_dijkstra_completo: {len(resultados)} destinos calculados")


def test_dijkstra_nodo_inexistente():
    """Verifica que se lance error con nodo inexistente."""
    g = _crear_grafo_prueba()
    try:
        dijkstra(g, "INEXISTENTE", "V01")
        assert False, "Debería haber lanzado KeyError"
    except KeyError:
        pass
    print("  [✓] test_dijkstra_nodo_inexistente")


def test_dijkstra_evitar_restringidos():
    """Verifica que evitar_restringidos=True evita nodos H intermedios."""
    g = GrafoLogistico()
    g.agregar_nodo(Nodo("P01", "Pesca", "P"))
    g.agregar_nodo(Nodo("H01", "Hábitat", "H", restriccion_ambiental=True))
    g.agregar_nodo(Nodo("A01", "Acopio", "A"))
    g.agregar_nodo(Nodo("V01", "Mercado", "V"))

    # Atajo tentador por H01 (0.2h total vs 0.6h por A01)
    g.agregar_arista(Arista("P01", "H01", distancia_km=2, tiempo_h=0.1))
    g.agregar_arista(Arista("H01", "V01", distancia_km=2, tiempo_h=0.1))
    g.agregar_arista(Arista("P01", "A01", distancia_km=5, tiempo_h=0.3))
    g.agregar_arista(Arista("A01", "V01", distancia_km=5, tiempo_h=0.3))

    dist_libre, camino_libre = dijkstra(
        g, "P01", "V01", criterio="tiempo_h", evitar_restringidos=False
    )
    assert "H01" in camino_libre
    assert abs(dist_libre - 0.2) < 1e-6

    dist_ev, camino_ev = dijkstra(
        g, "P01", "V01", criterio="tiempo_h", evitar_restringidos=True
    )
    assert "H01" not in camino_ev
    assert camino_ev == ["P01", "A01", "V01"]
    assert abs(dist_ev - 0.6) < 1e-6

    # Pero H01 sí puede ser destino directo
    dist_dest, camino_dest = dijkstra(
        g, "P01", "H01", criterio="tiempo_h", evitar_restringidos=True
    )
    assert camino_dest == ["P01", "H01"]
    assert abs(dist_dest - 0.1) < 1e-6
    print("  [✓] test_dijkstra_evitar_restringidos")


if __name__ == "__main__":
    print("\n═══ PRUEBAS DE DIJKSTRA ═══\n")
    test_dijkstra_camino_existe()
    test_dijkstra_camino_optimo()
    test_dijkstra_sin_camino()
    test_dijkstra_completo()
    test_dijkstra_nodo_inexistente()
    test_dijkstra_evitar_restringidos()
    print("\n  ✅ Todas las pruebas pasaron.\n")

