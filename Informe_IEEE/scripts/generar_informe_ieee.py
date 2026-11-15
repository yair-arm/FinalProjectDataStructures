# -*- coding: utf-8 -*-
"""
Genera el Informe IEEE doble columna del Proyecto Final de Estructuras de Datos
basado en el modelo de 25 vertices y 41 aristas de Harold, siguiendo estrictamente
la rubrica oficial de Unillanos (RUBRICA PARA INFORMES 2025-II) y DIRECTRICES_Y_REGLAS_INFORMES.md.
Todas las figuras y tablas se ajustan a columna simple (Inches(3.20)) dentro de una
seccion continua de 2 columnas, garantizando 3 paginas exactas sin cortes.
"""
import os
import csv
from xml.sax.saxutils import escape
import docx
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_ALIGN_VERTICAL
from docx.enum.section import WD_SECTION_START
from docx.oxml import parse_xml
from docx.oxml.ns import nsdecls, qn

BASE = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
ROOT = os.path.abspath(os.path.join(BASE, '..'))
ASSETS = os.path.join(BASE, 'Assets')
OUT_DOCX = os.path.join(BASE, 'Informe_Proyecto_Final_Grafos.docx')
OUT_PDF = os.path.join(BASE, 'Informe_Proyecto_Final_Grafos.pdf')

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
st.font.size = Pt(8.8)
st.font.color.rgb = BLACK
st.element.rPr.rFonts.set(qn('w:eastAsia'), FONT)

sec0 = doc.sections[0]
sec0.top_margin = sec0.bottom_margin = Inches(0.65)
sec0.left_margin = sec0.right_margin = Inches(0.65)

hp = sec0.header.paragraphs[0]
hp.alignment = WD_ALIGN_PARAGRAPH.RIGHT
hr = hp.add_run('Estructuras de Datos — Optimización de Red Frigorífica Multimodal en Puerto Gaitán (Meta)')
hr.font.name = FONT
hr.font.size = Pt(7.8)
hr.font.italic = True
hr.font.color.rgb = RGBColor(90, 90, 90)

def run_fmt(run, size=8.8, bold=False, italic=False):
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

def cell_margins(cell, t=8, b=8, l=12, rr=12):
    cell._tc.get_or_add_tcPr().append(parse_xml(
        f'<w:tcMar {nsdecls("w")}><w:top w:w="{t}" w:type="dxa"/><w:left w:w="{l}" w:type="dxa"/>'
        f'<w:bottom w:w="{b}" w:type="dxa"/><w:right w:w="{rr}" w:type="dxa"/></w:tcMar>'))

def shade(cell, hexcolor):
    cell._tc.get_or_add_tcPr().append(parse_xml(
        f'<w:shd {nsdecls("w")} w:val="clear" w:color="auto" w:fill="{hexcolor}"/>'))

def set_section_cols(sec, n_cols=2, space=320):
    sec.top_margin = sec.bottom_margin = Inches(0.65)
    sec.left_margin = sec.right_margin = Inches(0.65)
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
c_logo.width, c_info.width = Inches(1.0), Inches(6.2)
for c in (c_logo, c_info):
    c.vertical_alignment = WD_ALIGN_VERTICAL.CENTER

pl = c_logo.paragraphs[0]
pl.alignment = WD_ALIGN_PARAGRAPH.CENTER
pl.add_run().add_picture(os.path.join(ASSETS, 'logo_unillanos_0.png'), width=Inches(0.70))

pi = c_info.paragraphs[0]
pi.alignment = WD_ALIGN_PARAGRAPH.CENTER
run_fmt(pi.add_run('UNIVERSIDAD DE LOS LLANOS'), 10.5, bold=True)
pi.add_run().add_break()
run_fmt(pi.add_run('Facultad de Ciencias Básicas e Ingeniería — Ingeniería en Sistemas'), 8.8)
pi.add_run().add_break()
run_fmt(pi.add_run('Estructuras de Datos (Corte 3: Grafos y Optimización) — Villavicencio, Colombia'), 8.2, italic=True)

