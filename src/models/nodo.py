"""
nodo.py — Modelo de datos para los nodos del grafo logístico.

Cada nodo representa un punto geográfico con atributos específicos
según su tipo: pesca, acopio, muelle, frío, venta, etc.

Tipos de nodo:
    P: Punto de Pesca      A: Centro de Acopio
    D: Zona de Deterioro   H: Hábitat Protegido
    M: Muelle              F: Red de Frío
    V: Lugar de Venta
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Optional, Dict, Any

from ..utils.constants import TipoNodo


@dataclass
class Nodo:
    """
    Representa un nodo dentro del grafo de la cadena pesquera.

    Attributes
    ----------
    id : str
        Identificador único (ej. "P01", "A03", "V_Bogota").
    nombre : str
        Nombre descriptivo del lugar.
    tipo : str
        Código de categoría (P, A, D, H, M, F, V).
    latitud : float
        Coordenada latitud (WGS 84).
    longitud : float
        Coordenada longitud (WGS 84).
    produccion_kg_dia : float
        Producción pesquera diaria (solo nodos tipo P).
    capacidad_frio_kg : float
        Capacidad de almacenamiento en frío (solo nodos tipo F).
    costo_fijo : float
        Costo fijo mensual de operación (COP).
    tiene_muelle : bool
        Si cuenta con infraestructura de desembarque.
    tiene_energia : bool
        Si tiene suministro eléctrico confiable.
    tiene_agua : bool
        Si tiene agua potable disponible.
    restriccion_ambiental : bool
        Si es zona de hábitat protegido.
    metadata : dict
        Atributos adicionales flexibles.
    """

    id: str
    nombre: str
    tipo: str
    latitud: float = 0.0
    longitud: float = 0.0
    produccion_kg_dia: float = 0.0
    capacidad_frio_kg: float = 0.0
    costo_fijo: float = 0.0
    tiene_muelle: bool = False
    tiene_energia: bool = True
    tiene_agua: bool = True
    restriccion_ambiental: bool = False
    metadata: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        if not TipoNodo.es_valido(self.tipo):
            raise ValueError(
                f"Tipo de nodo '{self.tipo}' no válido. "
                f"Use: P, A, D, H, M, F, V"
            )

    @property
    def coordenadas(self) -> tuple:
        """Devuelve (latitud, longitud)."""
        return (self.latitud, self.longitud)

    @property
    def tipo_descripcion(self) -> str:
        """Descripción legible del tipo de nodo."""
        return TipoNodo.descripcion(self.tipo)

    @property
    def es_candidato_frio(self) -> bool:
        """Indica si el nodo podría albergar un centro de frío."""
        return (
            self.tipo in (TipoNodo.ACOPIO, TipoNodo.FRIO)
            and self.tiene_energia
            and not self.restriccion_ambiental
        )

    @property
    def es_origen(self) -> bool:
        """Indica si es un nodo de producción (origen de flujo)."""
        return self.tipo == TipoNodo.PESCA

    @property
    def es_destino(self) -> bool:
        """Indica si es un nodo de mercado (destino de flujo)."""
        return self.tipo == TipoNodo.VENTA

    def to_dict(self) -> Dict[str, Any]:
        """Convierte el nodo a diccionario serializable."""
        return {
            "id": self.id,
            "nombre": self.nombre,
            "tipo": self.tipo,
            "tipo_descripcion": self.tipo_descripcion,
            "latitud": self.latitud,
            "longitud": self.longitud,
            "produccion_kg_dia": self.produccion_kg_dia,
            "capacidad_frio_kg": self.capacidad_frio_kg,
            "costo_fijo": self.costo_fijo,
            "tiene_muelle": self.tiene_muelle,
            "tiene_energia": self.tiene_energia,
            "tiene_agua": self.tiene_agua,
            "restriccion_ambiental": self.restriccion_ambiental,
        }

    def __repr__(self) -> str:
        return (
            f"Nodo(id='{self.id}', nombre='{self.nombre}', "
            f"tipo='{self.tipo}' [{self.tipo_descripcion}])"
        )

    def __hash__(self) -> int:
        return hash(self.id)

    def __eq__(self, other) -> bool:
        if isinstance(other, Nodo):
            return self.id == other.id
        return NotImplemented

