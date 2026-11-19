"""Pruebas de la red fluvial real."""
import pytest

pytest.importorskip("geopandas")

from src.visualization.river_network import (
    calcular_corredor_fluvial_puntos_campo,
    cargar_rios,
    obtener_capa_rios_geojson,
    obtener_red_fluvial,
)


def test_carga_no_vacia():
    gdf = cargar_rios()
    assert len(gdf) > 0
    assert gdf.crs.to_epsg() == 4326


def test_ruta_mismo_rio():
    red = obtener_red_fluvial()
    vs = sorted(red.adyacencia)
    # dos vértices alejados dentro de la misma componente conexa
    a = vs[len(vs) // 2]
    visitados, pila = {a}, [a]
    while pila and len(visitados) < 400:
        u = pila.pop()
        for v, _ in red.adyacencia[u]:
            if v not in visitados:
                visitados.add(v)
                pila.append(v)
    b = pila[-1] if pila else a
    res = red.ruta(a[1], a[0], b[1], b[0])
    assert res is not None
    coords, km = res
    assert len(coords) > 2 and km > 0


def test_punto_lejano_none():
    assert obtener_red_fluvial().ruta(4.3, -72.1, 0.0, -60.0) is None


def test_capa_geojson():
    capa = obtener_capa_rios_geojson()
    assert capa and capa["type"] == "FeatureCollection" and capa["features"]


def test_corredor_fluvial_49_puntos_campo():
    """Verifica que los 49 puntos de campo (incluidos M-08, A-09, A-01..A-13) se conecten por río real."""
    corredor = calcular_corredor_fluvial_puntos_campo()
    puntos = corredor["puntos"]
    assert len(puntos) == 49
    por_id = {p["id"]: p for p in puntos}
    for pid in ("M-08", "A-09", "A-01", "A-06", "A-02", "A-03", "A-07", "A-13"):
        assert pid in por_id
        pt = por_id[pid]
        assert len(pt["coords_latlon"]) >= 3
        assert pt["distancia_tramo_rio_km"] > 0
        assert pt["distancia_total_a_m03_km"] > 0
        assert pt["velocidad_lancha_ida_kmh"] > 0
        assert "condicion_cuesta_rio" in pt
