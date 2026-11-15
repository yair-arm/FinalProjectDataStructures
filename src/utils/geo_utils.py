"""
geo_utils.py — Funciones geográficas y cálculos de distancia.

Incluye la fórmula de Haversine para distancias geodésicas,
cálculo de tiempo de viaje y conversión de coordenadas.
"""

import math
from typing import Tuple

from .constants import VELOCIDAD_PROMEDIO_KMH


# Radio medio de la Tierra en kilómetros
_RADIO_TIERRA_KM = 6371.0


def haversine(coord1: Tuple[float, float],
              coord2: Tuple[float, float]) -> float:
    """
    Calcula la distancia en km entre dos puntos geográficos
    usando la fórmula de Haversine.

    Parameters
    ----------
    coord1 : tuple (lat, lon) en grados decimales.
    coord2 : tuple (lat, lon) en grados decimales.

    Returns
    -------
    float : distancia en kilómetros.
    """
    lat1, lon1 = math.radians(coord1[0]), math.radians(coord1[1])
    lat2, lon2 = math.radians(coord2[0]), math.radians(coord2[1])

    dlat = lat2 - lat1
    dlon = lon2 - lon1

    a = (math.sin(dlat / 2) ** 2
         + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2) ** 2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    return _RADIO_TIERRA_KM * c


def calcular_tiempo_viaje(distancia_km: float,
                          velocidad_kmh: float = VELOCIDAD_PROMEDIO_KMH,
                          factor_estado_via: float = 1.0) -> float:
    """
    Estima el tiempo de viaje en horas.

    Parameters
    ----------
    distancia_km : float
        Distancia del tramo en kilómetros.
    velocidad_kmh : float
        Velocidad promedio (por defecto la constante global).
    factor_estado_via : float
        Multiplicador que penaliza vías en mal estado (1.0 = buena,
        1.5 = regular, 2.0 = mala).

    Returns
    -------
    float : tiempo estimado en horas.
    """
    if velocidad_kmh <= 0:
        raise ValueError("La velocidad debe ser positiva.")
    velocidad_efectiva = velocidad_kmh / factor_estado_via
    return distancia_km / velocidad_efectiva


def calcular_deterioro(tiempo_sin_frio_h: float,
                       temp_ambiente_c: float = 30.0) -> float:
    """
    Estima el porcentaje de deterioro del pescado según el tiempo
    de exposición sin refrigeración y la temperatura ambiente.

    Modelo simplificado basado en datos FAO:
        deterioro(%) = tasa_base × tiempo × factor_temperatura

    Parameters
    ----------
    tiempo_sin_frio_h : float
        Horas sin refrigeración.
    temp_ambiente_c : float
        Temperatura ambiente en °C.

    Returns
    -------
    float : porcentaje de deterioro estimado (0-100).
    """
    # Factor de temperatura: crece exponencialmente sobre 0 °C
    factor_temp = 1.0 + (temp_ambiente_c / 10.0)
    tasa_base = 2.5  # %/hora a 30 °C
    deterioro = tasa_base * tiempo_sin_frio_h * (factor_temp / 4.0)
    return min(deterioro, 100.0)


def dms_a_decimal(grados: float, minutos: float, segundos: float,
                  direccion: str = "N") -> float:
    """
    Convierte coordenadas de grados/minutos/segundos a decimal.

    Parameters
    ----------
    grados, minutos, segundos : float
    direccion : str — 'N', 'S', 'E', 'W'

    Returns
    -------
    float : coordenada en grados decimales.
    """
    decimal = abs(grados) + minutos / 60.0 + segundos / 3600.0
    if direccion.upper() in ("S", "W"):
        decimal = -decimal
    return decimal

