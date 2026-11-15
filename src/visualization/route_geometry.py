"""
route_geometry.py — Obtención de geometrías reales de carreteras.

Consulta la API pública de OSRM (Open Source Routing Machine) para
obtener las rutas reales que siguen las carreteras de OpenStreetMap,
en lugar de líneas rectas entre nodos.

Para rutas fluviales, usa los segmentos del shapefile de ríos.

Los resultados se cachean en un JSON local para no repetir consultas.
"""

from __future__ import annotations

import json
import time
from pathlib import Path
from typing import List, Dict, Tuple, Optional, Any

from ..utils.data_loader import OUTPUT_DIR, SHP_DIR
from ..models.grafo_logistico import GrafoLogistico

# Ruta del archivo de caché
_CACHE_FILE = OUTPUT_DIR / "rutas_cache.json"


def obtener_geometria_carretera(
    lat1: float, lon1: float,
    lat2: float, lon2: float,
) -> Optional[List[List[float]]]:
    """
    Consulta OSRM para obtener la geometría real de la carretera
    entre dos coordenadas.

    Parameters
    ----------
    lat1, lon1 : float — coordenadas del origen.
    lat2, lon2 : float — coordenadas del destino.

    Returns
    -------
    list[list[float]] | None
        Lista de coordenadas [lon, lat] de la ruta real,
        o None si no se pudo obtener.
    """
    try:
        import urllib.request
        import urllib.error

        # OSRM usa formato: lon,lat
        url = (
            f"http://router.project-osrm.org/route/v1/driving/"
            f"{lon1},{lat1};{lon2},{lat2}"
            f"?overview=full&geometries=geojson"
        )

        req = urllib.request.Request(url)
        req.add_header("User-Agent", "ColdChainOptimization/1.0")

        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read().decode("utf-8"))

        if data.get("code") == "Ok" and data.get("routes"):
            coords = data["routes"][0]["geometry"]["coordinates"]
            return coords  # [[lon, lat], ...]

    except Exception:
        pass

    return None


def obtener_geometrias_grafo(
    grafo: GrafoLogistico,
    usar_cache: bool = True,
) -> Dict[str, List[List[float]]]:
    """
    Obtiene las geometrías reales de TODAS las aristas del grafo.

    Para aristas terrestres, consulta OSRM.
    Para aristas fluviales, intenta interpolar con el shapefile de ríos.
    Cachea los resultados para no repetir consultas.

    Parameters
    ----------
    grafo : GrafoLogistico
    usar_cache : bool — si usar/guardar caché de resultados.

    Returns
    -------
    dict[str, list[list[float]]]
        Diccionario {"{origen}-{destino}": [[lon, lat], ...]}
    """
    cache: Dict[str, List[List[float]]] = {}

    # Cargar caché existente
    if usar_cache and _CACHE_FILE.exists():
        try:
            with open(_CACHE_FILE, "r", encoding="utf-8") as f:
                cache = json.load(f)
        except (json.JSONDecodeError, IOError):
            cache = {}

    total = len(grafo.aristas)
    nuevas = 0

    print(f"\n  Obteniendo geometrías reales de {total} conexiones...")

    for i, arista in enumerate(grafo.aristas):
        clave = f"{arista.origen}-{arista.destino}"

        # Si ya está en caché, saltar
        es_fluvial = arista.tipo_via == "fluvial"
        if clave in cache and cache[clave]:
            # Una entrada fluvial con <= 2 puntos es una línea recta: recalcular
            if not (es_fluvial and len(cache[clave]) <= 2):
                continue

        n_o = grafo.obtener_nodo(arista.origen)
        n_d = grafo.obtener_nodo(arista.destino)
        if not n_o or not n_d:
            continue

        coords = None

        if arista.tipo_via in ("terrestre", "acceso_local"):
            # Ruta por carretera real via OSRM
            coords = obtener_geometria_carretera(
                n_o.latitud, n_o.longitud,
                n_d.latitud, n_d.longitud,
            )
            if coords:
                nuevas += 1
                print(f"    [{i+1}/{total}] {clave}: {len(coords)} puntos "
                      f"(carretera real) ✓")
            else:
                print(f"    [{i+1}/{total}] {clave}: OSRM sin respuesta, "
                      f"usando línea recta")
        elif arista.tipo_via == "fluvial":
            # Para rutas fluviales: intentar seguir el shapefile
            coords = _ruta_fluvial_real(
                n_o.latitud, n_o.longitud,
                n_d.latitud, n_d.longitud,
            )
            if coords:
                nuevas += 1
                print(f"    [{i+1}/{total}] {clave}: {len(coords)} puntos "
                      f"(río) ✓")
            else:
                print(f"    [{i+1}/{total}] {clave}: río no encontrado, "
                      f"usando línea recta")

        if coords:
            cache[clave] = coords
        else:
            # Línea recta como fallback
            cache[clave] = [
                [n_o.longitud, n_o.latitud],
                [n_d.longitud, n_d.latitud],
            ]

        # Rate limiting: esperar entre consultas OSRM
        if nuevas > 0 and arista.tipo_via != "fluvial":
            time.sleep(0.5)

    # Guardar caché
    if usar_cache:
        OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
        with open(_CACHE_FILE, "w", encoding="utf-8") as f:
            json.dump(cache, f, indent=2)

    print(f"  [✓] {nuevas} rutas nuevas obtenidas, "
          f"{len(cache)} en caché total")

    return cache


def obtener_geometria_ruta(
    grafo: GrafoLogistico,
    ruta: List[str],
    cache: Dict[str, List[List[float]]],
) -> List[List[float]]:
    """
    Construye la geometría completa de una ruta concatenando
    los segmentos reales de cada tramo.

    Parameters
    ----------
    grafo : GrafoLogistico
    ruta : list[str] — secuencia de IDs de nodos.
    cache : dict — caché de geometrías.

    Returns
    -------
    list[list[float]] — coordenadas [lon, lat] de la ruta completa.
    """
    coords_completas: List[List[float]] = []

    for i in range(len(ruta) - 1):
        clave = f"{ruta[i]}-{ruta[i + 1]}"
        segmento = cache.get(clave)

        if segmento:
            # Evitar duplicar el punto de conexión
            if coords_completas and segmento:
                coords_completas.extend(segmento[1:])
            else:
                coords_completas.extend(segmento)
        else:
            # Fallback: línea recta
            n_o = grafo.obtener_nodo(ruta[i])
            n_d = grafo.obtener_nodo(ruta[i + 1])
            if n_o and n_d:
                punto = [n_o.longitud, n_o.latitud]
                if not coords_completas or coords_completas[-1] != punto:
                    coords_completas.append(punto)
                coords_completas.append([n_d.longitud, n_d.latitud])

    return coords_completas


def _ruta_fluvial_real(
    lat1: float, lon1: float,
    lat2: float, lon2: float,
) -> Optional[List[List[float]]]:
    """Ruta sobre el cauce real (RedFluvial); None si no hay geopandas o conexión."""
    try:
        from .river_network import obtener_red_fluvial
        res = obtener_red_fluvial().ruta(lat1, lon1, lat2, lon2)
    except ImportError:
        return None
    return res[0] if res else None
