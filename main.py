#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
╔═══════════════════════════════════════════════════════════════════╗
║  OPTIMIZACIÓN DE CENTROS DE REFRIGERACIÓN PARA PESCA ARTESANAL  ║
║  Puerto Gaitán, Meta — Cadena de Frío mediante Teoría de Grafos ║
║  Estructuras de Datos — Semestre 03 — 2026-II                   ║
╚═══════════════════════════════════════════════════════════════════╝

Punto de entrada principal del proyecto. Ejecuta el flujo completo:

  1. Carga de datos (nodos y aristas desde CSV).
  2. Construcción del grafo logístico dirigido.
  3. Algoritmos de caminos mínimos (Dijkstra, Floyd-Warshall).
  4. Localización óptima de centros de refrigeración (FLP greedy).
  5. Simulación de cadena de frío.
  6. Comparación de escenarios.
  7. Visualización del grafo y resultados.

Uso:
    python main.py
"""

import os
import sys
import webbrowser
import subprocess

# Evitar error de memoria de OpenBLAS con numpy/matplotlib en Python 3.14
os.environ["OPENBLAS_NUM_THREADS"] = "1"
os.environ["OMP_NUM_THREADS"] = "1"

# ── Asegurar que el paquete src sea importable ────────────────
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE_DIR)

from src.models.nodo import Nodo
from src.models.arista import Arista
from src.models.grafo_logistico import GrafoLogistico
from src.algorithms.dijkstra import dijkstra, dijkstra_completo
from src.algorithms.floyd_warshall import floyd_warshall, reconstruir_camino, matriz_a_tabla
from src.algorithms.bellman_ford import bellman_ford, reconstruir_camino_bf
from src.algorithms.bfs import bfs_camino, bfs_nodo_mas_cercano_por_tipo, bfs_recorrido
from src.algorithms.dfs import dfs_recorrido, dfs_todos_los_caminos, dfs_resumen_rutas
from src.optimization.facility_location import resolver_localizacion
from src.optimization.cold_chain import SimuladorCadenaFrio
from src.optimization.scenario_evaluator import EvaluadorEscenarios
from src.optimization.itinerarios import calcular_itinerarios, Itinerario
from src.utils.data_loader import cargar_nodos_csv, cargar_aristas_csv, guardar_resultados_csv
from src.utils.constants import TipoNodo, TIEMPO_MAX_SIN_FRIO_H
from src.visualization.felt_exporter import exportar_para_felt
from src.visualization.folium_map import generar_mapa_interactivo


# ═══════════════════════════════════════════════════════════════
#  PASO 1: CARGA DE DATOS
# ═══════════════════════════════════════════════════════════════

def cargar_datos() -> GrafoLogistico:
    """
    Construye el grafo logístico completo a partir de los CSV.
    """
    print("\n" + "═" * 60)
    print("  PASO 1: CARGA DE DATOS")
    print("═" * 60)

    grafo = GrafoLogistico()

    # ── Nodos de pesca ────────────────────────────────────────
    try:
        datos_pesca = cargar_nodos_csv("nodos_pesca.csv")
        for d in datos_pesca:
            nodo = Nodo(
                id=d["id"],
                nombre=d["nombre"],
                tipo=d["tipo"],
                latitud=d.get("latitud", 0.0),
                longitud=d.get("longitud", 0.0),
                produccion_kg_dia=d.get("produccion_kg_dia", 0.0),
                metadata={"rio": d.get("rio_asociado", ""),
                           "pescadores": d.get("num_pescadores", 0)},
            )
            grafo.agregar_nodo(nodo)
        print(f"  [✓] {len(datos_pesca)} puntos de pesca cargados")
    except FileNotFoundError:
        print("  [!] No se encontró nodos_pesca.csv — usando datos de ejemplo")
        _cargar_datos_ejemplo(grafo)
        return grafo

    # ── Nodos de centros / acopio / muelles / deterioro / hábitat ─
    try:
        datos_centros = cargar_nodos_csv("nodos_centros.csv")
        conteo_tipo = {}
        for d in datos_centros:
            nodo = Nodo(
                id=d["id"],
                nombre=d["nombre"],
                tipo=d["tipo"],
                latitud=d.get("latitud", 0.0),
                longitud=d.get("longitud", 0.0),
                capacidad_frio_kg=d.get("capacidad_frio_kg", 0.0),
                costo_fijo=d.get("costo_fijo", 0.0),
                tiene_energia=bool(d.get("tiene_energia", 1)),
                tiene_agua=bool(d.get("tiene_agua", 1)),
                tiene_muelle=bool(d.get("tiene_muelle", 0)),
                restriccion_ambiental=bool(d.get("restriccion_ambiental", 0)),
                metadata={"observacion": d.get("observacion", "")},
            )
            grafo.agregar_nodo(nodo)
            conteo_tipo[d["tipo"]] = conteo_tipo.get(d["tipo"], 0) + 1
        detalle = ", ".join(f"{v} tipo {k}" for k, v in sorted(conteo_tipo.items()))
        print(f"  [✓] {len(datos_centros)} nodos de infraestructura cargados ({detalle})")
    except FileNotFoundError:
        print("  [!] No se encontró nodos_centros.csv")

    # ── Nodos de destino / venta ──────────────────────────────
    try:
        datos_destinos = cargar_nodos_csv("nodos_destinos.csv")
        for d in datos_destinos:
            nodo = Nodo(
                id=d["id"],
                nombre=d["nombre"],
                tipo=d["tipo"],
                latitud=d.get("latitud", 0.0),
                longitud=d.get("longitud", 0.0),
                metadata={"demanda_kg_dia": d.get("demanda_kg_dia", 0)},
            )
            grafo.agregar_nodo(nodo)
        print(f"  [✓] {len(datos_destinos)} mercados cargados")
    except FileNotFoundError:
        print("  [!] No se encontró nodos_destinos.csv")

    # ── Aristas ───────────────────────────────────────────────
    try:
        datos_aristas = cargar_aristas_csv("aristas.csv")
        tipos_via = {}
        for d in datos_aristas:
            arista = Arista(
                origen=d["origen"],
                destino=d["destino"],
                distancia_km=d.get("distancia_km", 0.0),
                tiempo_h=d.get("tiempo_h", 0.0),
                costo_cop=d.get("costo_cop", 0.0),
                riesgo_termico=d.get("riesgo_termico", 0.0),
                estado_via=d.get("estado_via", "buena"),
                tipo_via=d.get("tipo_via", "terrestre"),
                capacidad_kg=d.get("capacidad_kg", 2000),
                prob_retraso=d.get("prob_retraso", 0.0),
                riesgo_accidente=d.get("riesgo_accidente", 0.0),
                riesgo_derrumbe=d.get("riesgo_derrumbe", 0.0),
                restriccion_peso_ton=d.get("restriccion_peso_ton", 0.0),
                peajes=int(d.get("peajes", 0)),
                costo_peajes_cop=d.get("costo_peajes_cop", 0.0),
                horario_restriccion=d.get("horario_restriccion", "ninguno"),
                flujo_vehicular=d.get("flujo_vehicular", "bajo"),
                tiempo_espera_h=d.get("tiempo_espera_h", 0.0),
                confiabilidad_via=d.get("confiabilidad_via", 0.90),
            )
            grafo.agregar_arista(arista)
            tv = d.get("tipo_via", "terrestre")
            tipos_via[tv] = tipos_via.get(tv, 0) + 1
        detalle_via = ", ".join(f"{v} {k}" for k, v in sorted(tipos_via.items()))
        print(f"  [✓] {len(datos_aristas)} conexiones cargadas ({detalle_via})")
    except FileNotFoundError:
        print("  [!] No se encontró aristas.csv")

    return grafo


def _cargar_datos_ejemplo(grafo: GrafoLogistico):
    """Carga datos de ejemplo si no existen los CSV."""
    grafo.agregar_nodo(Nodo("P01", "ASOPESGA", "P", 4.35, -72.12, produccion_kg_dia=65))
    grafo.agregar_nodo(Nodo("P02", "Atarraya Verde", "P", 4.33, -72.10, produccion_kg_dia=40))
    grafo.agregar_nodo(Nodo("F01", "Centro Frío 1", "F", 4.345, -72.115,
                            capacidad_frio_kg=2000, costo_fijo=5000000))
    grafo.agregar_nodo(Nodo("F02", "Centro Puerto Gaitán", "F", 4.312, -72.082,
                            capacidad_frio_kg=5000, costo_fijo=3000000))
    grafo.agregar_nodo(Nodo("V_BOG1", "Buceo y Pesca Bogotá", "V", 4.6615, -74.059))
    grafo.agregar_arista(Arista("P01", "F01", 5, 0.2, 17500, 0.1))
    grafo.agregar_arista(Arista("P02", "F01", 7, 0.3, 24500, 0.12))
    grafo.agregar_arista(Arista("P01", "F02", 15, 0.6, 52500, 0.3))
    grafo.agregar_arista(Arista("F01", "F02", 12, 0.45, 42000, 0.15))
    grafo.agregar_arista(Arista("F02", "V_BOG1", 300, 7.0, 1050000, 0.2))
    print("  [✓] Datos de ejemplo cargados")


# ═══════════════════════════════════════════════════════════════
#  PASO 2: ALGORITMOS DE CAMINOS MÍNIMOS
# ═══════════════════════════════════════════════════════════════

def ejecutar_dijkstra(grafo: GrafoLogistico):
    """Ejecuta Dijkstra entre puntos clave."""
    print("\n" + "═" * 60)
    print("  PASO 2: DIJKSTRA — CAMINOS MÍNIMOS")
    print("═" * 60)

    pesca = grafo.puntos_pesca()
    mercados = grafo.mercados()

    if not pesca or not mercados:
        print("  [!] No hay suficientes nodos para calcular rutas.")
        return

    destino = mercados[0].id

    for punto in pesca:
        dist, camino = dijkstra(
            grafo, punto.id, destino, criterio="tiempo_h",
            evitar_restringidos=True,
        )
        if dist < float("inf"):
            print(f"\n  📍 {punto.nombre} → {mercados[0].nombre}")
            print(f"     Ruta:   {' → '.join(camino)}")
            print(f"     Tiempo: {dist:.2f} horas")

            # Calcular distancia total de la ruta
            dist_km = 0
            for i in range(len(camino) - 1):
                ar = grafo.obtener_arista(camino[i], camino[i+1])
                if ar:
                    dist_km += ar.distancia_km
            print(f"     Dist:   {dist_km:.1f} km")
        else:
            print(f"\n  ✗ No hay ruta de {punto.nombre} a {mercados[0].nombre}")


def ejecutar_bellman_ford(grafo: GrafoLogistico):
    """Ejecuta Bellman-Ford y verifica consistencia con Dijkstra."""
    print("\n" + "═" * 60)
    print("  PASO 3B: BELLMAN-FORD — VERIFICACIÓN")
    print("═" * 60)

    pesca = grafo.puntos_pesca()
    mercados = grafo.mercados()

    if not pesca or not mercados:
        print("  [!] No hay suficientes nodos.")
        return

    origen = pesca[0]
    dist_bf, prev_bf, ciclo_neg = bellman_ford(
        grafo, origen.id, criterio="tiempo_h", evitar_restringidos=True
    )

    # Verificar ciclos negativos
    if ciclo_neg:
        print("  ⚠️  CICLO NEGATIVO DETECTADO — resultados inválidos.")
    else:
        print("  [✓] Sin ciclos negativos — grafo válido para optimización")

    # Comparar con Dijkstra
    print(f"\n  Verificación cruzada Bellman-Ford vs Dijkstra (origen: {origen.nombre}):")
    print(f"  {'Destino':<25} {'BF (h)':>10} {'Dijkstra (h)':>12} {'Match':>7}")
    print("  " + "─" * 56)

    destinos_ver = mercados + grafo.centros_frio()[:2]
    coincidencias = 0
    total = 0
    for nodo in destinos_ver:
        t_bf = dist_bf.get(nodo.id, float("inf"))
        t_dj, _ = dijkstra(
            grafo, origen.id, nodo.id, criterio="tiempo_h",
            evitar_restringidos=True,
        )

        bf_str = f"{t_bf:.4f}" if t_bf < float("inf") else "∞"
        dj_str = f"{t_dj:.4f}" if t_dj < float("inf") else "∞"
        match = "✓" if abs(t_bf - t_dj) < 0.0001 else "✗"
        if match == "✓":
            coincidencias += 1
        total += 1

        print(f"  {nodo.nombre:<25} {bf_str:>10} {dj_str:>12} {match:>7}")

    print(f"\n  Resultado: {coincidencias}/{total} coincidencias exactas")

    # Ruta al primer mercado
    destino = mercados[0]
    camino_bf = reconstruir_camino_bf(prev_bf, destino.id)
    if camino_bf and dist_bf[destino.id] < float("inf"):
        print(f"\n  📍 Ruta BF: {origen.nombre} → {destino.nombre}")
        print(f"     Camino:  {' → '.join(camino_bf)}")
        print(f"     Tiempo:  {dist_bf[destino.id]:.2f} horas")


def ejecutar_recorridos_fundamentales(grafo: GrafoLogistico):
    """Ejecuta los algoritmos clásicos de recorrido (BFS y DFS) del tercer corte."""
    print("\n" + "═" * 60)
    print("  PASO 3C: RECORRIDOS FUNDAMENTALES (BFS Y DFS)")
    print("═" * 60)

    pesca = grafo.puntos_pesca()
    mercados = grafo.mercados()
    if not pesca:
        return

    # 1. BFS: Identificar acopio o cuarto frío más cercano en saltos desde cada pesca
    print("\n  [BFS] Acopio o Planta Frigorífica más cercana (mínimos transbordos):")
    for p in pesca:
        nodo_dest, saltos, camino = bfs_nodo_mas_cercano_por_tipo(
            grafo, p.id, tipos_objetivo=("A", "F"), evitar_restringidos=True
        )
        if nodo_dest:
            nombre_dest = grafo.obtener_nodo(nodo_dest).nombre
            print(f"    • {p.id} ({p.nombre}) → {nodo_dest} ({nombre_dest}): {saltos} saltos | {' → '.join(camino)}")
        else:
            print(f"    • {p.id} ({p.nombre}) → Sin conexión a acopio/frío")

    # 2. DFS: Enumeración exhaustiva de rutas simples alternativas hacia Bogotá
    if mercados:
        dest_bog = next((m.id for m in mercados if "BOG" in m.id.upper()), mercados[-1].id)
        p_origen = pesca[0]
        rutas_dfs = dfs_resumen_rutas(grafo, p_origen.id, dest_bog, evitar_restringidos=True)
        print(f"\n  [DFS] Exploración exhaustiva de rutas simples ({p_origen.id} → {dest_bog}):")
        print(f"    Se hallaron {len(rutas_dfs)} rutas alternativas por búsqueda en profundidad:")
        for idx, r in enumerate(rutas_dfs[:3], start=1):
            print(f"      Ruta #{idx} ({r['tiempo_h']:.2f} h, {r['distancia_km']} km): {' → '.join(r['camino'])}")
        if len(rutas_dfs) > 3:
            print(f"      ... y {len(rutas_dfs) - 3} rutas adicionales exploradas con backtracking.")


def ejecutar_floyd_warshall(grafo: GrafoLogistico):
    """Ejecuta Floyd-Warshall y muestra la matriz."""
    print("\n" + "═" * 60)
    print("  PASO 3: FLOYD-WARSHALL — TODOS LOS PARES")
    print("═" * 60)

    dist, sig = floyd_warshall(
        grafo, criterio="tiempo_h", evitar_restringidos=True
    )

    # Mostrar un subconjunto relevante
    ids_interes = []
    for n in grafo.puntos_pesca()[:3]:
        ids_interes.append(n.id)
    for n in grafo.centros_frio()[:2]:
        ids_interes.append(n.id)
    for n in grafo.mercados()[:2]:
        ids_interes.append(n.id)

    if ids_interes:
        print("\n  Matriz de tiempos (horas) — subconjunto:\n")
        print(matriz_a_tabla(dist, ids_interes))


# ═══════════════════════════════════════════════════════════════
#  PASO 3: LOCALIZACIÓN DE CENTROS DE FRÍO
# ═══════════════════════════════════════════════════════════════

def ejecutar_localizacion(grafo: GrafoLogistico):
    """Resuelve el problema de localización de instalaciones."""
    print("\n" + "═" * 60)
    print("  PASO 4: LOCALIZACIÓN ÓPTIMA DE CENTROS DE FRÍO")
    print("═" * 60)

    resultado = resolver_localizacion(
        grafo,
        metodo="greedy",
        tiempo_max_h=TIEMPO_MAX_SIN_FRIO_H,
    )
    print(resultado.resumen())
    return resultado


# ═══════════════════════════════════════════════════════════════
#  PASO 4: SIMULACIÓN DE CADENA DE FRÍO
# ═══════════════════════════════════════════════════════════════

def ejecutar_simulacion(grafo: GrafoLogistico):
    """Simula la cadena de frío para la ruta más larga."""
    print("\n" + "═" * 60)
    print("  PASO 5: SIMULACIÓN DE CADENA DE FRÍO")
    print("═" * 60)

    simulador = SimuladorCadenaFrio(grafo, tiempo_limite_h=TIEMPO_MAX_SIN_FRIO_H)

    pesca = grafo.puntos_pesca()
    mercados = grafo.mercados()
    if not pesca or not mercados:
        print("  [!] No hay datos suficientes para simular.")
        return

    destino = mercados[0].id

    for punto in pesca[:3]:  # Simular los primeros 3
        dist, camino = dijkstra(
            grafo, punto.id, destino, criterio="tiempo_h",
            evitar_restringidos=True,
        )
        if dist < float("inf") and len(camino) >= 2:
            resultado = simulador.simular_ruta(camino, punto.produccion_kg_dia)
            print(resultado.resumen())


# ═══════════════════════════════════════════════════════════════
#  ITINERARIOS POR PUNTO DE PESCA
# ═══════════════════════════════════════════════════════════════

def ejecutar_itinerarios(grafo: GrafoLogistico):
    """Calcula e imprime los itinerarios por punto de pesca hacia Bogotá y V_PG1."""
    print("\n" + "═" * 60)
    print("  ITINERARIOS POR PUNTO DE PESCA")
    print("═" * 60)

    mercados = grafo.mercados()
    if not mercados:
        print("  [!] No hay mercados definidos.")
        return []

    destino_bog = next(
        (m.id for m in mercados if "BOG" in m.id.upper() or "Bogotá" in m.nombre),
        mercados[-1].id,
    )
    destino_pg = next(
        (m.id for m in mercados if m.id == "V_PG1"),
        mercados[0].id,
    )

    print(f"\n  ── Destino Bogotá ({destino_bog}) ──")
    itinerarios_bog = calcular_itinerarios(grafo, destino_bog)
    for it in itinerarios_bog:
        print(f"  • {it.resumen()}")

    if destino_pg != destino_bog:
        print(f"\n  ── Destino Local Puerto Gaitán ({destino_pg}) ──")
        itinerarios_pg = calcular_itinerarios(grafo, destino_pg)
        for it in itinerarios_pg:
            print(f"  • {it.resumen()}")

    return itinerarios_bog


# ═══════════════════════════════════════════════════════════════
#  PASO 5: COMPARACIÓN DE ESCENARIOS
# ═══════════════════════════════════════════════════════════════

def ejecutar_comparacion(grafo: GrafoLogistico):
    """Compara escenarios con y sin centros de frío."""
    print("\n" + "═" * 60)
    print("  PASO 6: COMPARACIÓN DE ESCENARIOS")
    print("═" * 60)

    mercados = grafo.mercados()
    if not mercados:
        print("  [!] No hay mercados definidos.")
        return

    # Usar V_PG como destino (primer nodo de venta local)
    destino = mercados[0].id
    centros = [n.id for n in grafo.centros_frio()]

    evaluador = EvaluadorEscenarios(grafo, tiempo_limite_h=TIEMPO_MAX_SIN_FRIO_H)

    escenarios = [
        {"nombre": "Sin cadena de frío", "centros": []},
    ]

    # Un centro a la vez (solo los que están conectados a puntos de pesca)
    for c in centros:
        nodo_c = grafo.obtener_nodo(c)
        if not nodo_c:
            continue
        # Verificar si al menos un punto de pesca puede llegar
        puede = any(
            dijkstra(
                grafo, p.id, c, criterio="tiempo_h", evitar_restringidos=True
            )[0] < float("inf")
            for p in grafo.puntos_pesca()
        )
        if puede:
            escenarios.append({"nombre": f"Solo {nodo_c.nombre}", "centros": [c]})

    # Combinaciones de 2 centros
    centros_conectados = [e["centros"][0] for e in escenarios if e["centros"]]
    if len(centros_conectados) >= 2:
        escenarios.append({
            "nombre": f"{len(centros_conectados)} centros combinados",
            "centros": centros_conectados,
        })

    # Todos los centros
    if len(centros) > 1:
        escenarios.append({"nombre": "Todos los centros", "centros": centros})

    # Deduplicar escenarios con los mismos centros
    vistos = set()
    escenarios_unicos = []
    for esc in escenarios:
        clave = frozenset(esc["centros"])
        if clave not in vistos:
            vistos.add(clave)
            escenarios_unicos.append(esc)
    escenarios = escenarios_unicos

    resultados = evaluador.comparar_escenarios(escenarios, destino)

    # Mostrar tabla comparativa
    print(EvaluadorEscenarios.tabla_comparativa(resultados))

    # Mostrar detalle de cada escenario
    for m in resultados:
        print(m.resumen())

    # Comparación adicional orientada a Bogotá
    if len(mercados) > 1:
        destino_bog = next(
            (m.id for m in mercados
             if "BOG" in m.id.upper() or "Bogotá" in m.nombre),
            None,
        )
        if destino_bog and destino_bog != destino:
            print("\n" + "═" * 60)
            print("  PASO 6B: ESCENARIOS ORIENTADOS A BOGOTÁ")
            print("═" * 60)
            resultados_bog = evaluador.comparar_escenarios(
                escenarios, destino_bog
            )
            print(EvaluadorEscenarios.tabla_comparativa(resultados_bog))

    return resultados


# ═══════════════════════════════════════════════════════════════
#  PASO 6: VISUALIZACIÓN
# ═══════════════════════════════════════════════════════════════

def ejecutar_visualizacion(grafo: GrafoLogistico):
    """Genera la visualización del grafo."""
    print("\n" + "═" * 60)
    print("  PASO 7: VISUALIZACIÓN")
    print("═" * 60)

    try:
        from src.visualization.graph_plotter import graficar_grafo
        from src.utils.data_loader import OUTPUT_DIR

        ruta_img = str(OUTPUT_DIR / "grafo_logistico.png")

        # Buscar la ruta óptima para destacar
        ruta_destacada = None
        pesca = grafo.puntos_pesca()
        mercados = grafo.mercados()
        if pesca and mercados:
            _, camino = dijkstra(grafo, pesca[0].id, mercados[0].id,
                                 criterio="tiempo_h", evitar_restringidos=True)
            if camino:
                ruta_destacada = camino

        graficar_grafo(
            grafo,
            ruta_destacada=ruta_destacada,
            guardar_como=ruta_img,
            mostrar=False,
        )
    except Exception as e:
        print(f"  [!] No se pudo generar visualización: {e}")


# ═══════════════════════════════════════════════════════════════
#  FUNCIONES DE INTERFAZ DE CONSOLA Y MENÚ
# ═══════════════════════════════════════════════════════════════

def limpiar_pantalla():
    """Limpia la terminal según el sistema operativo."""
    os.system("cls" if os.name == "nt" else "clear")


def pausar():
    """Pausa para permitir al usuario revisar la salida."""
    print()
    input("  👉 Presione [ENTER] para regresar al menú principal...")


def opcion_resumen_red(grafo: GrafoLogistico):
    """Muestra el resumen completo y catálogo funcional de nodos."""
    limpiar_pantalla()
    print("\n" + "═" * 65)
    print("  [1] RESUMEN Y TOPOLOGÍA DE LA RED (25 NODOS Y 41 ARISTAS)")
    print("═" * 65)
    print(grafo.resumen())

    print("\n  📋 Desglose detallado por categoría de nodo:")
    categorias = [
        ("P", "Puntos de Pesca (Orígenes de flujo)"),
        ("M", "Muelles Fluviales (Transbordo multimodal)"),
        ("A", "Centros de Acopio Rural (Consolidación)"),
        ("F", "Centros Frigoríficos (Abatimiento térmico 0 °C)"),
        ("D", "Zonas de Deterioro Térmico Crítico (×1.5)"),
        ("H", "Hábitats Protegidos (Restricción ambiental)"),
        ("V", "Mercados y Puntos de Venta (Destinos comerciales)"),
    ]
    for tipo, desc in categorias:
        nodos_cat = grafo.nodos_por_tipo(tipo)
        print(f"\n    • {desc} [{len(nodos_cat)}]:")
        for n in nodos_cat:
            info_extra = ""
            if tipo == "P":
                info_extra = f" — {n.produccion_kg_dia} kg/día"
            elif tipo in ("A", "F"):
                info_extra = f" — Cap: {n.capacidad_frio_kg} kg | Energía: {'Sí' if n.tiene_energia else 'No'}"
            elif tipo == "H":
                info_extra = " — [Restricción Ambiental Activa]"
            elif tipo == "D":
                info_extra = " — [Deterioro Acelerado ×1.5]"
            elif tipo == "V":
                info_extra = f" — {n.ciudad}"
            print(f"      - {n.id:<6} {n.nombre:<32}{info_extra}")


def opcion_abrir_mapa(grafo: GrafoLogistico, itinerarios_bog=None):
    """Abre el mapa interactivo HTML en el navegador web predeterminado."""
    limpiar_pantalla()
    print("\n" + "═" * 65)
    print("  [8] MAPA INTERACTIVO (FOLIUM / LEAFLET CON RUTAS OSRM)")
    print("═" * 65)

    from src.utils.data_loader import OUTPUT_DIR
    ruta_mapa = OUTPUT_DIR / "mapa_interactivo.html"

    if not ruta_mapa.exists():
        print("  [i] Generando archivo HTML del mapa interactivo...")
        geo_cache = {}
        try:
            from src.visualization.route_geometry import obtener_geometrias_grafo
            geo_cache = obtener_geometrias_grafo(grafo, usar_cache=True)
        except Exception as e:
            print(f"  [!] Geometrías OSRM: {e}")
            geo_cache = {}

        ruta_mapa_gen = generar_mapa_interactivo(
            grafo,
            abrir_navegador=True,
            geometrias_reales=geo_cache,
            itinerarios=itinerarios_bog,
        )
        print(f"  [✓] Mapa generado en: {ruta_mapa_gen}")
    else:
        print(f"  [✓] Abriendo mapa interactivo en el navegador: {ruta_mapa.name}")
        webbrowser.open(f"file://{ruta_mapa.resolve()}")

    print("  ✅ Mapa interactivo abierto con éxito en su navegador.")


def opcion_ejecutar_pruebas():
    """Ejecuta toda la suite de pruebas unitarias (pytest)."""
    limpiar_pantalla()
    print("\n" + "═" * 65)
    print("  [9] EJECUCIÓN DE PRUEBAS UNITARIAS (PYTEST - 40 PRUEBAS)")
    print("═" * 65)
    subprocess.run([sys.executable, "-m", "pytest", "tests/", "-v"])


def ejecutar_pipeline_completo(grafo: GrafoLogistico):
    """Ejecuta el flujo completo automatizado con exportación de resultados."""
    limpiar_pantalla()
    print("\n" + "═" * 65)
    print("  [10] EJECUCIÓN DEL PIPELINE COMPLETO Y EXPORTACIÓN")
    print("═" * 65)

    print(grafo.resumen())
    ejecutar_dijkstra(grafo)
    ejecutar_floyd_warshall(grafo)
    ejecutar_bellman_ford(grafo)
    ejecutar_recorridos_fundamentales(grafo)
    ejecutar_localizacion(grafo)
    ejecutar_simulacion(grafo)
    itinerarios_bog = ejecutar_itinerarios(grafo)
    ejecutar_comparacion(grafo)
    ejecutar_visualizacion(grafo)

    print("\n" + "═" * 60)
    print("  EXPORTACIÓN DE RESULTADOS")
    print("═" * 60)
    nodos_export = [n.to_dict() for n in grafo.nodos]
    aristas_export = [a.to_dict() for a in grafo.aristas]
    ruta_n = guardar_resultados_csv(nodos_export, "nodos_resultado.csv")
    ruta_a = guardar_resultados_csv(aristas_export, "aristas_resultado.csv")
    print(f"  [✓] Nodos exportados:   {ruta_n}")
    print(f"  [✓] Aristas exportadas: {ruta_a}")

    pesca = grafo.puntos_pesca()
    mercados = grafo.mercados()
    ruta_felt = None
    if pesca and mercados:
        destino_felt = next(
            (m.id for m in mercados if "BOG" in m.id.upper()),
            mercados[-1].id,
        )
        _, ruta_felt = dijkstra(grafo, pesca[0].id, destino_felt,
                                criterio="tiempo_h", evitar_restringidos=True)

    exportar_para_felt(
        grafo,
        ruta_optima=ruta_felt,
        nombre_ruta=f"Ruta Óptima: {pesca[0].nombre} → Bogotá"
        if ruta_felt else "Ruta Óptima",
    )

    geo_cache = {}
    try:
        from src.visualization.route_geometry import obtener_geometrias_grafo
        geo_cache = obtener_geometrias_grafo(grafo, usar_cache=True)
    except Exception as e:
        print(f"  [!] Geometrías OSRM: {e}")

    try:
        ruta_mapa = generar_mapa_interactivo(
            grafo,
            ruta_optima=ruta_felt,
            nombre_ruta=f"Ruta Óptima: {pesca[0].nombre} → Bogotá"
            if ruta_felt else "Ruta Óptima",
            abrir_navegador=False,
            geometrias_reales=geo_cache,
            itinerarios=itinerarios_bog,
        )
        print(f"  [✓] Mapa interactivo actualizado: {ruta_mapa}")
    except Exception as e:
        print(f"  [!] Error mapa: {e}")

    print("\n  ✅ Pipeline completo finalizado con éxito.\n")
    return itinerarios_bog


# ═══════════════════════════════════════════════════════════════
#  MAIN INTERACTIVO
# ═══════════════════════════════════════════════════════════════

def main():
    """Punto de entrada interactivo con menú y limpieza de pantalla."""
    # Cargar datos inicialmente
    grafo = cargar_datos()
    itinerarios_cache = None

    # Modo batch automatizado (por parámetro en consola)
    if len(sys.argv) > 1 and sys.argv[1].lower() in ("--batch", "--all", "-b", "-a"):
        ejecutar_pipeline_completo(grafo)
        return

    while True:
        limpiar_pantalla()
        print("╔══════════════════════════════════════════════════════════════════════╗")
        print("║   OPTIMIZACIÓN DE CENTROS DE REFRIGERACIÓN — PUERTO GAITÁN, META   ║")
        print("║   Estructuras de Datos — Semestre 03 (2026-II) — Teoría de Grafos   ║")
        print("║   Autores: Yair Armando Ospino H.  •  Harold Esteban Padilla D.    ║")
        print("╚══════════════════════════════════════════════════════════════════════╝")
        print()
        print("  [1]  Resumen y Topología de la Red (25 Nodos y 41 Aristas)")
        print("  [2]  Caminos Mínimos con Dijkstra (Rutas Óptimas y Exclusión H)")
        print("  [3]  Bellman-Ford y Floyd-Warshall (Verificación y Matriz Global)")
        print("  [4]  Recorridos Canónicos del Corte: BFS y DFS")
        print("  [5]  Localización Óptima de Centros Frigoríficos (FLP Greedy)")
        print("  [6]  Simulación Térmica e Itinerarios (Cadena de Frío Poscaptura)")
        print("  [7]  Evaluación y Comparación de Escenarios Logísticos")
        print("  [8]  Abrir Mapa Interactivo en el Navegador (Folium / OSRM)")
        print("  [9]  Ejecutar Pruebas Unitarias Automatizadas (pytest - 40 tests)")
        print("  [10] Ejecutar Pipeline Completo (Reporte Integral / Exportación)")
        print("  [0]  Salir")
        print()

        try:
            opc = input("  👉 Seleccione una opción [0-10]: ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\n  Salida forzada.")
            break

        if opc == "1":
            opcion_resumen_red(grafo)
            pausar()
        elif opc == "2":
            limpiar_pantalla()
            ejecutar_dijkstra(grafo)
            pausar()
        elif opc == "3":
            limpiar_pantalla()
            ejecutar_bellman_ford(grafo)
            ejecutar_floyd_warshall(grafo)
            pausar()
        elif opc == "4":
            limpiar_pantalla()
            ejecutar_recorridos_fundamentales(grafo)
            pausar()
        elif opc == "5":
            limpiar_pantalla()
            ejecutar_localizacion(grafo)
            pausar()
        elif opc == "6":
            limpiar_pantalla()
            ejecutar_simulacion(grafo)
            itinerarios_cache = ejecutar_itinerarios(grafo)
            pausar()
        elif opc == "7":
            limpiar_pantalla()
            ejecutar_comparacion(grafo)
            pausar()
        elif opc == "8":
            opcion_abrir_mapa(grafo, itinerarios_cache)
            pausar()
        elif opc == "9":
            opcion_ejecutar_pruebas()
            pausar()
        elif opc == "10":
            itinerarios_cache = ejecutar_pipeline_completo(grafo)
            pausar()
        elif opc == "0":
            limpiar_pantalla()
            print("\n  👋 Gracias por utilizar el sistema de optimización logística.")
            print("     Universidad de los Llanos — 2026-II\n")
            break
        else:
            print("\n  ⚠️ Opción no válida. Intente de nuevo.")
            pausar()


if __name__ == "__main__":
    main()

