"""
scenario_evaluator.py — Evaluador y comparador de escenarios logísticos.

Compara distintas configuraciones de centros de refrigeración
y genera métricas cuantitativas para decidir cuál es la mejor.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import List, Dict, Optional

from ..models.grafo_logistico import GrafoLogistico
from ..algorithms.dijkstra import dijkstra
from ..optimization.cold_chain import SimuladorCadenaFrio, ResultadoSimulacion
from ..utils.constants import (
    TIEMPO_MAX_SIN_FRIO_H,
    COSTO_PERDIDA_KG,
    PRECIO_VENTA_KG,
    COSTO_FIJO_CENTRO_FRIO,
)


@dataclass
class MetricasEscenario:
    """Métricas cuantitativas para un escenario logístico."""
    nombre: str = ""
    num_centros: int = 0
    centros_ids: List[str] = field(default_factory=list)
    distancia_total_km: float = 0.0
    tiempo_total_h: float = 0.0
    tiempo_max_sin_frio_h: float = 0.0
    tiempo_promedio_sin_frio_h: float = 0.0
    kg_total_transportado: float = 0.0
    kg_perdido: float = 0.0
    pct_perdida: float = 0.0
    costo_transporte_cop: float = 0.0
    costo_centros_cop: float = 0.0
    costo_perdida_cop: float = 0.0
    costo_total_cop: float = 0.0
    costo_por_kg_cop: float = 0.0
    cumplimiento_termico_pct: float = 0.0
    cobertura_pesca_pct: float = 0.0

    def resumen(self) -> str:
        lineas = [
            f"\n{'═' * 55}",
            f"  ESCENARIO: {self.nombre}",
            f"{'═' * 55}",
            f"  Centros de frío:          {self.num_centros}",
            f"  Centros:                  {', '.join(self.centros_ids) or 'Ninguno'}",
            f"  Distancia total:          {self.distancia_total_km:,.1f} km",
            f"  Tiempo total:             {self.tiempo_total_h:.2f} h",
            f"  T. máx sin frío:          {self.tiempo_max_sin_frio_h:.2f} h",
            f"  T. prom sin frío:         {self.tiempo_promedio_sin_frio_h:.2f} h",
            f"  Kg transportados:         {self.kg_total_transportado:,.1f}",
            f"  Kg perdidos:              {self.kg_perdido:,.1f} ({self.pct_perdida:.1f}%)",
            f"  Costo transporte:         ${self.costo_transporte_cop:,.0f}",
            f"  Costo centros:            ${self.costo_centros_cop:,.0f}",
            f"  Costo pérdida:            ${self.costo_perdida_cop:,.0f}",
            f"  ─────────────────────────────────────────────",
            f"  COSTO TOTAL:              ${self.costo_total_cop:,.0f}",
            f"  Costo por kg:             ${self.costo_por_kg_cop:,.0f}",
            f"  Cumplimiento térmico:     {self.cumplimiento_termico_pct:.1f}%",
            f"  Cobertura de pesca:       {self.cobertura_pesca_pct:.1f}%",
            f"{'═' * 55}",
        ]
        return "\n".join(lineas)


class EvaluadorEscenarios:
    """
    Evalúa y compara múltiples escenarios logísticos.

    Escenarios típicos:
      1. Sin centros de frío (situación actual).
      2. Un centro de frío.
      3. Múltiples centros optimizados.
      4. Optimización conjunta de centros y rutas.
    """

    def __init__(self, grafo: GrafoLogistico,
                 temp_ambiente: float = 30.0,
                 tiempo_limite_h: float = TIEMPO_MAX_SIN_FRIO_H):
        self.grafo = grafo
        self.simulador = SimuladorCadenaFrio(
            grafo, temp_ambiente, tiempo_limite_h
        )

    def evaluar_escenario(
        self,
        nombre: str,
        centros_activos: List[str],
        destino_final: str = "V_Bogota"
    ) -> MetricasEscenario:
        """
        Evalúa un escenario específico con los centros dados.

        Parameters
        ----------
        nombre : str — nombre descriptivo del escenario.
        centros_activos : list[str] — IDs de centros de frío abiertos.
        destino_final : str — ID del nodo de destino final.
        """
        metricas = MetricasEscenario(
            nombre=nombre,
            num_centros=len(centros_activos),
            centros_ids=centros_activos.copy(),
        )

        puntos_pesca = self.grafo.puntos_pesca()
        if not puntos_pesca:
            return metricas

        simulaciones: List[ResultadoSimulacion] = []
        cubiertos = 0

        for punto in puntos_pesca:
            # Buscar la mejor ruta pasando por al menos un centro activo
            mejor_ruta = None
            mejor_dist = float("inf")

            if centros_activos:
                for centro_id in centros_activos:
                    # pesca → centro (puede pasar por nodos intermedios)
                    d1, r1 = dijkstra(self.grafo, punto.id, centro_id,
                                      criterio="tiempo_h", evitar_restringidos=True)
                    # centro → destino (puede pasar por otros nodos)
                    d2, r2 = dijkstra(self.grafo, centro_id, destino_final,
                                      criterio="tiempo_h", evitar_restringidos=True)
                    if (d1 < float("inf") and d2 < float("inf")
                            and d1 + d2 < mejor_dist):
                        mejor_dist = d1 + d2
                        mejor_ruta = r1 + r2[1:]  # evitar duplicar centro
            else:
                # Sin centros: ruta directa (Dijkstra puro)
                d, r = dijkstra(self.grafo, punto.id, destino_final,
                                criterio="tiempo_h", evitar_restringidos=True)
                if d < float("inf"):
                    mejor_dist = d
                    mejor_ruta = r

            if mejor_ruta and mejor_dist < float("inf"):
                sim = self.simulador.simular_ruta(
                    mejor_ruta, punto.produccion_kg_dia
                )
                simulaciones.append(sim)
                cubiertos += 1

        # Agregar métricas
        if simulaciones:
            metricas.kg_total_transportado = sum(s.kg_inicial for s in simulaciones)
            metricas.kg_perdido = sum(s.perdida_kg for s in simulaciones)
            metricas.distancia_total_km = sum(
                sum(
                    (self.grafo.obtener_arista(
                        s.ruta[i], s.ruta[i + 1]
                    ).distancia_km if self.grafo.obtener_arista(
                        s.ruta[i], s.ruta[i + 1]
                    ) else 0)
                    for i in range(len(s.ruta) - 1)
                )
                for s in simulaciones
            )
            metricas.pct_perdida = (
                metricas.kg_perdido / metricas.kg_total_transportado * 100
                if metricas.kg_total_transportado > 0 else 0
            )
            metricas.tiempo_total_h = sum(s.tiempo_total_h for s in simulaciones)
            metricas.tiempo_max_sin_frio_h = max(
                s.tiempo_sin_frio_total_h for s in simulaciones
            )
            metricas.tiempo_promedio_sin_frio_h = (
                sum(s.tiempo_sin_frio_total_h for s in simulaciones)
                / len(simulaciones)
            )
            metricas.costo_perdida_cop = metricas.kg_perdido * COSTO_PERDIDA_KG
            metricas.costo_centros_cop = len(centros_activos) * COSTO_FIJO_CENTRO_FRIO
            metricas.costo_transporte_cop = sum(
                sum(
                    (self.grafo.obtener_arista(
                        s.ruta[i], s.ruta[i + 1]
                    ).costo_cop if self.grafo.obtener_arista(
                        s.ruta[i], s.ruta[i + 1]
                    ) else 0)
                    for i in range(len(s.ruta) - 1)
                )
                for s in simulaciones
            )
            metricas.costo_total_cop = (
                metricas.costo_transporte_cop
                + metricas.costo_centros_cop
                + metricas.costo_perdida_cop
            )
            kg_entregados = metricas.kg_total_transportado - metricas.kg_perdido
            metricas.costo_por_kg_cop = (
                metricas.costo_total_cop / kg_entregados
                if kg_entregados > 0 else 0
            )
            cumplen = sum(1 for s in simulaciones if s.cumple_limite)
            metricas.cumplimiento_termico_pct = cumplen / len(simulaciones) * 100

        metricas.cobertura_pesca_pct = (
            cubiertos / len(puntos_pesca) * 100
            if puntos_pesca else 0
        )

        return metricas

    def comparar_escenarios(
        self,
        escenarios: List[Dict],
        destino_final: str = "V_Bogota"
    ) -> List[MetricasEscenario]:
        """
        Compara múltiples escenarios.

        Parameters
        ----------
        escenarios : list[dict]
            Cada dict tiene 'nombre' y 'centros'.
            Ejemplo: [
                {"nombre": "Sin frío", "centros": []},
                {"nombre": "1 centro", "centros": ["F01"]},
            ]
        """
        resultados = []
        for esc in escenarios:
            metricas = self.evaluar_escenario(
                esc["nombre"], esc["centros"], destino_final
            )
            resultados.append(metricas)
        return resultados

    @staticmethod
    def tabla_comparativa(metricas_lista: List[MetricasEscenario]) -> str:
        """Genera una tabla comparativa de escenarios."""
        ancho = 90
        lineas = [
            "\n" + "═" * ancho,
            "  COMPARACIÓN DE ESCENARIOS",
            "═" * ancho,
            f"  {'Escenario':<30} {'# CF':>5} {'Pérdida':>9} "
            f"{'Costo Total':>16} {'$/kg':>10} {'Cump.':>7}",
            "  " + "─" * (ancho - 2),
        ]
        for m in metricas_lista:
            cump = f"{m.cumplimiento_termico_pct:.0f}%" if m.kg_total_transportado > 0 else "N/A"
            lineas.append(
                f"  {m.nombre:<30} {m.num_centros:>5} "
                f"{m.pct_perdida:>8.1f}% "
                f"${m.costo_total_cop:>15,.0f} "
                f"${m.costo_por_kg_cop:>9,.0f} "
                f"{cump:>7}"
            )
        lineas.append("═" * ancho)
        return "\n".join(lineas)