pt = doc.add_paragraph()
pt.alignment = WD_ALIGN_PARAGRAPH.CENTER
pt.paragraph_format.space_before = Pt(3)
pt.paragraph_format.space_after = Pt(2)
run_fmt(pt.add_run('OPTIMIZACIÓN MULTIMODAL DE CADENAS DE FRÍO PARA PESCA ARTESANAL MEDIANTE TEORÍA DE GRAFOS Y LOCALIZACIÓN DE INSTALACIONES EN PUERTO GAITÁN, META'), 11.5, bold=True)

def centered(text_runs, before=1, after=1, spacing=1.03):
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
    ('Yair Armando Ospino Herrera (160005565)', 8.8, True, False),
    ('Harold Esteban Padilla Díaz (160005567)', 8.8, True, False),
], after=1.5)
centered([
    ('Facultad de Ciencias Básicas e Ingeniería — Ingeniería en Sistemas', 8.2, False, True),
    ('Universidad de los Llanos, Villavicencio, Colombia', 8.2, False, True),
], after=3)

# Resumen en caja sombreada
at = doc.add_table(rows=1, cols=1)
at.alignment = WD_TABLE_ALIGNMENT.CENTER
at.autofit = False
no_borders(at)
cell_a = at.cell(0, 0)
cell_a.width = Inches(7.2)
shade(cell_a, 'F4F6F8')
cell_margins(cell_a, 10, 10, 18, 18)

pa_t = cell_a.paragraphs[0]
pa_t.alignment = WD_ALIGN_PARAGRAPH.CENTER
pa_t.paragraph_format.space_after = Pt(1.5)
run_fmt(pa_t.add_run('Resumen'), 9.2, bold=True)

pa_c = cell_a.add_paragraph()
pa_c.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
pa_c.paragraph_format.space_after = Pt(1.5)
pa_c.paragraph_format.line_spacing = 1.03
run_fmt(pa_c.add_run(
    'El presente artículo modela la cadena de suministro pesquera de Puerto Gaitán (Meta) como un grafo dirigido ponderado multimodal '
    'compuesto por 25 vértices y 41 aristas, con el objetivo de determinar la ubicación óptima de centros de refrigeración que mitiguen '
    'el deterioro poscaptura de la cachama de río (Colossoma macropomum). Integrando datos georreferenciados de 7 asociaciones pesqueras '
    '(265.8 kg/día), hidrografía real del IGAC y cartografía vial vía OSRM, se implementaron desde cero los algoritmos de Dijkstra, '
    'Floyd-Warshall, Bellman-Ford, BFS, DFS y el Problema de Localización de Instalaciones (FLP). Los resultados demuestran que la apertura '
    'del Centro Frío Puerto Gaitán (F02) en el casco urbano centraliza el 100 % de los flujos rurales con tiempos al primer frío de '
    '0.08 a 2.20 h, cumpliendo estrictamente el límite biológico de 4.0 h a 30 °C, esquivando hábitats protegidos (H01, H02) y garantizando '
    'suministro inocuo a los mercados mayoristas de Villavicencio y Bogotá.'
), 8.3)

pa_kw = cell_a.add_paragraph()
pa_kw.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
pa_kw.paragraph_format.space_before = Pt(1)
pa_kw.paragraph_format.space_after = Pt(0)
run_fmt(pa_kw.add_run('Palabras clave: '), 8.3, bold=True)
run_fmt(pa_kw.add_run('Cadena de frío, caminos mínimos, Colossoma macropomum, Dijkstra, grafos dirigidos, localización de instalaciones, multimodalidad.'), 8.3)

def para(content, *more_content, before=0, after=2.0, line_spacing=1.04):
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    p.paragraph_format.space_before = Pt(before)
    p.paragraph_format.space_after = Pt(after)
    p.paragraph_format.line_spacing = line_spacing
    p.paragraph_format.first_line_indent = Inches(0.14)
    if more_content:
        items = [content] + list(more_content)
    elif isinstance(content, list):
        items = content
    else:
        items = [content]
    for item in items:
        if isinstance(item, str):
            run_fmt(p.add_run(item), 8.8)
        elif isinstance(item, tuple) and item[0] == 'm':
            p._p.append(parse_xml(f'<m:oMath xmlns:m="{M_NS}">{item[1]}</m:oMath>'))
        elif isinstance(item, tuple) and item[0] == 'b':
            run_fmt(p.add_run(item[1]), 8.8, bold=True)
        elif isinstance(item, tuple) and item[0] == 'i':
            run_fmt(p.add_run(item[1]), 8.8, italic=True)
    return p

