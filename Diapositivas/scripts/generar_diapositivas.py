# -*- coding: utf-8 -*-
"""
Genera la presentacion en PowerPoint (.pptx) para la exposicion del Proyecto Final
de Estructuras de Datos (Grafos) en Puerto Gaitan, Meta, basada en el modelo
multimodal de 25 nodos y 41 aristas de Harold Padilla y Yair Ospino.
Diseno profesional 16:9 con paleta institucional Unillanos, tarjetas, metricas y graficas.
"""
import os
import pptx
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE

BASE = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
ROOT = os.path.abspath(os.path.join(BASE, '..'))
ASSETS = os.path.join(ROOT, 'Informe_IEEE', 'Assets')
DATA_OUT = os.path.join(ROOT, 'data', 'output')
OUT_PPTX = os.path.join(BASE, 'Presentacion_Proyecto_Final_Grafos.pptx')
OUT_PDF = os.path.join(BASE, 'Presentacion_Proyecto_Final_Grafos.pdf')

prs = Presentation()
prs.slide_width = Inches(13.333)
prs.slide_height = Inches(7.5)
blank_layout = prs.slide_layouts[6]

# Paleta de colores profesional
NAVY = RGBColor(15, 23, 42)          # #0F172A
CARD_BG = RGBColor(30, 41, 59)       # #1E293B
WHITE = RGBColor(255, 255, 255)
LIGHT_GRAY = RGBColor(241, 245, 249)
MUTED = RGBColor(148, 163, 184)
ACCENT_BLUE = RGBColor(56, 189, 248) # #38BDF8
ACCENT_GREEN = RGBColor(52, 211, 153)# #34D399
ACCENT_RED = RGBColor(248, 113, 113) # #F87171
ACCENT_AMBER = RGBColor(251, 191, 36)# #FBBF24

def set_slide_background(slide, color):
    bg = slide.background
    fill = bg.fill
    fill.solid()
    fill.fore_color.rgb = color

def add_header(slide, title_text, category_text="ESTRUCTURAS DE DATOS • CORTE 3: GRAFOS"):
    cat_box = slide.shapes.add_textbox(Inches(0.8), Inches(0.4), Inches(11.5), Inches(0.4))
    tf_c = cat_box.text_frame
    tf_c.word_wrap = True
    p_c = tf_c.paragraphs[0]
    p_c.text = category_text.upper()
    p_c.font.size = Pt(10)
    p_c.font.bold = True
    p_c.font.color.rgb = ACCENT_BLUE

    title_box = slide.shapes.add_textbox(Inches(0.8), Inches(0.7), Inches(11.5), Inches(0.8))
    tf_t = title_box.text_frame
    tf_t.word_wrap = True
    p_t = tf_t.paragraphs[0]
    p_t.text = title_text
    p_t.font.size = Pt(22)
    p_t.font.bold = True
    p_t.font.color.rgb = WHITE

def add_card(slide, left, top, width, height, title, body_paragraphs, border_color=None, bg_color=CARD_BG):
    shape = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, left, top, width, height)
    shape.fill.solid()
    shape.fill.fore_color.rgb = bg_color
    if border_color:
        shape.line.color.rgb = border_color
        shape.line.width = Pt(1.5)
    else:
        shape.line.fill.background()

    tf = shape.text_frame
    tf.word_wrap = True
    tf.vertical_anchor = MSO_ANCHOR.TOP
    tf.margin_left = Inches(0.25)
    tf.margin_right = Inches(0.25)
    tf.margin_top = Inches(0.2)
    tf.margin_bottom = Inches(0.2)

    p0 = tf.paragraphs[0]
    p0.text = title
    p0.font.size = Pt(14)
    p0.font.bold = True
    p0.font.color.rgb = ACCENT_BLUE
    p0.space_after = Pt(8)

    for item in body_paragraphs:
        p = tf.add_paragraph()
        p.space_after = Pt(6)
        if isinstance(item, tuple):
            strong, normal = item
            r1 = p.add_run()
            r1.text = strong + " "
            r1.font.bold = True
            r1.font.size = Pt(11)
            r1.font.color.rgb = WHITE
            r2 = p.add_run()
            r2.text = normal
            r2.font.bold = False
            r2.font.size = Pt(11)
            r2.font.color.rgb = LIGHT_GRAY
        else:
            r = p.add_run()
            r.text = item
            r.font.size = Pt(11)
            r.font.color.rgb = LIGHT_GRAY

