# -*- coding: utf-8 -*-
"""
Generador del Informe IEEE Doble Columna (4 paginas simetricas)
Proyecto Final de Estructuras de Datos (Grafos) - Universidad de los Llanos
Sigue la rubrica oficial (RUBRICA PARA INFORMES 2025-II) y DIRECTRICES_Y_REGLAS_INFORMES.
"""
import os
from xml.sax.saxutils import escape
import docx
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_ALIGN_VERTICAL
from docx.enum.section import WD_SECTION_START
from docx.oxml import parse_xml
from docx.oxml.ns import nsdecls, qn

BASE = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
ASSETS = os.path.join(BASE, 'Assets')
OUT_DOCX = os.path.join(BASE, 'Informe_Proyecto_Final_Grafos.docx')

FONT = 'Times New Roman'
BLACK = RGBColor(0, 0, 0)
M_NS = 'http://schemas.openxmlformats.org/officeDocument/2006/math'


def r(t):
    return f'<m:r><m:t xml:space="preserve">{escape(t)}</m:t></m:r>'


def rp(t):
    return f'<m:r><m:rPr><m:sty m:val="p"/></m:rPr><m:t xml:space="preserve">{escape(t)}</m:t></m:r>'


def sub(base, s):
    return f'<m:sSub><m:e>{base}</m:e><m:sub>{s}</m:sub></m:sSub>'


def sup(base, s):
    return f'<m:sSup><m:e>{base}</m:e><m:sup>{s}</m:sup></m:sSup>'


def frac(n, d):
    return f'<m:f><m:num>{n}</m:num><m:den>{d}</m:den></m:f>'


def absval(inner):
    return f'<m:d><m:dPr><m:begChr m:val="|"/><m:endChr m:val="|"/></m:dPr><m:e>{inner}</m:e></m:d>'


doc = docx.Document()
st = doc.styles['Normal']
st.font.name = FONT
st.font.size = Pt(9)
st.font.color.rgb = BLACK
st.element.rPr.rFonts.set(qn('w:eastAsia'), FONT)

sec0 = doc.sections[0]
sec0.top_margin = sec0.bottom_margin = Inches(0.68)
sec0.left_margin = sec0.right_margin = Inches(0.70)

hp = sec0.header.paragraphs[0]
hp.alignment = WD_ALIGN_PARAGRAPH.RIGHT
hr = hp.add_run('Estructuras de Datos — Proyecto Final de Grafos: Logística Pesquera Puerto Gaitán, Meta')
hr.font.name = FONT
hr.font.size = Pt(8)
hr.font.italic = True
hr.font.color.rgb = RGBColor(90, 90, 90)


def run_fmt(run, size=9, bold=False, italic=False):
    run.font.name = FONT
    run.font.size = Pt(size)
    run.font.bold = bold
    run.font.italic = italic
    run.font.color.rgb = BLACK
    return run


def no_borders(table):
    table._tbl.tblPr.append(parse_xml(
        f'<w:tblBorders {nsdecls("w")}><w:top w:val="none"/><w:left w:val="none"/>'
        f'<w:bottom w:val="none"/><w:right w:val="none"/><w:insideH w:val="none"/>'
        f'<w:insideV w:val="none"/></w:tblBorders>'))


def cell_margins(cell, t=12, b=12, l=18, rr=18):
    cell._tc.get_or_add_tcPr().append(parse_xml(
        f'<w:tcMar {nsdecls("w")}><w:top w:w="{t}" w:type="dxa"/><w:left w:w="{l}" w:type="dxa"/>'
        f'<w:bottom w:w="{b}" w:type="dxa"/><w:right w:w="{rr}" w:type="dxa"/></w:tcMar>'))


def shade(cell, hexcolor):
    cell._tc.get_or_add_tcPr().append(parse_xml(f'<w:shd {nsdecls("w")} w:val="clear" w:color="auto" w:fill="{hexcolor}"/>'))


def set_section_cols(sec, n_cols=2, space=340):
    sec.top_margin = sec.bottom_margin = Inches(0.68)
    sec.left_margin = sec.right_margin = Inches(0.70)
    cols = sec._sectPr.xpath('./w:cols')
    if cols:
        cols[0].set(qn('w:num'), str(n_cols))
        if n_cols > 1:
            cols[0].set(qn('w:space'), str(space))
    else:
        if n_cols > 1:
            sec._sectPr.append(parse_xml(f'<w:cols {nsdecls("w")} w:num="{n_cols}" w:space="{space}"/>'))
        else:
            sec._sectPr.append(parse_xml(f'<w:cols {nsdecls("w")} w:num="1"/>'))


