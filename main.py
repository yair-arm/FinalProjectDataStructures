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
#  MAIN
# ═══════════════════════════════════════════════════════════════

def main():
    """Flujo principal del programa."""
    print()
    print("╔═══════════════════════════════════════════════════════════╗")
    print("║  OPTIMIZACIÓN DE CENTROS DE REFRIGERACIÓN               ║")
    print("║  Cadena de Frío — Pesca Artesanal Puerto Gaitán, Meta   ║")
    print("║  Estructuras de Datos — 2026-II                         ║")
    print("╚═══════════════════════════════════════════════════════════╝")

    # 1. Cargar datos
    grafo = cargar_datos()
    print(grafo.resumen())

    # 2. Dijkstra
    ejecutar_dijkstra(grafo)

    # 3. Floyd-Warshall
    ejecutar_floyd_warshall(grafo)

    # 3B. Bellman-Ford (verificación cruzada)
    ejecutar_bellman_ford(grafo)

    # 3C. Recorridos fundamentales (BFS y DFS)
    ejecutar_recorridos_fundamentales(grafo)

    # 4. Localización de centros
    ejecutar_localizacion(grafo)

    # 5. Simulación de cadena de frío
    ejecutar_simulacion(grafo)

    # 5B. Itinerarios por punto de pesca
    itinerarios_bog = ejecutar_itinerarios(grafo)

    # 6. Comparación de escenarios
    ejecutar_comparacion(grafo)

    # 7. Visualización
    ejecutar_visualizacion(grafo)

    # Exportar resultados
    print("\n" + "═" * 60)
    print("  EXPORTACIÓN DE RESULTADOS")
    print("═" * 60)

    nodos_export = [n.to_dict() for n in grafo.nodos]
    aristas_export = [a.to_dict() for a in grafo.aristas]
    ruta_n = guardar_resultados_csv(nodos_export, "nodos_resultado.csv")
    ruta_a = guardar_resultados_csv(aristas_export, "aristas_resultado.csv")
    print(f"  [✓] Nodos exportados:   {ruta_n}")
    print(f"  [✓] Aristas exportadas: {ruta_a}")

    # 8. Exportación para Felt.com (GeoJSON + ZIP)
    pesca = grafo.puntos_pesca()
    mercados = grafo.mercados()
    ruta_felt = None
    if pesca and mercados:
        # Calcular ruta óptima completa: primer punto de pesca → Bogotá
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

    # 9. Obtener geometrías reales de carreteras (OSRM)
    geo_cache = {}
    try:
        from src.visualization.route_geometry import obtener_geometrias_grafo
        geo_cache = obtener_geometrias_grafo(grafo, usar_cache=True)
    except Exception as e:
        print(f"  [!] No se pudieron obtener geometrías reales: {e}")
        geo_cache = {}

    # 10. Mapa interactivo HTML (Folium) con rutas reales
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
        print(f"  → Abre en tu navegador: {ruta_mapa}")
    except Exception as e:
        print(f"  [!] No se pudo generar mapa interactivo: {e}")

    print("\n  ✅ Ejecución completada exitosamente.\n")


if __name__ == "__main__":
    main()