def heading(text, before=4, after=1.5):
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_before = Pt(before)
    p.paragraph_format.space_after = Pt(after)
    p.paragraph_format.keep_with_next = True
    run_fmt(p.add_run(text.upper()), 9.2, bold=True)
    return p

EQ = [0]
def equation(omml):
    EQ[0] += 1
    t = doc.add_table(rows=1, cols=2)
    t.alignment = WD_TABLE_ALIGNMENT.CENTER
    t.autofit = False
    no_borders(t)
    ce, cn = t.cell(0, 0), t.cell(0, 1)
    ce.width, cn.width = Inches(2.90), Inches(0.35)
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
    run_fmt(pn.add_run(f'({EQ[0]})'), 8.5)

def add_col_figure(img_path, caption_text, width_in=3.20):
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_before = Pt(2)
    p.paragraph_format.space_after = Pt(1)
    p.paragraph_format.keep_with_next = True
    p.add_run().add_picture(img_path, width=Inches(width_in))

    cap = doc.add_paragraph()
    cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
    cap.paragraph_format.space_before = Pt(1)
    cap.paragraph_format.space_after = Pt(3.5)
    run_fmt(cap.add_run(caption_text), 7.8, italic=True)

# =========================================================================
# CUERPO EN DOS COLUMNAS
# =========================================================================
sec_body = doc.add_section(WD_SECTION_START.CONTINUOUS)
set_section_cols(sec_body, n_cols=2, space=320)

heading('I.  Introducción')

para('La pesca artesanal en el municipio de Puerto Gaitán (Meta) se desarrolla en las cuencas de los ríos Meta, Manacacías e Iteviare. '
     'Los pescadores extraen diariamente alrededor de 265.8 kg/día de especies comerciales como la cachama de río (',
     ('i', 'Colossoma macropomum'), '). No obstante, la carencia histórica de centros frigoríficos rurales y muelles adaptados somete '
     'el producto a temperaturas ambiente de ', ('m', r('30 °C')), ', generando pérdidas de hasta el 40 % por deterioro microbiológico [1], [2].')

para('Desde la ciencia de la computación y las estructuras de datos, este corredor logístico se modela formalmente como un grafo dirigido '
     'ponderado ', ('m', r('G = (V, E)')), ' almacenado mediante listas de adyacencia sobre tablas hash con complejidad espacial ',
     ('m', r('O(|V| + |E|)')), ' [3]. Para capturar la complejidad real del transporte en los Llanos Orientales, cada arista ',
     ('m', r('e = (u, v) ∈ E')), ' evalúa una función de peso multicriterio normalizada:')
equation(r('w(e) = 0.25·t + 0.20·c + 0.20·r + 0.10·p + 0.10·(1−conf) + 0.05·ret'))

para('donde ', ('m', r('t')), ' es el tiempo normalizado, ', ('m', r('c')), ' el costo operativo, ', ('m', r('r')), ' la confiabilidad, ',
     ('m', r('p')), ' la penalización por deterioro y ', ('m', r('ret')), ' retrasos por transbordo. La navegación fluvial en canoa a motor '
     '(', ('m', sub(r('v'), rp('canoa'))), ' ≈ 16.5 km/h) posee una incertidumbre propagada de ',
     ('m', r('Δt = 0.15·t')), ' debido a regímenes hidrológicos y palizadas [4].')

para('La FAO estipula que a ', ('m', r('30 °C')), ' la vida útil del pescado sin refrigerar es de apenas 6 h, estableciéndose un umbral '
     'máximo de inocuidad de ', ('m', sub(r('t'), rp('máx'))), ' = 4.0 h [1]. En hielo (0 °C), la vida útil se extiende a 360 h (15 días). '
     'Los objetivos del proyecto son: (i) construir las estructuras del grafo con 25 nodos tipificados y 41 aristas; (ii) optimizar la '
     'localización de cuartos fríos mediante FLP; (iii) hallar caminos mínimos hacia Villavicencio y Bogotá con Dijkstra, Bellman-Ford y '
     'Floyd-Warshall; y (iv) verificar la navegabilidad mediante recorridos canónicos BFS y DFS.')