# =========================================================================
# ENCABEZADO INSTITUCIONAL (1 COLUMNA)
# =========================================================================
ht = doc.add_table(rows=1, cols=2)
ht.alignment = WD_TABLE_ALIGNMENT.CENTER
ht.autofit = False
no_borders(ht)
c_logo, c_info = ht.cell(0, 0), ht.cell(0, 1)
c_logo.width, c_info.width = Inches(1.0), Inches(6.0)
for c in (c_logo, c_info):
    c.vertical_alignment = WD_ALIGN_VERTICAL.CENTER

pl = c_logo.paragraphs[0]
pl.alignment = WD_ALIGN_PARAGRAPH.CENTER
pl.add_run().add_picture(os.path.join(ASSETS, 'logo_unillanos_0.png'), width=Inches(0.72))

pi = c_info.paragraphs[0]
pi.alignment = WD_ALIGN_PARAGRAPH.CENTER
run_fmt(pi.add_run('UNIVERSIDAD DE LOS LLANOS'), 11, bold=True)
pi.add_run().add_break()
run_fmt(pi.add_run('Facultad de Ciencias Básicas e Ingeniería — Ingeniería en Sistemas'), 9)
pi.add_run().add_break()
run_fmt(pi.add_run('Estructuras de Datos (Tercer Corte) — Proyecto Final de Teoría de Grafos'), 8.5, italic=True)

pt = doc.add_paragraph()
pt.alignment = WD_ALIGN_PARAGRAPH.CENTER
pt.paragraph_format.space_before = Pt(3)
pt.paragraph_format.space_after = Pt(2)
run_fmt(pt.add_run(
    'MODELADO MEDIANTE GRAFOS DIRIGIDOS PARA LA UBICACIÓN ÓPTIMA DE CENTROS DE ACOPIO Y RED DE FRÍO '
    'EN LA PESQUERÍA ARTESANAL DE PUERTO GAITÁN, META'
), 11.5, bold=True)


def centered(text_runs, before=1, after=1, spacing=1.04):
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_before = Pt(before)
    p.paragraph_format.space_after = Pt(after)
    p.paragraph_format.line_spacing = spacing
    for i, (t, size, b, it) in enumerate(text_runs):
        if i:
            p.add_run().add_break()
        run_fmt(p.add_run(t), size, b, it)
    return p


centered([
    ('Yair Armando Ospino Herrera (160005565)', 9, True, False),
    ('Harold Esteban Padilla Díaz (160005567)', 9, True, False),
], after=2)
centered([
    ('Facultad de Ciencias Básicas e Ingeniería — Ingeniería en Sistemas', 8.5, False, True),
    ('Universidad de los Llanos, Villavicencio, Colombia', 8.5, False, True),
], after=3)

# Encabezado Resumen centrado en negrita (Directriz 1.6)
p_res_hdr = doc.add_paragraph()
p_res_hdr.alignment = WD_ALIGN_PARAGRAPH.CENTER
p_res_hdr.paragraph_format.space_before = Pt(1)
p_res_hdr.paragraph_format.space_after = Pt(1)
run_fmt(p_res_hdr.add_run('Resumen'), 9.5, bold=True)

at = doc.add_table(rows=1, cols=1)
at.alignment = WD_TABLE_ALIGNMENT.CENTER
at.autofit = False
no_borders(at)
cell_a = at.cell(0, 0)
cell_a.width = Inches(7.0)
shade(cell_a, 'F4F6F8')
cell_margins(cell_a, 14, 14, 24, 24)

pa_c = cell_a.paragraphs[0]
pa_c.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
pa_c.paragraph_format.space_after = Pt(2)
pa_c.paragraph_format.line_spacing = 1.04
run_fmt(pa_c.add_run(
    'Este proyecto modela mediante grafos dirigidos ponderados la logística fluvial-terrestre de la pesca artesanal de '
    'cachama de río en Puerto Gaitán (Meta) para determinar la ubicación estratégica de centros de acopio y refrigeración. '
    'A partir de 33 mapas encuestados a pescadores locales y la cartografía de sus subcuencas, se construyó un TAD Grafo '
    'en C++ con listas de adyacencia (16 vértices y 24 aristas) evaluando dos incógnitas mediante búsqueda en anchura '
    '(BFS) y búsqueda en profundidad (DFS) sobre 240 rutas simples hacia Puerto Gaitán, Villavicencio y Bogotá. En la red '
    'actual sin frío en cuencas, el tiempo medio sin refrigeración fue 373.0 min (6/10 zonas en riesgo y 61.3 % de rutas '
    'en deterioro crítico > 480 min). Al ubicar tres centros A+F en Bocas del Manacacías, Manacacías Medio y Río Muco, el '
    'tiempo medio bajó a 152.5 min (-59.1 %), eliminando el deterioro crítico (0/240 rutas) y asegurando el 80.0 % de rutas '
    'en frescura óptima (R² = 0.9998 en el tramo fluvial).'
), 8.5)

