"""
test_cold_chain.py — Pruebas unitarias para la simulación de cadena de frío.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.models.nodo import Nodo
from src.models.arista import Arista
from src.models.grafo_logistico import GrafoLogistico
from src.optimization.cold_chain import SimuladorCadenaFrio
from src.optimization.itinerarios import calcular_itinerarios
from src.utils.constants import FACTOR_DETERIORO_ZONA_D, TIEMPO_TRANSBORDO_MUELLE_H


def _crear_grafo_frio() -> GrafoLogistico:
    """Grafo de prueba con y sin centros de frío."""
    g = GrafoLogistico()

    g.agregar_nodo(Nodo("P01", "Pesca", "P", produccion_kg_dia=100))
    g.agregar_nodo(Nodo("F01", "Frío", "F", capacidad_frio_kg=5000))
    g.agregar_nodo(Nodo("A01", "Acopio", "A", capacidad_frio_kg=0))
    g.agregar_nodo(Nodo("V01", "Mercado", "V"))

    g.agregar_arista(Arista("P01", "F01", distancia_km=10, tiempo_h=0.5))
    g.agregar_arista(Arista("P01", "A01", distancia_km=15, tiempo_h=1.5))
    g.agregar_arista(Arista("F01", "V01", distancia_km=200, tiempo_h=4.0))
    g.agregar_arista(Arista("A01", "V01", distancia_km=210, tiempo_h=5.0))

    return g


def test_simulacion_con_frio():
    """Simula ruta pasando por centro de frío."""
    g = _crear_grafo_frio()
    sim = SimuladorCadenaFrio(g, tiempo_limite_h=4.0)
    resultado = sim.simular_ruta(["P01", "F01", "V01"], 100.0)

    assert resultado.kg_inicial == 100.0
    assert resultado.kg_final > 0
    assert resultado.kg_final <= 100.0
    assert resultado.num_paradas_frio >= 1
    assert resultado.tiempo_total_h > 0
    print(f"  [✓] test_simulacion_con_frio: {resultado.kg_final:.1f} kg final, "
          f"{resultado.num_paradas_frio} parada(s) frío")


def test_simulacion_sin_frio():
    """Simula ruta sin ningún centro de frío."""
    g = _crear_grafo_frio()
    sim = SimuladorCadenaFrio(g, tiempo_limite_h=4.0)
    resultado = sim.simular_ruta(["P01", "A01", "V01"], 100.0)

    assert resultado.num_paradas_frio == 0
    assert resultado.perdida_kg > 0  # Hay deterioro sin frío
    assert resultado.cumple_limite is False  # 1.5 + 5.0 = 6.5h > 4h
    print(f"  [✓] test_simulacion_sin_frio: pérdida={resultado.perdida_pct:.1f}%, "
          f"cumple={resultado.cumple_limite}")


def test_simulacion_deterioro_mayor_sin_frio():
    """Verifica que sin frío el deterioro es mayor que con frío."""
    g = _crear_grafo_frio()
    sim = SimuladorCadenaFrio(g, tiempo_limite_h=4.0)

    con_frio = sim.simular_ruta(["P01", "F01", "V01"], 100.0)
    sin_frio = sim.simular_ruta(["P01", "A01", "V01"], 100.0)

    # Sin frío debería tener más pérdida (ruta más larga y sin refrigeración)
    assert sin_frio.perdida_pct >= con_frio.perdida_pct
    print(f"  [✓] test_simulacion_deterioro_mayor_sin_frio: "
          f"con_frio={con_frio.perdida_pct:.1f}% vs sin_frio={sin_frio.perdida_pct:.1f}%")


def test_simulacion_ruta_corta():
    """Verifica que una ruta corta cumple el límite térmico."""
    g = _crear_grafo_frio()
    sim = SimuladorCadenaFrio(g, tiempo_limite_h=4.0)
    resultado = sim.simular_ruta(["P01", "F01"], 50.0)

    assert resultado.tiempo_total_h == 0.5
    assert resultado.kg_final > 0
    # F01 tiene frío, el timer se resetea → tiempo_sin_frio = 0
    assert resultado.cumple_limite is True
    print(f"  [✓] test_simulacion_ruta_corta: {resultado.tiempo_total_h:.2f}h, "
          f"cumple={resultado.cumple_limite}")


def test_simulacion_resumen():
    """Verifica que el resumen se genera sin errores."""
    g = _crear_grafo_frio()
    sim = SimuladorCadenaFrio(g, tiempo_limite_h=4.0)
    resultado = sim.simular_ruta(["P01", "F01", "V01"], 80.0)
    texto = resultado.resumen()
    assert "SIMULACIÓN" in texto
    assert "Kg" in texto or "kg" in texto.lower()
    print("  [✓] test_simulacion_resumen")


def test_efecto_zona_deterioro_y_muelle():
    """Verifica el efecto de zona de deterioro (D) y muelle (M) en cadena de frío."""
    g = GrafoLogistico()
    g.agregar_nodo(Nodo("P01", "Pesca", "P", produccion_kg_dia=100))
    g.agregar_nodo(Nodo("M01", "Muelle", "M", tiene_muelle=True))
    g.agregar_nodo(Nodo("D01", "Zona Deterioro", "D"))
    g.agregar_nodo(Nodo("A01", "Acopio", "A", capacidad_frio_kg=0))
    g.agregar_nodo(Nodo("F01", "Frío", "F", capacidad_frio_kg=2000))

    g.agregar_arista(Arista("P01", "A01", distancia_km=10, tiempo_h=1.0))
    g.agregar_arista(Arista("P01", "D01", distancia_km=10, tiempo_h=1.0))
    g.agregar_arista(Arista("P01", "M01", distancia_km=10, tiempo_h=1.0, tipo_via="fluvial"))
    g.agregar_arista(Arista("M01", "F01", distancia_km=5, tiempo_h=0.5))

    sim = SimuladorCadenaFrio(g)
    res_base = sim.simular_ruta(["P01", "A01"], 100.0)
    res_d = sim.simular_ruta(["P01", "D01"], 100.0)
    res_m = sim.simular_ruta(["P01", "M01", "F01"], 100.0)

    # En D el deterioro del tramo se multiplica por FACTOR_DETERIORO_ZONA_D (1.5)
    assert abs(res_d.perdida_pct - res_base.perdida_pct * FACTOR_DETERIORO_ZONA_D) < 1e-4
    assert res_d.estados[-1].efecto == "Zona de deterioro ×1.5"

    # En M suma TIEMPO_TRANSBORDO_MUELLE_H y registra 1 transbordo
    assert res_m.num_transbordos == 1
    assert abs(res_m.tiempo_total_h - (1.0 + TIEMPO_TRANSBORDO_MUELLE_H + 0.5)) < 1e-6
    assert res_m.estados[1].efecto == "Transbordo en muelle"
    assert res_m.estados[2].efecto == "Refrigerado"
    assert "Transbordos (muelle):   1" in res_m.resumen()
    print("  [✓] test_efecto_zona_deterioro_y_muelle")


def test_itinerario_pasa_por_acopio():
    """Verifica que calcular_itinerarios construye ruta P → A → F → V evitando H."""
    g = GrafoLogistico()
    g.agregar_nodo(Nodo("P01", "Pesca 1", "P", produccion_kg_dia=80))
    g.agregar_nodo(Nodo("M01", "Muelle 1", "M", tiene_muelle=True))
    g.agregar_nodo(Nodo("H01", "Hábitat", "H", restriccion_ambiental=True))
    g.agregar_nodo(Nodo("A01", "Acopio 1", "A", capacidad_frio_kg=500))
    g.agregar_nodo(Nodo("F01", "Centro Frío", "F", capacidad_frio_kg=2000))
    g.agregar_nodo(Nodo("V01", "Mercado", "V"))

    # Atajo por H01 vs camino por M01 -> A01
    g.agregar_arista(Arista("P01", "H01", distancia_km=2, tiempo_h=0.05, tipo_via="fluvial"))
    g.agregar_arista(Arista("H01", "A01", distancia_km=2, tiempo_h=0.05, tipo_via="acceso_local"))
    g.agregar_arista(Arista("P01", "M01", distancia_km=4, tiempo_h=0.20, tipo_via="fluvial"))
    g.agregar_arista(Arista("M01", "A01", distancia_km=3, tiempo_h=0.15, tipo_via="acceso_local"))
    g.agregar_arista(Arista("A01", "F01", distancia_km=10, tiempo_h=0.40, tipo_via="terrestre"))
    g.agregar_arista(Arista("F01", "V01", distancia_km=50, tiempo_h=1.00, tipo_via="terrestre"))

    its = calcular_itinerarios(g, "V01")
    assert len(its) == 1
    it = its[0]
    assert it.acopio_id == "A01"
    assert it.centro_frio_id == "F01"
    assert "A01" in it.ruta
    assert "H01" not in it.ruta
    assert "H01" in it.nodos_restringidos_evitados
    assert len(it.tramos) == len(it.ruta) - 1
    print(f"  [✓] test_itinerario_pasa_por_acopio: {it.resumen()}")


if __name__ == "__main__":
    print("\n═══ PRUEBAS DE CADENA DE FRÍO ═══\n")
    test_simulacion_con_frio()
    test_simulacion_sin_frio()
    test_simulacion_deterioro_mayor_sin_frio()
    test_simulacion_ruta_corta()
    test_simulacion_resumen()
    test_efecto_zona_deterioro_y_muelle()
    test_itinerario_pasa_por_acopio()
    print("\n  ✅ Todas las pruebas pasaron.\n")
