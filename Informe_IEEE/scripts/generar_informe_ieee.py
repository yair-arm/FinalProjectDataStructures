# -*- coding: utf-8 -*-
"""
Genera el Informe IEEE doble columna del Proyecto Final de Estructuras de Datos
siguiendo estrictamente la rubrica oficial de la Facultad de Ciencias Basicas e
Ingenieria (RUBRICA PARA INFORMES 2025-II) y DIRECTRICES_Y_REGLAS_INFORMES.md.
Todas las figuras se acoplan al ancho de columna (Inches(3.25)) dentro de una
unica seccion continua de dos columnas, eliminando cortes y espacios en blanco.
"""
import csv
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
ROOT = os.path.abspath(os.path.join(BASE, '..'))
ASSETS = os.path.join(BASE, 'Assets')
DATA_CSV = os.path.join(ROOT, 'Codigo', 'data', 'comparativa_resultados.csv')
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

# Leer datos exactos generados por el binario C++
rows_csv = []
with open(DATA_CSV, encoding='utf-8') as f:
    for row in csv.DictReader(f):
        rows_csv.append(row)

doc = docx.Document()
st = doc.styles['Normal']
st.font.name = FONT
st.font.size = Pt(9)
st.font.color.rgb = BLACK
st.element.rPr.rFonts.set(qn('w:eastAsia'), FONT)

sec0 = doc.sections[0]
sec0.top_margin = sec0.bottom_margin = Inches(0.70)
sec0.left_margin = sec0.right_margin = Inches(0.70)

hp = sec0.header.paragraphs[0]
hp.alignment = WD_ALIGN_PARAGRAPH.RIGHT
hr = hp.add_run('Estructuras de Datos (Grafos) — Optimización de Acopio y Red de Frío Pesquera en Puerto Gaitán, Meta')
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

def cell_margins(cell, t=10, b=10, l=14, rr=14):
    cell._tc.get_or_add_tcPr().append(parse_xml(
        f'<w:tcMar {nsdecls("w")}><w:top w:w="{t}" w:type="dxa"/><w:left w:w="{l}" w:type="dxa"/>'
        f'<w:bottom w:w="{b}" w:type="dxa"/><w:right w:w="{rr}" w:type="dxa"/></w:tcMar>'))

def shade(cell, hexcolor):
    cell._tc.get_or_add_tcPr().append(parse_xml(
        f'<w:shd {nsdecls("w")} w:val="clear" w:color="auto" w:fill="{hexcolor}"/>'))

def set_section_cols(sec, n_cols=2, space=340):
    sec.top_margin = sec.bottom_margin = Inches(0.70)
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
c_logo.width, c_info.width = Inches(1.0), Inches(6.1)
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
run_fmt(pi.add_run('Estructuras de Datos (Tercer Corte: Grafos) — Villavicencio, Colombia'), 8.5, italic=True)

pt = doc.add_paragraph()
pt.alignment = WD_ALIGN_PARAGRAPH.CENTER
pt.paragraph_format.space_before = Pt(4)
pt.paragraph_format.space_after = Pt(2)
run_fmt(pt.add_run('MODELADO MEDIANTE GRAFOS DIRIGIDOS PARA LA OPTIMIZACIÓN DE PUNTOS DE ACOPIO Y RED DE FRÍO PESQUERA EN PUERTO GAITÁN, META'), 12, bold=True)

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
], after=4)

# Resumen en caja sombreada con encabezado centrado en negrita (DIRECTRICES)
at = doc.add_table(rows=1, cols=1)
at.alignment = WD_TABLE_ALIGNMENT.CENTER
at.autofit = False
no_borders(at)
cell_a = at.cell(0, 0)
cell_a.width = Inches(7.1)
shade(cell_a, 'F4F6F8')
cell_margins(cell_a, 12, 12, 20, 20)

pa_t = cell_a.paragraphs[0]
pa_t.alignment = WD_ALIGN_PARAGRAPH.CENTER
pa_t.paragraph_format.space_after = Pt(2)
run_fmt(pa_t.add_run('Resumen'), 9.5, bold=True)