pa_kw = cell_a.add_paragraph()
pa_kw.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
pa_kw.paragraph_format.space_before = Pt(1)
pa_kw.paragraph_format.space_after = Pt(0)
pa_kw.paragraph_format.line_spacing = 1.04
run_fmt(pa_kw.add_run('Palabras clave— '), 8.5, bold=True, italic=True)
run_fmt(pa_kw.add_run(
    'Búsqueda en anchura (BFS), búsqueda en profundidad (DFS), cachama de río, cadena de frío, '
    'grafos dirigidos, lista de adyacencia, Puerto Gaitán.'
), 8.5)


def para(content, *more_content, before=0, after=2.2, line_spacing=1.04, indent=0.14):
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    p.paragraph_format.space_before = Pt(before)
    p.paragraph_format.space_after = Pt(after)
    p.paragraph_format.line_spacing = line_spacing
    p.paragraph_format.first_line_indent = Inches(indent)
    if more_content:
        items = [content] + list(more_content)
    elif isinstance(content, list):
        items = content
    else:
        items = [content]
    for item in items:
        if isinstance(item, str):
            run_fmt(p.add_run(item), 9)
        elif isinstance(item, tuple) and item[0] == 'm':
            p._p.append(parse_xml(f'<m:oMath xmlns:m="{M_NS}">{item[1]}</m:oMath>'))
        elif isinstance(item, tuple) and item[0] == 'b':
            run_fmt(p.add_run(item[1]), 9, bold=True)
        elif isinstance(item, tuple) and item[0] == 'i':
            run_fmt(p.add_run(item[1]), 9, italic=True)
    return p


def heading(text, before=4, after=2):
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_before = Pt(before)
    p.paragraph_format.space_after = Pt(after)
    p.paragraph_format.keep_with_next = True
    run_fmt(p.add_run(text.upper()), 9.5, bold=True)
    return p


EQ = [0]


def equation(omml):
    EQ[0] += 1
    t = doc.add_table(rows=1, cols=2)
    t.alignment = WD_TABLE_ALIGNMENT.CENTER
    t.autofit = False
    no_borders(t)
    ce, cn = t.cell(0, 0), t.cell(0, 1)
    ce.width, cn.width = Inches(3.0), Inches(0.35)
    for c in (ce, cn):
        c.vertical_alignment = WD_ALIGN_VERTICAL.CENTER
        cell_margins(c, 1, 1, 0, 0)
    pe = ce.paragraphs[0]
    pe.alignment = WD_ALIGN_PARAGRAPH.CENTER
    pe.paragraph_format.space_before = Pt(1)
    pe.paragraph_format.space_after = Pt(1)
    pe._p.append(parse_xml(f'<m:oMathPara xmlns:m="{M_NS}"><m:oMath>{omml}</m:oMath></m:oMathPara>'))
    pn = cn.paragraphs[0]
    pn.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    run_fmt(pn.add_run(f'({EQ[0]})'), 9)


# =========================================================================
# PÁGINA 1 (PARTE INFERIOR): I. INTRODUCCIÓN (2 COLUMNAS)
# =========================================================================
sec_p1 = doc.add_section(WD_SECTION_START.CONTINUOUS)
set_section_cols(sec_p1, n_cols=2, space=340)

heading('I.  Introducción')

para('La logística de distribución fluvial puede formalizarse mediante un grafo dirigido ponderado ',
     ('m', r('G = (V, E, w)')),
     ', donde ', ('m', r('V')), ' representa los vértices espaciales (puntos de pesca, acopio, deterioro y mercados) y ',
     ('m', r('E')), ' las conexiones navegables o viales con peso ', ('m', r('w(u,v)')),
     ' igual al tiempo de tránsito en minutos [1]. Al representarse mediante listas de adyacencia, los algoritmos '
     'de búsqueda en anchura (BFS) y búsqueda en profundidad (DFS) operan en complejidad lineal respecto al tamaño '
     'de la red [1]:')
equation(r('T(V,E) = O(|V| + |E|)'))

para('Para evaluar el deterioro microbiológico de la cachama de río (', ('i', 'Colossoma macropomum'),
     ') a temperatura ambiente tropical (', ('m', r('27 ± 3 °C')),
     '), el tiempo acumulado sin cadena de frío ', ('m', sub(r('t'), rp('sf'))),
     ' se define sumando los pesos ', ('m', r('w(u,v)')),
     ' hasta alcanzar el primer vértice equipado con refrigeración (', ('m', sub(r('F'), rp('1'))),
     '), mientras que la reducción porcentual de exposición al comparar escenarios se cuantifica por:')
equation(sub(r('t'), rp('sf')) + rp(' = ∑ ') + r('w(u,v)  ,   Δ') + sub(r('t'), rp('%')) + rp(' = ') +
         frac(sub(r('t'), rp('act')) + rp(' − ') + sub(r('t'), rp('opt')), sub(r('t'), rp('act'))) + rp(' × 100 %'))

