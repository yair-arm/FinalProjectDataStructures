# -*- coding: utf-8 -*-
"""
Genera la presentacion en PowerPoint (.pptx) para la exposicion del Proyecto Final
de Estructuras de Datos (Grafos) en Puerto Gaitan, Meta.
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
OUT_PPTX = os.path.join(BASE, 'Presentacion_Proyecto_Final_Grafos.pptx')
OUT_PDF = os.path.join(BASE, 'Presentacion_Proyecto_Final_Grafos.pdf')

prs = Presentation()
prs.slide_width = Inches(13.333)
prs.slide_height = Inches(7.5)
blank_layout = prs.slide_layouts[6]

# Paleta de colores
NAVY = RGBColor(15, 23, 42)       # #0F172A
CARD_BG = RGBColor(30, 41, 59)    # #1E293B
WHITE = RGBColor(255, 255, 255)
LIGHT_GRAY = RGBColor(241, 245, 249)
MUTED = RGBColor(148, 163, 184)
ACCENT_BLUE = RGBColor(56, 189, 248) # #38BDF8
ACCENT_GREEN = RGBColor(52, 211, 153) # #34D399
ACCENT_RED = RGBColor(248, 113, 113)  # #F87171
ACCENT_AMBER = RGBColor(251, 191, 36) # #FBBF24

def set_slide_background(slide, color):
    bg = slide.background
    fill = bg.fill
    fill.solid()
    fill.fore_color.rgb = color

def add_header(slide, title_text, category_text="ESTRUCTURAS DE DATOS • TERCER CORTE"):
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

# =========================================================================
# DIAPOSITIVA 1: PORTADA
# =========================================================================
s1 = prs.slides.add_slide(blank_layout)
set_slide_background(s1, NAVY)

# Logo Unillanos
logo_path = os.path.join(ASSETS, 'logo_unillanos_0.png')
if os.path.exists(logo_path):
    s1.shapes.add_picture(logo_path, Inches(1.0), Inches(1.0), width=Inches(1.3))

t_box = s1.shapes.add_textbox(Inches(2.6), Inches(0.9), Inches(9.8), Inches(2.8))
tf1 = t_box.text_frame
tf1.word_wrap = True
p = tf1.paragraphs[0]
p.text = "UNIVERSIDAD DE LOS LLANOS"
p.font.size = Pt(14)
p.font.bold = True
p.font.color.rgb = ACCENT_BLUE

p = tf1.add_paragraph()
p.text = "Facultad de Ciencias Básicas e Ingeniería — Ingeniería en Sistemas"
p.font.size = Pt(12)
p.font.color.rgb = MUTED
p.space_after = Pt(14)

p = tf1.add_paragraph()
p.text = "Modelado Mediante Grafos Dirigidos para la Optimización de Puntos de Acopio y Red de Frío Pesquera en Puerto Gaitán, Meta"
p.font.size = Pt(24)
p.font.bold = True
p.font.color.rgb = WHITE
p.space_after = Pt(10)

p = tf1.add_paragraph()
p.text = "Proyecto Final de Estructuras de Datos • Tercer Corte (Grafos)"
p.font.size = Pt(14)
p.font.color.rgb = ACCENT_AMBER

# Tarjeta de Integrantes
card_int = s1.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(1.0), Inches(4.3), Inches(11.3), Inches(2.3))
card_int.fill.solid()
card_int.fill.fore_color.rgb = CARD_BG
card_int.line.color.rgb = ACCENT_BLUE
card_int.line.width = Pt(1.5)

tf_int = card_int.text_frame
tf_int.word_wrap = True
tf_int.margin_left = Inches(0.35)
tf_int.margin_top = Inches(0.25)

p = tf_int.paragraphs[0]
p.text = "EQUIPO DE TRABAJO E INVESTIGACIÓN"
p.font.size = Pt(13)
p.font.bold = True
p.font.color.rgb = ACCENT_BLUE
p.space_after = Pt(10)

p = tf_int.add_paragraph()
p.text = "• Yair Armando Ospino Herrera — Código: 160005565"
p.font.size = Pt(13)
p.font.bold = True
p.font.color.rgb = WHITE
p.space_after = Pt(4)

p = tf_int.add_paragraph()
p.text = "• Harold Esteban Padilla Díaz — Código: 160005567"
p.font.size = Pt(13)
p.font.bold = True
p.font.color.rgb = WHITE
p.space_after = Pt(10)

p = tf_int.add_paragraph()
p.text = "Villavicencio, Meta — Noviembre de 2026"
p.font.size = Pt(11)
p.font.color.rgb = MUTED

# =========================================================================
# DIAPOSITIVA 2: PROBLEMÁTICA Y DATOS DE CAMPO
# =========================================================================
s2 = prs.slides.add_slide(blank_layout)
set_slide_background(s2, NAVY)
add_header(s2, "1. Contexto Territorial y Problemática Pesquera en Puerto Gaitán")

add_card(s2, Inches(0.8), Inches(1.6), Inches(5.6), Inches(5.2),
         "Realidad de la Pesca Artesanal",
         [("Cuenca de la Altillanura:", "Extensa red hídrica (ríos Meta, Manacacías, Yucao, Muco, Planas, Tomo, Vichada)."),
          ("Carencia de Infraestructura:", "Ausencia crítica de muelles adecuados, centros de acopio y red de frío en las riberas fluviales."),
          ("Tránsito Térmico Crítico:", "Los pescadores navegan en canoa bajo temperaturas de 27–30 °C. Sin hielo, el pescado sufre descomposición acelerada."),
          ("Impacto Socioeconómico:", "Pérdida de toneladas de producto ('M3 dañados'), depreciación del valor comercial y riesgos de inocuidad alimentaria.")],
         border_color=ACCENT_RED)

add_card(s2, Inches(6.8), Inches(1.6), Inches(5.7), Inches(5.2),
         "Diagnóstico de las 33 Encuestas Cartográficas",
         [("Datos de Campo Reales:", "Análisis y digitalización de 33 encuestas directas a pescadores de Puerto Gaitán y Puerto López."),
          ("Concentración en Confluencias:", "19 de 33 pescadores (57.6 %) convergen en la desembocadura de Bocas del Manacacías."),
          ("Punto Crítico Manacacías Medio:", "14 encuestas (42.4 %) reportan deterioro severo (D), destrucción de hábitat (H) y falta de muelle (M)."),
          ("Denuncia Explícita (Encuesta 31):", "'No tenemos muelles, no tenemos puntos de acopio, no tenemos red de frío, no tenemos lugares de venta.'"),
          ("Oportunidad Computacional:", "Estructurar esta cartografía en un modelo formal de grafos para optimizar la logística fluvial.")],
         border_color=ACCENT_BLUE)

# =========================================================================
# DIAPOSITIVA 3: FUNDAMENTO BIOLÓGICO (CACHAMA DE RÍO)
# =========================================================================
s3 = prs.slides.add_slide(blank_layout)
set_slide_background(s3, NAVY)
add_header(s3, "2. Fundamento Biológico: Cachama de Río (Colossoma macropomum)")

add_card(s3, Inches(0.8), Inches(1.6), Inches(3.7), Inches(5.2),
         "Cinética de Deterioro Térmico",
         [("Especie Representativa:", "Cachama de río, pilar de la pesca artesanal y piscicultura en la Orinoquía colombiana."),
          ("Sensibilidad a 28–30 °C:", "La exposición al calor tropical acelera la pérdida de ATP y desencadena un rigor mortis prematuro."),
          ("Proliferación Mesófila:", "Bacterias alterantes invaden el músculo estéril generando olores putrefactos y pérdida total de firmeza."),
          ("Estudios FAO & SciELO:", "Respaldan que el frío a 0 °C alarga la vida útil a 14 días; a temperatura ambiente el colapso ocurre en horas.")],
         border_color=ACCENT_AMBER)

add_card(s3, Inches(4.8), Inches(1.6), Inches(3.7), Inches(5.2),
         "Umbrales Operativos de Decisión",
         [("≤ 360 min (6.0 h) — ÓPTIMO:", "Máxima frescura comercial. El pez conserva textura firme, ojos convexos y nula carga bacteriana."),
          ("360–480 min (6–8 h) — ALERTA:", "Fase crítica. Inicio de proliferación microbiana. Pérdida parcial de calidad comercial."),
          ("> 480 min (8.0 h) — CRÍTICO:", "Deterioro irreversible. No apto para consumo humano ni transporte a Villavicencio o Bogotá."),
          ("Regla del Algoritmo:", "Todo trayecto que supere 360 min sin tocar un nodo de frío (F) entra en estado de alerta o rechazo.")],
         border_color=ACCENT_RED)

add_card(s3, Inches(8.8), Inches(1.6), Inches(3.7), Inches(5.2),
         "Impacto de la Red de Frío",
         [("Detención del Reloj Térmico:", "Al arribar a un centro con red de frío (F), la carga bacteriana se estabiliza a 0 °C."),
          ("Transporte Intermodal Seguro:", "Permite acondicionar el pescado en cajas con hielo para el tramo terrestre hacia Bogotá (110 km)."),
          ("Objetivo de los Algoritmos:", "Garantizar que todo punto de pesca alcance un centro A+F en menos de 360 minutos de viaje fluvial."),
          ("Respaldo Científico:", "Citado formalmente bajo directrices técnicas de la FAO [1] y ensayos en cachama [2].")],
         border_color=ACCENT_GREEN)

# =========================================================================
# DIAPOSITIVA 4: MODELADO FORMAL CON GRAFOS
# =========================================================================
s4 = prs.slides.add_slide(blank_layout)
set_slide_background(s4, NAVY)
add_header(s4, "3. Modelado Formal con Grafos Dirigidos y Ponderados")

add_card(s4, Inches(0.8), Inches(1.6), Inches(5.6), Inches(5.2),
         "Abstracción Matemática G = (V, E, w)",
         [("Vértices V (16 Nodos Tipificados):", "Puntos espaciales de la red categorizados según la convención del curso:"),
          ("  • P (Pesca):", "10 puntos (Yucao, Manacacías, Muco, Guarrojo, Planas, Tomo, etc.)"),
          ("  • D (Deterioro):", "2 nodos de alta criticidad (Manacacías Medio, Bocas)"),
          ("  • A / F (Acopio y Frío):", "Centros receptores con hielo y refrigeración"),
          ("  • M (Muelle):", "Puntos de desembarque formal"),
          ("  • V / Ciudad (Venta):", "Puerto Gaitán, Puerto López, Villavicencio, Bogotá"),
          ("Aristas Dirigidas E (24 Arcos):", "Conexiones fluviales (canoa ~15 km/h) y viales (camión)"),
          ("Pesos w(u, v):", "Tiempo de traslado en minutos + distancia en km")],
         border_color=ACCENT_BLUE)

add_card(s4, Inches(6.8), Inches(1.6), Inches(5.7), Inches(5.2),
         "Estructura de Datos Implementada en C++",
         [("Herencia de las Prácticas del Curso:", "Reutilización de clases plantilla POO desarrolladas en los laboratorios:"),
          ("  • List<T>:", "Lista enlazada simple genérica para almacenar vértices y aristas."),
          ("  • Edge<T>:", "Arista dirigida con peso en minutos, distancia km y medio."),
          ("  • Vertex<T>:", "Vértice con lista de adyacencia (connectedTo), color, distancia, predecesor."),
          ("  • Graph<T>:", "Grafo con métodos addEdge, addVertex, imprimirListaAdyacencia."),
          ("Eficiencia Algorítmica:", "Almacenamiento en lista de adyacencia con espacio O(|V| + |E|) y recorridos en tiempo lineal O(|V| + |E|)."),
          ("Interacción y Persistencia:", "Carga desde archivos planos txt/csv y menú interactivo de consola en C++.")],
         border_color=ACCENT_GREEN)

# =========================================================================
# DIAPOSITIVA 5: TOPOLOGÍA DE LA RED POR CAPAS
# =========================================================================
s5 = prs.slides.add_slide(blank_layout)
set_slide_background(s5, NAVY)
add_header(s5, "4. Arquitectura Topológica de la Red Logística")

# Imagen de la topologia
fig1_path = os.path.join(ASSETS, 'figura_1_topologia_grafo.png')
if os.path.exists(fig1_path):
    s5.shapes.add_picture(fig1_path, Inches(0.8), Inches(1.6), width=Inches(8.5))

add_card(s5, Inches(9.6), Inches(1.6), Inches(2.9), Inches(5.2),
         "Estructura en 4 Capas",
         [("Capa 1: Puntos Pesca", "10 subcuencas periféricas."),
          ("Capa 2: Confluencias", "Puntos críticos de deterioro reconvertidos a Centros A+F."),
          ("Capa 3: Cabeceras", "Desembarque en Puerto Gaitán y Puerto López."),
          ("Capa 4: Mercados", "Corredores viales hacia Villavicencio (193 km) y Bogotá (110 km adicionales)."),
          ("Flujo Logístico:", "Navegación aguas abajo -> consolidación con frío -> despacho intermodal.")],
         border_color=ACCENT_BLUE)

# =========================================================================
# DIAPOSITIVA 6: INCÓGNITA 1 (BFS)
# =========================================================================
s6 = prs.slides.add_slide(blank_layout)
set_slide_background(s6, NAVY)
add_header(s6, "5. Incógnita 1 (BFS): Centro de Frío Más Cercano en Saltos")

add_card(s6, Inches(0.8), Inches(1.6), Inches(4.5), Inches(5.2),
         "Algoritmo BFS (Búsqueda en Anchura)",
         [("Objetivo Operativo:", "Identificar desde cada punto de pesca el primer nodo equipado con frío (A/F/V) con el menor número de saltos topológicos."),
          ("Mecanismo en C++:", "Implementado con cola FIFO (std::queue), coloreado de vértices (blanco -> gris -> negro) y distancias enteras."),
          ("Reconstrucción de Ruta:", "Punteros al predecesor para obtener el camino mínimo y sumar el tiempo fluvial sin frío acumulado."),
          ("Diagnóstico Red Actual:", "Al no haber frío en origen ni en cuencas, BFS debe viajar hasta Puerto López:"),
          ("  • Caño Morroco: 3 saltos, 470 min (ALERTA)"),
          ("  • Alto Vichada: 4 saltos, 580 min (CRÍTICO)"),
          ("  • Río Planas: 4 saltos, 510 min (CRÍTICO)"),
          ("  • Cañalute: 4 saltos, 485 min (CRÍTICO)")],
         border_color=ACCENT_RED)

# Imagen de grafica 1
g1_path = os.path.join(ASSETS, 'grafica_1_bfs_col.png')
if os.path.exists(g1_path):
    s6.shapes.add_picture(g1_path, Inches(5.6), Inches(1.6), width=Inches(3.8))

add_card(s6, Inches(9.6), Inches(1.6), Inches(2.9), Inches(5.2),
         "Impacto Cuantitativo",
         [("Red Actual:", "Tiempo medio BFS = 373.0 min (> 6 h)."),
          ("6 de 10 puntos (60 %)", "superan el límite óptimo antes de recibir frío."),
          ("Red Optimizada:", "Tiempo medio BFS = 152.5 min."),
          ("Reducción Global:", "59.1 % de disminución en exposición térmica."),
          ("0 de 10 puntos", "en riesgo crítico bajo la red propuesta.")],
         border_color=ACCENT_GREEN)

# =========================================================================
# DIAPOSITIVA 7: INCÓGNITA 2 (DFS)
# =========================================================================
s7 = prs.slides.add_slide(blank_layout)
set_slide_background(s7, NAVY)
add_header(s7, "6. Incógnita 2 (DFS): Rutas Hacia Mercados y Riesgo de Deterioro")

add_card(s7, Inches(0.8), Inches(1.6), Inches(4.5), Inches(5.2),
         "Algoritmo DFS (Búsqueda en Profundidad)",
         [("Objetivo Operativo:", "Explorar exhaustivamente todas las rutas simples posibles desde cada punto P hasta los mercados finales (Gaitán, López, Villavo, Bogotá)."),
          ("Mecanismo en C++:", "Implementado mediante recursión con retroceso (backtracking) y pila de llamada del sistema."),
          ("Seguimiento Acumulado:", "Calcula tiempo total, distancia total y tiempo previo al primer nodo con frío."),
          ("Evaluación Fisiológica:", "Cada ruta se cataloga como Óptima (≤360 min), Alerta (360–480 min) o Deterioro Crítico (>480 min)."),
          ("Universo Evaluado:", "240 rutas simples hacia mercados regionales y nacionales.")],
         border_color=ACCENT_BLUE)

g2a_path = os.path.join(ASSETS, 'grafica_2a_dfs_col.png')
if os.path.exists(g2a_path):
    s7.shapes.add_picture(g2a_path, Inches(5.6), Inches(1.6), width=Inches(3.8))

add_card(s7, Inches(9.6), Inches(1.6), Inches(2.9), Inches(5.2),
         "Diagnóstico de las 240 Rutas",
         [("Red Actual:", "Solo 44 rutas (18.3 %) son óptimas."),
          ("147 rutas (61.3 %)", "terminan en deterioro crítico (> 8 horas)."),
          ("Red Optimizada:", "192 rutas (80.0 %) en estado óptimo."),
          ("Incremento Óptimo:", "+336 % de rutas viables."),
          ("Cero Rutas Críticas:", "0 de 240 rutas sufren descomposición (>480 min).")],
         border_color=ACCENT_GREEN)

# =========================================================================
# DIAPOSITIVA 8: PROPUESTA ÓPTIMA (3 CENTROS A+F)
# =========================================================================
s8 = prs.slides.add_slide(blank_layout)
set_slide_background(s8, NAVY)
add_header(s8, "7. Propuesta Óptima: Ubicación Estratégica de Centros de Acopio y Frío")

add_card(s8, Inches(0.8), Inches(1.6), Inches(3.7), Inches(5.2),
         "1. Bocas del Manacacías",
         [("Ubicación Estratégica:", "Confluencia de los ríos Manacacías, Yucao y Meta."),
          ("Demanda Cubierta:", "Atiende directamente al 57.6 % de los pescadores reportados en encuestas."),
          ("Intercepción Fluvial:", "Permite que las capturas de Yucao y Meta desembarquen en solo 105 min."),
          ("Equipamiento Propuesto:", "Muelle flotante, cuarto frío solar y planta de hielo en escamas.")],
         border_color=ACCENT_GREEN)

add_card(s8, Inches(4.8), Inches(1.6), Inches(3.7), Inches(5.2),
         "2. Manacacías Medio",
         [("Ubicación Estratégica:", "Sector intermedio del río Manacacías (nodo D_Manacacias_Medio)."),
          ("Demanda Cubierta:", "42.4 % de pescadores que denunciaban deterioro y ausencia de muelle."),
          ("Rescate de Cuencas Sur:", "Capta producto de Cañalute, Maiciana, Río Planas y Manacacías Sur."),
          ("Tiempo a Frío:", "Baja de 485 min a 255 min (47.4 % de reducción en exposición térmica).")],
         border_color=ACCENT_GREEN)

add_card(s8, Inches(8.8), Inches(1.6), Inches(3.7), Inches(5.2),
         "3. Confluencia Río Muco / Meta",
         [("Ubicación Estratégica:", "Desembocadura del río Muco sobre el río Meta."),
          ("Rescate Cuencas Lejanas:", "Salva la producción más aislada del extremo oriental: Caño Morroco y Alto Vichada."),
          ("Reducción Histórica:", "Caño Morroco pasa de 470 min a 170 min (63.8 % de mejora)."),
          ("Seguridad Logística:", "Evita que las rutas largas superen las 8 horas antes de tocar muelle.")],
         border_color=ACCENT_GREEN)

# =========================================================================
# DIAPOSITIVA 9: RESULTADOS CUANTITATIVOS Y REGRESIÓN
# =========================================================================
s9 = prs.slides.add_slide(blank_layout)
set_slide_background(s9, NAVY)
add_header(s9, "8. Validación Cuantitativa y Modelo Lineal Predictivo")

g2b_path = os.path.join(ASSETS, 'grafica_2b_regresion_col.png')
if os.path.exists(g2b_path):
    s9.shapes.add_picture(g2b_path, Inches(0.8), Inches(1.6), width=Inches(4.8))

add_card(s9, Inches(6.0), Inches(1.6), Inches(6.5), Inches(5.2),
         "Síntesis Metrológica y Regresión Lineal",
         [("Regresión Red Actual:", "t = 2.06 · d + 43.8 min  (R² = 0.8851). Dispersión debida a la mezcla de canoa fluvial con carretera a Puerto López."),
          ("Regresión Red Optimizada:", "t = 3.99 · d + 0.90 min  (R² = 0.9998). Ajuste determinista lineal casi perfecto."),
          ("Significado Físico de la Pendiente:", "m = 3.99 min/km equivale con rigor al inverso de la velocidad media fluvial en canoa: 1 / (15.04 km/h)."),
          ("Herramienta Predictiva:", "Permite calcular el radio máximo fluvial admisible antes de exceder las 6 h (360 min) de la cachama:"),
          ("  d_máx = (360 − 0.90) / 3.99 ≈ 90.0 km", "(radio de cobertura seguro para cada nuevo centro de acopio)."),
          ("Resumen de Mejoras Globales:", "Tiempo medio BFS: 373 min -> 152.5 min (-59.1 %). Rutas críticas DFS: 147 -> 0 (-100 %).")],
         border_color=ACCENT_BLUE)

# =========================================================================
# DIAPOSITIVA 10: CONCLUSIONES Y DEMOSTRACIÓN
# =========================================================================
s10 = prs.slides.add_slide(blank_layout)
set_slide_background(s10, NAVY)
add_header(s10, "9. Conclusiones y Demostración en Vivo")

add_card(s10, Inches(0.8), Inches(1.6), Inches(5.6), Inches(5.2),
         "Conclusiones del Proyecto",
         [("1. Estructuración Rigurosa:", "Se transformaron 33 encuestas cualitativas en un grafo dirigido de 16 vértices y 24 aristas con listas de adyacencia en C++."),
          ("2. Eficacia de BFS:", "Comprobó que la Red Actual dejaba al 60 % de puntos en deterioro térmico, mientras la Red Optimizada reduce el tiempo en 59.1 % sin puntos en riesgo."),
          ("3. Poder Explicativo de DFS:", "Demostró un incremento de rutas viables del 18.3 % al 80.0 %, erradicando las 147 rutas con pérdida comercial."),
          ("4. Impacto en Ingeniería de Sistemas:", "Evidencia cómo las estructuras de datos y algoritmos fundamentales resuelven problemáticas complejas reales en el territorio llanero.")],
         border_color=ACCENT_BLUE)

add_card(s10, Inches(6.8), Inches(1.6), Inches(5.7), Inches(5.2),
         "Demostración y Recursos Disponibles",
         [("Menú Interactivo de Consola (C++):", "Compilado con g++ -std=c++17. Permite navegar adyacencias, ejecutar BFS y DFS dinámicos."),
          ("Visualizador Gráfico Interactivo:", "visualizador_grafo.html con física en tiempo real, cambio de escenario y trazado de rutas."),
          ("Informe Científico Doble Columna:", "Elaborado bajo normativa IEEE y rúbrica oficial de laboratorios Unillanos."),
          ("Preguntas y Discusión:", "¡Muchas gracias por su atención! Quedamos atentos a sus preguntas y comentarios.")],
         border_color=ACCENT_GREEN)

prs.save(OUT_PPTX)
print("Presentación PPTX generada exitosamente en:", OUT_PPTX)

# Exportar a PDF via PowerPoint COM
try:
    import win32com.client as win32
    ppt = win32.Dispatch('PowerPoint.Application')
    pres = ppt.Presentations.Open(OUT_PPTX)
    pres.SaveAs(OUT_PDF, FileFormat=32)
    pres.Close()
    ppt.Quit()
    print("Presentación PDF exportada exitosamente en:", OUT_PDF)
except Exception as e:
    print("Exportación de PPTX a PDF omitida o fallida:", e)