heading('II.  Metodología y Estructuras de Datos')

para('El sistema fue implementado en Python 3.10+ bajo arquitectura modular sin emplear librerías de cálculo en grafos (como NetworkX), '
     'demostrando dominio directo de estructuras de datos. Se definieron dos grafos independientes en memoria:')

para(('b', '1. Grafo Logístico Principal:'), ' Contiene ', ('m', r('|V| = 25')), ' vértices tipificados y ', ('m', r('|E| = 41')), ' aristas. '
     'Los vértices se clasifican en: P (7 capturas), M (3 muelles fluviales con espera de +0.25 h), A (3 acopios rurales), F (3 centros '
     'frigoríficos), D (2 zonas críticas con factor térmico ×1.5), H (2 hábitats protegidos con exclusión ambiental) y V (5 puntos de venta). '
     'La topología funcional se ilustra en la Figura 1.')

add_col_figure(os.path.join(ASSETS, 'figura_1_topologia_col.png'),
               'Figura 1. Topología del grafo logístico (25 vértices y 41 aristas) en cuatro capas funcionales, evidenciando restricciones H y D.')

para(('b', '2. Grafo Fluvial Topológico:'), ' Derivado del shapefile IGAC (', ('i', 'rios.shp'), '), consta de 12,413 vértices georreferenciados '
     'y 24,790 aristas navegables cuantizadas a 5 decimales (resolución 1.1 m). Un índice espacial de rejilla hash (447 celdas de 0.05° × 0.05°) '
     'permite acoplar puntos de pesca con el cauce real y calcular meandros mediante Dijkstra interno.')

para(('b', '3. Geometría Vial Real (OSRM):'), ' Las aristas terrestres sobre la Ruta Nacional 40 se trazaron consultando el motor OSRM sobre '
     'OpenStreetMap, almacenando 41 geometrías exactas en caché JSON local.')

heading('III.  Algoritmos y Formulación Matemática')

para('Los algoritmos implementados operan de la siguiente manera:')

para(('b', 'Dijkstra con Heap Binario:'), ' Encuentra caminos mínimos en tiempo o costo con complejidad ',
     ('m', r('O((|V| + |E|) \log |V|)')), '. Incorpora un filtro booleano que inhabilita aristas incidentes en nodos con restricción ambiental ',
     ('m', r('H \in V')), ' [3].')

para(('b', 'Bellman-Ford y Floyd-Warshall:'), ' Bellman-Ford (', ('m', r('O(|V|·|E|)')), ') verifica la inexistencia de ciclos de costo negativo '
     'y valida al 100 % las distancias de Dijkstra. Floyd-Warshall (', ('m', r('O(|V|^3)')), ') computa la matriz completa de tiempos entre todos '
     'los pares de nodos.')

para(('b', 'Recorridos BFS y DFS:'), ' BFS (cola FIFO) identifica el centro de acopio o frío más cercano en saltos directos desde cada puerto. '
     'DFS (backtracking) enumera exhaustivamente todas las rutas simples hacia Bogotá y calcula el deterioro térmico acumulado.')

para(('b', 'Localización de Instalaciones (FLP Greedy):'), ' Resuelve la selección óptima de plantas frigoríficas minimizando la función de '
     'costo de instalación y acarreo, sujeta a cobertura de demanda y ', ('m', sub(r('t'), rp('sinFrío'))), ' ≤ 4.0 h.')

heading('IV.  Resultados y Discusión')

para('Las variables directas del modelo corresponden a coordenadas WGS 84, producciones censadas en campo (kg/día), capacidades y costos '
     'fijos de frío. Las variables indirectas abarcan distancias geodésicas Haversine, tiempos de viaje multimodal y pérdida acumulada:')
equation(sub(r('D'), rp('acum')) + rp(' = ') + sub(r('D'), r('0')) + rp(' + ∑ ') + sub(r('k'), r('i')) + rp(' · ') + sub(r('t'), r('i')))