para('En cuanto al estado del arte, la gestión pesquera artesanal ha evolucionado desde registros empíricos '
     'aislados en libreta hasta sistemas de apoyo espacial (SIMA-DSS) y optimización por teoría de grafos en redes '
     'agroalimentarias de cadena de frío [2]. Estudios de la FAO y ensayos cinéticos en cachama demuestran que, sin '
     'hielo, la pérdida de ATP y proliferación de bacterias mesófilas limitan la frescura óptima a 6 h (360 min) y '
     'producen deterioro comercial severo tras 8 h (480 min), mientras que el enfriamiento a 0 °C extiende la vida '
     'útil hasta 14 días [3], [4].')

para('Entre las restricciones del modelo destacan: (i) las 33 encuestas cartográficas aportan topología y '
     'frecuencia cualitativa de uso, mas no volúmenes diarios en kilogramos ni cronometrajes por pescador; (ii) las '
     'distancias fluviales se estimaron sobre la cartografía de subcuencas del Meta asumiendo velocidad media de '
     'canoa artesanal ',
     ('m', sub(r('v'), rp('f')) + rp(' = 15 ± 3 km/h')),
     ' (incertidumbre relativa del ', ('m', rp('±20 %')),
     '); y (iii) la temperatura ambiental fluvial se asume constante sin considerar variaciones estacionales de '
     'sequía o creciente [5].')

para('En consecuencia, este estudio persigue cuatro objetivos específicos: (i) consolidar en un grafo dirigido '
     'mediante lista de adyacencia la red pesquera reportada en Puerto Gaitán; (ii) resolver con BFS la distancia en '
     'saltos y tiempo mínimo hacia el primer punto de frío (Incógnita 1); (iii) enumerar con DFS las rutas completas '
     'hacia mercados evaluando riesgo bacteriano en cachama (Incógnita 2); y (iv) cuantificar la mejora al ubicar '
     'tres centros estratégicos de acopio y refrigeración.')

# =========================================================================
# PÁGINA 2: FIGURA 1 (1 COL) -> II. SECCIÓN EXPERIMENTAL + III. RESULTADOS (2 COLS)
# =========================================================================
sec_p2_top = doc.add_section(WD_SECTION_START.NEW_PAGE)
set_section_cols(sec_p2_top, n_cols=1)

p_fig1 = doc.add_paragraph()
p_fig1.alignment = WD_ALIGN_PARAGRAPH.CENTER
p_fig1.paragraph_format.space_before = Pt(2)
p_fig1.paragraph_format.space_after = Pt(1)
p_fig1.paragraph_format.keep_with_next = True
p_fig1.add_run().add_picture(os.path.join(ASSETS, 'figura_1_topologia_grafo.png'), width=Inches(6.95))

cap_fig1 = doc.add_paragraph()
cap_fig1.alignment = WD_ALIGN_PARAGRAPH.CENTER
cap_fig1.paragraph_format.space_before = Pt(1)
cap_fig1.paragraph_format.space_after = Pt(3)
run_fmt(cap_fig1.add_run(
    'Figura 1. Topología por capas del grafo dirigido G = (V, E) (16 vértices y 24 aristas) que integra los '
    'puntos de pesca (P), nodos críticos propuestos como centros A+F, cabeceras municipales y mercados regionales/nacionales.'
), 8.5, italic=True)

sec_p2_bot = doc.add_section(WD_SECTION_START.CONTINUOUS)
set_section_cols(sec_p2_bot, n_cols=2, space=340)

heading('II.  Sección Experimental')

para('Para la construcción del sistema computacional se emplearon las 33 encuestas cartográficas del proyecto '
     'pesquero en Puerto Gaitán y Puerto López, los mapas hidrológicos de subcuencas de la plataforma SIMA-DSS '
     '(ríos Manacacías, Yucao, Meta, Muco, Guarrojo, Planas, Tomo y Vichada), las distancias viales oficiales del '
     'corredor Puerto Gaitán–Villavicencio–Bogotá, el compilador g++ con estándar C++17 reutilizando los TAD '
     'List<T>, Vertex<T>, Edge<T> y Graph<T> desarrollados en clase con contenedores STL (queue, map, set, vector), y '
     'el entorno Python con Matplotlib para el procesamiento gráfico y regresión lineal [1], [5].')

