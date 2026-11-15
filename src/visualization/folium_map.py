"""
folium_map.py — Mapa interactivo HTML con Folium.

Genera un mapa web interactivo que se abre en el navegador,
sin necesidad de cuentas externas ni servicios de pago.

Las rutas siguen las carreteras y ríos reales obtenidos
desde OSRM (Open Source Routing Machine) y el shapefile de ríos.

Capas generadas:
  1. Nodos de la red — marcadores categorizados por tipo y color.
  2. Ruta óptima — polilínea roja siguiendo carreteras reales.
  3. Todas las aristas — conexiones siguiendo vías reales.
  4. Ríos — capa GeoJSON de la red fluvial.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import List, Optional, Dict

import folium
from folium import plugins

from ..models.grafo_logistico import GrafoLogistico
from ..utils.data_loader import OUTPUT_DIR, SHP_DIR
from ..utils.constants import TipoNodo

# Ruta al GeoJSON de puntos de campo
_GEOJSON_DIR = Path(__file__).resolve().parent.parent.parent / "data" / "geojson"


# ═══════════════════════════════════════════════════════════════════
#  CONFIGURACIÓN DE COLORES Y ICONOS POR TIPO DE NODO
# ═══════════════════════════════════════════════════════════════════

COLORES_FELT = {
    TipoNodo.PESCA:     "#2196F3",  # Azul
    TipoNodo.ACOPIO:    "#FF9800",  # Naranja
    TipoNodo.FRIO:      "#00BCD4",  # Cyan
    TipoNodo.MUELLE:    "#9C27B0",  # Púrpura
    TipoNodo.VENTA:     "#E91E63",  # Rosa
    TipoNodo.HABITAT:   "#4CAF50",  # Verde
    TipoNodo.DETERIORO: "#F44336",  # Rojo
}

ICONOS_FOLIUM = {
    TipoNodo.PESCA:     ("fish",      "blue"),
    TipoNodo.ACOPIO:    ("warehouse", "orange"),
    TipoNodo.FRIO:      ("snowflake", "cadetblue"),
    TipoNodo.MUELLE:    ("anchor",    "purple"),
    TipoNodo.VENTA:     ("shop",      "pink"),
    TipoNodo.HABITAT:   ("leaf",      "green"),
    TipoNodo.DETERIORO: ("warning",   "red"),
}


# ═══════════════════════════════════════════════════════════════════
#  GENERADOR DE MAPA INTERACTIVO
# ═══════════════════════════════════════════════════════════════════

def generar_mapa_interactivo(
    grafo: GrafoLogistico,
    ruta_optima: Optional[List[str]] = None,
    nombre_ruta: str = "Ruta Óptima Dijkstra",
    nombre_archivo: str = "mapa_interactivo.html",
    abrir_navegador: bool = False,
    geometrias_reales: Optional[Dict[str, list]] = None,
    itinerarios: Optional[list] = None,
) -> str:
    """
    Genera un mapa HTML interactivo con Folium.

    Parameters
    ----------
    grafo : GrafoLogistico
    ruta_optima : list[str] | None — IDs de nodos de la ruta óptima.
    nombre_ruta : str — nombre descriptivo para la ruta.
    nombre_archivo : str — nombre del archivo HTML de salida.
    abrir_navegador : bool — si abrir automáticamente en el navegador.
    geometrias_reales : dict | None — caché de geometrías reales
        {"{origen}-{destino}": [[lon, lat], ...]}

    Returns
    -------
    str : ruta absoluta del archivo HTML generado.
    """
    geo_cache = geometrias_reales or {}

    # ── Calcular centro del mapa ─────────────────────────────
    lats = [n.latitud for n in grafo.nodos if n.latitud != 0]
    lons = [n.longitud for n in grafo.nodos if n.longitud != 0]

    if not lats or not lons:
        centro = [4.31, -72.08]  # Puerto Gaitán por defecto
    else:
        centro = [sum(lats) / len(lats), sum(lons) / len(lons)]

    # ── Crear mapa base ──────────────────────────────────────
    mapa = folium.Map(
        location=centro,
        zoom_start=9,
        tiles="CartoDB positron",
        control_scale=True,
    )

    # Agregar capas base adicionales
    folium.TileLayer("OpenStreetMap", name="OpenStreetMap").add_to(mapa)
    folium.TileLayer(
        "https://server.arcgisonline.com/ArcGIS/rest/services/"
        "World_Imagery/MapServer/tile/{z}/{y}/{x}",
        attr="Esri",
        name="Satélite (Esri)",
    ).add_to(mapa)

    itinerarios = list(itinerarios or [])

    # ── Capa de ríos reales (siempre visible) ────────────────
    _agregar_capa_rios(mapa)

    # ── Capa de puntos de campo (GeoJSON externo) ─────────
    _agregar_puntos_campo(mapa)

    # ── Capa de aristas (todas las conexiones) ───────────────
    capa_aristas = folium.FeatureGroup(name="🔗 Conexiones del Grafo", show=True)
    colores_tipo_estado = {
        ("terrestre", "buena"): ("#2E7D32", 3.5, None),
        ("terrestre", "regular"): ("#EF6C00", 3.0, None),
        ("terrestre", "mala"): ("#C62828", 2.5, "6 4"),
        ("acceso_local", "buena"): ("#546E7A", 2.5, None),
        ("acceso_local", "regular"): ("#78909C", 2.2, "4 4"),
        ("acceso_local", "mala"): ("#8D6E63", 2.0, "3 5"),
        ("fluvial", "buena"): ("#1565C0", 3.0, "8 6"),
        ("fluvial", "regular"): ("#42A5F5", 2.5, "8 6"),
        ("fluvial", "mala"): ("#0D47A1", 2.2, "4 6"),
    }
    for arista in grafo.aristas:
        n_o = grafo.obtener_nodo(arista.origen)
        n_d = grafo.obtener_nodo(arista.destino)
        if not n_o or not n_d:
            continue

        color_via, peso_via, dash_via = colores_tipo_estado.get(
            (arista.tipo_via, arista.estado_via),
            ("#616161", 2.5, None),
        )

        popup_html = (
            f"<b>{n_o.nombre} ({arista.origen}) → {n_d.nombre} ({arista.destino})</b><br>"
            f"🛣️ <b>tipo_via:</b> {arista.tipo_via} | <b>estado_via:</b> {arista.estado_via}<br>"
            f"📏 <b>distancia_km:</b> {arista.distancia_km:.2f} km<br>"
            f"⏱️ <b>tiempo_h:</b> {arista.tiempo_h:.2f} h | "
            f"<b>tiempo_espera_h:</b> {arista.tiempo_espera_h:.2f} h | "
            f"<b>tiempo_efectivo_h:</b> {arista.tiempo_efectivo_h:.2f} h<br>"
            f"💰 <b>costo_cop:</b> ${arista.costo_cop:,.0f} | "
            f"<b>peajes:</b> {arista.peajes} (${arista.costo_peajes_cop:,.0f}) | "
            f"<b>costo_total_cop:</b> ${arista.costo_total_cop:,.0f}<br>"
            f"🚗 <b>flujo_vehicular:</b> {arista.flujo_vehicular} | "
            f"<b>confiabilidad_via:</b> {arista.confiabilidad_via:.2f} | "
            f"<b>prob_retraso:</b> {arista.prob_retraso:.2f}<br>"
            f"🌡️ <b>riesgo_termico:</b> {arista.riesgo_termico:.2f} | "
            f"<b>riesgo_accidente:</b> {arista.riesgo_accidente:.2f} | "
            f"<b>riesgo_derrumbe:</b> {arista.riesgo_derrumbe:.2f} | "
            f"<b>riesgo_combinado:</b> {arista.riesgo_combinado:.3f}<br>"
            f"⚖️ <b>capacidad_kg:</b> {arista.capacidad_kg:,.0f} kg | "
            f"<b>restriccion_peso_ton:</b> {arista.restriccion_peso_ton} t | "
            f"<b>horario_restriccion:</b> {arista.horario_restriccion}<br>"
            f"📉 <b>perdida_esperada:</b> {arista.perdida_esperada:.2f}% | "
            f"⚖️ <b>peso_default:</b> {arista.peso_default:.4f}"
        )

        # Usar geometría real si disponible, si no línea recta
        clave = f"{arista.origen}-{arista.destino}"
        geo_coords = geo_cache.get(clave)
        if geo_coords and len(geo_coords) > 1:
            # geo_coords es [[lon, lat], ...] → convertir a [[lat, lon], ...]
            locations = [[c[1], c[0]] for c in geo_coords]
        else:
            locations = [[n_o.latitud, n_o.longitud],
                         [n_d.latitud, n_d.longitud]]

        folium.PolyLine(
            locations=locations,
            color=color_via,
            weight=peso_via,
            opacity=0.75,
            dash_array=dash_via,
            popup=folium.Popup(popup_html, max_width=360),
            tooltip=(
                f"{arista.origen}→{arista.destino} ({arista.tipo_via}/{arista.estado_via}): "
                f"{arista.distancia_km} km | {arista.tiempo_efectivo_h:.2f}h | w={arista.peso_default:.3f}"
            ),
        ).add_to(capa_aristas)

    capa_aristas.add_to(mapa)

    # ── Capa de ruta óptima ──────────────────────────────────
    if ruta_optima and len(ruta_optima) >= 2:
        capa_ruta = folium.FeatureGroup(name=f"🛤️ {nombre_ruta}")
        dist_total = 0.0
        tiempo_total = 0.0

        # Construir coordenadas de la ruta usando geometrías reales
        coordenadas_ruta = []
        for i in range(len(ruta_optima) - 1):
            clave = f"{ruta_optima[i]}-{ruta_optima[i + 1]}"
            ar = grafo.obtener_arista(ruta_optima[i], ruta_optima[i + 1])
            if ar:
                dist_total += ar.distancia_km
                tiempo_total += ar.tiempo_h

            geo_seg = geo_cache.get(clave)
            if geo_seg and len(geo_seg) > 1:
                segmento = [[c[1], c[0]] for c in geo_seg]
            else:
                n_o = grafo.obtener_nodo(ruta_optima[i])
                n_d = grafo.obtener_nodo(ruta_optima[i + 1])
                segmento = []
                if n_o:
                    segmento.append([n_o.latitud, n_o.longitud])
                if n_d:
                    segmento.append([n_d.latitud, n_d.longitud])

            # Evitar duplicar punto de conexión
            if coordenadas_ruta and segmento:
                coordenadas_ruta.extend(segmento[1:])
            else:
                coordenadas_ruta.extend(segmento)

        # Línea principal de la ruta
        folium.PolyLine(
            locations=coordenadas_ruta,
            color="#D32F2F",
            weight=5,
            opacity=0.9,
            popup=folium.Popup(
                f"<b>{nombre_ruta}</b><br>"
                f"📏 {dist_total:.1f} km<br>"
                f"⏱️ {tiempo_total:.2f} horas<br>"
                f"📍 {' → '.join(ruta_optima)}",
                max_width=300,
            ),
            tooltip=f"{nombre_ruta}: {dist_total:.1f} km",
            dash_array="",
        ).add_to(capa_ruta)

        # Decorador con flechas de dirección
        try:
            plugins.AntPath(
                locations=coordenadas_ruta,
                color="#D32F2F",
                weight=3,
                opacity=0.6,
                delay=1000,
            ).add_to(capa_ruta)
        except Exception:
            pass  # AntPath es decorativo, no crítico

        capa_ruta.add_to(mapa)

    # ── Capa de nodos (marcadores) ───────────────────────────
    acopio_info = _resumen_acopios(itinerarios)
    for tipo_code in [TipoNodo.PESCA, TipoNodo.ACOPIO, TipoNodo.FRIO,
                      TipoNodo.VENTA]:
        nodos_tipo = grafo.nodos_por_tipo(tipo_code)
        if not nodos_tipo:
            continue

        desc = TipoNodo.descripcion(tipo_code)
        icono_nombre, icono_color = ICONOS_FOLIUM.get(
            tipo_code, ("circle", "gray")
        )
        capa = folium.FeatureGroup(
            name=f"{'🐟' if tipo_code == 'P' else '❄️' if tipo_code == 'F' else '📦' if tipo_code == 'A' else '🏪' if tipo_code == 'V' else '⚓'} {desc}"
        )

        for nodo in nodos_tipo:
            # Construir popup HTML rico
            popup_lines = [f"<b>{nodo.nombre}</b><br>"]
            popup_lines.append(f"<i>{desc}</i> ({nodo.id})<br>")

            if nodo.tipo == TipoNodo.PESCA:
                popup_lines.append(
                    f"🐟 Producción: {nodo.produccion_kg_dia} kg/día<br>"
                )
                if nodo.metadata.get("rio"):
                    popup_lines.append(
                        f"🌊 Río: {nodo.metadata['rio']}<br>"
                    )
                if nodo.metadata.get("pescadores"):
                    popup_lines.append(
                        f"👥 Pescadores: {nodo.metadata['pescadores']}<br>"
                    )
            elif nodo.tipo in (TipoNodo.FRIO, TipoNodo.ACOPIO):
                popup_lines.append(
                    f"❄️ Capacidad: {nodo.capacidad_frio_kg:,.0f} kg<br>"
                )
                popup_lines.append(
                    f"💰 Costo fijo: ${nodo.costo_fijo:,.0f}/mes<br>"
                )
                popup_lines.append(
                    f"⚡ Energía: {'Sí' if nodo.tiene_energia else 'No'}<br>"
                )
            elif nodo.tipo == TipoNodo.VENTA:
                demanda = nodo.metadata.get("demanda_kg_dia", 0)
                if demanda:
                    popup_lines.append(
                        f"📊 Demanda: {demanda} kg/día<br>"
                    )

            if nodo.tipo == TipoNodo.ACOPIO:
                info = acopio_info.get(nodo.id)
                if info:
                    pts = ", ".join(sorted(info["origenes"]))
                    popup_lines.append(
                        f"📥 <b>Recibe de:</b> {pts}<br>"
                        f"⚖️ <b>Flujo total:</b> {info['kg']:,.1f} kg/día<br>"
                    )
                else:
                    popup_lines.append("📥 Sin flujo asignado en los itinerarios<br>")

            popup_lines.append(
                f"📍 {nodo.latitud:.4f}, {nodo.longitud:.4f}"
            )

            # Determinar tamaño del marcador
            if nodo.tipo == TipoNodo.PESCA:
                radio = max(6, min(nodo.produccion_kg_dia / 5, 15))
            elif nodo.tipo in (TipoNodo.FRIO, TipoNodo.ACOPIO):
                radio = max(8, min(nodo.capacidad_frio_kg / 400, 18))
            else:
                radio = 10

            # Marcador circular con color del tipo
            folium.CircleMarker(
                location=[nodo.latitud, nodo.longitud],
                radius=radio,
                color=COLORES_FELT.get(tipo_code, "#757575"),
                fill=True,
                fill_color=COLORES_FELT.get(tipo_code, "#757575"),
                fill_opacity=0.8,
                popup=folium.Popup("".join(popup_lines), max_width=280),
                tooltip=f"{nodo.nombre} ({desc})",
            ).add_to(capa)

        capa.add_to(mapa)

    # ── Nodos M, D, H (capas propias con efecto) ─────────────
    _agregar_nodos_especiales(mapa, grafo, itinerarios)

    # ── Itinerarios por punto de pesca + flujo de acopio ─────
    if itinerarios:
        _agregar_itinerarios(mapa, grafo, itinerarios, geo_cache)

    # ── Leyenda y panel de itinerarios ───────────────────────
    _agregar_leyenda(mapa)
    if itinerarios:
        _agregar_panel_itinerarios(mapa, grafo, itinerarios)

    # ── Título ───────────────────────────────────────────────
    titulo_html = """
    <div style="position:fixed; top:10px; left:60px; z-index:1000;
         background:white; padding:10px 18px; border-radius:8px;
         box-shadow:0 2px 6px rgba(0,0,0,0.3); font-family:Arial;">
      <b>🐟 Cadena de Frío — Pesca Artesanal</b><br>
      <span style="font-size:12px; color:#666;">
        Puerto Gaitán, Meta, Colombia
      </span>
    </div>
    """
    mapa.get_root().html.add_child(folium.Element(titulo_html))

    # ── Control de capas ─────────────────────────────────────
    folium.LayerControl(collapsed=False).add_to(mapa)

    # ── Guardar ──────────────────────────────────────────────
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    ruta_archivo = OUTPUT_DIR / nombre_archivo
    mapa.save(str(ruta_archivo))

    print(f"  [✓] Mapa interactivo generado: {ruta_archivo}")

    if abrir_navegador:
        import webbrowser
        webbrowser.open(str(ruta_archivo))

    return str(ruta_archivo)


# ═══════════════════════════════════════════════════════════════════
#  FUNCIONES AUXILIARES
# ═══════════════════════════════════════════════════════════════════

# Estilo por tipo de vía: (color, grosor, dash_array)
_ESTILO_VIA = {
    "fluvial":      ("#1565C0", 5, "10 8"),
    "acceso_local": ("#757575", 4, None),
    "terrestre":    ("#E65100", 4, None),
}
_NOMBRE_VIA = {
    "fluvial": "Fluvial",
    "acceso_local": "Acceso local",
    "terrestre": "Terrestre",
}


def _agregar_capa_rios(mapa: folium.Map) -> None:
    """Agrega la capa de ríos reales (siempre visible) con tooltip del nombre."""
    datos = None
    try:
        from .river_network import obtener_capa_rios_geojson
        datos = obtener_capa_rios_geojson()
    except Exception as exc:  # módulo ausente o error de lectura
        print(f"  [!] Capa de ríos no disponible: {exc}")
    if not datos or not datos.get("features"):
        return

    for idx, feat in enumerate(datos.get("features", []), start=1):
        props = feat.setdefault("properties", {})
        if not props.get("nombre"):
            props["nombre"] = f"Tramo fluvial #{idx} (Red Hidrográfica Meta)"

    capa = folium.FeatureGroup(name="🌊 Red Fluvial (ríos reales)", show=True)
    folium.GeoJson(
        datos,
        style_function=lambda _f: {
            "color": "#1E88E5", "weight": 2.5, "opacity": 0.85,
        },
        tooltip=folium.GeoJsonTooltip(
            fields=["nombre"], aliases=["Río:"], labels=True, sticky=True,
        ),
    ).add_to(capa)
    capa.add_to(mapa)


def _tiene_propiedad(datos: dict, clave: str) -> bool:
    """Indica si todas las features del GeoJSON tienen la propiedad dada."""
    feats = datos.get("features", [])
    return bool(feats) and all(
        clave in (f.get("properties") or {}) for f in feats
    )


def _locs_tramo(grafo: GrafoLogistico, geo_cache: dict, o: str, d: str) -> list:
    """Coordenadas [[lat, lon], ...] de un tramo (geometría real o recta)."""
    geo = geo_cache.get(f"{o}-{d}")
    if geo and len(geo) > 1:
        return [[c[1], c[0]] for c in geo]
    n_o, n_d = grafo.obtener_nodo(o), grafo.obtener_nodo(d)
    if n_o and n_d:
        return [[n_o.latitud, n_o.longitud], [n_d.latitud, n_d.longitud]]
    return []


def _paradas(it) -> list:
    """Lista ordenada de IDs de parada de un itinerario."""
    paradas = [it.origen_id]
    for t in it.tramos:
        paradas.append(t.destino)
    return paradas


def _resumen_acopios(itinerarios: list) -> Dict[str, dict]:
    """Por acopio: puntos de pesca que recibe y kg/día totales."""
    res: Dict[str, dict] = {}
    for it in itinerarios:
        if not getattr(it, "acopio_id", None):
            continue
        r = res.setdefault(it.acopio_id, {"origenes": set(), "kg": 0.0})
        r["origenes"].add(it.origen_id)
        r["kg"] += float(getattr(it, "kg_inicial", 0.0) or 0.0)
    return res


def _tramo_popup(grafo: GrafoLogistico, t) -> str:
    """HTML del popup de un tramo."""
    n_o, n_d = grafo.obtener_nodo(t.origen), grafo.obtener_nodo(t.destino)
    no = n_o.nombre if n_o else t.origen
    nd = n_d.nombre if n_d else t.destino
    efecto = getattr(t, "efecto", "") or "—"
    return (
        f"<b>{no} → {nd}</b><br>"
        f"🛣️ Vía: {_NOMBRE_VIA.get(t.tipo_via, t.tipo_via)}<br>"
        f"📏 {t.distancia_km:.1f} km<br>⏱️ {t.tiempo_h:.2f} h<br>"
        f"✨ Efecto: {efecto}"
    )


def _icono_numerado(num: int, color: str) -> folium.DivIcon:
    """Marca circular numerada para una parada."""
    html = (
        f'<div style="background:{color};color:white;border:2px solid white;'
        f'border-radius:50%;width:22px;height:22px;line-height:18px;'
        f'text-align:center;font:bold 12px Arial;'
        f'box-shadow:0 0 3px rgba(0,0,0,.6);">{num}</div>'
    )
    return folium.DivIcon(html=html, icon_size=(22, 22), icon_anchor=(11, 11))


def _agregar_itinerarios(mapa, grafo, itinerarios, geo_cache) -> None:
    """Una capa por itinerario + capa resumen 'Flujo de acopio'."""
    flujo = folium.FeatureGroup(name="📦 Flujo de acopio (P→A / P→M→A)", show=False)

    for i, it in enumerate(itinerarios):
        capa = folium.FeatureGroup(
            name=(f"🐟 Recorrido {it.origen_id} → Acopio → Frío → Destino"
                  f" ({it.acopio_id or '—'} / {it.centro_frio_id or '—'}"
                  f" / {it.destino_id or '—'})"),
            show=(i == 0),
        )
        llegado_a_acopio = False
        for t in it.tramos:
            locs = _locs_tramo(grafo, geo_cache, t.origen, t.destino)
            if len(locs) < 2:
                continue
            color, peso, dash = _ESTILO_VIA.get(t.tipo_via, ("#E65100", 4, None))
            folium.PolyLine(
                locs, color=color, weight=peso, opacity=0.9, dash_array=dash,
                popup=folium.Popup(_tramo_popup(grafo, t), max_width=300),
                tooltip=f"{t.origen}→{t.destino}: {t.distancia_km:.1f} km",
            ).add_to(capa)
            if not llegado_a_acopio:  # tramos hasta alcanzar el acopio
                folium.PolyLine(
                    locs, color=color, weight=peso + 1, opacity=0.65,
                    dash_array=dash,
                    tooltip=f"{it.origen_id} → {it.acopio_id}: aporta "
                            f"{getattr(it, 'kg_inicial', 0):.0f} kg/día",
                ).add_to(flujo)
                n_d = grafo.obtener_nodo(t.destino)
                if n_d and n_d.tipo == TipoNodo.ACOPIO:
                    llegado_a_acopio = True

        for k, nid in enumerate(_paradas(it), start=1):
            n = grafo.obtener_nodo(nid)
            if not n:
                continue
            color = COLORES_FELT.get(n.tipo, "#757575")
            folium.Marker(
                [n.latitud, n.longitud],
                icon=_icono_numerado(k, color),
                tooltip=f"Parada {k}: {n.nombre} ({n.id})",
            ).add_to(capa)
        capa.add_to(mapa)

    flujo.add_to(mapa)


def _agregar_nodos_especiales(mapa, grafo, itinerarios) -> None:
    """Capas de muelles (M), zonas de deterioro (D) y hábitats (H)."""
    evitados: Dict[str, list] = {}
    for it in itinerarios:
        for h in (getattr(it, "nodos_restringidos_evitados", None) or []):
            evitados.setdefault(h, []).append(it.origen_id)

    config = [
        (TipoNodo.MUELLE, "⚓ Muelles (transbordo fluvial→terrestre)", "anchor", "purple"),
        (TipoNodo.DETERIORO, "⚠️ Zonas de deterioro (×1.5)", "exclamation-triangle", "orange"),
        (TipoNodo.HABITAT, "🌿 Hábitats protegidos (restringidos)", "leaf", "green"),
    ]
    for tipo, titulo, icono, color in config:
        nodos = grafo.nodos_por_tipo(tipo)
        if not nodos:
            continue
        capa = folium.FeatureGroup(name=titulo, show=True)
        for n in nodos:
            if tipo == TipoNodo.MUELLE:
                efecto = ("Transbordo fluvial → terrestre: añade tiempo de "
                          "espera y la carga pierde frío durante el cambio.")
            elif tipo == TipoNodo.DETERIORO:
                efecto = ("Zona de deterioro: el tramo entrante multiplica "
                          "el deterioro del pescado ×1.5 (calor, sin frío).")
            else:
                ev = sorted(set(evitados.get(n.id, [])))
                efecto = ("Hábitat protegido: tránsito restringido, las rutas "
                          "lo evitan como nodo intermedio.<br>"
                          + ("🚫 Evitado por itinerarios de: " + ", ".join(ev)
                             if ev else "🚫 Ningún itinerario necesitó desviarse."))
            popup = f"<b>{n.nombre}</b> ({n.id})<br>{efecto}"
            if tipo == TipoNodo.DETERIORO:
                folium.Circle(
                    [n.latitud, n.longitud], radius=1500, color="#FB8C00",
                    weight=1, fill=True, fill_color="#FB8C00", fill_opacity=0.25,
                    tooltip="Zona de deterioro: deterioro ×1.5",
                ).add_to(capa)
            elif tipo == TipoNodo.HABITAT:
                folium.Circle(
                    [n.latitud, n.longitud], radius=2000, color="#D32F2F",
                    weight=2, dash_array="6 6", fill=True,
                    fill_color="#43A047", fill_opacity=0.25,
                    tooltip="Hábitat protegido — tránsito restringido; rutas lo evitan",
                ).add_to(capa)
            folium.Marker(
                [n.latitud, n.longitud],
                icon=folium.Icon(color=color, icon=icono, prefix="fa"),
                popup=folium.Popup(popup, max_width=300),
                tooltip=f"{n.nombre} ({TipoNodo.descripcion(tipo)})",
            ).add_to(capa)
        capa.add_to(mapa)


def _agregar_leyenda(mapa: folium.Map) -> None:
    """Leyenda: tipos de nodo, tipos de vía y círculos D/H."""
    nodos = [
        ("#2196F3", "Punto de Pesca (P)"), ("#FF9800", "Centro de Acopio (A)"),
        ("#00BCD4", "Centro de Frío (F)"), ("#E91E63", "Venta (V)"),
        ("#9C27B0", "Muelle (M) ⚓"), ("#F57C00", "Deterioro (D) ⚠"),
        ("#4CAF50", "Hábitat protegido (H) 🌿"),
    ]
    vias = [
        ("#1565C0", "Fluvial (punteada)", "10 8"), ("#757575", "Acceso local", None),
        ("#E65100", "Terrestre", None), ("#1E88E5", "Río real", None),
    ]
    h = ('<div style="position:fixed; bottom:30px; right:10px; z-index:1000;'
         'background:white; padding:12px 16px; border-radius:8px;'
         'box-shadow:0 2px 6px rgba(0,0,0,0.3); font-family:Arial;'
         'font-size:12px; line-height:20px;"><b>Leyenda</b><br>')
    for c, l in nodos:
        h += (f'<span style="display:inline-block;width:12px;height:12px;'
              f'background:{c};border-radius:50%;margin-right:6px;'
              f'vertical-align:middle;"></span>{l}<br>')
    h += '<b>Vías</b><br>'
    for c, l, d in vias:
        borde = "dashed" if d else "solid"
        h += (f'<span style="display:inline-block;width:22px;height:0;'
              f'border-top:3px {borde} {c};margin-right:6px;'
              f'vertical-align:middle;"></span>{l}<br>')
    h += ('<b>Zonas</b><br>'
          '<span style="display:inline-block;width:12px;height:12px;'
          'background:rgba(251,140,0,.35);border:1px solid #FB8C00;'
          'border-radius:50%;margin-right:6px;vertical-align:middle;"></span>'
          'Deterioro ×1.5 (r=1.5 km)<br>'
          '<span style="display:inline-block;width:12px;height:12px;'
          'background:rgba(67,160,71,.35);border:2px dashed #D32F2F;'
          'border-radius:50%;margin-right:6px;vertical-align:middle;"></span>'
          'Hábitat restringido (r=2 km)<br></div>')
    mapa.get_root().html.add_child(folium.Element(h))


def _agregar_panel_itinerarios(mapa, grafo, itinerarios) -> None:
    """Panel lateral con la tabla resumen de itinerarios."""
    filas = ""
    for it in itinerarios:
        filas += (
            f"<tr><td>{it.origen_id}</td><td>{it.acopio_id or '—'}</td>"
            f"<td>{it.centro_frio_id or '—'}</td>"
            f"<td align='right'>{it.distancia_total_km:.1f}</td>"
            f"<td align='right'>{it.tiempo_total_h:.2f}</td>"
            f"<td align='right'>{it.perdida_pct:.1f}%</td></tr>"
        )
    h = (
        '<div style="position:fixed; top:80px; left:10px; z-index:1000;'
        'background:white; padding:8px 12px; border-radius:8px;'
        'box-shadow:0 2px 6px rgba(0,0,0,0.3); font-family:Arial;'
        'font-size:11px; max-height:60vh; overflow:auto;">'
        '<details open><summary><b>📋 Itinerarios por punto de pesca</b></summary>'
        '<table style="border-collapse:collapse;margin-top:4px;" cellpadding="3">'
        '<tr style="background:#eee;"><th>Origen</th><th>Acopio</th>'
        '<th>Centro</th><th>km</th><th>h</th><th>% pérdida</th></tr>'
        f'{filas}</table></details></div>'
    )
    mapa.get_root().html.add_child(folium.Element(h))


def _agregar_puntos_campo(mapa: folium.Map) -> None:
    """
    Carga los puntos de campo desde data/geojson/puntos_campo.geojson
    y los agrega como capas categorizadas al mapa.

    Categorías:
      A — Acopio (naranja)
      D — Deterioro (rojo)
      H — Hábitat (verde)
      M — Muelle (azul)
      V — Venta (púrpura)
    """
    geojson_path = _GEOJSON_DIR / "puntos_campo.geojson"
    if not geojson_path.exists():
        return

    try:
        with open(geojson_path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except (json.JSONDecodeError, IOError):
        return

    features = data.get("features", [])
    if not features:
        return

    # Configuración visual por categoría
    categorias_config = {
        "A": {"nombre": "📦 Puntos de Acopio (campo)",    "color": "#F39C12", "icono": "warehouse"},
        "D": {"nombre": "🌡️ Zonas de Deterioro (campo)", "color": "#E74C3C", "icono": "warning"},
        "H": {"nombre": "🌿 Hábitat Protegido (campo)",   "color": "#27AE60", "icono": "leaf"},
        "M": {"nombre": "⚓ Muelles (campo)",             "color": "#3498DB", "icono": "anchor"},
        "V": {"nombre": "🏪 Puntos de Venta (campo)",     "color": "#8E44AD", "icono": "shop"},
    }

    # Agrupar features por categoría
    grupos: Dict[str, list] = {}
    for feat in features:
        cat = feat.get("properties", {}).get("categoria", "?")
        grupos.setdefault(cat, []).append(feat)

    # Crear una capa por categoría
    for cat, feats in sorted(grupos.items()):
        config = categorias_config.get(cat, {
            "nombre": f"❓ {cat} (campo)",
            "color": "#757575",
            "icono": "circle",
        })

        capa = folium.FeatureGroup(name=config["nombre"], show=False)

        for feat in feats:
            props = feat.get("properties", {})
            coords = feat.get("geometry", {}).get("coordinates", [0, 0])
            lat, lon = coords[1], coords[0]  # GeoJSON es [lon, lat]

            # Popup HTML informativo
            popup_html = (
                f"<b>{props.get('title', props.get('id', ''))}</b><br>"
                f"<i>{props.get('tipo', cat)}</i><br>"
                f"📍 {props.get('lat_dms', f'{lat:.4f}')}, "
                f"{props.get('lon_dms', f'{lon:.4f}')}"
            )

            folium.CircleMarker(
                location=[lat, lon],
                radius=6,
                color=config["color"],
                fill=True,
                fill_color=config["color"],
                fill_opacity=0.7,
                weight=2,
                popup=folium.Popup(popup_html, max_width=250),
                tooltip=props.get("title", props.get("id", "")),
            ).add_to(capa)

        capa.add_to(mapa)

    print(f"  [✓] {len(features)} puntos de campo cargados "
          f"({', '.join(f'{k}:{len(v)}' for k, v in sorted(grupos.items()))})")

