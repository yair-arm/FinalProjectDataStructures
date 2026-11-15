"""
grafo_logistico.py — Grafo dirigido multicriterio para la cadena pesquera.

Implementa un grafo dirigido ponderado donde:
  - Cada nodo representa un punto de la cadena (pesca, acopio, venta…).
  - Cada arista tiene peso multicriterio (tiempo, costo, riesgo, pérdida).
  - Soporta consultas por tipo de nodo y exportación a NetworkX.
"""

from __future__ import annotations
from typing import Dict, List, Optional, Set, Tuple, Any
from collections import defaultdict

from .nodo import Nodo
from .arista import Arista
from ..utils.constants import TipoNodo
from ..utils.geo_utils import haversine, calcular_tiempo_viaje


class GrafoLogistico:
    """
    Grafo dirigido ponderado para modelar la cadena de suministro
    pesquera de Puerto Gaitán.

    Internamente usa lista de adyacencia:
        _adyacencia[origen_id] = [(destino_id, Arista), ...]
    """

    def __init__(self):
        self._nodos: Dict[str, Nodo] = {}
        self._adyacencia: Dict[str, List[Tuple[str, Arista]]] = defaultdict(list)
        self._num_aristas: int = 0

    # ═══════════════════════════════════════════════════════════
    #  NODOS
    # ═══════════════════════════════════════════════════════════

    def agregar_nodo(self, nodo: Nodo) -> None:
        """Agrega un nodo al grafo. Si ya existe, lo reemplaza."""
        self._nodos[nodo.id] = nodo
        if nodo.id not in self._adyacencia:
            self._adyacencia[nodo.id] = []

    def obtener_nodo(self, id_nodo: str) -> Optional[Nodo]:
        """Devuelve el nodo con el ID dado, o None."""
        return self._nodos.get(id_nodo)

    def eliminar_nodo(self, id_nodo: str) -> bool:
        """Elimina un nodo y todas sus aristas asociadas."""
        if id_nodo not in self._nodos:
            return False
        # Eliminar aristas salientes
        self._num_aristas -= len(self._adyacencia[id_nodo])
        del self._adyacencia[id_nodo]
        # Eliminar aristas entrantes
        for origen in list(self._adyacencia.keys()):
            antes = len(self._adyacencia[origen])
            self._adyacencia[origen] = [
                (dest, ar) for dest, ar in self._adyacencia[origen]
                if dest != id_nodo
            ]
            self._num_aristas -= (antes - len(self._adyacencia[origen]))
        del self._nodos[id_nodo]
        return True

    @property
    def nodos(self) -> List[Nodo]:
        """Lista de todos los nodos."""
        return list(self._nodos.values())

    @property
    def num_nodos(self) -> int:
        return len(self._nodos)

    def nodos_por_tipo(self, tipo: str) -> List[Nodo]:
        """Filtra nodos por código de tipo (P, A, D, H, M, F, V)."""
        return [n for n in self._nodos.values() if n.tipo == tipo]

    # ═══════════════════════════════════════════════════════════
    #  ARISTAS
    # ═══════════════════════════════════════════════════════════

    def agregar_arista(self, arista: Arista) -> None:
        """Agrega una arista dirigida al grafo."""
        if arista.origen not in self._nodos:
            raise KeyError(f"Nodo origen '{arista.origen}' no existe.")
        if arista.destino not in self._nodos:
            raise KeyError(f"Nodo destino '{arista.destino}' no existe.")
        self._adyacencia[arista.origen].append((arista.destino, arista))
        self._num_aristas += 1

    def agregar_arista_auto(self, id_origen: str, id_destino: str,
                            estado_via: str = "buena",
                            tipo_via: str = "terrestre",
                            **kwargs) -> Arista:
        """
        Crea y agrega una arista calculando automáticamente la distancia
        (Haversine) y el tiempo de viaje a partir de las coordenadas.
        """
        n_o = self._nodos.get(id_origen)
        n_d = self._nodos.get(id_destino)
        if not n_o or not n_d:
            raise KeyError(f"Nodo '{id_origen}' o '{id_destino}' no existe.")

        dist = haversine(n_o.coordenadas, n_d.coordenadas)
        factor = {"buena": 1.0, "regular": 1.5, "mala": 2.0}.get(estado_via, 1.0)
        tiempo = calcular_tiempo_viaje(dist, factor_estado_via=factor)

        arista = Arista(
            origen=id_origen,
            destino=id_destino,
            distancia_km=round(dist, 2),
            tiempo_h=round(tiempo, 3),
            estado_via=estado_via,
            tipo_via=tipo_via,
            **kwargs,
        )
        self.agregar_arista(arista)
        return arista

    def obtener_aristas(self, id_origen: str) -> List[Arista]:
        """Devuelve todas las aristas que salen de un nodo."""
        return [ar for _, ar in self._adyacencia.get(id_origen, [])]

    def obtener_arista(self, id_origen: str,
                       id_destino: str) -> Optional[Arista]:
        """Devuelve la arista entre dos nodos, o None."""
        for dest, ar in self._adyacencia.get(id_origen, []):
            if dest == id_destino:
                return ar
        return None

    @property
    def aristas(self) -> List[Arista]:
        """Lista de todas las aristas del grafo."""
        resultado = []
        for vecinos in self._adyacencia.values():
            for _, ar in vecinos:
                resultado.append(ar)
        return resultado

    @property
    def num_aristas(self) -> int:
        return self._num_aristas

    def vecinos(self, id_nodo: str) -> List[str]:
        """IDs de los nodos adyacentes (sucesores)."""
        return [dest for dest, _ in self._adyacencia.get(id_nodo, [])]

    # ═══════════════════════════════════════════════════════════
    #  CONSULTAS DE ALTO NIVEL
    # ═══════════════════════════════════════════════════════════

    def puntos_pesca(self) -> List[Nodo]:
        return self.nodos_por_tipo(TipoNodo.PESCA)

    def centros_frio(self) -> List[Nodo]:
        return self.nodos_por_tipo(TipoNodo.FRIO)

    def centros_acopio(self) -> List[Nodo]:
        return self.nodos_por_tipo(TipoNodo.ACOPIO)

    def mercados(self) -> List[Nodo]:
        return self.nodos_por_tipo(TipoNodo.VENTA)

    def candidatos_frio(self) -> List[Nodo]:
        """Nodos que podrían albergar un centro de frío."""
        return [n for n in self._nodos.values() if n.es_candidato_frio]

    def produccion_total_kg(self) -> float:
        """Suma de producción diaria de todos los puntos de pesca."""
        return sum(n.produccion_kg_dia for n in self.puntos_pesca())

    # ═══════════════════════════════════════════════════════════
    #  MATRIZ DE PESOS
    # ═══════════════════════════════════════════════════════════

    def matriz_adyacencia(self, criterio: str = "peso") -> Dict[str, Dict[str, float]]:
        """
        Construye la matriz de adyacencia como diccionario de diccionarios.

        Parameters
        ----------
        criterio : str
            'peso'          — peso multicriterio combinado
            'distancia_km'  — distancia en km
            'tiempo_h'      — tiempo en horas
            'costo_cop'     — costo en COP

        Returns
        -------
        dict[str, dict[str, float]]
        """
        INF = float("inf")
        ids = list(self._nodos.keys())
        matriz = {i: {j: INF for j in ids} for i in ids}
        for i in ids:
            matriz[i][i] = 0.0

        for vecinos in self._adyacencia.values():
            for dest, ar in vecinos:
                if criterio == "peso":
                    valor = ar.peso_default
                else:
                    valor = getattr(ar, criterio, ar.peso_default)
                if valor < matriz[ar.origen][dest]:
                    matriz[ar.origen][dest] = valor

        return matriz

    # ═══════════════════════════════════════════════════════════
    #  EXPORTACIÓN A NETWORKX
    # ═══════════════════════════════════════════════════════════

    def to_networkx(self):
        """
        Convierte el grafo a un objeto networkx.DiGraph.
        Requiere networkx instalado.
        """
        import networkx as nx

        G = nx.DiGraph()

        for nodo in self._nodos.values():
            G.add_node(nodo.id, **nodo.to_dict())

        for vecinos in self._adyacencia.values():
            for dest, ar in vecinos:
                G.add_edge(ar.origen, dest, **ar.to_dict())

        return G

    # ═══════════════════════════════════════════════════════════
    #  REPRESENTACIÓN
    # ═══════════════════════════════════════════════════════════

    def resumen(self) -> str:
        """Resumen textual del grafo."""
        lineas = [
            "═" * 60,
            "  GRAFO LOGÍSTICO — CADENA PESQUERA PUERTO GAITÁN",
            "═" * 60,
            f"  Nodos totales:        {self.num_nodos}",
            f"  Aristas totales:      {self.num_aristas}",
            f"  Puntos de pesca:      {len(self.puntos_pesca())}",
            f"  Centros de acopio:    {len(self.centros_acopio())}",
            f"  Centros de frío:      {len(self.centros_frio())}",
            f"  Mercados (venta):     {len(self.mercados())}",
            f"  Producción total:     {self.produccion_total_kg():.0f} kg/día",
            "═" * 60,
        ]
        return "\n".join(lineas)

    def __repr__(self) -> str:
        return f"GrafoLogistico(nodos={self.num_nodos}, aristas={self.num_aristas})"

    def __contains__(self, id_nodo: str) -> bool:
        return id_nodo in self._nodos

    def __len__(self) -> int:
        return self.num_nodos