para('El procedimiento metodológico se ejecutó en cuatro etapas secuenciales. Primero, se tabularon las 33 hojas '
     'escaneadas en formato CSV identificando localidades, cuencas y etiquetas operativas (P: pesca, A: acopio, '
     'D: deterioro, H: destrucción de hábitat, M: muelle, F: red de frío, V: venta). Segundo, se sintetizaron 16 '
     'vértices representativos y 24 aristas dirigidas ponderadas en minutos de viaje fluvial en canoa y terrestre en '
     'camión, configurando la topología mostrada en la Figura 1. Tercero, se implementó en C++ la impresión de la '
     'lista de adyacencia, el algoritmo BFS (con colores blanco, gris y negro) para hallar el nodo con frío más '
     'cercano en saltos, y el algoritmo DFS recursivo con retroceso para enumerar todas las rutas simples hasta los '
     'mercados finales. Finalmente, se contrastaron dos escenarios: la Red Actual (sin infraestructura en cuencas, '
     'donde solo Puerto López, Villavicencio y Bogotá poseen frío estable) y la Red Optimizada (instalando tres '
     'centros A+F estratégicos en Bocas del Manacacías, Manacacías Medio y Río Muco, más cabecera en Puerto Gaitán).')

heading('III.  Resultados y Análisis')

para('En la clasificación formal de variables, las variables directas independientes fueron la topología hidrográfica '
     'reportada, las frecuencias de mención por cuenca (N = 33 encuestas), las distancias viales terrestres '
     '(Puerto Gaitán–Puerto López 110 km, Puerto Gaitán–Villavicencio 193 km, Villavicencio–Bogotá 110 km) y las '
     'longitudes fluviales medidas sobre mapa (d). Las variables directas dependientes fueron la presencia de '
     'etiquetas D/H y la ausencia de infraestructura A/M/F. Como variables indirectas se calcularon el tiempo fluvial '
     'estimado (', ('m', r('t = d / ') + sub(r('v'), rp('f'))), '), el número de saltos BFS, el tiempo acumulado sin '
     'frío (', ('m', sub(r('t'), rp('sf'))), '), la clasificación microbiológica de rutas DFS y la reducción ',
     ('m', r('Δ') + sub(r('t'), rp('%'))), '.')

para('La propagación de incertidumbre instrumental y cartográfica para cada tramo fluvial en canoa (',
     ('m', sub(r('v'), rp('f')) + rp(' = 15 ± 3 km/h')), ') se determinó mediante derivación parcial de la '
     'velocidad promedio respecto al tiempo:')
equation(frac(r('δ') + sub(r('t'), rp('f')), sub(r('t'), rp('f'))) + rp(' = ') +
         frac(r('δ') + sub(r('v'), rp('f')), sub(r('v'), rp('f'))) + rp(' = ') +
         frac(rp('3 km/h'), rp('15 km/h')) + rp(' = ±20.0 %'))

para('Esta cota implica que un trayecto estimado de 470 min en condiciones nominales puede oscilar realmente entre '
     '376 y 564 min según la corriente del río y la carga de la embarcación, acelerando o mitigando el ingreso a la '
     'zona de deterioro severo (> 480 min).')

# =========================================================================
# PÁGINA 3: GRÁFICA 1 (1 COL) -> TABLA 1 (COL 1) Y TABLA 2 + ANALISIS (COL 2)
# =========================================================================
sec_p3_top = doc.add_section(WD_SECTION_START.NEW_PAGE)
set_section_cols(sec_p3_top, n_cols=1)

p_g1 = doc.add_paragraph()
p_g1.alignment = WD_ALIGN_PARAGRAPH.CENTER
p_g1.paragraph_format.space_before = Pt(2)
p_g1.paragraph_format.space_after = Pt(1)
p_g1.paragraph_format.keep_with_next = True
p_g1.add_run().add_picture(os.path.join(ASSETS, 'grafica_1_bfs_y_encuestas.png'), width=Inches(6.95))

cap_g1 = doc.add_paragraph()
cap_g1.alignment = WD_ALIGN_PARAGRAPH.CENTER
cap_g1.paragraph_format.space_before = Pt(1)
cap_g1.paragraph_format.space_after = Pt(3)
run_fmt(cap_g1.add_run(
    'Gráfica 1. (a) Comparativa de tiempos sin cadena de frío hasta el primer centro A+F por BFS en Red Actual vs. '
    'Red Optimizada respecto a los umbrales de frescura de la cachama; (b) Frecuencia de reporte en las 33 encuestas.'
), 8.5, italic=True)

sec_p3_bot = doc.add_section(WD_SECTION_START.CONTINUOUS)
set_section_cols(sec_p3_bot, n_cols=2, space=340)

para('La Tabla 1 consolida la solución completa de la Incógnita 1 (BFS) ejecutada en C++ sobre los diez puntos de '
     'pesca evaluados, incluyendo la incertidumbre ', ('m', r('±20 %')), ' y el porcentaje de reducción obtenido.')

