"""
river_network.py — Red fluvial real a partir de data/shapefiles/rios.shp.

Construye un grafo propio (dict de adyacencia, sin networkx) con los
vértices de las líneas del shapefile y calcula rutas con Dijkstra propio
(heapq), de modo que las rutas fluviales sigan el cauce real.
"""

from __future__ import annotations

import heapq
import math
from typing import Dict, List, Optional, Tuple

from ..utils.data_loader import SHP_DIR
from ..utils.geo_utils import haversine

BBOX_DEFECTO: Tuple[float, float, float, float] = (-73.1, 3.9, -71.3, 4.7)
DISTANCIA_MAX_ENLACE_KM = 5.0

Vertice = Tuple[float, float]  # (lon, lat) redondeados a 5 decimales

_GDF_CACHE: Dict[Tuple[float, ...], object] = {}
_RED: Optional["RedFluvial"] = None


def cargar_rios(bbox: Tuple[float, float, float, float] = BBOX_DEFECTO):
    """
    Carga el shapefile de ríos en EPSG:4326, recortado al bbox
    (lon_min, lat_min, lon_max, lat_max) y con las líneas explotadas.

    Devuelve un GeoDataFrame (cacheado en memoria por bbox).
    Lanza ImportError si geopandas no está disponible.
    """
    clave = tuple(bbox)
    if clave in _GDF_CACHE:
        return _GDF_CACHE[clave]

    import geopandas as gpd
    from shapely.geometry import box

    gdf = gpd.read_file(str(SHP_DIR / "rios.shp"))
    if gdf.crs is None:
        gdf = gdf.set_crs(epsg=4326)
    elif gdf.crs.to_epsg() != 4326:
        gdf = gdf.to_crs(epsg=4326)

    lon_min, lat_min, lon_max, lat_max = bbox
    gdf = gdf.cx[lon_min:lon_max, lat_min:lat_max]
    gdf = gdf.explode(index_parts=False, ignore_index=True)
    gdf = gdf[~gdf.geometry.is_empty & gdf.geometry.notna()].reset_index(drop=True)
    # Recorte exacto al bbox (conserva solo las partes dentro)
    gdf["geometry"] = gdf.geometry.intersection(box(*bbox))
    gdf = gdf.explode(index_parts=False, ignore_index=True)
    gdf = gdf[gdf.geometry.geom_type == "LineString"].reset_index(drop=True)

    _GDF_CACHE[clave] = gdf
    return gdf