def add_metric_badge(slide, left, top, width, height, number_str, label_str, color=ACCENT_GREEN):
    shape = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, left, top, width, height)
    shape.fill.solid()
    shape.fill.fore_color.rgb = CARD_BG
    shape.line.color.rgb = color
    shape.line.width = Pt(1.5)
    tf = shape.text_frame
    tf.word_wrap = True
    tf.vertical_anchor = MSO_ANCHOR.MIDDLE

    p1 = tf.paragraphs[0]
    p1.alignment = PP_ALIGN.CENTER
    r1 = p1.add_run()
    r1.text = number_str
    r1.font.size = Pt(24)
    r1.font.bold = True
    r1.font.color.rgb = color

    p2 = tf.add_paragraph()
    p2.alignment = PP_ALIGN.CENTER
    r2 = p2.add_run()
    r2.text = label_str
    r2.font.size = Pt(10)
    r2.font.color.rgb = LIGHT_GRAY

# =========================================================================
# SLIDE 1: PORTADA INSTITUCIONAL
# =========================================================================
s1 = prs.slides.add_slide(blank_layout)
set_slide_background(s1, NAVY)

logo_path = os.path.join(ASSETS, 'logo_unillanos_0.png')
if os.path.exists(logo_path):
    s1.shapes.add_picture(logo_path, Inches(5.9), Inches(0.8), width=Inches(1.5))

tb1 = s1.shapes.add_textbox(Inches(1.0), Inches(2.5), Inches(11.3), Inches(3.2))
tf1 = tb1.text_frame
tf1.word_wrap = True

p = tf1.paragraphs[0]
p.alignment = PP_ALIGN.CENTER
p.text = "UNIVERSIDAD DE LOS LLANOS"
p.font.size = Pt(14)
p.font.bold = True
p.font.color.rgb = ACCENT_AMBER
p.space_after = Pt(4)

p = tf1.add_paragraph()
p.alignment = PP_ALIGN.CENTER
p.text = "FACULTAD DE CIENCIAS BÁSICAS E INGENIERÍA — INGENIERÍA EN SISTEMAS"
p.font.size = Pt(11)
p.font.color.rgb = MUTED
p.space_after = Pt(16)

p = tf1.add_paragraph()
p.alignment = PP_ALIGN.CENTER
p.text = "Optimización Multimodal de Cadenas de Frío para Pesca Artesanal\nmediante Teoría de Grafos y Localización de Instalaciones (FLP)"
p.font.size = Pt(23)
p.font.bold = True
p.font.color.rgb = WHITE
p.space_after = Pt(8)

p = tf1.add_paragraph()
p.alignment = PP_ALIGN.CENTER
p.text = "Caso de Estudio: Corredor Fluvial y Terrestre de Puerto Gaitán, Meta"
p.font.size = Pt(13)
p.font.italic = True
p.font.color.rgb = ACCENT_BLUE

foot_b = s1.shapes.add_textbox(Inches(1.0), Inches(5.9), Inches(11.3), Inches(1.2))
tff = foot_b.text_frame
p = tff.paragraphs[0]
p.alignment = PP_ALIGN.CENTER
p.text = "Autores: Yair Armando Ospino Herrera (160005565)  •  Harold Esteban Padilla Díaz (160005567)"
p.font.size = Pt(12)
p.font.bold = True
p.font.color.rgb = WHITE

p = tff.add_paragraph()
p.alignment = PP_ALIGN.CENTER
p.text = "Docente: Estructuras de Datos • Semestre 2026-II • Villavicencio, Meta"
p.font.size = Pt(10)
p.font.color.rgb = MUTED

# =========================================================================
# SLIDE 2: CONTEXTO Y PROBLEMÁTICA REAL
# =========================================================================
s2 = prs.slides.add_slide(blank_layout)
set_slide_background(s2, NAVY)
add_header(s2, "Contexto Territorial y Problemática Pesquera en Puerto Gaitán")

