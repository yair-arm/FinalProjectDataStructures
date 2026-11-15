"""
graph_plotter.py — Visualización de grafos con matplotlib.

Dibuja el grafo logístico usando posiciones geográficas (lat, lon),
colorea los nodos por tipo y destaca rutas óptimas.
"""

from __future__ import annotations
from typing import List, Optional, Dict
import matplotlib
matplotlib.use("Agg")  # Backend no interactivo por defecto
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

from ..models.grafo_logistico import GrafoLogistico
from ..utils.constants import TipoNodo


# Colores por tipo de nodo
COLORES_NODO = {
    TipoNodo.PESCA:    "#2196F3",  # Azul
    TipoNodo.ACOPIO:   "#FF9800",  # Naranja
    TipoNodo.DETERIORO:"#F44336",  # Rojo
    TipoNodo.HABITAT:  "#4CAF50",  # Verde
    TipoNodo.MUELLE:   "#9C27B0",  # Púrpura
    TipoNodo.FRIO:     "#00BCD4",  # Cyan
    TipoNodo.VENTA:    "#E91E63",  # Rosa
}

SIMBOLOS_NODO = {
    TipoNodo.PESCA:    "o",
    TipoNodo.ACOPIO:   "s",
    TipoNodo.FRIO:     "D",
    TipoNodo.MUELLE:   "^",
    TipoNodo.VENTA:    "*",
    TipoNodo.HABITAT:  "p",
    TipoNodo.DETERIORO:"X",
}


def graficar_grafo(
    grafo: GrafoLogistico,
    titulo: str = "Grafo Logístico — Cadena Pesquera Puerto Gaitán",
    ruta_destacada: Optional[List[str]] = None,
    guardar_como: Optional[str] = None,
    mostrar: bool = True,
    figsize: tuple = (14, 10),
) -> None:
    """
    Dibuja el grafo completo con posiciones geográficas.

    Parameters
    ----------
    grafo : GrafoLogistico
    titulo : str
    ruta_destacada : list[str] | None — IDs de nodos para resaltar ruta.
    guardar_como : str | None — ruta de archivo para guardar la imagen.
    mostrar : bool — si se muestra la ventana interactiva.
    figsize : tuple
    """
    fig, ax = plt.subplots(1, 1, figsize=figsize)

    # Posiciones: (longitud, latitud) para que el mapa se vea correcto
    posiciones: Dict[str, tuple] = {}
    for nodo in grafo.nodos:
        posiciones[nodo.id] = (nodo.longitud, nodo.latitud)

    # Dibujar aristas
    for arista in grafo.aristas:
        if arista.origen in posiciones and arista.destino in posiciones:
            x_o, y_o = posiciones[arista.origen]
            x_d, y_d = posiciones[arista.destino]

            # Verificar si la arista es parte de la ruta (consecutiva)
            es_ruta = False
            if ruta_destacada is not None:
                for idx in range(len(ruta_destacada) - 1):
                    if (ruta_destacada[idx] == arista.origen
                            and ruta_destacada[idx + 1] == arista.destino):
                        es_ruta = True
                        break

            ax.annotate(
                "",
                xy=(x_d, y_d),
                xytext=(x_o, y_o),
                arrowprops=dict(
                    arrowstyle="->",
                    color="red" if es_ruta else "#BDBDBD",
                    linewidth=2.5 if es_ruta else 0.8,
                    alpha=1.0 if es_ruta else 0.5,
                ),
            )

            # Etiqueta de distancia en la arista
            mx = (x_o + x_d) / 2
            my = (y_o + y_d) / 2
            ax.annotate(
                f"{arista.distancia_km:.0f}km",
                (mx, my),
                fontsize=5,
                color="#666666" if not es_ruta else "#CC0000",
                ha="center",
                alpha=0.7,
            )

    # Dibujar nodos por tipo
    for tipo_code in COLORES_NODO:
        nodos_tipo = grafo.nodos_por_tipo(tipo_code)
        if not nodos_tipo:
            continue

        xs = [posiciones[n.id][0] for n in nodos_tipo if n.id in posiciones]
        ys = [posiciones[n.id][1] for n in nodos_tipo if n.id in posiciones]

        ax.scatter(
            xs, ys,
            c=COLORES_NODO[tipo_code],
            marker=SIMBOLOS_NODO.get(tipo_code, "o"),
            s=120,
            zorder=5,
            edgecolors="white",
            linewidth=0.5,
            label=TipoNodo.descripcion(tipo_code),
        )

    # Etiquetas
    for nodo in grafo.nodos:
        if nodo.id in posiciones:
            x, y = posiciones[nodo.id]
            ax.annotate(
                nodo.nombre,
                (x, y),
                textcoords="offset points",
                xytext=(5, 5),
                fontsize=7,
                ha="left",
            )

    ax.set_title(titulo, fontsize=14, fontweight="bold")
    ax.set_xlabel("Longitud")
    ax.set_ylabel("Latitud")

    # Subtítulo con estadísticas
    prod_total = sum(n.produccion_kg_dia for n in grafo.nodos if n.tipo == "P")
    subtitulo = (
        f"{grafo.num_nodos} nodos | {grafo.num_aristas} aristas | "
        f"{prod_total:.0f} kg/día producción total"
    )
    ax.text(
        0.5, 1.02, subtitulo,
        transform=ax.transAxes, fontsize=9,
        ha="center", color="#666666", style="italic",
    )

    ax.legend(loc="lower left", fontsize=8)
    ax.grid(True, alpha=0.3)
    plt.tight_layout()

    if guardar_como:
        fig.savefig(guardar_como, dpi=150, bbox_inches="tight")
        print(f"  [✓] Gráfico guardado en: {guardar_como}")

    if mostrar:
        plt.show()
    else:
        plt.close(fig)


def graficar_ruta(
    grafo: GrafoLogistico,
    ruta: List[str],
    titulo: str = "Ruta Óptima",
    guardar_como: Optional[str] = None,
) -> None:
    """Atajo para graficar el grafo con una ruta destacada."""
    graficar_grafo(
        grafo,
        titulo=titulo,
        ruta_destacada=ruta,
        guardar_como=guardar_como,
        mostrar=True,
    )

