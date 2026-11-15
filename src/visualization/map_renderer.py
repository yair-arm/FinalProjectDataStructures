"""
map_renderer.py — Renderizado de mapas geográficos.

Genera mapas con las rutas, nodos y ríos sobre un fondo
geográfico, usando matplotlib y opcionalmente geopandas.
"""

from __future__ import annotations
from typing import List, Optional

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from ..models.grafo_logistico import GrafoLogistico
from ..utils.constants import TipoNodo


def renderizar_mapa(
    grafo: GrafoLogistico,
    ruta: Optional[List[str]] = None,
    titulo: str = "Mapa — Red Logística Pesquera",
    mostrar_rios: bool = True,
    guardar_como: Optional[str] = None,
    mostrar: bool = True,
) -> None:
    """
    Renderiza un mapa geográfico con los nodos y rutas del grafo.

    Si geopandas está disponible y hay shapefiles de ríos, los
    dibuja como fondo. De lo contrario, solo muestra los nodos.
    """
    fig, ax = plt.subplots(1, 1, figsize=(16, 12))

    # ── Capa de ríos (si está disponible) ────────────────────
    if mostrar_rios:
        try:
            from ..utils.data_loader import cargar_shapefile_rios
            gdf_rios = cargar_shapefile_rios()
            gdf_rios.plot(ax=ax, color="#64B5F6", linewidth=0.5, alpha=0.6)
        except (ImportError, FileNotFoundError):
            pass  # Sin capa de ríos

    # ── Nodos ────────────────────────────────────────────────
    colores = {
        TipoNodo.PESCA:  "#2196F3",
        TipoNodo.ACOPIO: "#FF9800",
        TipoNodo.FRIO:   "#00BCD4",
        TipoNodo.MUELLE: "#9C27B0",
        TipoNodo.VENTA:  "#E91E63",
        TipoNodo.HABITAT:"#4CAF50",
    }

    for nodo in grafo.nodos:
        color = colores.get(nodo.tipo, "#757575")
        ax.plot(
            nodo.longitud, nodo.latitud,
            marker="o", markersize=8,
            color=color, markeredgecolor="white",
            zorder=5,
        )
        ax.annotate(
            nodo.nombre,
            (nodo.longitud, nodo.latitud),
            textcoords="offset points",
            xytext=(6, 6),
            fontsize=7,
        )

    # ── Ruta destacada ───────────────────────────────────────
    if ruta and len(ruta) >= 2:
        for i in range(len(ruta) - 1):
            n1 = grafo.obtener_nodo(ruta[i])
            n2 = grafo.obtener_nodo(ruta[i + 1])
            if n1 and n2:
                ax.plot(
                    [n1.longitud, n2.longitud],
                    [n1.latitud, n2.latitud],
                    color="red", linewidth=2, zorder=4,
                )

    ax.set_title(titulo, fontsize=14, fontweight="bold")
    ax.set_xlabel("Longitud")
    ax.set_ylabel("Latitud")
    ax.grid(True, alpha=0.3)
    plt.tight_layout()

    if guardar_como:
        fig.savefig(guardar_como, dpi=150, bbox_inches="tight")
        print(f"  [✓] Mapa guardado en: {guardar_como}")

    if mostrar:
        plt.show()
    else:
        plt.close(fig)