add_card(s2, Inches(0.8), Inches(1.8), Inches(5.6), Inches(5.0),
         "Realidad del Pescador Artesanal", [
             ("Cuencas Hidrográficas:", "Actividad pesquera concentrada en los ríos Meta, Manacacías e Iteviare."),
             ("7 Asociaciones Censadas:", "ASOPESGA, Atarraya Verde, Asovida, Asopespor, Puerto Trujillo, Desembarcadero y Soplaviento."),
             ("Producción Regional:", "265.8 kg/día censados en campo con picos estacionales de subienda."),
             ("Aislamiento Fluvial:", "Comunidades como Puerto Trujillo (P05) distan a más de 63 km de navegación de centros poblados."),
             ("Temperatura Ambiente:", "Temperaturas promedio de 30 °C con alta radiación solar directa sobre las canoas."),
         ], border_color=ACCENT_BLUE)

add_card(s2, Inches(6.8), Inches(1.8), Inches(5.7), Inches(3.2),
         "El Cuello de Botella Logístico", [
             ("Pérdidas Poscaptura:", "Hasta un 40% del pescado se deteriora antes de alcanzar los centros de venta."),
             ("Ausencia de Infraestructura:", "Falta de cuartos fríos y muelles con energía continua en las riberas rurales."),
             ("Límite de Inocuidad:", "El pescado fresco supera el umbral sanitario admisible tras 4.0 h sin refrigeración."),
         ], border_color=ACCENT_RED)

add_metric_badge(s2, Inches(6.8), Inches(5.3), Inches(2.7), Inches(1.5), "265.8 kg", "Captura Diaria Censada", ACCENT_BLUE)
add_metric_badge(s2, Inches(9.8), Inches(5.3), Inches(2.7), Inches(1.5), "40%", "Pérdida Poscaptura Sin Frío", ACCENT_RED)

# =========================================================================
# SLIDE 3: MODELO BIOLÓGICO Y CADENA DE FRÍO
# =========================================================================
s3 = prs.slides.add_slide(blank_layout)
set_slide_background(s3, NAVY)
add_header(s3, "Fundamento Biológico: Cinética de Deterioro de la Cachama")

add_card(s3, Inches(0.8), Inches(1.8), Inches(5.8), Inches(5.0),
         "Comportamiento Térmico del Pescado", [
             ("Especie Foco:", "Cachama de río (Colossoma macropomum), altamente comercial en la Orinoquía."),
             ("Tasa de Deterioro Base:", "2.5% por cada hora transcurrida a temperatura ambiente (30 °C)."),
             ("Zonas Críticas (D):", "En pasos destapados sin sombra, la degradación se acelera con factor ×1.5 (3.75%/h)."),
             ("Tiempo Máximo Sin Frío:", "4.0 horas (240 min) es el límite estricto de inocuidad según parámetros FAO."),
             ("Efecto de la Cadena de Frío:", "A 0 °C (hielo 1:1), la vida útil se extiende hasta 360 horas (15 días)."),
         ], border_color=ACCENT_AMBER)

add_card(s3, Inches(7.0), Inches(1.8), Inches(5.5), Inches(5.0),
         "Modelo Matemático Térmico", [
             ("Función de Pérdida:", "D_acum = D_0 + ∑ (k_i · t_i)"),
             ("Reinicio Térmico:", "Al ingresar a un Centro Frío (F), la temperatura baja a 0 °C y el reloj sin frío se reinicia a 0.0 h."),
             ("Penalización de Muelle:", "Cada transbordo fluvial-terrestre en muelle suma +0.25 h bajo el sol."),
             ("Conservación a Mercados:", "El producto consolidado en frío viaja en furgón isotérmico por carretera nacional."),
         ], border_color=ACCENT_GREEN)

# =========================================================================
# SLIDE 4: ESTRUCTURAS DE DATOS Y ARQUITECTURA
# =========================================================================
s4 = prs.slides.add_slide(blank_layout)
set_slide_background(s4, NAVY)
add_header(s4, "Estructuras de Datos y Arquitectura del Sistema")

