"""
felt_exporter.py — Exportador de datos geográficos para Felt.com.

Genera archivos GeoJSON y ZIP listos para importar directamente
en la plataforma de mapas colaborativos Felt.com:

  1. nodos_red.geojson      — Puntos con propiedades para categorizar por color.
  2. ruta_dijkstra.geojson   — LineString de la ruta óptima con métricas.
  3. rios.zip                — Shapefile empaquetado de la red fluvial.

No requiere geopandas: genera GeoJSON con el módulo estándar `json`.
"""

from __future__ import annotations

import json
import os
import zipfile
from pathlib import Path
from typing import List, Dict, Any, Optional

from ..models.grafo_logistico import GrafoLogistico
from ..utils.data_loader import OUTPUT_DIR, SHP_DIR
from ..utils.constants import TipoNodo


# ═══════════════════════════════════════════════════════════════════
#  1. EXPORTAR NODOS COMO GEOJSON (Point)
# ═══════════════════════════════════════════════════════════════════

def exportar_nodos_geojson(
    grafo: GrafoLogistico,
    nombre_archivo: str = "nodos_red.geojson",
) -> str:
    """
    Exporta todos los nodos del grafo como GeoJSON FeatureCollection
    de tipo Point, listo para importar en Felt.com.

    Cada Feature incluye en 'properties':
        - nombre: nombre descriptivo del nodo
        - tipo_nodo: código de tipo (P, A, D, H, M, F, V)
        - tipo_descripcion: descripción legible del tipo
        - capacidad: capacidad de frío (kg) o producción diaria (kg)
        - produccion_kg_dia: producción pesquera diaria
        - capacidad_frio_kg: capacidad de refrigeración
        - costo_fijo: costo fijo mensual de operación
        - tiene_energia: si tiene suministro eléctrico
        - tiene_muelle: si tiene infraestructura de desembarque
        - rio_asociado: río asociado (si existe en metadata)
        - num_pescadores: número de pescadores (si existe)

    Parameters
    ----------
    grafo : GrafoLogistico
    nombre_archivo : str — nombre del archivo de salida.

    Returns
    -------
    str : ruta absoluta del archivo generado.
    """
    features: List[Dict[str, Any]] = []

    for nodo in grafo.nodos:
        # Determinar la capacidad principal según el tipo
        if nodo.tipo == TipoNodo.PESCA:
            capacidad = nodo.produccion_kg_dia
        elif nodo.tipo in (TipoNodo.FRIO, TipoNodo.ACOPIO):
            capacidad = nodo.capacidad_frio_kg
        else:
            capacidad = 0.0

        properties = {
            "id": nodo.id,
            "nombre": nodo.nombre,
            "tipo_nodo": nodo.tipo,
            "tipo_descripcion": TipoNodo.descripcion(nodo.tipo),
            "capacidad": capacidad,
            "produccion_kg_dia": nodo.produccion_kg_dia,
            "capacidad_frio_kg": nodo.capacidad_frio_kg,
            "costo_fijo": nodo.costo_fijo,
            "tiene_energia": nodo.tiene_energia,
            "tiene_muelle": nodo.tiene_muelle,
        }

        # Agregar metadata si existe
        if nodo.metadata:
            if "rio" in nodo.metadata:
                properties["rio_asociado"] = nodo.metadata["rio"]
            if "pescadores" in nodo.metadata:
                properties["num_pescadores"] = nodo.metadata["pescadores"]
            if "demanda_kg_dia" in nodo.metadata:
                properties["demanda_kg_dia"] = nodo.metadata["demanda_kg_dia"]

        feature = {
            "type": "Feature",
            "geometry": {
                "type": "Point",
                "coordinates": [nodo.longitud, nodo.latitud],  # GeoJSON: [lon, lat]
            },
            "properties": properties,
        }
        features.append(feature)

    geojson = {
        "type": "FeatureCollection",
        "name": "Red Logística Pesquera — Puerto Gaitán, Meta",
        "features": features,
    }

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    ruta = OUTPUT_DIR / nombre_archivo
    with open(ruta, "w", encoding="utf-8") as f:
        json.dump(geojson, f, ensure_ascii=False, indent=2)

    print(f"  [✓] Nodos GeoJSON exportados: {ruta}")
    print(f"      {len(features)} features (tipos: "
          f"{', '.join(sorted(set(n.tipo for n in grafo.nodos)))})")
    return str(ruta)


