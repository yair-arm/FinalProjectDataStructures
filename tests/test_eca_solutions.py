"""Pruebas unitarias para los 6 módulos algorítmicos de la ECA (C05-01-2026-003)."""

from main import cargar_datos
from src.algorithms.dijkstra import dijkstra_con_cota_inocuidad
from src.optimization.eca_solutions import (
    LoteTrazabilidadDAG,
    NodoEventoDAG,
    TablaHashTrazabilidad,
    auditar_proteccion_habitats_y_resguardos,
    calcular_dimensionamiento_hielo_red,
    construir_grafo_veda_bitemporal,
    construir_trazabilidad_lotes_red,
    ejecutar_suite_eca,
    evaluar_inocuidad_histamina_red,
)


def test_grafo_bitemporal_veda():
    """2.1 Verifica que G_veda desactiva captura en ríos y activa piscicultura nativa."""
    grafo_pesca = cargar_datos()
    grafo_veda, info = construir_grafo_veda_bitemporal(grafo_pesca)

    ids_veda = {p.id for p in grafo_veda.puntos_pesca()}
    assert ids_veda == {"P_PISC1", "P_PISC2", "P_PISC3"}
    assert info["regimen_veda_piscicultura"]["produccion_kg_dia"] == 240.0
    assert info["regimen_veda_piscicultura"]["tiempo_max_a_f02_h"] <= 1.0


def test_dijkstra_con_cota_inocuidad_histamina():
    """2.2 Verifica poda de inocuidad FAO (t <= 4.0 h) y bloqueo cuando la cota es estricta."""
    grafo = cargar_datos()
    costo, camino, max_t_sf, cumple = dijkstra_con_cota_inocuidad(
        grafo, "P05", "F02", tiempo_limite_h=4.0
    )
    assert cumple is True
    assert len(camino) >= 2
    assert max_t_sf <= 4.0

    # Si se impone una cota imposible (0.05 h para P05 que está a 63 km), debe podar y no hallar ruta
    costo_imp, cam_imp, _, cumple_imp = dijkstra_con_cota_inocuidad(
        grafo, "P05", "F02", tiempo_limite_h=0.05
    )
    assert cumple_imp is False
    assert cam_imp == []


def test_evaluacion_inocuidad_todas_asociaciones():
    """2.2 Verifica que las 7 asociaciones tengan riesgo de histamina controlado."""
    grafo = cargar_datos()
    info = evaluar_inocuidad_histamina_red(grafo)
    assert info["cumplimiento_global_pct"] == 100.0
    assert len(info["asociaciones"]) == 7
    assert all(a["riesgo_histamina"] == "CONTROLADO" for a in info["asociaciones"])


def test_dimensionamiento_hielo_1a1():
    """2.3 Verifica relación 1:1 hielo:pescado y factibilidad de capacidad vehicular."""
    grafo = cargar_datos()
    info = calcular_dimensionamiento_hielo_red(grafo)
    assert info["total_pescado_kg_dia"] == info["total_hielo_kg_dia"]
    assert info["masa_bruta_total_kg_dia"] == round(info["total_pescado_kg_dia"] * 2, 2)
    assert info["todos_factibles_capacidad"] is True


def test_auditoria_habitats_y_resguardos():
    """2.5 Verifica exclusión 100% de nodos H (H01, H02) como paso intermedio."""
    grafo = cargar_datos()
    info = auditar_proteccion_habitats_y_resguardos(grafo)
    assert info["violaciones_ambientales"] == 0
    assert "H01" in info["nodos_habitat_protegidos"]
    assert "H02" in info["nodos_habitat_protegidos"]


def test_dag_y_tabla_hash_trazabilidad():
    """2.6 Verifica orden topológico de Kahn en DAG y consulta O(1) en Tabla Hash."""
    grafo = cargar_datos()
    tabla, info = construir_trazabilidad_lotes_red(grafo)
    assert len(tabla) == 7
    assert info["todos_dags_aciclicos"] is True

    lote_p05 = tabla.consultar_lote("ECA-2026-P05")
    assert lote_p05 is not None
    es_dag, orden = lote_p05.orden_topologico_kahn()
    assert es_dag is True
    assert len(orden) >= 3
    assert lote_p05.exposicion_grado_hora() > 0

    # Verificar detección de ciclo si se intenta corromper un DAG
    dag_ciclo = LoteTrazabilidadDAG("LOTE-TEST", "Test")
    dag_ciclo.agregar_evento(NodoEventoDAG("E1", "Captura", "P01", 0.0, 30.0, 0.0, 10.0, "OK"))
    dag_ciclo.agregar_evento(NodoEventoDAG("E2", "Acopio", "A01", 1.0, 30.0, 2.5, 9.75, "OK"))
    dag_ciclo.conectar_etapas("E1", "E2")
    dag_ciclo.conectar_etapas("E2", "E1")
    es_valido, _ = dag_ciclo.orden_topologico_kahn()
    assert es_valido is False