add_card(s4, Inches(0.8), Inches(1.8), Inches(3.8), Inches(5.0),
         "1. Grafo Logístico", [
             ("Representación:", "Grafo dirigido ponderado G = (V, E)."),
             ("Estructura Interna:", "Lista de Adyacencia con diccionario Hash O(1)."),
             ("Complejidad:", "Espacio O(|V| + |E|), inserción de aristas O(1)."),
             ("Peso Multicriterio:", "Pondera tiempo, costo, confiabilidad, pérdida y retrasos."),
         ], border_color=ACCENT_BLUE)

add_card(s4, Inches(4.8), Inches(1.8), Inches(3.8), Inches(5.0),
         "2. Grafo Fluvial Real", [
             ("Origen de Datos:", "Shapefile IGAC rios.shp con cauces reales."),
             ("Topología Cuantizada:", "12,413 vértices a 5 decimales (1.1 m) y 24,790 aristas."),
             ("Índice Espacial:", "Rejilla Hash de 447 celdas (0.05° × 0.05°) para búsqueda rápida."),
             ("Dijkstra Fluvial:", "Navega por meandros reales del río."),
         ], border_color=ACCENT_GREEN)

add_card(s4, Inches(8.8), Inches(1.8), Inches(3.7), Inches(5.0),
         "3. Malla Vial OSRM", [
             ("Geometría de Carreteras:", "Motor OSRM sobre OpenStreetMap."),
             ("Corredor Vial:", "Ruta Nacional 40 (Puerto Gaitán - Puerto López - Villavicencio - Bogotá)."),
             ("Caché Persistente:", "rutas_cache.json con 41 polilíneas exactas."),
             ("Sin Dependencias Web:", "Garantiza ejecución local inmediata."),
         ], border_color=ACCENT_AMBER)

# =========================================================================
# SLIDE 5: TOPOLOGÍA MULTIMODAL (25 VÉRTICES)
# =========================================================================
s5 = prs.slides.add_slide(blank_layout)
set_slide_background(s5, NAVY)
add_header(s5, "Topología de la Red: Catálogo de 25 Vértices y 41 Aristas")

fig1_path = os.path.join(ASSETS, 'figura_1_topologia_col.png')
if os.path.exists(fig1_path):
    s5.shapes.add_picture(fig1_path, Inches(0.8), Inches(1.8), width=Inches(3.8))

add_card(s5, Inches(4.9), Inches(1.8), Inches(7.6), Inches(5.0),
         "Los 7 Tipos Funcionales de Vértices", [
             ("🐟 P — Puntos de Pesca (7):", "P01 a P07; orígenes de flujo (captura total 265.8 kg/día)."),
             ("⚓ M — Muelles Fluviales (3):", "M01, M02, M03; transbordo lancha → camión (+0.25 h al sol)."),
             ("📦 A — Centros de Acopio (3):", "A01, A02, A03; consolidación obligatoria de pesca rural."),
             ("❄️ F — Centros Frigoríficos (3):", "F01 (Alto Neblinas), F02 (Puerto Gaitán), F03 (Puerto López). Abatimiento térmico a 0 °C."),
             ("🌡️ D — Zonas de Deterioro (2):", "D01 y D02; tramos sin sombra donde la tasa se multiplica por ×1.5."),
             ("🌿 H — Hábitats Protegidos (2):", "H01 y H02; áreas de desove con restricción ambiental (bloqueadas para paso intermedio)."),
             ("🏪 V — Mercados de Venta (5):", "V_PG1, V_PG2 (Pto. Gaitán), V_VLL (Villavicencio), V_BOG1, V_BOG2 (Bogotá)."),
         ], border_color=ACCENT_BLUE)

# =========================================================================
# SLIDE 6: ALGORITMOS DE CAMINO MÍNIMO
# =========================================================================
s6 = prs.slides.add_slide(blank_layout)
set_slide_background(s6, NAVY)
add_header(s6, "Algoritmos de Caminos Mínimos y Verificación Cruzada")