pa_c = cell_a.add_paragraph()
pa_c.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
pa_c.paragraph_format.space_after = Pt(2)
pa_c.paragraph_format.line_spacing = 1.04
run_fmt(pa_c.add_run(
    'El presente proyecto modela mediante un grafo dirigido ponderado implementado en C++ (lista de adyacencia basada en listas '
    'enlazadas simples) la red fluvial y terrestre de comercialización pesquera en Puerto Gaitán, Meta, con el objetivo de determinar '
    'la ubicación óptima de centros de acopio y refrigeración para reducir el deterioro bacteriano de la cachama de río. A partir de '
    '33 encuestas cartográficas reales de pescadores artesanales y de la hidrografía regional, se construyeron 16 vértices tipificados '
    'y 24 aristas ponderadas en tiempo y distancia, resolviendo dos incógnitas operativas mediante búsqueda en anchura (BFS) y '
    'búsqueda en profundidad (DFS) antes y después de ubicar tres nodos de acopio y frío en las confluencias del río Muco, Manacacías '
    'Medio y Bocas del Manacacías. La simulación demostró que el tiempo medio de exposición sin frío desciende de 373.0 min a 152.5 min '
    '(reducción de 59.1 %), los puntos de pesca fuera del límite óptimo (360 min) bajan de 6/10 a 0/10, y las rutas DFS viables hacia '
    'Puerto Gaitán, Villavicencio y Bogotá pasan de 18.3 % a 80.0 % sin pérdidas críticas, comprobando la eficacia estructural de la propuesta.'
), 8.5)

pa_kw = cell_a.add_paragraph()
pa_kw.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
pa_kw.paragraph_format.space_before = Pt(1)
pa_kw.paragraph_format.space_after = Pt(0)
run_fmt(pa_kw.add_run('Palabras clave: '), 8.5, bold=True)
run_fmt(pa_kw.add_run('Búsqueda en anchura, búsqueda en profundidad, cachama de río, cadena de frío, grafos dirigidos, lista de adyacencia.'), 8.5)

def para(content, *more_content, before=0, after=2.5, line_spacing=1.05):
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
            run_fmt(p.add_run(item), 9)
        elif isinstance(item, tuple) and item[0] == 'm':
            p._p.append(parse_xml(f'<m:oMath xmlns:m="{M_NS}">{item[1]}</m:oMath>'))
        elif isinstance(item, tuple) and item[0] == 'b':
            run_fmt(p.add_run(item[1]), 9, bold=True)
        elif isinstance(item, tuple) and item[0] == 'i':
            run_fmt(p.add_run(item[1]), 9, italic=True)
    return p

def heading(text, before=5, after=2):
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
    ce.width, cn.width = Inches(2.95), Inches(0.35)
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

def add_col_figure(img_path, caption_text, width_in=3.25):
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_before = Pt(2)
    p.paragraph_format.space_after = Pt(1)
    p.paragraph_format.keep_with_next = True
    p.add_run().add_picture(img_path, width=Inches(width_in))

    cap = doc.add_paragraph()
    cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
    cap.paragraph_format.space_before = Pt(1)
    cap.paragraph_format.space_after = Pt(4)
    run_fmt(cap.add_run(caption_text), 8.0, italic=True)

# =========================================================================
# CUERPO COMPLETO EN UNA SOLA SECCIÓN CONTINUA DE 2 COLUMNAS
# =========================================================================
sec_body = doc.add_section(WD_SECTION_START.CONTINUOUS)
set_section_cols(sec_body, n_cols=2, space=340)

heading('I.  Introducción')

para('La pesca artesanal en el municipio de Puerto Gaitán (Meta) depende de una extensa red hidrográfica integrada por los ríos '
     'Manacacías, Yucao, Meta, Muco, Guarrojo, Planas y Tomo. Las fallas de infraestructura logística —ausencia de muelles, centros de '
     'acopio y red de frío— provocan que la captura quede expuesta a temperaturas tropicales de ',
     ('m', r('27–30 °C')), ' durante largos trayectos fluviales en canoa, acelerando el rigor mortis y la multiplicación de bacterias '
     'mesófilas en especies nativas como la cachama de río [1], [2].')