rows_t1 = [
    ('Caño Morroco', '3', '470 ± 94', '1', '170 ± 34', '63.8 %'),
    ('Alto Vichada', '4', '580 ± 116', '2', '305 ± 61', '47.4 %'),
    ('Río Planas', '4', '510 ± 102', '2', '235 ± 47', '53.9 %'),
    ('Río Guarrojo', '3', '395 ± 79', '1', '120 ± 24', '69.6 %'),
    ('Río Muco', '3', '370 ± 74', '1*', '0 ± 0', '100.0 %'),
    ('Meta / Ventura', '2', '260 ± 52', '1', '130 ± 26', '50.0 %'),
    ('Cañalute / Maic.', '4', '485 ± 97', '2', '255 ± 51', '47.4 %'),
    ('Manacacías Sur', '3', '345 ± 69', '1', '115 ± 23', '66.7 %'),
    ('Río Yucao', '2', '225 ± 45', '1', '105 ± 21', '53.3 %'),
    ('Chaviva / P. Lóp.', '1', '90 ± 18', '1', '90 ± 18', '0.0 %'),
]
heads_t1 = ['Punto (P)', 'S.Act', 't_sf Act [m]', 'S.Opt', 't_sf Opt [m]', 'Mejora']
w_t1 = [0.88, 0.34, 0.66, 0.34, 0.66, 0.48]

tb1 = doc.add_table(rows=len(rows_t1) + 1, cols=6)
tb1.alignment = WD_TABLE_ALIGNMENT.CENTER
tb1.autofit = False
tb1._tbl.tblPr.append(parse_xml(
    f'<w:tblBorders {nsdecls("w")}><w:top w:val="single" w:sz="8" w:space="0" w:color="000000"/>'
    f'<w:left w:val="none"/><w:bottom w:val="single" w:sz="8" w:space="0" w:color="000000"/>'
    f'<w:right w:val="none"/><w:insideH w:val="single" w:sz="4" w:space="0" w:color="999999"/>'
    f'<w:insideV w:val="none"/></w:tblBorders>'))

for i in range(len(rows_t1) + 1):
    r_obj = tb1.rows[i]
    r_obj._tr.get_or_add_trPr().append(parse_xml(f'<w:cantSplit {nsdecls("w")}/>'))
    for j in range(6):
        c = tb1.cell(i, j)
        c.width = Inches(w_t1[j])
        cell_margins(c, 4, 4, 3, 3)
        c.vertical_alignment = WD_ALIGN_VERTICAL.CENTER
        pc = c.paragraphs[0]
        pc.alignment = WD_ALIGN_PARAGRAPH.LEFT if j == 0 and i > 0 else WD_ALIGN_PARAGRAPH.CENTER
        pc.paragraph_format.space_after = Pt(0)
        if i == 0:
            shade(c, 'E6E6E6')
            run_fmt(pc.add_run(heads_t1[j]), 7.6, bold=True)
        else:
            run_fmt(pc.add_run(rows_t1[i - 1][j]), 7.6)

cap_t1 = doc.add_paragraph()
cap_t1.alignment = WD_ALIGN_PARAGRAPH.CENTER
cap_t1.paragraph_format.space_before = Pt(2)
cap_t1.paragraph_format.space_after = Pt(3)
run_fmt(cap_t1.add_run('Tabla 1. Respuesta de la Incógnita 1 (BFS): saltos y tiempo sin frío hasta el primer centro A+F (*Muco pasa a ser nodo A+F).'), 7.8, italic=True)

para('Cualitativamente, en la Red Actual 6 de 10 puntos de pesca superan el umbral óptimo de 360 min y 3 superan '
     'los 480 min antes de acceder a refrigeración en Puerto López, obligando a transitar en canoa hasta la cabecera '
     'de Puerto Gaitán y luego por carretera sin hielo. Al activar los 3 centros A+F propuestos (elegidos por '
     'concentrar 19, 14 y 7 reportes en encuestas y mayor centralidad fluvial), el tiempo medio desciende de 373.0 min '
     'a 152.5 min (mejora global de 59.1 %) y el 100 % de los puntos alcanza frío en 1 o 2 saltos debajo de 305 min.')

para('La Tabla 2 sintetiza la resolución de la Incógnita 2 (DFS) evaluando la totalidad de las 240 rutas simples '
     'posibles desde las cuencas hacia Puerto Gaitán, Villavicencio y Bogotá.')

rows_t2 = [
    ('Óptimo (≤ 360 min)', '44', '18.3 %', '192', '80.0 %', '+336.4 %'),
    ('Alerta (360–480 min)', '49', '20.4 %', '48', '20.0 %', '-2.0 %'),
    ('Crítico (> 480 min)', '147', '61.3 %', '0', '0.0 %', '-100.0 %'),
    ('Total Rutas DFS', '240', '100.0 %', '240', '100.0 %', '—'),
]
heads_t2 = ['Estado Cachama', 'Act.', '% Act.', 'Opt.', '% Opt.', 'Variación']
w_t2 = [1.06, 0.36, 0.44, 0.36, 0.44, 0.56]