class RedFluvial:
    """Grafo no dirigido de la red fluvial (los botes navegan en ambos sentidos)."""

    def __init__(self, bbox: Tuple[float, float, float, float] = BBOX_DEFECTO) -> None:
        self.adyacencia: Dict[Vertice, List[Tuple[Vertice, float]]] = {}
        gdf = cargar_rios(bbox)
        for geom in gdf.geometry:
            coords = [(round(x, 5), round(y, 5)) for x, y, *_ in geom.coords]
            for a, b in zip(coords[:-1], coords[1:]):
                if a == b:
                    continue
                d = haversine((a[1], a[0]), (b[1], b[0]))
                self.adyacencia.setdefault(a, []).append((b, d))
                self.adyacencia.setdefault(b, []).append((a, d))
        self._vertices: List[Vertice] = list(self.adyacencia)
        # Índice de rejilla para búsqueda del vértice más cercano
        self._celda = 0.05
        self._rejilla: Dict[Tuple[int, int], List[Vertice]] = {}
        for v in self._vertices:
            self._rejilla.setdefault(self._ij(v[0], v[1]), []).append(v)

    def _ij(self, lon: float, lat: float) -> Tuple[int, int]:
        return (math.floor(lon / self._celda), math.floor(lat / self._celda))

    def nodo_mas_cercano(self, lat: float, lon: float) -> Tuple[Optional[Vertice], float]:
        """Vértice fluvial más cercano: (clave_vertice (lon, lat), distancia_km)."""
        if not self._vertices:
            return None, float("inf")
        ci, cj = self._ij(lon, lat)
        mejor: Optional[Vertice] = None
        mejor_d = float("inf")
        radio = 0
        while radio < 400:
            for i in range(ci - radio, ci + radio + 1):
                for j in range(cj - radio, cj + radio + 1):
                    if max(abs(i - ci), abs(j - cj)) != radio:
                        continue
                    for v in self._rejilla.get((i, j), ()):
                        d = haversine((lat, lon), (v[1], v[0]))
                        if d < mejor_d:
                            mejor, mejor_d = v, d
            # Con el anillo r, todo lo no visitado está a >= r*celda grados
            if mejor is not None and mejor_d <= radio * self._celda * 100.0:
                break
            radio += 1
        return mejor, mejor_d

    def _dijkstra(self, origen: Vertice, destino: Vertice) -> Optional[Tuple[List[Vertice], float]]:
        dist: Dict[Vertice, float] = {origen: 0.0}
        previo: Dict[Vertice, Vertice] = {}
        cola: List[Tuple[float, Vertice]] = [(0.0, origen)]
        while cola:
            d, u = heapq.heappop(cola)
            if u == destino:
                break
            if d > dist.get(u, float("inf")):
                continue
            for v, w in self.adyacencia.get(u, ()):
                nd = d + w
                if nd < dist.get(v, float("inf")):
                    dist[v] = nd
                    previo[v] = u
                    heapq.heappush(cola, (nd, v))
        if destino not in dist:
            return None
        camino = [destino]
        while camino[-1] != origen:
            camino.append(previo[camino[-1]])
        camino.reverse()
        return camino, dist[destino]

    def ruta(self, lat1: float, lon1: float, lat2: float, lon2: float
             ) -> Optional[Tuple[List[List[float]], float]]:
        """
        Ruta por el río entre dos puntos: ([[lon, lat], ...], km).
        Incluye los enlaces punto→río y río→punto. None si no hay conexión
        o si algún punto queda a más de 5 km del río.
        """
        v1, d1 = self.nodo_mas_cercano(lat1, lon1)
        v2, d2 = self.nodo_mas_cercano(lat2, lon2)
        if v1 is None or v2 is None:
            return None
        if d1 > DISTANCIA_MAX_ENLACE_KM or d2 > DISTANCIA_MAX_ENLACE_KM:
            return None
        res = self._dijkstra(v1, v2)
        if res is None:
            return None
        camino, km = res
        coords = [[lon1, lat1]] + [[v[0], v[1]] for v in camino] + [[lon2, lat2]]
        return coords, km + d1 + d2


def obtener_red_fluvial() -> RedFluvial:
    """Singleton de la red fluvial."""
    global _RED
    if _RED is None:
        _RED = RedFluvial()
    return _RED


def obtener_capa_rios_geojson(bbox: Optional[Tuple[float, float, float, float]] = None,
                              tolerancia: float = 0.0005) -> Optional[dict]:
    """FeatureCollection simplificada de los ríos para el mapa; None si falla."""
    try:
        gdf = cargar_rios(bbox or BBOX_DEFECTO)
        col_nombre = next((c for c in gdf.columns
                           if c.lower() in ("nombre", "name", "nom_rio", "rio")), None)
        features = []
        for i, row in gdf.iterrows():
            geom = row.geometry.simplify(tolerancia, preserve_topology=False)
            if geom.is_empty:
                continue
            props = {}
            if col_nombre and row[col_nombre]:
                props["nombre"] = str(row[col_nombre])
            features.append({
                "type": "Feature",
                "properties": props,
                "geometry": {"type": "LineString",
                             "coordinates": [[round(x, 5), round(y, 5)]
                                             for x, y, *_ in geom.coords]},
            })
        return {"type": "FeatureCollection", "features": features}
    except Exception:
        return None