# ═══════════════════════════════════════════════════════════════════
#  2. EXPORTAR RUTA ÓPTIMA COMO GEOJSON (LineString)
# ═══════════════════════════════════════════════════════════════════

def exportar_ruta_geojson(
    grafo: GrafoLogistico,
    ruta: List[str],
    nombre_archivo: str = "ruta_dijkstra.geojson",
    nombre_ruta: str = "Ruta Óptima Dijkstra",
) -> str:
    """
    Exporta una ruta (lista de IDs de nodos) como GeoJSON LineString
    con propiedades de métricas logísticas.

    Cada tramo también se exporta como Feature individual para
    permitir pop-ups detallados por segmento en Felt.com.

    Parameters
    ----------
    grafo : GrafoLogistico
    ruta : list[str] — secuencia de IDs de nodos de la ruta.
    nombre_archivo : str — nombre del archivo de salida.
    nombre_ruta : str — nombre descriptivo para la ruta.

    Returns
    -------
    str : ruta absoluta del archivo generado.
    """
    if not ruta or len(ruta) < 2:
        print("  [!] Ruta vacía o insuficiente para exportar.")
        return ""

    features: List[Dict[str, Any]] = []

    # ── Feature 1: Ruta completa como LineString ──────────────
    coordenadas = []
    distancia_total = 0.0
    tiempo_total = 0.0
    costo_total = 0.0
    riesgo_max = 0.0
    perdida_estimada_total = 0.0

    for i in range(len(ruta)):
        nodo = grafo.obtener_nodo(ruta[i])
        if nodo:
            coordenadas.append([nodo.longitud, nodo.latitud])

        if i < len(ruta) - 1:
            arista = grafo.obtener_arista(ruta[i], ruta[i + 1])
            if arista:
                distancia_total += arista.distancia_km
                tiempo_total += arista.tiempo_h
                costo_total += arista.costo_cop
                riesgo_max = max(riesgo_max, arista.riesgo_termico)
                perdida_estimada_total += arista.perdida_esperada

    ruta_feature = {
        "type": "Feature",
        "geometry": {
            "type": "LineString",
            "coordinates": coordenadas,
        },
        "properties": {
            "nombre": nombre_ruta,
            "tipo": "ruta_completa",
            "origen": ruta[0],
            "destino": ruta[-1],
            "num_tramos": len(ruta) - 1,
            "distancia_km": round(distancia_total, 2),
            "tiempo_horas": round(tiempo_total, 2),
            "costo_cop": round(costo_total, 0),
            "riesgo_termico_max": round(riesgo_max, 2),
            "perdida_estimada_pct": round(
                min(perdida_estimada_total, 100.0), 2
            ),
            "nodos_recorridos": " → ".join(ruta),
        },
    }
    features.append(ruta_feature)

    # ── Features 2+: Cada tramo como LineString individual ────
    for i in range(len(ruta) - 1):
        nodo_o = grafo.obtener_nodo(ruta[i])
        nodo_d = grafo.obtener_nodo(ruta[i + 1])
        arista = grafo.obtener_arista(ruta[i], ruta[i + 1])

        if not nodo_o or not nodo_d:
            continue

        tramo_props = {
            "nombre": f"Tramo {i + 1}: {nodo_o.nombre} → {nodo_d.nombre}",
            "tipo": "tramo",
            "origen": ruta[i],
            "destino": ruta[i + 1],
            "origen_nombre": nodo_o.nombre,
            "destino_nombre": nodo_d.nombre,
        }

        if arista:
            tramo_props.update({
                "distancia_km": arista.distancia_km,
                "tiempo_horas": arista.tiempo_h,
                "costo_cop": arista.costo_cop,
                "riesgo_termico": arista.riesgo_termico,
                "estado_via": arista.estado_via,
                "tipo_via": arista.tipo_via,
                "perdida_estimada_pct": round(arista.perdida_esperada, 2),
            })

        tramo_feature = {
            "type": "Feature",
            "geometry": {
                "type": "LineString",
                "coordinates": [
                    [nodo_o.longitud, nodo_o.latitud],
                    [nodo_d.longitud, nodo_d.latitud],
                ],
            },
            "properties": tramo_props,
        }
        features.append(tramo_feature)

    geojson = {
        "type": "FeatureCollection",
        "name": nombre_ruta,
        "features": features,
    }

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    ruta_archivo = OUTPUT_DIR / nombre_archivo
    with open(ruta_archivo, "w", encoding="utf-8") as f:
        json.dump(geojson, f, ensure_ascii=False, indent=2)

    print(f"  [✓] Ruta GeoJSON exportada: {ruta_archivo}")
    print(f"      {' → '.join(ruta)} ({distancia_total:.1f} km, "
          f"{tiempo_total:.2f} h)")
    return str(ruta_archivo)


