"""
test_grafo.py — Pruebas unitarias para el grafo logístico.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.models.nodo import Nodo
from src.models.arista import Arista
from src.models.grafo_logistico import GrafoLogistico


def test_crear_nodo():
    """Verifica la creación correcta de un nodo."""
    nodo = Nodo(
        id="P01",
        nombre="Punto de Pesca 1",
        tipo="P",
        latitud=4.35,
        longitud=-72.12,
        produccion_kg_dia=65.75,
    )
    assert nodo.id == "P01"
    assert nodo.tipo == "P"
    assert nodo.es_origen is True
    assert nodo.es_destino is False
    assert nodo.coordenadas == (4.35, -72.12)
    print("  [✓] test_crear_nodo")


def test_crear_arista():
    """Verifica la creación de una arista con peso multicriterio."""
    arista = Arista(
        origen="P01",
        destino="F01",
        distancia_km=10.0,
        tiempo_h=0.5,
        costo_cop=35000,
        riesgo_termico=0.15,
        estado_via="buena",
    )
    assert arista.origen == "P01"
    assert arista.destino == "F01"
    assert arista.peso_default > 0
    assert arista.perdida_esperada >= 0
    print("  [✓] test_crear_arista")


def test_grafo_agregar_nodos():
    """Verifica la adición de nodos al grafo."""
    g = GrafoLogistico()
    g.agregar_nodo(Nodo("P01", "Pesca 1", "P", 4.35, -72.12, produccion_kg_dia=50))
    g.agregar_nodo(Nodo("F01", "Frío 1", "F", 4.34, -72.11, capacidad_frio_kg=2000))
    g.agregar_nodo(Nodo("V01", "Venta 1", "V", 4.60, -74.08))

    assert g.num_nodos == 3
    assert len(g.puntos_pesca()) == 1
    assert len(g.centros_frio()) == 1
    assert len(g.mercados()) == 1
    print("  [✓] test_grafo_agregar_nodos")


def test_grafo_agregar_aristas():
    """Verifica la adición de aristas y cálculo de vecinos."""
    g = GrafoLogistico()
    g.agregar_nodo(Nodo("P01", "Pesca 1", "P", 4.35, -72.12))
    g.agregar_nodo(Nodo("F01", "Frío 1", "F", 4.34, -72.11))
    g.agregar_nodo(Nodo("V01", "Venta 1", "V", 4.60, -74.08))

    g.agregar_arista(Arista("P01", "F01", distancia_km=5, tiempo_h=0.2))
    g.agregar_arista(Arista("F01", "V01", distancia_km=200, tiempo_h=4.0))

    assert g.num_aristas == 2
    assert "F01" in g.vecinos("P01")
    assert "V01" in g.vecinos("F01")
    assert g.vecinos("V01") == []
    print("  [✓] test_grafo_agregar_aristas")


def test_grafo_arista_auto():
    """Verifica creación automática de arista con Haversine."""
    g = GrafoLogistico()
    g.agregar_nodo(Nodo("A", "Nodo A", "P", 4.3128, -72.0826))
    g.agregar_nodo(Nodo("B", "Nodo B", "V", 4.1420, -73.6266))

    arista = g.agregar_arista_auto("A", "B")
    assert arista.distancia_km > 100  # ~170 km aprox
    assert arista.tiempo_h > 0
    print(f"  [✓] test_grafo_arista_auto (dist={arista.distancia_km:.1f} km)")


def test_grafo_resumen():
    """Verifica que el resumen se genera sin errores."""
    g = GrafoLogistico()
    g.agregar_nodo(Nodo("P01", "Pesca", "P", produccion_kg_dia=100))
    g.agregar_nodo(Nodo("F01", "Frío", "F", capacidad_frio_kg=2000))
    texto = g.resumen()
    assert "GRAFO LOGÍSTICO" in texto
    assert "1" in texto
    print("  [✓] test_grafo_resumen")


def test_nodo_tipo_invalido():
    """Verifica que un tipo de nodo inválido lance error."""
    try:
        Nodo("X01", "Inválido", "Z")
        assert False, "Debería haber lanzado ValueError"
    except ValueError:
        pass
    print("  [✓] test_nodo_tipo_invalido")


if __name__ == "__main__":
    print("\n═══ PRUEBAS DE GRAFO LOGÍSTICO ═══\n")
    test_crear_nodo()
    test_crear_arista()
    test_grafo_agregar_nodos()
    test_grafo_agregar_aristas()
    test_grafo_arista_auto()
    test_grafo_resumen()
    test_nodo_tipo_invalido()
    print("\n  ✅ Todas las pruebas pasaron.\n")