add_card(s6, Inches(0.8), Inches(1.8), Inches(5.8), Inches(5.0),
         "Dijkstra con Cola de Prioridad", [
             ("Implementación Propia:", "Cola de prioridad binaria (heapq) en Python, O((V + E) log V)."),
             ("Criterios Minimizables:", "Tiempo (horas), distancia (km), costo (COP) o peso multicriterio."),
             ("Filtro Ambiental:", "Parámetro evitar_restringidos=True bloquea vértices tipo H como nodos intermedios."),
             ("Ejemplo Real:", "P04 evita el hábitat H01 y toma la ruta segura P04 → A01 → F02."),
         ], border_color=ACCENT_GREEN)

add_card(s6, Inches(7.0), Inches(1.8), Inches(5.5), Inches(5.0),
         "Bellman-Ford y Floyd-Warshall", [
             ("Bellman-Ford O(V·E):", "Verificación cruzada de caminos y detección formal de ciclos negativos."),
             ("Validación 100% Exitosa:", "Coincidencia exacta de tiempos entre Bellman-Ford y Dijkstra en todas las consultas."),
             ("Floyd-Warshall O(V³):", "Matriz global de tiempos mínimos entre los 25 nodos del sistema."),
             ("Reconstrucción de Caminos:", "Matriz de predecesores que permite consultar cualquier ruta en O(L)."),
         ], border_color=ACCENT_BLUE)

# =========================================================================
# SLIDE 7: RECORRIDOS BFS Y DFS
# =========================================================================
s7 = prs.slides.add_slide(blank_layout)
set_slide_background(s7, NAVY)
add_header(s7, "Recorridos Canónicos del Curso: Algoritmos BFS y DFS")

add_card(s7, Inches(0.8), Inches(1.8), Inches(5.8), Inches(5.0),
         "Búsqueda en Amplitud (BFS)", [
             ("Estructura:", "Cola FIFO (collections.deque), complejidad O(V + E)."),
             ("Objetivo Operativo:", "Identificar el centro de acopio o frío más cercano en número de saltos/transbordos."),
             ("Garantía de Saltos Mínimos:", "P01 alcanza F02 en 2 saltos (P01 → M03 → F02)."),
             ("Puntos Críticos:", "Detecta que P05 requiere 5 saltos hacia F02 debido a su ubicación extrema en el río Iteviare."),
         ], border_color=ACCENT_BLUE)

add_card(s7, Inches(7.0), Inches(1.8), Inches(5.5), Inches(5.0),
         "Búsqueda en Profundidad (DFS)", [
             ("Estructura:", "Recursión y retroceso (backtracking) con límite de profundidad."),
             ("Enumeración Exhaustiva:", "Halla todas las rutas simples alternativas entre captura y mercados mayoristas."),
             ("Evaluación de Resiliencia:", "Permite desviar carga en caso de bloqueo o contingencia en carreteras o ríos."),
             ("Trazabilidad Térmica:", "Calcula el deterioro acumulado para cada ruta alternativa."),
         ], border_color=ACCENT_AMBER)

# =========================================================================
# SLIDE 8: LOCALIZACIÓN DE INSTALACIONES (FLP)
# =========================================================================
s8 = prs.slides.add_slide(blank_layout)
set_slide_background(s8, NAVY)
add_header(s8, "Problema de Localización de Instalaciones (FLP Greedy)")

g2a_path = os.path.join(ASSETS, 'grafica_2a_dfs_col.png')
if os.path.exists(g2a_path):
    s8.shapes.add_picture(g2a_path, Inches(0.8), Inches(1.8), width=Inches(5.0))

add_card(s8, Inches(6.1), Inches(1.8), Inches(6.4), Inches(5.0),
         "Selección de la Configuración Óptima", [
             ("Problema FLP:", "Determinar cuántos y cuáles cuartos fríos abrir minimizando costos fijos y acarreo."),
             ("Restricción de Inocuidad:", "Todo punto de pesca debe alcanzar frío en t ≤ 4.0 h."),
             ("Escenario Óptimo Seleccionado:", "Solo Centro Frío Puerto Gaitán (F02) en el casco urbano."),
             ("Costo Operativo:", "$13,023,272 COP/mes ($59,080 COP/kg)."),
             ("Cobertura Total:", "100% de los puntos de pesca cubiertos dentro del límite sanitario."),
             ("Ahorro Económico:", "Evita el sobrecosto de operar 3 plantas frigoríficas ($23,023,272 COP/mes, $104,444 COP/kg)."),
         ], border_color=ACCENT_GREEN)

