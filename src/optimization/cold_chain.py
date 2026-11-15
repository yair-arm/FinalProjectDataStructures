"""
cold_chain.py — Simulador de cadena de frío.

Modela el deterioro del pescado a lo largo de una ruta, considerando
temperatura ambiente, presencia de hielo, paradas en centros de
frío y transbordos.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import List, Dict, Optional

from ..models.grafo_logistico import GrafoLogistico
from ..utils.constants import (
    TEMP_OBJETIVO_C,
    TEMP_AMBIENTE_LLANOS_C,
    RELACION_HIELO_PESCADO,
    VIDA_UTIL_HORAS,
    COSTO_PERDIDA_KG,
    PRECIO_VENTA_KG,
    FACTOR_DETERIORO_ZONA_D,
    TIEMPO_TRANSBORDO_MUELLE_H,
)
from ..utils.geo_utils import calcular_deterioro


@dataclass
class EstadoProducto:
    """Estado del pescado en un punto de la ruta."""
    nodo_id: str
    tiempo_acumulado_h: float = 0.0
    tiempo_sin_frio_h: float = 0.0
    temperatura_actual_c: float = TEMP_AMBIENTE_LLANOS_C
    deterioro_pct: float = 0.0
    kg_inicial: float = 0.0
    kg_actual: float = 0.0
    refrigerado: bool = False
    efecto: str = ""


@dataclass
class ResultadoSimulacion:
    """Resultado completo de la simulación de una ruta."""
    ruta: List[str] = field(default_factory=list)
    estados: List[EstadoProducto] = field(default_factory=list)
    kg_inicial: float = 0.0
    kg_final: float = 0.0
    perdida_kg: float = 0.0
    perdida_pct: float = 0.0
    costo_perdida_cop: float = 0.0
    tiempo_total_h: float = 0.0
    tiempo_sin_frio_total_h: float = 0.0
    num_paradas_frio: int = 0
    num_transbordos: int = 0
    cumple_limite: bool = False

    def resumen(self) -> str:
        lineas = [
            "═" * 55,
            "  SIMULACIÓN DE CADENA DE FRÍO",
            "═" * 55,
            f"  Ruta:                   {' → '.join(self.ruta)}",
            f"  Kg iniciales:           {self.kg_inicial:.1f}",
            f"  Kg finales:             {self.kg_final:.1f}",
            f"  Pérdida:                {self.perdida_kg:.1f} kg ({self.perdida_pct:.1f}%)",
            f"  Costo pérdida:          ${self.costo_perdida_cop:,.0f} COP",
            f"  Tiempo total:           {self.tiempo_total_h:.2f} h",
            f"  Tiempo sin frío:        {self.tiempo_sin_frio_total_h:.2f} h",
            f"  Paradas con frío:       {self.num_paradas_frio}",
            f"  Transbordos (muelle):   {self.num_transbordos}",
            f"  Cumple límite:          {'✓ Sí' if self.cumple_limite else '✗ No'}",
            "═" * 55,
        ]
        return "\n".join(lineas)


class SimuladorCadenaFrio:
    """
    Simula el recorrido de un lote de pescado a lo largo de una ruta
    y calcula el deterioro acumulado paso a paso.
    """

    def __init__(self, grafo: GrafoLogistico,
                 temp_ambiente: float = TEMP_AMBIENTE_LLANOS_C,
                 tiempo_limite_h: float = 4.0):
        self.grafo = grafo
        self.temp_ambiente = temp_ambiente
        self.tiempo_limite_h = tiempo_limite_h

    def simular_ruta(self, ruta: List[str],
                     kg_pescado: float) -> ResultadoSimulacion:
        """
        Simula el transporte de pescado a lo largo de una ruta.

        Parameters
        ----------
        ruta : list[str] — secuencia de IDs de nodos.
        kg_pescado : float — kilogramos iniciales de pescado.

        Returns
        -------
        ResultadoSimulacion
        """
        resultado = ResultadoSimulacion(
            ruta=ruta,
            kg_inicial=kg_pescado,
        )

        if len(ruta) < 2:
            resultado.kg_final = kg_pescado
            resultado.cumple_limite = True
            return resultado

        kg_actual = kg_pescado
        tiempo_acumulado = 0.0
        tiempo_sin_frio = 0.0
        deterioro_total = 0.0

        # Estado inicial
        estado_inicio = EstadoProducto(
            nodo_id=ruta[0],
            kg_inicial=kg_pescado,
            kg_actual=kg_pescado,
            temperatura_actual_c=self.temp_ambiente,
        )
        resultado.estados.append(estado_inicio)

        for i in range(len(ruta) - 1):
            origen = ruta[i]
            destino = ruta[i + 1]

            # Obtener arista
            arista = self.grafo.obtener_arista(origen, destino)
            if arista is None:
                continue

            # Recorrer el tramo
            tiempo_acumulado += arista.tiempo_h

            # ¿El nodo destino tiene frío?
            nodo_destino = self.grafo.obtener_nodo(destino)
            tiene_frio = (
                nodo_destino is not None
                and nodo_destino.tipo in ("F", "A")
                and nodo_destino.capacidad_frio_kg > 0
            )

            tipo_destino = nodo_destino.tipo if nodo_destino else ""
            efecto = ""
            tiempo_tramo = arista.tiempo_h
            deterioro_tramo = calcular_deterioro(
                arista.tiempo_h, self.temp_ambiente
            )

            if tipo_destino == "D":
                deterioro_tramo *= FACTOR_DETERIORO_ZONA_D
                efecto = f"Zona de deterioro ×{FACTOR_DETERIORO_ZONA_D:g}"
            elif tipo_destino == "M":
                # Transbordo fluvial→terrestre: espera sin frío
                tiempo_tramo += TIEMPO_TRANSBORDO_MUELLE_H
                tiempo_acumulado += TIEMPO_TRANSBORDO_MUELLE_H
                deterioro_tramo = calcular_deterioro(
                    tiempo_tramo, self.temp_ambiente
                )
                resultado.num_transbordos += 1
                efecto = "Transbordo en muelle"

            tiempo_sin_frio += tiempo_tramo
            deterioro_total += deterioro_tramo
            kg_perdidos = kg_actual * (deterioro_tramo / 100.0)
            kg_actual -= kg_perdidos

            if tiene_frio:
                # Refrigeración: reset del timer
                resultado.num_paradas_frio += 1
                tiempo_sin_frio = 0.0
                efecto = "Refrigerado"

            # Registrar estado
            estado = EstadoProducto(
                nodo_id=destino,
                tiempo_acumulado_h=tiempo_acumulado,
                tiempo_sin_frio_h=tiempo_sin_frio,
                temperatura_actual_c=(
                    TEMP_OBJETIVO_C if tiene_frio else self.temp_ambiente
                ),
                deterioro_pct=deterioro_total,
                kg_inicial=kg_pescado,
                kg_actual=max(kg_actual, 0),
                refrigerado=tiene_frio,
                efecto=efecto,
            )
            resultado.estados.append(estado)

        # Resultados finales
        resultado.kg_final = max(kg_actual, 0)
        resultado.perdida_kg = kg_pescado - resultado.kg_final
        resultado.perdida_pct = (
            (resultado.perdida_kg / kg_pescado * 100) if kg_pescado > 0 else 0
        )
        resultado.costo_perdida_cop = resultado.perdida_kg * COSTO_PERDIDA_KG
        resultado.tiempo_total_h = tiempo_acumulado
        resultado.tiempo_sin_frio_total_h = tiempo_sin_frio
        resultado.cumple_limite = (
            tiempo_sin_frio <= self.tiempo_limite_h
        )

        return resultado

    def simular_todas_rutas(
        self, rutas: Dict[str, List[str]], kg_por_punto: Dict[str, float]
    ) -> List[ResultadoSimulacion]:
        """Simula múltiples rutas y devuelve todos los resultados."""
        resultados = []
        for origen, ruta in rutas.items():
            kg = kg_por_punto.get(origen, 0)
            if kg > 0:
                res = self.simular_ruta(ruta, kg)
                resultados.append(res)
        return resultados

