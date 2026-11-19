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

# Cubre los 25 nodos del modelo y los 49 puntos de campo (lat 3.20–4.99, lon -72.54 – -70.56)
BBOX_DEFECTO: Tuple[float, float, float, float] = (-73.80, 3.00, -70.40, 5.20)
DISTANCIA_MAX_ENLACE_KM = 6.0

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
        self._conectar_confluencias_afluentes()

    def _conectar_confluencias_afluentes(self) -> None:
        """
        Une micro-discontinuidades de digitalización entre afluentes secundarios
        y el cauce principal del shapefile `rios.shp` usando BFS + rejilla espacial.
        """
        from collections import deque

        if not self._vertices:
            return
        comp: Dict[Vertice, int] = {}
        grupos: Dict[int, List[Vertice]] = {}
        cid = 0
        for v in self._vertices:
            if v in comp:
                continue
            cid += 1
            cola: deque[Vertice] = deque([v])
            comp[v] = cid
            lista = [v]
            while cola:
                u = cola.popleft()
                for w, _ in self.adyacencia.get(u, ()):
                    if w not in comp:
                        comp[w] = cid
                        cola.append(w)
                        lista.append(w)
            grupos[cid] = lista

        if len(grupos) <= 1:
            return

        # Componente hidrográfica principal (mayor número de vértices)
        cid_principal = max(grupos, key=lambda k: len(grupos[k]))
        set_principal = set(grupos[cid_principal])
        rejilla_prin: Dict[Tuple[int, int], List[Vertice]] = {}
        for v in set_principal:
            rejilla_prin.setdefault(self._ij(v[0], v[1]), []).append(v)

        for k, Sub in grupos.items():
            if k == cid_principal:
                continue
            # Tomar extremos o muestra de vértices del afluente para enlazar a la confluencia más cercana
            extremos = [v for v in Sub if len(self.adyacencia.get(v, ())) <= 1] or Sub[:: max(1, len(Sub) // 10)]
            mejor_par: Optional[Tuple[Vertice, Vertice, float]] = None
            for u in extremos[:20]:
                ci, cj = self._ij(u[0], u[1])
                for r in range(0, 8):
                    encontrado = False
                    for i in range(ci - r, ci + r + 1):
                        for j in range(cj - r, cj + r + 1):
                            if max(abs(i - ci), abs(j - cj)) != r:
                                continue
                            for w in rejilla_prin.get((i, j), ()):
                                d = haversine((u[1], u[0]), (w[1], w[0]))
                                if mejor_par is None or d < mejor_par[2]:
                                    mejor_par = (u, w, d)
                                    encontrado = True
                    if encontrado:
                        break
            if mejor_par is not None:
                u, w, d = mejor_par
                self.adyacencia[u].append((w, d))
                self.adyacencia[w].append((u, d))

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

    def enlace_al_cauce(self, lat: float, lon: float
                        ) -> Tuple[Optional[List[float]], Optional[Vertice], float]:
        """
        Proyecta el punto sobre el tramo de río más cercano (no solo el vértice).

        Devuelve ([lon, lat] del punto proyectado, vértice ancla del grafo, km).
        """
        v, d = self.nodo_mas_cercano(lat, lon)
        if v is None:
            return None, None, float("inf")
        mejor_p: List[float] = [v[0], v[1]]
        mejor_d = d
        k = math.cos(math.radians(lat))  # corrección equirectangular local
        for w, _ in self.adyacencia.get(v, ()):
            dx, dy = (w[0] - v[0]) * k, w[1] - v[1]
            largo2 = dx * dx + dy * dy
            if largo2 == 0:
                continue
            t = ((lon - v[0]) * k * dx + (lat - v[1]) * dy) / largo2
            t = max(0.0, min(1.0, t))
            q_lon = v[0] + t * (w[0] - v[0])
            q_lat = v[1] + t * (w[1] - v[1])
            dq = haversine((lat, lon), (q_lat, q_lon))
            if dq < mejor_d:
                mejor_p, mejor_d = [round(q_lon, 6), round(q_lat, 6)], dq
        return mejor_p, v, mejor_d

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
        q1, v1, d1 = self.enlace_al_cauce(lat1, lon1)
        q2, v2, d2 = self.enlace_al_cauce(lat2, lon2)
        if v1 is None or v2 is None:
            return None
        if d1 > DISTANCIA_MAX_ENLACE_KM or d2 > DISTANCIA_MAX_ENLACE_KM:
            return None
        res = self._dijkstra(v1, v2)
        if res is None:
            return None
        camino, km = res
        bruto = ([[lon1, lat1], q1] + [[v[0], v[1]] for v in camino]
                 + [q2, [lon2, lat2]])
        coords: List[List[float]] = []
        for p in bruto:  # eliminar puntos consecutivos repetidos
            if not coords or coords[-1] != p:
                coords.append(p)
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


# ═══════════════════════════════════════════════════════════════════
# MODELO HIDROLÓGICO Y DE NAVEGACIÓN EN LANCHA PARA LOS 49 PUNTOS DE CAMPO
# ═══════════════════════════════════════════════════════════════════

_CORREDOR_CAMPO_CACHE: Optional[Dict[str, object]] = None


def estimar_cota_cauce_msnm(lat: float, lon: float) -> float:
    """
    Estima la cota hidrométrica del cauce fluvial (m s.n.m.) en la cuenca de los Llanos
    Orientales (ríos Manacacías, Meta, Tillavá, Planas, Iteviare y Yucao).

    El gradiente topográfico regional desciende de suroeste a noreste:
      - Cuenca alta sur (M-08 / A-09, lat ~3.30°N, lon ~-72.50°W): ~225–238 m s.n.m.
      - Confluencia Puerto Gaitán (M03, lat 4.3168°N, lon -72.0835°W): ~142 m s.n.m.
      - Cuenca baja oriental Río Meta (H-02 / A-08, lon ~-70.56°W): ~104–115 m s.n.m.
    """
    # Modelo planar calibrado con cotas IGAC/IDEAM de la cuenca del río Meta y Manacacías
    cota = 142.0 - 46.0 * (lat - 4.3168) - 28.5 * (lon - (-72.0835))
    return round(max(85.0, min(280.0, cota)), 1)


def calcular_corredor_fluvial_puntos_campo() -> Dict[str, object]:
    """
    Conecta los 49 puntos reales de campo (`data/geojson/puntos_campo.geojson`)
    sobre la red hidrográfica real (`rios.shp`) mediante un árbol de relevo fluvial
    hacia el Muelle Principal de Puerto Gaitán (`M03` -> Centro Frío `F02`).

    Para cada punto y tramo calcula:
      - Trazado geométrico real sobre los meandros del río (`coords_latlon`).
      - Distancia por cauce real (`distancia_rio_km`) vs. línea recta (`indice_sinuosidad`).
      - Cota hidrométrica (`cota_origen_msnm`, `cota_destino_msnm`), desnivel (`desnivel_m`)
        y pendiente hidráulica (`pendiente_m_km`).
      - Condición de cuesta del río:
          * 'Aguas abajo (a favor de corriente)' -> v_corriente +3.8 km/h, v_lancha = 21.5 km/h
          * 'Cuesta arriba (contra corriente)'   -> v_corriente -3.8 km/h, v_lancha = 13.5 km/h
          * 'Remanso de planicie aluvial'        -> v_corriente +1.2 km/h, v_lancha = 18.0 km/h
      - Tiempo de navegación en lancha (tramo y acumulado hasta Puerto Gaitán),
        consumo de combustible (galones y COP), requerimiento de hielo 1:1 y pérdida térmica.
    """
    global _CORREDOR_CAMPO_CACHE
    if _CORREDOR_CAMPO_CACHE is not None:
        return _CORREDOR_CAMPO_CACHE

    import json
    from ..utils.data_loader import DATA_DIR

    ruta_gj = DATA_DIR / "geojson" / "puntos_campo.geojson"
    if not ruta_gj.exists():
        return {"puntos": [], "tramos": [], "resumen": {}}

    gj = json.loads(ruta_gj.read_text(encoding="utf-8"))
    features = gj.get("features", [])
    if not features:
        return {"puntos": [], "tramos": [], "resumen": {}}

    red = obtener_red_fluvial()
    lat_m03, lon_m03 = 4.3168, -72.0835
    q_m03, v_m03, d_m03 = red.enlace_al_cauce(lat_m03, lon_m03)
    if v_m03 is None:
        return {"puntos": [], "tramos": [], "resumen": {}}

    # 1. Árbol Dijkstra desde v_m03 hacia toda la red fluvial en una sola pasada O((V+E) log V)
    dist_a_m03: Dict[Vertice, float] = {v_m03: 0.0}
    padre_hacia_m03: Dict[Vertice, Vertice] = {}
    cola: List[Tuple[float, Vertice]] = [(0.0, v_m03)]
    while cola:
        d_act, u = heapq.heappop(cola)
        if d_act > dist_a_m03.get(u, float("inf")):
            continue
        for vec, peso_km in red.adyacencia.get(u, ()):
            nd = d_act + peso_km
            if nd < dist_a_m03.get(vec, float("inf")):
                dist_a_m03[vec] = nd
                padre_hacia_m03[vec] = u
                heapq.heappush(cola, (nd, vec))

    # 2. Proyectar los 49 puntos de campo al cauce real y obtener su distancia fluvial a M03
    nodos_campo: List[Dict[str, object]] = []
    for feat in features:
        props = feat.get("properties", {})
        coords = feat.get("geometry", {}).get("coordinates", [0.0, 0.0])
        lon, lat = float(coords[0]), float(coords[1])
        q_proy, v_ancla, d_enlace = red.enlace_al_cauce(lat, lon)
        km_rio_m03 = dist_a_m03.get(v_ancla, 0.0) + d_enlace if v_ancla else haversine((lat, lon), (lat_m03, lon_m03))
        nodos_campo.append({
            "id": str(props.get("id", "")),
            "title": str(props.get("title", props.get("id", ""))),
            "categoria": str(props.get("categoria", "")),
            "tipo": str(props.get("tipo", "")),
            "lat_dms": str(props.get("lat_dms", "")),
            "lon_dms": str(props.get("lon_dms", "")),
            "latitud": round(lat, 6),
            "longitud": round(lon, 6),
            "cota_msnm": estimar_cota_cauce_msnm(lat, lon),
            "v_ancla": v_ancla,
            "q_proy": q_proy or [lon, lat],
            "dist_al_cauce_km": round(d_enlace, 2),
            "dist_fluvial_a_m03_km": round(km_rio_m03, 2),
        })

    # 3. Construir árbol de relevo fluvial (cada punto remoto navega hacia el siguiente
    #    muelle M / acopio A aguas adelante rumbo a M03, o directo a M03 si es el más próximo)
    cota_m03 = estimar_cota_cauce_msnm(lat_m03, lon_m03)
    hubs_relevo = [n for n in nodos_campo if n["categoria"] in ("M", "A")]

    def _reconstruir_cauce_hacia_m03(v_ini: Optional[Vertice], max_pasos: int = 4000) -> List[Vertice]:
        if v_ini is None or v_ini not in dist_a_m03:
            return []
        cam = [v_ini]
        act = v_ini
        pasos = 0
        while act in padre_hacia_m03 and pasos < max_pasos:
            act = padre_hacia_m03[act]
            cam.append(act)
            pasos += 1
        return cam

    # Mapa de vértices del cauce que pertenecen a algún hub (M o A) para detectar relevo natural sobre el mismo río
    ancla_a_hub: Dict[Vertice, Dict[str, object]] = {}
    for h in hubs_relevo:
        if h["v_ancla"] is not None:
            ancla_a_hub[h["v_ancla"]] = h

    tramos_corredor: List[Dict[str, object]] = []
    for p in nodos_campo:
        v_ini = p["v_ancla"]
        cam_completo_m03 = _reconstruir_cauce_hacia_m03(v_ini)
        d_total_m03 = float(p["dist_fluvial_a_m03_km"])

        # Buscar el mejor nodo de relevo (M o A) más cercano a M03 en su misma cuenca
        mejor_destino = None
        mejor_cam_tramo: List[Vertice] = cam_completo_m03
        mejor_km_tramo = d_total_m03

        # Candidatos: hubs M o A que estén más cerca de M03 en distancia fluvial y a menos de 45 km del punto actual
        candidatos = [
            h for h in hubs_relevo
            if h["id"] != p["id"]
            and float(h["dist_fluvial_a_m03_km"]) + 2.5 < d_total_m03
            and haversine((float(p["latitud"]), float(p["longitud"])), (float(h["latitud"]), float(h["longitud"]))) < 55.0
        ]
        if candidatos:
            # Elegir el candidato que minimice (distancia fluvial p->h + 0.35 * distancia h->M03)
            mejor_h = min(
                candidatos,
                key=lambda h: haversine(
                    (float(p["latitud"]), float(p["longitud"])),
                    (float(h["latitud"]), float(h["longitud"])),
                ) + abs(d_total_m03 - float(h["dist_fluvial_a_m03_km"])) * 0.5,
            )
            res_sub = red._dijkstra(v_ini, mejor_h["v_ancla"]) if (v_ini and mejor_h["v_ancla"]) else None
            if res_sub is not None and res_sub[1] < d_total_m03 * 1.15:
                mejor_destino = mejor_h
                mejor_cam_tramo = res_sub[0]
                mejor_km_tramo = res_sub[1] + float(p["dist_al_cauce_km"]) + float(mejor_h["dist_al_cauce_km"])

        if mejor_destino is not None:
            dest_id = str(mejor_destino["id"])
            dest_nombre = str(mejor_destino["title"])
            dest_lat = float(mejor_destino["latitud"])
            dest_lon = float(mejor_destino["longitud"])
            dest_cota = float(mejor_destino["cota_msnm"])
        else:
            dest_id = "M03"
            dest_nombre = "M03 - Muelle Principal Puerto Gaitán"
            dest_lat = lat_m03
            dest_lon = lon_m03
            dest_cota = cota_m03

        # Submuestrear geometría para mantener HTML ligero pero fiel a las curvas reales del río
        paso_simpl = max(1, len(mejor_cam_tramo) // 65)
        coords_cauce = [[v[1], v[0]] for v in mejor_cam_tramo[::paso_simpl]]
        if mejor_cam_tramo and coords_cauce[-1] != [mejor_cam_tramo[-1][1], mejor_cam_tramo[-1][0]]:
            coords_cauce.append([mejor_cam_tramo[-1][1], mejor_cam_tramo[-1][0]])
        coords_latlon = (
            [[round(float(p["latitud"]), 5), round(float(p["longitud"]), 5)]]
            + [[round(lat_v, 5), round(lon_v, 5)] for lat_v, lon_v in coords_cauce]
            + [[round(dest_lat, 5), round(dest_lon, 5)]]
        )

        # Variables hidrológicas y de cuesta del río
        cota_orig = float(p["cota_msnm"])
        desnivel_m = round(dest_cota - cota_orig, 1)  # negativo = baja el río (a favor); positivo = sube (contra corriente)
        dist_tramo = round(max(0.5, mejor_km_tramo), 2)
        dist_recta = round(max(0.2, haversine((float(p["latitud"]), float(p["longitud"])), (dest_lat, dest_lon))), 2)
        sinuosidad = round(max(1.0, dist_tramo / dist_recta), 2)
        pendiente_m_km = round(abs(desnivel_m) / dist_tramo, 3)

        # Determinar régimen de cuesta respecto al viaje hacia Puerto Gaitán (M03)
        desnivel_a_m03 = round(cota_m03 - cota_orig, 1)
        if desnivel_a_m03 < -2.0:
            condicion_cuesta = "Aguas abajo (a favor de la corriente)"
            vel_corriente_kmh = 3.8
            vel_lancha_ida_kmh = 21.5
            vel_lancha_retorno_hielo_kmh = 13.5
            costo_km_lancha_cop = 1900.0
            esfuerzo_motor = "Bajo (0.82× — corriente impulsa la canoa)"
        elif desnivel_a_m03 > 2.0:
            condicion_cuesta = "Cuesta arriba (remontando contra corriente)"
            vel_corriente_kmh = -3.8
            vel_lancha_ida_kmh = 13.5
            vel_lancha_retorno_hielo_kmh = 21.5
            costo_km_lancha_cop = 3100.0
            esfuerzo_motor = "Alto (1.35× — motor 40 HP vence pendiente fluvial)"
        else:
            condicion_cuesta = "Remanso de planicie aluvial (corriente suave)"
            vel_corriente_kmh = 1.2
            vel_lancha_ida_kmh = 18.0
            vel_lancha_retorno_hielo_kmh = 16.5
            costo_km_lancha_cop = 2400.0
            esfuerzo_motor = "Medio (1.00× — cauce meándrico estable)"

        tiempo_tramo_h = round(dist_tramo / vel_lancha_ida_kmh, 2)
        tiempo_total_a_m03_h = round(d_total_m03 / vel_lancha_ida_kmh, 2)
        tiempo_retorno_hielo_h = round(d_total_m03 / vel_lancha_retorno_hielo_kmh, 2)

        # Variables térmicas y de cadena de frío (lote típico 40 kg en punto de campo)
        lote_tipo_kg = 40.0
        hielo_1a1_kg = 40.0
        factor_zona_d = 1.5 if p["categoria"] == "D" else 1.0
        perdida_sin_hielo_pct = round(min(100.0, tiempo_total_a_m03_h * 2.5 * factor_zona_d), 1)
        perdida_con_hielo_1a1_pct = round(min(100.0, tiempo_total_a_m03_h * 0.25), 1)
        requiere_hielo_abordo = tiempo_total_a_m03_h > 3.5
        costo_combustible_a_m03_cop = round(d_total_m03 * costo_km_lancha_cop, 0)
        galones_combustible = round(d_total_m03 * (0.18 if desnivel_a_m03 < 0 else 0.29), 1)

        info_enriquecida = {
            "id": p["id"],
            "title": p["title"],
            "categoria": p["categoria"],
            "tipo": p["tipo"],
            "lat_dms": p["lat_dms"],
            "lon_dms": p["lon_dms"],
            "latitud": p["latitud"],
            "longitud": p["longitud"],
            "destino_relevo_id": dest_id,
            "destino_relevo_nombre": dest_nombre,
            "distancia_al_cauce_km": p["dist_al_cauce_km"],
            "distancia_tramo_rio_km": dist_tramo,
            "distancia_total_a_m03_km": d_total_m03,
            "distancia_recta_km": dist_recta,
            "indice_sinuosidad": sinuosidad,
            "cota_origen_msnm": cota_orig,
            "cota_destino_msnm": dest_cota,
            "cota_m03_msnm": cota_m03,
            "desnivel_tramo_m": desnivel_m,
            "desnivel_a_m03_m": desnivel_a_m03,
            "pendiente_m_km": pendiente_m_km,
            "condicion_cuesta_rio": condicion_cuesta,
            "velocidad_corriente_kmh": vel_corriente_kmh,
            "velocidad_lancha_ida_kmh": vel_lancha_ida_kmh,
            "velocidad_lancha_retorno_kmh": vel_lancha_retorno_hielo_kmh,
            "esfuerzo_motor": esfuerzo_motor,
            "tiempo_tramo_h": tiempo_tramo_h,
            "tiempo_tramo_min": round(tiempo_tramo_h * 60.0, 1),
            "tiempo_total_a_m03_h": tiempo_total_a_m03_h,
            "tiempo_total_a_m03_min": round(tiempo_total_a_m03_h * 60.0, 1),
            "tiempo_retorno_hielo_h": tiempo_retorno_hielo_h,
            "lote_referencia_kg": lote_tipo_kg,
            "hielo_requerido_1a1_kg": hielo_1a1_kg,
            "perdida_sin_hielo_pct": perdida_sin_hielo_pct,
            "perdida_con_hielo_1a1_pct": perdida_con_hielo_1a1_pct,
            "requiere_hielo_abordo": requiere_hielo_abordo,
            "estado_fao_sin_hielo": (
                "VIOLA LÍMITE FAO (>4.0 h: exige hielo 1:1 en lancha)"
                if tiempo_total_a_m03_h > 4.0
                else "DENTRO DE VENTANA FAO (≤4.0 h)"
            ),
            "costo_combustible_cop": costo_combustible_a_m03_cop,
            "galones_gasolina": galones_combustible,
            "coords_latlon": coords_latlon,
        }
        p.update(info_enriquecida)
        tramos_corredor.append(info_enriquecida)

    # Limpiar claves internas no serializables (v_ancla)
    for p in nodos_campo:
        p.pop("v_ancla", None)
        p.pop("q_proy", None)

    _CORREDOR_CAMPO_CACHE = {
        "puntos": nodos_campo,
        "tramos": tramos_corredor,
        "resumen": {
            "total_puntos_conectados": len(nodos_campo),
            "km_totales_tramos_rio": round(sum(float(t["distancia_tramo_rio_km"]) for t in tramos_corredor), 1),
            "puntos_aguas_abajo": sum(1 for t in tramos_corredor if "Aguas abajo" in str(t["condicion_cuesta_rio"])),
            "puntos_cuesta_arriba": sum(1 for t in tramos_corredor if "Cuesta arriba" in str(t["condicion_cuesta_rio"])),
            "puntos_requieren_hielo_abordo": sum(1 for t in tramos_corredor if t["requiere_hielo_abordo"]),
        },
    }
    return _CORREDOR_CAMPO_CACHE