para('Desde el enfoque formal de las estructuras de datos, dicha red logística se representa como un grafo dirigido ponderado ',
     ('m', r('G = (V, E)')), ', almacenado mediante listas de adyacencia con complejidad espacial ',
     ('m', r('O(|V| + |E|)')), ' [3]. Cada vértice ', ('m', r('v ∈ V')), ' codifica una localización hidrográfica tipificada y cada arista ',
     ('m', r('e = (u, v) ∈ E')), ' posee un peso ', ('m', r('w(e)')), ' equivalente al tiempo de tránsito en minutos. Tanto la búsqueda en '
     'anchura (BFS) como la búsqueda en profundidad (DFS) operan con complejidad temporal ',
     ('m', r('O(|V| + |E|)')), ' para explorar el alcance y las rutas de evacuación [3].')

para('Para cuantificar el riesgo microbiológico de la cachama sin refrigeración, el tiempo acumulado sin frío ',
     ('m', sub(r('t'), rp('sinFrío'))), ' sobre una ruta simple ', ('m', r('R')), ' se define sumando los pesos de los arcos previos al '
     'primer vértice equipado con cadena de frío ', ('m', sub(r('v'), rp('F'))), ':')
equation(sub(r('t'), rp('sinFrío')) + rp('(R) = ') + rp('∑ ') + r('w(') + sub(r('e'), r('i')) + rp(') ,  ') + r('v') + rp(' previa a ') + sub(r('v'), rp('F')))

para('Considerando la velocidad de navegación fluvial en canoa artesanal ', ('m', sub(r('v'), rp('c'))), ' = 15 ± 3 km/h, la incertidumbre '
     'propagada en los tiempos de traslado fluvial ', ('m', r('Δt')), ' a partir de la distancia estimada ', ('m', r('d')), ' sigue la relación [4]:')
equation(r('Δt = t · ') + frac(r('Δ') + sub(r('v'), rp('c')), sub(r('v'), rp('c'))) + rp(' = ') + r('0.20 · t'))

para('En cuanto al estado del arte, la modelización de redes de transporte mediante teoría de grafos ha evolucionado desde los problemas '
     'clásicos de caminos mínimos hasta sistemas modernos de trazabilidad y ubicación óptima de centros de acopio en cadenas agroalimentarias '
     'y pesqueras [3], [5]. La Organización de las Naciones Unidas para la Alimentación y la Agricultura (FAO) establece que la conservación '
     'en hielo a ', ('m', r('0 °C')), ' extiende la vida útil de peces tropicales como la cachama hasta por 14 días, mientras que a '
     'temperatura ambiente su frescura óptima decae tras 6 a 8 h (360–480 min) [1], [2].')

para('Como restricciones del modelo deben considerarse: (i) las 33 encuestas cartográficas originales contienen marcas cualitativas sobre '
     'cuencas sin registros exactos de masa capturada ni cronometraje individual; (ii) los tiempos fluviales se derivaron de distancias '
     'cartográficas con incertidumbre del ±20 %; y (iii) se asume que todo nodo equipado con red de frío estabiliza térmicamente el producto '
     'para el tramo terrestre posterior hacia Villavicencio y Bogotá.')

para('El proyecto persigue cuatro objetivos específicos: (i) estructurar en un TAD grafo con lista de adyacencia en C++ los datos de las '
     '33 encuestas cartográficas; (ii) resolver mediante BFS la primera incógnita identificando el centro de frío más cercano en saltos '
     'desde cada punto de pesca; (iii) resolver mediante DFS la segunda incógnita enumerando todas las rutas hacia mercados y detectando '
     'trayectos con deterioro bacteriano de cachama; y (iv) evaluar cuantitativamente el impacto porcentual de ubicar tres centros de acopio '
     'y frío estratégicos frente al escenario base actual.')

heading('II.  Sección Experimental')

para('El desarrollo experimental se ejecutó sobre un computador con compilador ', ('i', 'g++'), ' (estándar C++17) y entorno Python 3.14 '
     'para análisis estadístico, partiendo de la digitalización de las 33 fichas cartográficas recolectadas en campo junto a pescadores '
     'artesanales de Puerto Gaitán y Puerto López, el esquema de siete tipos de vértices definido en clase (P: pesca, A: acopio, D: deterioro, '
     'H: destrucción de hábitat, M: muelle, F: red de frío, V: lugar de venta) y las cartas hidrográficas del sistema regional del Meta. '
     'Toda la información cualitativa fue consolidada en archivos planos estructurados y reutilizó las clases plantilla genéricas del curso '
     'implementadas en lista enlazada simple.')

