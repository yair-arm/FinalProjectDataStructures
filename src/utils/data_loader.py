"""
data_loader.py — Carga y exportación de datos del proyecto.

Lee archivos CSV con nodos y aristas, carga shapefiles de ríos
y exporta resultados en distintos formatos.
"""

import csv
import os
from pathlib import Path
from typing import List, Dict, Any, Optional

# Ruta base del proyecto (dos niveles arriba de este archivo)
_BASE_DIR = Path(__file__).resolve().parent.parent.parent
DATA_DIR = _BASE_DIR / "data"
CSV_DIR = DATA_DIR / "csv"
SHP_DIR = DATA_DIR / "shapefiles"
OUTPUT_DIR = DATA_DIR / "output"


def cargar_nodos_csv(nombre_archivo: str) -> List[Dict[str, Any]]:
    """
    Lee un CSV de nodos y devuelve una lista de diccionarios.

    El CSV debe tener encabezados; las columnas numéricas se
    convierten automáticamente a float/int.
    """
    ruta = CSV_DIR / nombre_archivo
    if not ruta.exists():
        raise FileNotFoundError(f"No se encontró: {ruta}")

    nodos: List[Dict[str, Any]] = []
    with open(ruta, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for fila in reader:
            nodo = {}
            for clave, valor in fila.items():
                nodo[clave] = _convertir_valor(valor)
            nodos.append(nodo)
    return nodos


def cargar_aristas_csv(nombre_archivo: str = "aristas.csv") -> List[Dict[str, Any]]:
    """
    Lee un CSV de aristas y devuelve una lista de diccionarios.

    Columnas esperadas: origen, destino, distancia_km, tiempo_h,
    costo_cop, riesgo_termico, estado_via.
    """
    return cargar_nodos_csv(nombre_archivo)


def guardar_resultados_csv(datos: List[Dict[str, Any]],
                           nombre_archivo: str) -> str:
    """Escribe una lista de diccionarios como CSV en data/output/."""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    ruta = OUTPUT_DIR / nombre_archivo

    if not datos:
        return str(ruta)

    encabezados = list(datos[0].keys())
    with open(ruta, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=encabezados)
        writer.writeheader()
        writer.writerows(datos)

    return str(ruta)


def cargar_shapefile_rios() -> Any:
    """
    Carga el shapefile de ríos como GeoDataFrame.
    Requiere geopandas instalado.
    """
    try:
        import geopandas as gpd
    except ImportError:
        raise ImportError(
            "Se necesita geopandas para cargar shapefiles. "
            "Instalar con: pip install geopandas"
        )

    ruta_shp = SHP_DIR / "rios.shp"
    if not ruta_shp.exists():
        raise FileNotFoundError(f"No se encontró el shapefile: {ruta_shp}")

    gdf = gpd.read_file(str(ruta_shp))
    return gdf


def listar_archivos_datos() -> Dict[str, List[str]]:
    """Lista todos los archivos disponibles en data/."""
    resultado = {"csv": [], "shapefiles": [], "output": []}
    for carpeta, clave in [(CSV_DIR, "csv"), (SHP_DIR, "shapefiles"),
                            (OUTPUT_DIR, "output")]:
        if carpeta.exists():
            resultado[clave] = [f.name for f in carpeta.iterdir() if f.is_file()]
    return resultado


# ─── Utilidades internas ─────────────────────────────────────────

def _convertir_valor(valor: str) -> Any:
    """Intenta convertir un string a int, float o lo deja como str."""
    valor = valor.strip()
    if not valor:
        return None
    try:
        return int(valor)
    except ValueError:
        pass
    try:
        return float(valor)
    except ValueError:
        pass
    return valor

