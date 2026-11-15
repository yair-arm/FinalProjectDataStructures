"""
test_facility_location.py — Pruebas para la localización de centros de frío.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.models.nodo import Nodo
from src.models.arista import Arista
from src.models.grafo_logistico import GrafoLogistico
from src.optimization.facility_location import resolver_localizacion


def _crear_grafo_fl() -> GrafoLogistico:
    """Grafo de prueba para localización de instalaciones."""
    g = GrafoLogistico()

    # Puntos de pesca
    g.agregar_nodo(Nodo("P01", "Pesca A", "P", 4.35, -72.12, produccion_kg_dia=65))
    g.agregar_nodo(Nodo("P02", "Pesca B", "P", 4.33, -72.10, produccion_kg_dia=40))
    g.agregar_nodo(Nodo("P03", "Pesca C", "P", 4.29, -72.06, produccion_kg_dia=25))

    # Candidatos a centro de frío
    g.agregar_nodo(Nodo(
        "F01", "Centro 1", "F", 4.345, -72.115,
        capacidad_frio_kg=2000, costo_fijo=5000000,
        tiene_energia=True,
    ))
    g.agregar_nodo(Nodo(
        "F02", "Centro 2", "F", 4.312, -72.082,
        capacidad_frio_kg=5000, costo_fijo=3000000,
        tiene_energia=True,
    ))

    # Mercado
    g.agregar_nodo(Nodo("V01", "Mercado", "V", 4.60, -74.08))

    # Aristas: pesca → centros
    g.agregar_arista(Arista("P01", "F01", tiempo_h=0.3, distancia_km=5))
    g.agregar_arista(Arista("P01", "F02", tiempo_h=1.0, distancia_km=15))
    g.agregar_arista(Arista("P02", "F01", tiempo_h=0.5, distancia_km=7))
    g.agregar_arista(Arista("P02", "F02", tiempo_h=0.8, distancia_km=12))
    g.agregar_arista(Arista("P03", "F01", tiempo_h=2.0, distancia_km=30))
    g.agregar_arista(Arista("P03", "F02", tiempo_h=0.6, distancia_km=10))

    # Aristas: centros → mercado
    g.agregar_arista(Arista("F01", "V01", tiempo_h=5.0, distancia_km=250))
    g.agregar_arista(Arista("F02", "V01", tiempo_h=4.5, distancia_km=220))

    return g


def test_localizacion_greedy():
    """Verifica que el greedy encuentra una solución factible."""
    g = _crear_grafo_fl()
    resultado = resolver_localizacion(g, metodo="greedy", tiempo_max_h=4.0)
    assert len(resultado.centros_abiertos) > 0
    assert resultado.cobertura > 0
    print(f"  [✓] test_localizacion_greedy:")
    print(f"       Centros: {resultado.centros_abiertos}")
    print(f"       Cobertura: {resultado.cobertura:.0f}%")


def test_localizacion_cobertura_total():
    """Verifica que con tiempo suficiente se cubren todos los puntos."""
    g = _crear_grafo_fl()
    resultado = resolver_localizacion(g, metodo="greedy", tiempo_max_h=10.0)
    assert resultado.cobertura == 100.0
    print(f"  [✓] test_localizacion_cobertura_total: 100% cobertura")


def test_localizacion_sin_candidatos():
    """Verifica manejo de grafo sin candidatos."""
    g = GrafoLogistico()
    g.agregar_nodo(Nodo("P01", "Pesca", "P"))
    resultado = resolver_localizacion(g, metodo="greedy")
    assert len(resultado.centros_abiertos) == 0
    print("  [✓] test_localizacion_sin_candidatos")


if __name__ == "__main__":
    print("\n═══ PRUEBAS DE LOCALIZACIÓN DE CENTROS ═══\n")
    test_localizacion_greedy()
    test_localizacion_cobertura_total()
    test_localizacion_sin_candidatos()
    print("\n  ✅ Todas las pruebas pasaron.\n")