# ═══════════════════════════════════════════════════════════════════
#  3. EMPAQUETAR SHAPEFILE DE RÍOS (ZIP)
# ═══════════════════════════════════════════════════════════════════

def empaquetar_rios_zip(
    nombre_archivo: str = "rios.zip",
) -> str:
    """
    Comprime todos los archivos del shapefile de ríos en un ZIP
    listo para subir a Felt.com.

    Archivos incluidos: rios.shp, rios.dbf, rios.prj, rios.shx, rios.cst

    Parameters
    ----------
    nombre_archivo : str — nombre del archivo ZIP de salida.

    Returns
    -------
    str : ruta absoluta del archivo generado.
    """
    extensiones = [".shp", ".dbf", ".prj", ".shx", ".cst"]
    archivos_encontrados = []

    for ext in extensiones:
        archivo = SHP_DIR / f"rios{ext}"
        if archivo.exists():
            archivos_encontrados.append(archivo)

    if not archivos_encontrados:
        print("  [!] No se encontraron archivos del shapefile de ríos.")
        return ""

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    ruta_zip = OUTPUT_DIR / nombre_archivo

    with zipfile.ZipFile(ruta_zip, "w", zipfile.ZIP_DEFLATED) as zf:
        for archivo in archivos_encontrados:
            zf.write(archivo, archivo.name)

    tamano_kb = ruta_zip.stat().st_size / 1024
    print(f"  [✓] Shapefile de ríos empaquetado: {ruta_zip}")
    print(f"      {len(archivos_encontrados)} archivos, "
          f"{tamano_kb:.1f} KB")
    return str(ruta_zip)


# ═══════════════════════════════════════════════════════════════════
#  EXPORTACIÓN COMPLETA PARA FELT
# ═══════════════════════════════════════════════════════════════════

def exportar_para_felt(
    grafo: GrafoLogistico,
    ruta_optima: Optional[List[str]] = None,
    nombre_ruta: str = "Ruta Óptima Dijkstra",
) -> Dict[str, str]:
    """
    Ejecuta las tres exportaciones para Felt.com en un solo paso.

    Parameters
    ----------
    grafo : GrafoLogistico
    ruta_optima : list[str] | None — ruta calculada por Dijkstra.
    nombre_ruta : str — nombre descriptivo de la ruta.

    Returns
    -------
    dict : rutas de los archivos generados.
    """
    print("\n" + "═" * 60)
    print("  EXPORTACIÓN PARA FELT.COM")
    print("═" * 60)

    archivos = {}

    # 1. Nodos como GeoJSON
    archivos["nodos"] = exportar_nodos_geojson(grafo)

    # 2. Ruta como GeoJSON
    if ruta_optima and len(ruta_optima) >= 2:
        archivos["ruta"] = exportar_ruta_geojson(
            grafo, ruta_optima, nombre_ruta=nombre_ruta
        )
    else:
        print("  [!] No hay ruta óptima para exportar.")

    # 3. Shapefile de ríos como ZIP
    archivos["rios"] = empaquetar_rios_zip()

    print(f"\n  📂 Archivos listos en: {OUTPUT_DIR}")
    print("  → Sube estos 3 archivos a felt.com/map para visualizar")

    return archivos