# =========================================================================
# SLIDE 9: RESULTADOS Y SIMULACIÓN TÉRMICA
# =========================================================================
s9 = prs.slides.add_slide(blank_layout)
set_slide_background(s9, NAVY)
add_header(s9, "Resultados de Itinerarios y Cumplimiento Térmico")

g1_path = os.path.join(ASSETS, 'grafica_1_bfs_col.png')
if os.path.exists(g1_path):
    s9.shapes.add_picture(g1_path, Inches(0.8), Inches(1.8), width=Inches(4.8))

add_card(s9, Inches(5.9), Inches(1.8), Inches(6.6), Inches(5.0),
         "Tiempos de Acceso a Cadena de Frío", [
             ("P06 Desembarcadero Central:", "0.08 h (5 min) al frío — acceso urbano inmediato."),
             ("P03 San Miguel / P04 Asopespor:", "0.25 h y 0.40 h al acopio A01 en el río Meta."),
             ("P01 Neblinas / P02 Atarraya / P07 Soplaviento:", "0.38 a 0.48 h a través del muelle M03."),
             ("P05 Puerto Trujillo (Cuenca Crítica):", "2.20 h de travesía fluvial compleja, pero < 4.0 h de límite."),
             ("Cumplimiento Sanitario Regional:", "100% de las asociaciones pesqueras operan dentro del límite inocuo."),
             ("Mapa Interactivo Folium:", "Visualización web con capas de calor, rutas reales OSRM y GeoJSON."),
         ], border_color=ACCENT_BLUE)

# =========================================================================
# SLIDE 10: CONCLUSIONES E IMPACTO
# =========================================================================
s10 = prs.slides.add_slide(blank_layout)
set_slide_background(s10, NAVY)
add_header(s10, "Conclusiones del Proyecto e Impacto Socioeconómico")

add_card(s10, Inches(0.8), Inches(1.8), Inches(5.8), Inches(5.0),
         "Aportes en Estructuras de Datos", [
             ("Dominio Teórico-Práctico:", "Construcción integral de grafos dirigidos multimodales con listas de adyacencia y hashing."),
             ("Algoritmia Completa:", "Implementación desde cero de Dijkstra, Floyd-Warshall, Bellman-Ford, BFS, DFS y FLP."),
             ("Datos Reales de Campo:", "Integración de encuestas de pescadores, shapefiles hidrográficos y rutas OSRM."),
             ("Pruebas Unitarias Verificadas:", "34+ pruebas unitarias con pytest 100% verdes."),
         ], border_color=ACCENT_GREEN)

add_card(s10, Inches(7.0), Inches(1.8), Inches(5.5), Inches(5.0),
         "Impacto en la Región", [
             ("Seguridad Alimentaria:", "Erradicación del 100% de pérdidas críticas en la comercialización de cachama."),
             ("Sostenibilidad Ambiental:", "Preservación estricta de hábitats de desove mediante ruteo con exclusión."),
             ("Eficiencia Financiera:", "Ahorro de $10M COP mensuales demostrando la viabilidad de un único centro central en Puerto Gaitán."),
             ("Sustentabilidad Pesquera:", "Herramienta computacional escalable para la toma de decisiones públicas en el Meta."),
         ], border_color=ACCENT_BLUE)

# Guardar presentacion PPTX
prs.save(OUT_PPTX)
print("Presentacion PowerPoint guardada en:", OUT_PPTX)

# Conversion a PDF usando PowerPoint COM
try:
    import win32com.client
    ppt_app = win32com.client.DispatchEx("PowerPoint.Application")
    presentation = ppt_app.Presentations.Open(OUT_PPTX, WithWindow=False)
    presentation.SaveAs(OUT_PDF, 32) # 32 = ppSaveAsPDF
    presentation.Close()
    ppt_app.Quit()
    print("Presentacion PDF generada exitosamente en:", OUT_PDF)
except Exception as e:
    print("Aviso COM PowerPoint:", e)