para('El diseño metodológico se dividió en tres etapas secuenciales. Primero, se agruparon las marcas repetidas de las 33 hojas en 16 '
     'vértices representativos y 24 aristas dirigidas ponderadas, estimando los tramos fluviales a razón de 4 min/km (15 km/h en canoa) y '
     'los corredores terrestres según distancias viales reales entre Puerto Gaitán, Puerto López (110 km), Villavicencio (193 km) y Bogotá '
     '(110 km adicionales). Segundo, se construyeron dos grafos comparativos: ', ('i', 'Red Actual'), ' (sin centros de frío en las '
     'subcuencas, reflejando la ausencia reportada en la encuesta 31) y ', ('i', 'Red Optimizada'), ' (incorporando tres centros integrales '
     'A+F en Río Muco, Manacacías Medio y Bocas del Manacacías, además de red de frío en Puerto Gaitán). Tercero, se implementaron los '
     'métodos ', ('i', 'imprimirListaAdyacencia()'), ', ', ('i', 'bfsObjetivo()'), ' con cola FIFO y ', ('i', 'dfsTodasLasRutas()'), ' con '
     'retroceso recursivo, cuya topología por capas ajustada a columna se presenta en la Figura 1.')

# Insertar Figura 1 en una sola columna (width=3.25 in)
add_col_figure(os.path.join(ASSETS, 'figura_1_topologia_col.png'),
               'Figura 1. Topología del grafo por capas (16 vértices y 24 aristas), acoplada a una columna con los 3 centros propuestos A+F.')

heading('III.  Resultados y Análisis')

para('En la caracterización de variables del modelo computacional, las ', ('b', 'variables directas'), ' correspondieron a la frecuencia de '
     'mención por subcuenca extraída de las 33 encuestas, la tipología cualitativa de los nodos, las distancias cartográficas ',
     ('m', r('d')), ' [km] y los tiempos individuales de arista ', ('m', sub(r('w'), r('i'))), ' [min]. Las ', ('b', 'variables indirectas'),
     ' incluyeron la distancia topológica en saltos mediante BFS, el tiempo acumulado sin refrigeración ', ('m', sub(r('t'), rp('sinFrío'))),
     ' con su incertidumbre ', ('m', r('Δt = 0.20·t')), ', la clasificación fisiológica de deterioro de la cachama y la reducción porcentual '
     'de exposición térmica:')
equation(sub(r('η'), rp('%')) + rp(' = ') + frac(absval(sub(r('t'), rp('act')) + rp(' − ') + sub(r('t'), rp('opt'))), sub(r('t'), rp('act'))) + rp(' × 100 %'))

para('La Tabla 1 consolida la respuesta cuantitativa de la Incógnita 1 (BFS) y del mejor trayecto DFS por cada punto de pesca, comparando '
     'la Red Actual frente a la Red Optimizada con sus incertidumbres fluviales propagadas y porcentajes de mejora.')

# TABLA 1 ajustada al ancho de columna
heads_t1 = ['Punto (Cuenca)', 'Rep.', 'BFS Act (m)', 'BFS Opt (m)', 'Mejora']
w_t1 = [1.12, 0.34, 0.68, 0.68, 0.43]
tb1 = doc.add_table(rows=len(rows_csv) + 1, cols=5)
tb1.alignment = WD_TABLE_ALIGNMENT.CENTER
tb1.autofit = False
tb1._tbl.tblPr.append(parse_xml(
    f'<w:tblBorders {nsdecls("w")}><w:top w:val="single" w:sz="8" w:space="0" w:color="000000"/>'
    f'<w:left w:val="none"/><w:bottom w:val="single" w:sz="8" w:space="0" w:color="000000"/>'
    f'<w:right w:val="none"/><w:insideH w:val="single" w:sz="4" w:space="0" w:color="AAAAAA"/>'
    f'<w:insideV w:val="none"/></w:tblBorders>'))

