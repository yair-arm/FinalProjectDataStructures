"""
itinerarios.py — Itinerarios completos por punto de pesca.

Para cada punto de pesca (P) construye la ruta real de la cadena:

    P → (muelle M) → acopio A → centro de frío F → destino V

usando Dijkstra propio con criterio ``tiempo_h`` y evitando los nodos
de hábitat protegido (``restriccion_ambiental``), conforme a ADR-04 y
ADR-06. Si un punto de pesca no alcanza ningún acopio (p. ej. P06, en
el casco urbano junto a F02) se usa la ruta directa P → F → destino.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import List, Optional, Tuple

from ..algorithms.dijkstra import dijkstra
from ..models.grafo_logistico import GrafoLogistico
from .cold_chain import SimuladorCadenaFrio

INF = float("inf")


@dataclass
class Tramo:
    """Un tramo (arista) del itinerario."""
    origen: str
    destino: str
    tipo_via: str
    distancia_km: float
    tiempo_h: float
    tipo_nodo_destino: str
    efecto: str


@dataclass
class Itinerario:
    """Itinerario completo de un punto de pesca hasta el destino."""
    origen_id: str
    tramos: List[Tramo] = field(default_factory=list)
    acopio_id: Optional[str] = None
    centro_frio_id: Optional[str] = None
    destino_id: str = ""
    distancia_total_km: float = 0.0
    tiempo_total_h: float = 0.0
    perdida_pct: float = 0.0
    kg_inicial: float = 0.0
    kg_final: float = 0.0
    nodos_restringidos_evitados: List[str] = field(default_factory=list)
    ruta: List[str] = field(default_factory=list)

    def resumen(self) -> str:
        """Texto legible de una línea con el recorrido y sus métricas."""
        evitados = (
            f" | evita hábitat: {', '.join(self.nodos_restringidos_evitados)}"
            if self.nodos_restringidos_evitados else ""
        )
        return (
            f"{self.origen_id} → {self.destino_id}: "
            f"{' → '.join(self.ruta)}\n"
            f"     Acopio: {self.acopio_id or '—'} | "
            f"Frío: {self.centro_frio_id or '—'} | "
            f"{self.distancia_total_km:.1f} km | "
            f"{self.tiempo_total_h:.2f} h | "
            f"pérdida {self.perdida_pct:.1f}% "
            f"({self.kg_inicial:.1f} → {self.kg_final:.1f} kg){evitados}"
        )


def _unir(*segmentos: List[str]) -> List[str]:
    """Concatena caminos que comparten nodo de empalme."""
    ruta: List[str] = []
    for seg in segmentos:
        ruta.extend(seg if not ruta else seg[1:])
    return ruta


def _camino(grafo: GrafoLogistico, a: str, b: str,
            evitar: bool) -> Tuple[float, List[str]]:
    if a == b:
        return 0.0, [a]
    return dijkstra(grafo, a, b, criterio="tiempo_h",
                    evitar_restringidos=evitar)


def _mejor_ruta(grafo: GrafoLogistico, origen: str, destino: str,
                acopios: List[str], centros: List[str]
                ) -> Tuple[List[str], Optional[str], Optional[str]]:
    """Elige la combinación (A, F) de menor tiempo total evitando H."""
    mejor: Tuple[float, List[str], Optional[str], Optional[str]] = (
        INF, [], None, None)

    # P06 está en el casco urbano junto a F02 (excepción explícita ADR-06)
    excepcion_directa = (origen == "P06")

    if not excepcion_directa:
        for c in centros:
            d3, r3 = _camino(grafo, c, destino, True)
            if d3 == INF:
                continue
            for a in acopios:
                d1, r1 = _camino(grafo, origen, a, True)
                d2, r2 = _camino(grafo, a, c, True)
                if INF in (d1, d2):
                    continue
                total = d1 + d2 + d3
                if total < mejor[0]:
                    mejor = (total, _unir(r1, r2, r3), a, c)

    if mejor[0] == INF:
        # Sin acopio alcanzable o caso directo P06: ruta directa P → F → destino
        for c in centros:
            d1, r1 = _camino(grafo, origen, c, True)
            d3, r3 = _camino(grafo, c, destino, True)
            if INF in (d1, d3):
                continue
            if d1 + d3 < mejor[0]:
                mejor = (d1 + d3, _unir(r1, r3), None, c)

    if mejor[0] == INF:
        # Último recurso: camino directo al destino
        d, r = _camino(grafo, origen, destino, True)
        if d < INF:
            return r, None, None
        return [], None, None
    return mejor[1], mejor[2], mejor[3]


def _restringidos_en(grafo: GrafoLogistico, ruta: List[str]) -> List[str]:
    return [n for n in ruta
            if (grafo.obtener_nodo(n) is not None
                and grafo.obtener_nodo(n).restriccion_ambiental)]


def _evitados(grafo: GrafoLogistico, origen: str, destino: str,
              acopio: Optional[str], centro: Optional[str],
              ruta: List[str]) -> List[str]:
    """Nodos H que aparecerían en el mismo recorrido sin la restricción."""
    puntos = [origen] + [x for x in (acopio, centro) if x] + [destino]
    segmentos: List[List[str]] = []
    for a, b in zip(puntos, puntos[1:]):
        d, r = _camino(grafo, a, b, False)
        if d == INF:
            return []
        segmentos.append(r)
    libre = _unir(*segmentos)
    usados = set(_restringidos_en(grafo, ruta))
    evitados: List[str] = []
    for n in _restringidos_en(grafo, libre):
        if n not in usados and n not in evitados:
            evitados.append(n)
    return evitados


def calcular_itinerarios(grafo: GrafoLogistico, destino_id: str,
                         centros_frio: Optional[List[str]] = None
                         ) -> List[Itinerario]:
    """
    Calcula un itinerario por cada punto de pesca hacia ``destino_id``.

    Parameters
    ----------
    grafo : GrafoLogistico
    destino_id : str — nodo de venta final.
    centros_frio : list[str] | None — centros F a usar (por defecto, todos
        los F del grafo).
    """
    if destino_id not in grafo:
        raise KeyError(f"Destino '{destino_id}' no existe en el grafo.")

    centros = list(centros_frio) if centros_frio else [
        n.id for n in grafo.centros_frio()]
    acopios = [n.id for n in grafo.nodos_por_tipo("A")]
    simulador = SimuladorCadenaFrio(grafo)
    resultado: List[Itinerario] = []

    for punto in grafo.puntos_pesca():
        ruta, acopio, centro = _mejor_ruta(
            grafo, punto.id, destino_id, acopios, centros)
        if not ruta:
            continue

        kg = punto.produccion_kg_dia
        sim = simulador.simular_ruta(ruta, kg)

        tramos: List[Tramo] = []
        efectos = {e.nodo_id: e.efecto for e in sim.estados[1:]}
        km = 0.0
        for a, b in zip(ruta, ruta[1:]):
            ar = grafo.obtener_arista(a, b)
            if ar is None:
                continue
            nodo_b = grafo.obtener_nodo(b)
            km += ar.distancia_km
            tramos.append(Tramo(
                origen=a, destino=b, tipo_via=ar.tipo_via,
                distancia_km=ar.distancia_km, tiempo_h=ar.tiempo_h,
                tipo_nodo_destino=nodo_b.tipo if nodo_b else "",
                efecto=efectos.get(b, ""),
            ))

        resultado.append(Itinerario(
            origen_id=punto.id, tramos=tramos, acopio_id=acopio,
            centro_frio_id=centro, destino_id=destino_id,
            distancia_total_km=km, tiempo_total_h=sim.tiempo_total_h,
            perdida_pct=sim.perdida_pct, kg_inicial=sim.kg_inicial,
            kg_final=sim.kg_final,
            nodos_restringidos_evitados=_evitados(
                grafo, punto.id, destino_id, acopio, centro, ruta),
            ruta=ruta,
        ))
    return resultado