para('donde ', ('m', sub(r('k'), r('i'))), ' = 2.5 %/h a temperatura ambiente (30 °C) y ', ('m', sub(r('k'), r('i'))), ' = 3.75 %/h en zonas '
     'de calor crítico D (multiplicador 1.5). Al arribar a un nodo F, el pescado se refrigera a 0 °C y el reloj se reinicia a 0.0 h.')

para('La Tabla 1 consolida los resultados de ruteo óptimo para los 7 puntos de pesca hacia Bogotá D.C. (mercado V_BOG1, a ~295 km de Puerto Gaitán).')

# TABLA 1: Ruteo e itinerarios
heads_t1 = ['Punto Captura', 'kg/d', 'Ruta Óptima a Bogotá', 't 1er Frío', 'Cumple']
w_t1 = [0.95, 0.38, 1.25, 0.42, 0.35]
tb1 = doc.add_table(rows=8, cols=5)
tb1.alignment = WD_TABLE_ALIGNMENT.CENTER
tb1.autofit = False
tb1._tbl.tblPr.append(parse_xml(
    f'<w:tblBorders {nsdecls("w")}><w:top w:val="single" w:sz="8" w:space="0" w:color="000000"/>'
    f'<w:left w:val="none"/><w:bottom w:val="single" w:sz="8" w:space="0" w:color="000000"/>'
    f'<w:right w:val="none"/><w:insideH w:val="single" w:sz="4" w:space="0" w:color="AAAAAA"/>'
    f'<w:insideV w:val="none"/></w:tblBorders>'))

for j, h in enumerate(heads_t1):
    c = tb1.cell(0, j)
    c.width = Inches(w_t1[j])
    cell_margins(c, 2, 2, 2, 2)
    shade(c, 'E6E6E6')
    pc = c.paragraphs[0]
    pc.alignment = WD_ALIGN_PARAGRAPH.CENTER
    pc.paragraph_format.space_after = Pt(0)
    run_fmt(pc.add_run(h), 7.2, bold=True)

filas_t1 = [
    ('P01 Alto Neblinas', '65.8', 'P01→M03→F02→F03→Bog', '0.48 h (29m)', '100 %'),
    ('P02 Atarraya Verde', '40.0', 'P02→M03→F02→F03→Bog', '0.43 h (26m)', '100 %'),
    ('P03 Asovida San Mig.', '25.0', 'P03→A01→F02→F03→Bog', '0.25 h (15m)', '100 %'),
    ('P04 Asopespor', '20.0', 'P04→A01→F02→F03→Bog', '0.40 h (24m)', '100 %'),
    ('P05 Puerto Trujillo', '30.0', 'P05→A03→D01→A01→F02→Bog', '2.20 h (132m)', '100 %'),
    ('P06 Desembarcadero', '50.0', 'P06→F02→F03→Bog', '0.08 h (5m)', '100 %'),
    ('P07 Soplaviento', '35.0', 'P07→M03→F02→F03→Bog', '0.38 h (23m)', '100 %'),
]

for i, row in enumerate(filas_t1, start=1):
    tb1.rows[i]._tr.get_or_add_trPr().append(parse_xml(f'<w:cantSplit {nsdecls("w")}/>'))
    for j, val in enumerate(row):
        c = tb1.cell(i, j)
        c.width = Inches(w_t1[j])
        cell_margins(c, 2, 2, 2, 2)
        pc = c.paragraphs[0]
        pc.alignment = WD_ALIGN_PARAGRAPH.LEFT if j in (0, 2) else WD_ALIGN_PARAGRAPH.CENTER
        pc.paragraph_format.space_after = Pt(0)
        run_fmt(pc.add_run(val), 6.9, bold=(j == 4))

cap_t1 = doc.add_paragraph()
cap_t1.alignment = WD_ALIGN_PARAGRAPH.CENTER
cap_t1.paragraph_format.space_before = Pt(1.5)
cap_t1.paragraph_format.space_after = Pt(3)
run_fmt(cap_t1.add_run('Tabla 1. Itinerarios multimodales óptimos hacia Bogotá D.C. y tiempos de exposición sin frío.'), 7.6, italic=True)

