"""
arista.py — Modelo de datos para las aristas del grafo logístico.

Cada arista conecta dos nodos y almacena atributos logísticos
multicriterio completos: distancia, tiempo, costo, riesgo térmico,
probabilidad de retrasos, riesgo de accidentes/derrumbes, peajes,
restricciones de peso, horarios, flujo vehicular, confiabilidad
de la vía y tiempo de espera.

El peso combinado se calcula con la función multicriterio de 6 factores:
  w_ij = α·tiempo + β·costo + γ·riesgo + δ·pérdida + ε·(1-confiab) + ζ·retraso
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, Any, Optional

from ..utils.constants import (
    ALPHA, BETA, GAMMA, DELTA, EPSILON, ZETA,
    COSTO_TRANSPORTE_KM,
    TASA_DETERIORO_BASE,
    COSTO_PEAJE_PROMEDIO,
)


@dataclass
class Arista:
    """
    Representa una conexión dirigida entre dos nodos del grafo.

    Attributes — Básicos
    ----------
    origen, destino : str — IDs de los nodos.
    distancia_km : float — Distancia del tramo (km).
    tiempo_h : float — Tiempo de recorrido estimado (horas).
    costo_cop : float — Costo de transporte (COP).
    riesgo_termico : float — Riesgo de ruptura de cadena de frío (0–1).
    estado_via : str — 'buena', 'regular', 'mala'.
    tipo_via : str — 'terrestre', 'fluvial', 'acceso_local'.
    capacidad_kg : float — Capacidad máxima de transporte (kg).

    Attributes — Extendidos (FLP multicriterio)
    ----------
    prob_retraso : float — Probabilidad de retrasos (0–1).
    riesgo_accidente : float — Riesgo de accidentes (0–1).
    riesgo_derrumbe : float — Riesgo de derrumbes (0–1).
    restriccion_peso_ton : float — Límite de peso (toneladas, 0=sin límite).
    peajes : int — Número de peajes en el tramo.
    costo_peajes_cop : float — Costo total de peajes (COP).
    horario_restriccion : str — 'ninguno', 'nocturno', 'diurno'.
    flujo_vehicular : str — 'bajo', 'medio', 'alto'.
    tiempo_espera_h : float — Tiempo de espera (carga/descarga/peajes).
    confiabilidad_via : float — Confiabilidad general (0–1, 1=muy confiable).
    num_transbordos : int — Cambios de vehículo/contenedor.
    metadata : dict — Atributos adicionales flexibles.
    """

    # ── Campos básicos ───────────────────────────────────────
    origen: str
    destino: str
    distancia_km: float = 0.0
    tiempo_h: float = 0.0
    costo_cop: float = 0.0
    riesgo_termico: float = 0.0
    estado_via: str = "buena"
    tipo_via: str = "terrestre"
    capacidad_kg: float = 2000.0

    # ── Campos extendidos (FLP multicriterio) ────────────────
    prob_retraso: float = 0.0
    riesgo_accidente: float = 0.0
    riesgo_derrumbe: float = 0.0
    restriccion_peso_ton: float = 0.0
    peajes: int = 0
    costo_peajes_cop: float = 0.0
    horario_restriccion: str = "ninguno"
    flujo_vehicular: str = "bajo"
    tiempo_espera_h: float = 0.0
    confiabilidad_via: float = 0.90

    num_transbordos: int = 0
    metadata: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        """Calcula costos por defecto si no fueron provistos."""
        if self.costo_cop == 0.0 and self.distancia_km > 0:
            self.costo_cop = self.distancia_km * COSTO_TRANSPORTE_KM
        if self.costo_peajes_cop == 0.0 and self.peajes > 0:
            self.costo_peajes_cop = self.peajes * COSTO_PEAJE_PROMEDIO

    # ── Factores derivados ──────────────────────────────────

    @property
    def factor_estado_via(self) -> float:
        """Multiplicador de penalización por estado de la vía."""
        factores = {"buena": 1.0, "regular": 1.5, "mala": 2.0}
        return factores.get(self.estado_via, 1.0)

    @property
    def factor_flujo(self) -> float:
        """Multiplicador por nivel de flujo vehicular."""
        factores = {"bajo": 1.0, "medio": 1.15, "alto": 1.35}
        return factores.get(self.flujo_vehicular, 1.0)

    @property
    def riesgo_combinado(self) -> float:
        """Riesgo combinado: térmico + accidente + derrumbe (0–1)."""
        r = (0.50 * self.riesgo_termico
             + 0.25 * self.riesgo_accidente
             + 0.25 * self.riesgo_derrumbe)
        return min(r, 1.0)

    @property
    def tiempo_efectivo_h(self) -> float:
        """Tiempo total incluyendo espera y factor de flujo."""
        return (self.tiempo_h * self.factor_flujo) + self.tiempo_espera_h

    @property
    def costo_total_cop(self) -> float:
        """Costo total del tramo: transporte + peajes."""
        return self.costo_cop + self.costo_peajes_cop

    @property
    def perdida_esperada(self) -> float:
        """Porcentaje de pérdida estimada en el tramo (0–100)."""
        factor_conf = 1.0 + (1.0 - self.confiabilidad_via) * 0.5
        factor_retraso = 1.0 + self.prob_retraso * 0.3
        return min(
            TASA_DETERIORO_BASE
            * self.tiempo_efectivo_h
            * self.factor_estado_via
            * factor_conf
            * factor_retraso,
            100.0,
        )

    # ── Peso multicriterio ──────────────────────────────────

    def peso(self, alpha: float = ALPHA, beta: float = BETA,
             gamma: float = GAMMA, delta: float = DELTA,
             epsilon: float = EPSILON, zeta: float = ZETA) -> float:
        """
        Calcula el peso combinado multicriterio de la arista.

        w_ij = α·tiempo + β·costo + γ·riesgo + δ·pérdida
               + ε·(1 - confiabilidad) + ζ·prob_retraso

        Normalización:
          - tiempo:       horas (0–48), incluye espera
          - costo:        millones COP (0–5), incluye peajes
          - riesgo:       combinado térmico+accidente+derrumbe (0–1)
          - pérdida:      porcentaje normalizado (0–1)
          - confiabilidad: invertida (0–1)
          - retraso:      probabilidad (0–1)
        """
        t_norm = self.tiempo_efectivo_h / 48.0
        c_norm = self.costo_total_cop / 5_000_000.0
        r_norm = self.riesgo_combinado
        p_norm = self.perdida_esperada / 100.0
        conf_norm = 1.0 - self.confiabilidad_via
        ret_norm = self.prob_retraso

        return (alpha * t_norm
                + beta * c_norm
                + gamma * r_norm
                + delta * p_norm
                + epsilon * conf_norm
                + zeta * ret_norm)

    @property
    def peso_default(self) -> float:
        """Peso con coeficientes por defecto."""
        return self.peso()

    # ── Serialización ────────────────────────────────────────

    def to_dict(self) -> Dict[str, Any]:
        """Convierte la arista a diccionario serializable."""
        return {
            "origen": self.origen,
            "destino": self.destino,
            "distancia_km": self.distancia_km,
            "tiempo_h": self.tiempo_h,
            "costo_cop": self.costo_cop,
            "riesgo_termico": self.riesgo_termico,
            "estado_via": self.estado_via,
            "tipo_via": self.tipo_via,
            "capacidad_kg": self.capacidad_kg,
            "prob_retraso": self.prob_retraso,
            "riesgo_accidente": self.riesgo_accidente,
            "riesgo_derrumbe": self.riesgo_derrumbe,
            "restriccion_peso_ton": self.restriccion_peso_ton,
            "peajes": self.peajes,
            "costo_peajes_cop": self.costo_peajes_cop,
            "horario_restriccion": self.horario_restriccion,
            "flujo_vehicular": self.flujo_vehicular,
            "tiempo_espera_h": self.tiempo_espera_h,
            "confiabilidad_via": self.confiabilidad_via,
            "num_transbordos": self.num_transbordos,
            "peso_combinado": self.peso_default,
            "perdida_esperada": self.perdida_esperada,
            "riesgo_combinado": self.riesgo_combinado,
            "tiempo_efectivo_h": self.tiempo_efectivo_h,
            "costo_total_cop": self.costo_total_cop,
        }

    def __repr__(self) -> str:
        return (
            f"Arista({self.origen} → {self.destino}, "
            f"{self.distancia_km:.1f}km, {self.tiempo_efectivo_h:.2f}h, "
            f"peso={self.peso_default:.4f})"
        )