short_lbl_t1 = {
    'P_Cano_Morroco': 'Caño Morroco',
    'P_Vichada': 'Alto Vichada',
    'P_Planas': 'Río Planas',
    'P_Guarrojo': 'Río Guarrojo',
    'P_Muco': 'Río Muco',
    'P_Meta_Ventura': 'Meta / Ventura',
    'P_Canalete_Maiciana': 'Cañalute',
    'P_Manacacias_Sur': 'Manacacías Sur',
    'P_Yucao': 'Río Yucao',
    'P_Chaviva_PtoLopez': 'Chaviva / López'
}

for j, h in enumerate(heads_t1):
    c = tb1.cell(0, j)
    c.width = Inches(w_t1[j])
    cell_margins(c, 2, 2, 2, 2)
    shade(c, 'E6E6E6')
    pc = c.paragraphs[0]
    pc.alignment = WD_ALIGN_PARAGRAPH.CENTER
    pc.paragraph_format.space_after = Pt(0)
    run_fmt(pc.add_run(h), 7.2, bold=True)

for i, row in enumerate(rows_csv, start=1):
    t_a = int(row['tiempo_sin_frio_bfs_actual'])
    t_o = int(row['tiempo_sin_frio_bfs_opt'])
    unc_o = int(round(0.20 * t_o))
    unc_a = int(round(0.20 * (t_a - (105 if i <= 8 else 0))))
    vals = [
        short_lbl_t1.get(row['punto'], row['punto']),
        row['reportes'],
        f"{t_a}±{unc_a}",
        f"{t_o}±{unc_o}",
        f"{float(row['reduccion_tiempo_pct']):.1f}%"
    ]
    tb1.rows[i]._tr.get_or_add_trPr().append(parse_xml(f'<w:cantSplit {nsdecls("w")}/>'))
    for j, val_s in enumerate(vals):
        c = tb1.cell(i, j)
        c.width = Inches(w_t1[j])
        cell_margins(c, 2, 2, 2, 2)
        pc = c.paragraphs[0]
        pc.alignment = WD_ALIGN_PARAGRAPH.LEFT if j == 0 else WD_ALIGN_PARAGRAPH.CENTER
        pc.paragraph_format.space_after = Pt(0)
        run_fmt(pc.add_run(val_s), 7.2, bold=(j == 4))

cap_t1 = doc.add_paragraph()
cap_t1.alignment = WD_ALIGN_PARAGRAPH.CENTER
cap_t1.paragraph_format.space_before = Pt(2)
cap_t1.paragraph_format.space_after = Pt(4)
run_fmt(cap_t1.add_run('Tabla 1. Tiempos sin frío en ruta BFS con incertidumbre fluvial (±20 %) y reducción porcentual obtenida.'), 7.8, italic=True)

para('Cualitativamente, las encuestas muestran que el 57.6 % de los pescadores (19/33) converge en Bocas del Manacacías y el 42.4 % '
     '(14/33) reporta deterioro y ausencia de muelle en Manacacías Medio. Al carecer de frío intermedio en la Red Actual, las capturas de '
     'cuencas periféricas (Vichada, Planas, Cañalute, Caño Morroco) tardan entre 470 y 580 min en alcanzar refrigeración estable en Puerto '
     'López, superando el umbral óptimo de 360 min para la cachama e ingresando en zona de proliferación mesófila acelerada [1], [2].')

# Insertar Gráfica 1 (BFS tiempos sin frío) en ancho de columna
add_col_figure(os.path.join(ASSETS, 'grafica_1_bfs_col.png'),
               'Gráfica 1. Tiempo sin frío por punto de pesca vía BFS frente a los umbrales fisiológicos de la cachama.')

para('Al resolver la Incógnita 2 mediante DFS sobre los 240 trayectos simples posibles hacia Puerto Gaitán, Puerto López, Villavicencio y '
     'Bogotá (Gráfica 2a), en la Red Actual únicamente 44 rutas (18.3 %) mantienen el pescado en estado óptimo (≤360 min), mientras 49 (20.4 %) '
     'entran en alerta bacteriana y 147 (61.3 %) sufren deterioro crítico (>480 min). Al incorporar los tres centros de acopio y frío, '
     '192 rutas (80.0 %) alcanzan estado óptimo, 48 (20.0 %) permanecen en rango de alerta moderada y las rutas críticas se reducen a 0 (0.0 %).')

