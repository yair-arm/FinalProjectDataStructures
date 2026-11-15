"""Pruebas de la red fluvial real."""
import pytest

pytest.importorskip("geopandas")

from src.visualization.river_network import (
    cargar_rios, obtener_red_fluvial, obtener_capa_rios_geojson)


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
    b = pila[0] if pila else a
    res = red.ruta(a[1], a[0], b[1], b[0])
    assert res is not None
    coords, km = res
    assert len(coords) > 2 and km > 0


def test_punto_lejano_none():
    assert obtener_red_fluvial().ruta(4.3, -72.1, 0.0, -60.0) is None


def test_capa_geojson():
    capa = obtener_capa_rios_geojson()
    assert capa and capa["type"] == "FeatureCollection" and capa["features"]