tb2 = doc.add_table(rows=len(rows_t2) + 1, cols=6)
tb2.alignment = WD_TABLE_ALIGNMENT.CENTER
tb2.autofit = False
tb2._tbl.tblPr.append(parse_xml(
    f'<w:tblBorders {nsdecls("w")}><w:top w:val="single" w:sz="8" w:space="0" w:color="000000"/>'
    f'<w:left w:val="none"/><w:bottom w:val="single" w:sz="8" w:space="0" w:color="000000"/>'
    f'<w:right w:val="none"/><w:insideH w:val="single" w:sz="4" w:space="0" w:color="999999"/>'
    f'<w:insideV w:val="none"/></w:tblBorders>'))

for i in range(len(rows_t2) + 1):
    r_obj = tb2.rows[i]
    r_obj._tr.get_or_add_trPr().append(parse_xml(f'<w:cantSplit {nsdecls("w")}/>'))
    for j in range(6):
        c = tb2.cell(i, j)
        c.width = Inches(w_t2[j])
        cell_margins(c, 4, 4, 3, 3)
        c.vertical_alignment = WD_ALIGN_VERTICAL.CENTER
        pc = c.paragraphs[0]
        pc.alignment = WD_ALIGN_PARAGRAPH.LEFT if j == 0 and i > 0 else WD_ALIGN_PARAGRAPH.CENTER
        pc.paragraph_format.space_after = Pt(0)
        if i == 0:
            shade(c, 'E6E6E6')
            run_fmt(pc.add_run(heads_t2[j]), 7.6, bold=True)
        else:
            is_b = (i == len(rows_t2))
            run_fmt(pc.add_run(rows_t2[i - 1][j]), 7.6, bold=is_b)

cap_t2 = doc.add_paragraph()
cap_t2.alignment = WD_ALIGN_PARAGRAPH.CENTER
cap_t2.paragraph_format.space_before = Pt(2)
cap_t2.paragraph_format.space_after = Pt(3)
run_fmt(cap_t2.add_run('Tabla 2. Respuesta de la Incógnita 2 (DFS): clasificación de las 240 rutas simples según deterioro de cachama.'), 7.8, italic=True)

para('Fenomenológicamente, la Red Actual condena el 61.3 % de las combinaciones de evacuación (147 rutas, con extremos '
     'de hasta 850 min sin frío desde Alto Vichada hasta Bogotá) a pérdida comercial segura, validando la queja literal '
     'de las encuestas 31 y 32 sobre pescado dañado por ausencia de muelles y red de frío. Con la Red Optimizada, las '
     '147 rutas críticas desaparecen por completo (0.0 %) y el 80.0 % cumple frescura óptima.')

# =========================================================================
# PÁGINA 4: GRÁFICA 2 (1 COL) -> ANALISIS REGRESION (COL 1) -> CONCLUSIONES + REFS (COL 2)
# =========================================================================
sec_p4_top = doc.add_section(WD_SECTION_START.NEW_PAGE)
set_section_cols(sec_p4_top, n_cols=1)

p_g2 = doc.add_paragraph()
p_g2.alignment = WD_ALIGN_PARAGRAPH.CENTER
p_g2.paragraph_format.space_before = Pt(2)
p_g2.paragraph_format.space_after = Pt(1)
p_g2.paragraph_format.keep_with_next = True
p_g2.add_run().add_picture(os.path.join(ASSETS, 'grafica_2_dfs_y_regresion.png'), width=Inches(6.95))

cap_g2 = doc.add_paragraph()
cap_g2.alignment = WD_ALIGN_PARAGRAPH.CENTER
cap_g2.paragraph_format.space_before = Pt(1)
cap_g2.paragraph_format.space_after = Pt(3)
run_fmt(cap_g2.add_run(
    'Gráfica 2. (a) Distribución porcentual de las 240 rutas DFS evaluadas según estado de frescura de la cachama; '
    '(b) Regresión lineal de tiempo expuesto sin frío t [min] frente a la distancia acumulada d [km].'
), 8.5, italic=True)

sec_p4_bot = doc.add_section(WD_SECTION_START.CONTINUOUS)
set_section_cols(sec_p4_bot, n_cols=2, space=340)

para('Al aplicar regresión lineal por mínimos cuadrados entre la distancia acumulada ', ('m', r('d')),
     ' [km] y el tiempo sin frío ', ('m', r('t')), ' [min] (Gráfica 2b), la Red Actual arroja ',
     ('m', r('t = 2.06d + 43.8')), ' (', ('m', sup(r('R'), rp('2')) + rp(' = 0.8851')),
     '), mientras que la Red Optimizada sigue una relación casi exacta ', ('m', r('t = 3.99d + 0.9')),
     ' con ', ('m', sup(r('R'), rp('2')) + rp(' = 0.9998')),
     '. Físicamente, la pendiente en el escenario optimizado representa el inverso de la velocidad fluvial de '
     'canoa (', ('m', r('m = 1 / ') + sub(r('v'), rp('f'))), '), frente al valor teórico de ',
     ('m', rp('4.00 min/km')), ' (', ('m', rp('15 km/h')), '), arrojando un error porcentual mínimo de apenas ',
     ('m', rp('0.25 %')), '; la baja correlación de la Red Actual obedece a la mezcla forzada de tramos fluviales '
     'lentos con tramos terrestres rápidos sin refrigeración.')