# Insertar Gráfica 2a (Distribución DFS) en ancho de columna
add_col_figure(os.path.join(ASSETS, 'grafica_2a_dfs_col.png'),
               'Gráfica 2. Clasificación de las 240 rutas simples DFS según riesgo bacteriano en Red Actual vs. Optimizada.')

# Tabla 2 comparativa global
heads_t2 = ['Indicador Global', 'Red Actual', 'Red Optim.', 'Variación']
rows_t2 = [
    ('Tiempo medio BFS sin frío', '373.0 min', '152.5 min', '-59.1 %'),
    ('Puntos fuera rango (>360 m)', '6 / 10 (60%)', '0 / 10 (0%)', '-100.0 %'),
    ('Rutas DFS óptimas (≤360 m)', '44 / 240', '192 / 240', '+336.4 %'),
    ('Rutas DFS críticas (>480 m)', '147 / 240', '0 / 240', '-100.0 %'),
]
w_t2 = [1.38, 0.62, 0.62, 0.60]
tb2 = doc.add_table(rows=5, cols=4)
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
    run_fmt(pc.add_run(h), 7.2, bold=True)
for i, rdata in enumerate(rows_t2, start=1):
    tb2.rows[i]._tr.get_or_add_trPr().append(parse_xml(f'<w:cantSplit {nsdecls("w")}/>'))
    for j, val_s in enumerate(rdata):
        c = tb2.cell(i, j)
        c.width = Inches(w_t2[j])
        cell_margins(c, 2, 2, 2, 2)
        pc = c.paragraphs[0]
        pc.alignment = WD_ALIGN_PARAGRAPH.LEFT if j == 0 else WD_ALIGN_PARAGRAPH.CENTER
        pc.paragraph_format.space_after = Pt(0)
        run_fmt(pc.add_run(val_s), 7.2, bold=(j == 3))

cap_t2 = doc.add_paragraph()
cap_t2.alignment = WD_ALIGN_PARAGRAPH.CENTER
cap_t2.paragraph_format.space_before = Pt(2)
cap_t2.paragraph_format.space_after = Pt(4)
run_fmt(cap_t2.add_run('Tabla 2. Síntesis comparativa global del sistema antes y después de optimizar la red de frío.'), 7.8, italic=True)

para('La regresión lineal entre distancia acumulada ', ('m', r('d')), ' [km] y tiempo sin frío ', ('m', r('t')), ' [min] (Gráfica 3) arroja '
     'para la Red Actual la ecuación ', ('m', r('t = 2.06·d + 43.8')), ' con ', ('m', r('R² = 0.8851')), ', debido a la mezcla heterogénea '
     'entre navegación lenta en canoa y transporte terrestre hasta Puerto López. En contraste, la Red Optimizada sigue un ajuste casi '
     'determinista ', ('m', r('t = 3.99·d + 0.90')), ' (', ('m', r('R² = 0.9998')), '), cuya pendiente ', ('m', r('m = 3.99 min/km')),
     ' representa físicamente el inverso de la velocidad fluvial promedio (', ('m', r('1 / 15.04 km/h')), ') porque todos los lotes reciben '
     'refrigeración antes de salir de la red hídrica.')

# Insertar Gráfica 2b (Regresión distancia-tiempo) en ancho de columna
add_col_figure(os.path.join(ASSETS, 'grafica_2b_regresion_col.png'),
               'Gráfica 3. Regresión lineal distancia acumulada vs. tiempo expuesto sin frío en Red Actual y Red Optimizada.')

para('Aplicando la ecuación experimental optimizada como herramienta predictiva para nuevas veredas sin medición previa, el radio fluvial '
     'máximo permisible antes de superar el límite óptimo de ', ('m', r('360 min')), ' para cachama es ',
     ('m', sub(r('d'), rp('máx')) + rp(' = (360 − 0.90)/3.99 ≈ 90.0 km')), '. En términos de teoría de grafos, los tiempos de ejecución empíricos verificaron '
     'la cota lineal ', ('m', r('O(|V| + |E|)')), ' de Cormen et al. [3] para BFS y confirmaron las curvas de deterioro térmico descritas '
     'por la FAO y la literatura ictiológica tropical [1], [2].')

heading('IV.  Conclusiones')

