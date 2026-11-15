"""
constants.py — Constantes globales del proyecto.

Define parámetros fijos del modelo: tasas de deterioro, temperaturas,
costos base y coordenadas de referencia del corredor logístico.
"""

# ═══════════════════════════════════════════════════════════════════
# COORDENADAS DE REFERENCIA (WGS 84  —  lat, lon)
# ═══════════════════════════════════════════════════════════════════

COORDENADAS = {
    "Puerto Gaitán":  (4.3128, -72.0826),
    "Villavicencio":  (4.1387, -73.6310),
    "Bogotá":         (4.6615, -74.0590),
    "Puerto López":   (4.0862, -72.9550),
}

# ═══════════════════════════════════════════════════════════════════
# CADENA DE FRÍO — parámetros basados en FAO
# ═══════════════════════════════════════════════════════════════════

# Temperatura objetivo para pescado fresco (°C)
TEMP_OBJETIVO_C = 0.0

# Temperatura ambiente promedio en los Llanos (°C)
TEMP_AMBIENTE_LLANOS_C = 30.0

# Tiempo máximo permitido sin refrigeración (horas)
TIEMPO_MAX_SIN_FRIO_H = 4.0

# Vida útil del pescado según temperatura (horas)  — FAO
VIDA_UTIL_HORAS = {
    0:  360,   # ~15 días
    6:  144,   # ~6 días
    12: 72,    # ~3 días
    18: 36,    # ~1.5 días
    24: 12,    # ~0.5 día
    30: 6,     # horas
}

# Relación hielo/pescado recomendada (kg hielo : kg pescado)
RELACION_HIELO_PESCADO = 1.0   # 1:1

# Tasa de deterioro base (%/hora a temperatura ambiente)
TASA_DETERIORO_BASE = 2.5

# ═══════════════════════════════════════════════════════════════════
# COSTOS (COP — Pesos Colombianos)
# ═══════════════════════════════════════════════════════════════════

COSTO_TRANSPORTE_KM = 3500          # COP por km recorrido
COSTO_HIELO_KG = 800                # COP por kg de hielo
COSTO_PERDIDA_KG = 12000            # COP por kg de pescado perdido
PRECIO_VENTA_KG = 15000             # COP precio de venta promedio
COSTO_FIJO_CENTRO_FRIO = 5_000_000  # COP costo fijo mensual por centro

# ═══════════════════════════════════════════════════════════════════
# CAPACIDADES
# ═══════════════════════════════════════════════════════════════════

CAPACIDAD_VEHICULO_KG = 2000        # Capacidad máxima del vehículo
CAPACIDAD_CENTRO_FRIO_KG = 5000     # Capacidad máxima de almacenamiento en frío
VELOCIDAD_PROMEDIO_KMH = 50         # Velocidad promedio en carretera

# ═══════════════════════════════════════════════════════════════════
# TIPOS DE NODOS
# ═══════════════════════════════════════════════════════════════════

class TipoNodo:
    """Códigos de categoría para los nodos del grafo."""
    PESCA       = "P"   # Punto de captura / producción
    ACOPIO      = "A"   # Centro de acopio
    DETERIORO   = "D"   # Zona de medición de deterioro
    HABITAT     = "H"   # Hábitat protegido (restricción ambiental)
    MUELLE      = "M"   # Infraestructura de desembarque
    FRIO        = "F"   # Red de frío / centro de refrigeración
    VENTA       = "V"   # Lugar de venta / mercado

    _TODOS = {
        "P": "Punto de Pesca",
        "A": "Centro de Acopio",
        "D": "Zona de Deterioro",
        "H": "Hábitat Protegido",
        "M": "Muelle",
        "F": "Red de Frío",
        "V": "Lugar de Venta",
    }

    @classmethod
    def descripcion(cls, codigo: str) -> str:
        return cls._TODOS.get(codigo, "Desconocido")

    @classmethod
    def es_valido(cls, codigo: str) -> bool:
        return codigo in cls._TODOS

# ═══════════════════════════════════════════════════════════════════
# PESOS DE LA FUNCIÓN MULTICRITERIO
# ═══════════════════════════════════════════════════════════════════

# w_ij = α·tiempo + β·costo + γ·riesgo + δ·pérdida
#       + ε·(1 - confiabilidad) + ζ·prob_retraso
ALPHA   = 0.25   # peso del tiempo (incluye espera)
BETA    = 0.20   # peso del costo
GAMMA   = 0.20   # peso del riesgo combinado (térmico + accidente + derrumbe)
DELTA   = 0.10   # peso de la pérdida esperada
EPSILON = 0.10   # peso de la no-confiabilidad de la vía
ZETA    = 0.05   # peso de la probabilidad de retraso

# ═══════════════════════════════════════════════════════════════════
# PEAJES
# ═══════════════════════════════════════════════════════════════════

COSTO_PEAJE_PROMEDIO = 12_000   # COP por peaje promedio



# ═══════════════════════════════════════════════════════════════
# EFECTOS DE NODOS ESPECIALES (ADR-04)
# ═══════════════════════════════════════════════════════════════

FACTOR_DETERIORO_ZONA_D = 1.5        # multiplicador de deterioro al entrar a una zona D
TIEMPO_TRANSBORDO_MUELLE_H = 0.25    # espera por transbordo fluvial→terrestre en un muelle M