para('Empleando la ecuación experimental optimizada para determinar una variable desconocida crítica, se despeja '
     'el radio máximo de cobertura fluvial ', ('m', sub(r('d'), rp('max'))),
     ' antes de exceder el límite de frescura óptima de ', ('m', rp('360 min')), ':')
equation(sub(r('d'), rp('max')) + rp(' = ') + frac(rp('360 − 0.9'), rp('3.99')) + rp(' = 90.0 km'))

para('Este radio de ', ('m', rp('90.0 km')), ' concuerda con exactitud con el umbral teórico fluvial y confirma que, '
     'contrastado con la teoría microbiológica de FAO y estudios en cachama [3], [4], capturar el producto dentro de '
     'los primeros 170–305 min en centros A+F detiene la fase exponencial mesófila y habilita el despacho refrigerado '
     'seguro hacia Villavicencio y Bogotá.')

heading('IV.  Conclusiones')

para([('b', '1. '), 'La consolidación de las 33 encuestas en el grafo dirigido de 16 vértices y 24 aristas mediante '
      'listas de adyacencia en C++ demostró que el eje Manacacías–Yucao–Meta concentra la mayor actividad pesquera '
      '(19, 18 y 14 menciones), siendo las confluencias críticas donde se reportan nodos D, H y ausencia de muelles.'],
     indent=0.0)

para([('b', '2. '), 'La resolución de la Incógnita 1 mediante BFS confirmó que la red actual somete a 6 de 10 zonas a '
      'tiempos superiores a 360 min (media de 373.0 min); al instalar tres centros A+F en Bocas del Manacacías, '
      'Manacacías Medio y Río Muco, la distancia en saltos cae a 1–2 tramos y el tiempo medio baja a 152.5 min (-59.1 %).'],
     indent=0.0)

para([('b', '3. '), 'La exploración exhaustiva con DFS (Incógnita 2) sobre 240 rutas simples reveló que en el escenario '
      'actual el 61.3 % (147/240 rutas) sufre deterioro bacteriano crítico (> 480 min) de la cachama; en la red '
      'optimizada las rutas críticas se reducen a 0 (0.0 %) y las rutas óptimas ascienden del 18.3 % al 80.0 %.'],
     indent=0.0)

para([('b', '4. '), 'La regresión lineal del escenario optimizado validó el modelo de transporte fluvial puro '
      '(', ('m', r('t = 3.99d + 0.9')), ', ', ('m', sup(r('R'), rp('2')) + rp(' = 0.9998')), ', error de 0.25 % '
      'respecto a 15 km/h) y permitió establecer un radio máximo seguro de 90.0 km por centro A+F antes de iniciar '
      'la cadena de frío a 0 °C.'],
     indent=0.0)

heading('Referencias')

refs = [
    '[1] T. H. Cormen, C. E. Leiserson, R. L. Rivest y C. Stein, Introduction to Algorithms, 4.ª ed. Cambridge, MA: MIT Press, 2022, pp. 549–580.',
    '[2] R. F. Gilberg y B. A. Forouzan, Data Structures: A Pseudocode Approach with C++. Boston, MA: Cengage Learning, 2004.',
    '[3] FAO, El pescado fresco: su calidad y cambios de su calidad, Documento Técnico de Pesca n.º 348. Roma: Organización de las Naciones Unidas para la Alimentación y la Agricultura, 1998.',
    '[4] G. A. Otero et al., "Evaluación de la vida útil de cachama blanca (Piaractus brachypomus) almacenada en hielo y a temperatura ambiente," SciELO / Anales Venezolanos de Nutrición, vol. 25, n.º 2, pp. 78–86, 2012.',
    '[5] Grupo de Investigación GRITOX y Corporación Kotsala, "Piscicultura sostenible con especies nativas como alternativa productiva para pescadores artesanales en Puerto Gaitán, Meta," Univ. de los Llanos / SIMA-DSS, 2026.',
]
for ref in refs:
    pr = doc.add_paragraph()
    pr.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    pr.paragraph_format.space_before = Pt(0)
    pr.paragraph_format.space_after = Pt(1.5)
    pr.paragraph_format.line_spacing = 1.02
    pr.paragraph_format.left_indent = Inches(0.18)
    pr.paragraph_format.first_line_indent = Inches(-0.18)
    run_fmt(pr.add_run(ref), 7.8)

doc.save(OUT_DOCX)
print('Informe generado exitosamente:', OUT_DOCX)