def concl(num, text):
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    p.paragraph_format.space_before = Pt(1)
    p.paragraph_format.space_after = Pt(2.5)
    p.paragraph_format.line_spacing = 1.05
    p.paragraph_format.left_indent = Inches(0.16)
    p.paragraph_format.first_line_indent = Inches(-0.16)
    run_fmt(p.add_run(f'{num}. '), 9, bold=True)
    run_fmt(p.add_run(text), 9)

concl(1, 'La consolidación de las 33 encuestas cartográficas en un grafo dirigido de 16 vértices y 24 aristas mediante listas de adyacencia '
         'en C++ permitió identificar formalmente que el 57.6 % de los pescadores converge en Bocas del Manacacías y el 42.4 % reporta '
         'deterioro en Manacacías Medio, validando la capacidad del TAD grafo para estructurar información hidrográfica heterogénea.')
concl(2, 'La resolución de la Incógnita 1 mediante BFS demostró que en la Red Actual el 60 % de los puntos de pesca (6/10) excede los '
         '360 min antes de acceder a refrigeración (promedio 373.0 min), mientras que la ubicación de los tres centros propuestos en Río '
         'Muco, Manacacías Medio y Bocas del Manacacías reduce dicho tiempo medio a 152.5 min (mejora de 59.1 %) con 0/10 puntos en riesgo.')
concl(3, 'El análisis exhaustivo de la Incógnita 2 vía DFS sobre 240 rutas simples probó que las trayectorias en estado óptimo para cachama '
         'de río se incrementan del 18.3 % (44/240) al 80.0 % (192/240), eliminando por completo las 147 rutas en deterioro crítico (>480 min) '
         'que impedían la llegada de producto sano a Villavicencio y Bogotá.')
concl(4, 'La regresión lineal de la Red Optimizada (t = 3.99 d + 0.90 min, R² = 0.9998) valida el régimen de navegación fluvial uniforme '
         'a 15.04 km/h y establece un radio de cobertura máximo de 90.0 km (±18.0 km) por cada centro de acopio con frío para garantizar la '
         'inocuidad pesquera en futuros nodos de la altillanura.')

heading('Referencias')

refs = [
    '[1] Organización de las Naciones Unidas para la Alimentación y la Agricultura (FAO), "El pescado fresco: su calidad y cambios de su calidad", Documento Técnico de Pesca 348, Roma, 1998.',
    '[2] M. A. Ramírez et al., "Evaluación sensorial y microbiológica de cachama (Colossoma macropomum) almacenada a temperatura ambiente y en refrigeración", Anales de Nutrición / SciELO, vol. 24, pp. 45–53, 2018.',
    '[3] T. H. Cormen, C. E. Leiserson, R. L. Rivest y C. Stein, Introduction to Algorithms, 4.ª ed. Cambridge, MA: MIT Press, 2022, pp. 549–572.',
    '[4] R. F. Gilberg y B. A. Forouzan, Data Structures: A Pseudocode Approach with C++, 2.ª ed. Boston, MA: Cengage Learning, 2004.',
    '[5] Grupo de Investigación GRITOX y Corporación Kotsala, "Piscicultura sostenible con especies nativas como alternativa productiva para pescadores artesanales en Puerto Gaitán, Meta", Universidad de los Llanos, Villavicencio, 2026.'
]
for rf in refs:
    pr = doc.add_paragraph()
    pr.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    pr.paragraph_format.space_before = Pt(0)
    pr.paragraph_format.space_after = Pt(2)
    pr.paragraph_format.line_spacing = 1.03
    pr.paragraph_format.left_indent = Inches(0.18)
    pr.paragraph_format.first_line_indent = Inches(-0.18)
    run_fmt(pr.add_run(rf), 8.0)

doc.save(OUT_DOCX)
print('Informe DOCX generado exitosamente en:', OUT_DOCX)

# Exportar a PDF via Word COM
try:
    import win32com.client as win32
    word = win32.Dispatch('Word.Application')
    word.Visible = False
    doc_word = word.Documents.Open(OUT_DOCX)
    doc_word.SaveAs(OUT_PDF, FileFormat=17)
    doc_word.Close()
    word.Quit()
    print('Informe PDF exportado exitosamente en:', OUT_PDF)
except Exception as e:
    print('Exportación a PDF omitida o fallida:', e)