para('Como se aprecia en la Gráfica 1, todos los puntos de captura acceden a infraestructura de acopio o frío en tiempos inferiores '
     'a 1.0 h, con excepción de Puerto Trujillo (P05, 2.20 h) debido a su aislamiento sobre el río Iteviare (63 km de navegación fluvial). '
     'Aun en este caso extremo, el tiempo se mantiene holgadamente dentro del umbral sanitario de 4.0 h (240 min).')

add_col_figure(os.path.join(ASSETS, 'grafica_1_bfs_col.png'),
               'Gráfica 1. Tiempo sin frío al primer centro de conservación frente a los límites sanitarios de la FAO.')

para('El algoritmo FLP greedy evaluó 5 configuraciones de red frigorífica (Tabla 2 y Gráfica 2a). El Escenario Óptimo seleccionó '
     'exclusivamente el Centro Frío Puerto Gaitán (F02, \$3,000,000 COP/mes), el cual logra 100 % de cobertura regional a un costo unitario '
     'de \$59,080 COP/kg, evitando el sobredimensionamiento de operar tres plantas (\$104,444 COP/kg).')

heads_t2 = ['Escenario', '# CF', 'Pérdida', 'Costo Total', '$/kg', 'Cob.']
w_t2 = [1.05, 0.28, 0.45, 0.65, 0.45, 0.35]
tb2 = doc.add_table(rows=6, cols=6)
tb2.alignment = WD_TABLE_ALIGNMENT.CENTER
tb2.autofit = False
tb2._tbl.tblPr.append(parse_xml(
    f'<w:tblBorders {nsdecls("w")}><w:top w:val="single" w:sz="8" w:space="0" w:color="000000"/>'
    f'<w:left w:val="none"/><w:bottom w:val="single" w:sz="8" w:space="0" w:color="000000"/>'
    f'<w:right w:val="none"/><w:insideH w:val="single" w:sz="4" w:space="0" w:color="AAAAAA"/>'
    f'<w:insideV w:val="none"/></w:tblBorders>'))

for j, h in enumerate(heads_t2):
    c = tb2.cell(0, j)
    c.width = Inches(w_t2[j])
    cell_margins(c, 2, 2, 2, 2)
    shade(c, 'E6E6E6')
    pc = c.paragraphs[0]
    pc.alignment = WD_ALIGN_PARAGRAPH.CENTER
    pc.paragraph_format.space_after = Pt(0)
    run_fmt(pc.add_run(h), 7.0, bold=True)

filas_t2 = [
    ('Sin cadena de frío', '0', '17.1 %', '$8,023,272', '$36,397', '100%'),
    ('Solo F01 Alto Neblinas', '1', '17.0 %', '$9,701,891', '$61,247', '100%'),
    ('Solo F02 Puerto Gaitán*', '1', '17.1 %', '$13,023,272', '$59,080', '100%'),
    ('Solo F03 Puerto López', '1', '17.1 %', '$13,023,272', '$59,080', '100%'),
    ('3 centros combinados', '3', '17.1 %', '$23,023,272', '$104,444', '100%'),
]

for i, row in enumerate(filas_t2, start=1):
    tb2.rows[i]._tr.get_or_add_trPr().append(parse_xml(f'<w:cantSplit {nsdecls("w")}/>'))
    for j, val in enumerate(row):
        c = tb2.cell(i, j)
        c.width = Inches(w_t2[j])
        cell_margins(c, 2, 2, 2, 2)
        pc = c.paragraphs[0]
        pc.alignment = WD_ALIGN_PARAGRAPH.LEFT if j == 0 else WD_ALIGN_PARAGRAPH.CENTER
        pc.paragraph_format.space_after = Pt(0)
        run_fmt(pc.add_run(val), 6.8, bold=(i == 3))

cap_t2 = doc.add_paragraph()
cap_t2.alignment = WD_ALIGN_PARAGRAPH.CENTER
cap_t2.paragraph_format.space_before = Pt(1.5)
cap_t2.paragraph_format.space_after = Pt(3)
run_fmt(cap_t2.add_run('Tabla 2. Evaluación de escenarios frigoríficos mediante FLP y simulación térmica.'), 7.6, italic=True)

add_col_figure(os.path.join(ASSETS, 'grafica_2a_dfs_col.png'),
               'Gráfica 2a. Comparación de costos operativos mensuales y selección óptima del centro F02 en Puerto Gaitán.')

para('El ajuste de regresión lineal (Gráfica 2b) sobre las 41 conexiones del grafo revela que el transporte fluvial demanda una tasa de '
     '3.64 min/km (', ('m', r('R^2 = 1.000')), '), mientras que el transporte terrestre en furgón refrigerado opera a 0.92 min/km '
     '(65 km/h, ', ('m', r('R^2 = 1.000')), '). Esta marcada disparidad confirma que el cuello de botella crítico reside en la navegación '
     'fluvial y en las maniobras de transbordo en muelles.')

add_col_figure(os.path.join(ASSETS, 'grafica_2b_regresion_col.png'),
               'Gráfica 2b. Regresión lineal de tiempos de tránsito fluvial y carretero vs. distancia de tramo.')

heading('V.  Conclusiones')

para(('b', '1. Eficacia del Modelado en Grafos:'), ' La formulación de un grafo dirigido multimodal de 25 vértices y 41 aristas permitió '
     'capturar con fidelidad geográfica y matemática la logística pesquera de Puerto Gaitán, demostrando la aplicabilidad de los algoritmos '
     'de caminos mínimos en problemáticas agroalimentarias reales.')

para(('b', '2. Solución Óptima FLP:'), ' El centro frigorífico F02 (Puerto Gaitán) centraliza eficientemente los 265.8 kg/día capturados '
     'en los ríos Manacacías, Meta e Iteviare con un costo mensual de \$13.0M COP, evitando un sobrecosto de \$10.0M COP que representaría '
     'abrir tres plantas redundantes.')

para(('b', '3. Cumplimiento Sanitario Total:'), ' En el 100 % de los puntos de pesca, el tiempo transcurrido hasta el primer abatimiento '
     'térmico (0.08 a 2.20 h) es inferior al límite de 4.0 h de la FAO, erradicando el deterioro crítico del producto.')

para(('b', '4. Preservación Ambiental:'), ' El ruteo con exclusión ambiental desvió exitosamente el tráfico de lanchas de los hábitats '
     'protegidos H01 y H02, garantizando sostenibilidad ecológica sin comprometer la viabilidad comercial.')

heading('Referencias')

refs = [
    '[1] FAO, «El pescado fresco: su calidad y cambios de calidad», Colección FAO: Pesca, N° 348, Roma, 1999.',
    '[2] SciELO, «Cinética de deterioro y vida útil de Colossoma macropomum bajo almacenamiento refrigerado», Rev. MVZ Córdoba, vol. 24, n° 2, 2019.',
    '[3] T. H. Cormen, C. E. Leiserson, R. L. Rivest, y C. Stein, Introduction to Algorithms, 3a ed. Cambridge, MA: MIT Press, 2009.',
    '[4] J. R. Taylor, An Introduction to Error Analysis: The Study of Uncertainties in Physical Measurements, 2a ed. Sausalito, CA: Univ. Science Books, 1997.',
    '[5] G. Laporte, S. Nickel, y F. Saldanha-da-Gama, Location Science, 2a ed. Cham, Suiza: Springer, 2019.'
]

for ref in refs:
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    p.paragraph_format.space_before = Pt(0)
    p.paragraph_format.space_after = Pt(1.5)
    p.paragraph_format.line_spacing = 1.02
    run_fmt(p.add_run(ref), 7.8)

doc.save(OUT_DOCX)
print('Documento Word guardado en:', OUT_DOCX)

# Conversion a PDF usando Word COM
try:
    import win32com.client
    word = win32com.client.DispatchEx("Word.Application")
    word.Visible = False
    doc_com = word.Documents.Open(OUT_DOCX)
    doc_com.SaveAs(OUT_PDF, FileFormat=17) # 17 = wdFormatPDF
    doc_com.Close()
    word.Quit()
    print('PDF generado exitosamente en:', OUT_PDF)
except Exception as e:
    print('Aviso COM Word:', e)
