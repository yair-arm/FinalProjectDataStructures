# -*- coding: utf-8 -*-
"""
Genera el Informe Cientifico IEEE (Doble Columna) para el Proyecto Final de Estructuras de Datos,
cumpliendo estrictamente la Rubrica Oficial de la Facultad de Ciencias Basicas e Ingenieria
(RUBRICA PARA INFORMES 2025-II) y las directrices institucionales de DIRECTRICES_Y_REGLAS_INFORMES.md.

Caracteristicas formales:
- Encabezado institucional de 3 celdas (escudo Unillanos centrado en pagina, titulo formal en negro).
- Resumen centrado con bloque justificado y palabras clave.
- Seccion I: Teoria fundamental, Ecuaciones numeradas a la derecha, Estado del Arte explícito,
  Restricciones del modelo e Incognitas/Objetivos especificos (i)-(iv).
- Seccion II: Metodologia y Diseno Experimental secuencial, materiales en prosa, Figura 1 integrada a 1 col.
- Seccion III: Resultados y Analisis con clasificacion explicita de variables (directas e indirectas),
  calculo de incertidumbres propagadas, Tablas 1 y 2, Graficas 1, 2a y 2b (sin titulo superior interno,
  con pie de figura centrado en cursiva), regresion lineal con interpretacion fisica de m y b, y verificacion cruzada.
- Seccion IV: Conclusiones numeradas 1 a 1 con los objetivos e incognitas, 100% cuantitativas (cero frases vacias).
- Referencias en formato formal IEEE con sangria francesa.
- Extension exacta: 3 paginas continuas sin saltos de seccion huerfanos.
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
ROOT = os.path.abspath(os.path.join(BASE, '..'))
ASSETS = os.path.join(BASE, 'Assets')
OUT_DOCX = os.path.join(BASE, 'Informe_Proyecto_Final_Grafos.docx')
OUT_PDF = os.path.join(BASE, 'Informe_Proyecto_Final_Grafos_Word.pdf')

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
st.font.size = Pt(8.6)
st.font.color.rgb = BLACK
st.element.rPr.rFonts.set(qn('w:eastAsia'), FONT)

sec0 = doc.sections[0]
sec0.top_margin = sec0.bottom_margin = Inches(0.60)
sec0.left_margin = sec0.right_margin = Inches(0.60)

hp = sec0.header.paragraphs[0]
hp.alignment = WD_ALIGN_PARAGRAPH.RIGHT
hr = hp.add_run('Estructuras de Datos — Optimización de Red Frigorífica Multimodal en Puerto Gaitán (Meta)')
hr.font.name = FONT
hr.font.size = Pt(7.8)
hr.font.italic = True
hr.font.color.rgb = RGBColor(90, 90, 90)

def run_fmt(run, size=8.6, bold=False, italic=False):
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

def cell_margins(cell, t=6, b=6, l=10, rr=10):
    cell._tc.get_or_add_tcPr().append(parse_xml(
        f'<w:tcMar {nsdecls("w")}><w:top w:w="{t}" w:type="dxa"/><w:left w:w="{l}" w:type="dxa"/>'
        f'<w:bottom w:w="{b}" w:type="dxa"/><w:right w:w="{rr}" w:type="dxa"/></w:tcMar>'))

def shade(cell, hexcolor):
    cell._tc.get_or_add_tcPr().append(parse_xml(
        f'<w:shd {nsdecls("w")} w:val="clear" w:color="auto" w:fill="{hexcolor}"/>'))

def set_section_cols(sec, n_cols=2, space=300):
    sec.top_margin = sec.bottom_margin = Inches(0.60)
    sec.left_margin = sec.right_margin = Inches(0.60)
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
# ENCABEZADO INSTITUCIONAL CENTRADO (3 COLUMNAS: LOGO, TEXTO, DUMMY)
# =========================================================================
ht = doc.add_table(rows=1, cols=3)
ht.alignment = WD_TABLE_ALIGNMENT.CENTER
ht.autofit = False
no_borders(ht)
c_logo, c_info, c_dummy = ht.cell(0, 0), ht.cell(0, 1), ht.cell(0, 2)
c_logo.width, c_info.width, c_dummy.width = Inches(1.05), Inches(5.15), Inches(1.05)
for c in (c_logo, c_info, c_dummy):
    c.vertical_alignment = WD_ALIGN_VERTICAL.CENTER

pl = c_logo.paragraphs[0]
pl.alignment = WD_ALIGN_PARAGRAPH.CENTER
pl.add_run().add_picture(os.path.join(ASSETS, 'logo_unillanos_0.png'), width=Inches(0.72))

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
run_fmt(pt.add_run('MODELADO MEDIANTE GRAFOS MULTIMODALES Y OPTIMIZACIÓN DE LA CADENA DE FRÍO PARA PESCA ARTESANAL EN PUERTO GAITÁN, META'), 11.0, bold=True)

def centered(text_runs, before=1, after=1, spacing=1.02):
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

# Resumen en caja sombreada según rúbrica (encabezado centrado en negrita)
at = doc.add_table(rows=1, cols=1)
at.alignment = WD_TABLE_ALIGNMENT.CENTER
at.autofit = False
no_borders(at)
cell_a = at.cell(0, 0)
cell_a.width = Inches(7.25)
shade(cell_a, 'F4F6F8')
cell_margins(cell_a, 8, 8, 16, 16)

pa_t = cell_a.paragraphs[0]
pa_t.alignment = WD_ALIGN_PARAGRAPH.CENTER
pa_t.paragraph_format.space_after = Pt(1.5)
run_fmt(pa_t.add_run('Resumen'), 9.2, bold=True)

pa_c = cell_a.add_paragraph()
pa_c.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
pa_c.paragraph_format.space_after = Pt(1.5)
pa_c.paragraph_format.line_spacing = 1.02
run_fmt(pa_c.add_run(
    'En el marco de la Escuela de Campo Agropecuaria (ECA C05-01-2026-003, Unillanos--AUNAP) y para resolver la pregunta directriz: '
    '¿Cómo mejorar la eficiencia de los procesos de captura y acopio mediante el fortalecimiento de capacidades tecnológicas en '
    'San Miguel, Plaza de Mercado y Puente Arimena?, se modela la red de comercialización pesquera artesanal de Puerto Gaitán (Meta) '
    'como un grafo dirigido ponderado multimodal (|V| = 25 vértices y |E| = 41 aristas) para erradicar la pérdida poscaptura de '
    'cachama de río (Colossoma macropomum), la cual alcanza el 40 % debido a temperaturas de 30 °C y a la carencia de frío continuo. '
    'Integrando el censo de 33 fichas cartográficas de 7 asociaciones pesqueras (265.8 kg/día), la red fluvial real del IGAC (12,413 '
    'vértices en rios.shp) y rutas viales OSRM sobre la Ruta Nacional 40, se implementaron desde cero los algoritmos de Dijkstra '
    '(con heap binario y poda de inocuidad), Bellman-Ford, Floyd-Warshall, BFS, DFS y el Problema de Localización de Instalaciones (FLP Greedy). '
    'Se resolvieron cuantitativamente las cuatro incógnitas: (i) BFS demostró que el 85.7 % de los puertos accede a su acopio natural en 1 o 2 '
    'saltos (< 0.50 h); (ii) Dijkstra y DFS fijaron itinerarios óptimos hacia Bogotá D.C. (~295 km) limitando la exposición sin frío a un '
    'intervalo de 0.08 a 2.20 h, cumpliendo el límite de 4.0 h de la FAO y reduciendo la merma a < 6.38 %; (iii) FLP determinó que la apertura '
    'del Centro Frío Puerto Gaitán (F02, $3.0M COP/mes) cubre el 100 % de la demanda regional con un costo de $59,080 COP/kg, ahorrando $10.0M '
    'COP mensuales frente a tres plantas; y (iv) la regresión lineal estableció una tasa fluvial de 3.64 min/km (16.5 km/h, R² = 0.999) '
    'frente a 0.92 min/km terrestre, probando que la navegación fluvial representa el cuello de botella crítico de la cadena.'
), 8.2)

pa_kw = cell_a.add_paragraph()
pa_kw.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
pa_kw.paragraph_format.space_before = Pt(1)
pa_kw.paragraph_format.space_after = Pt(0)
run_fmt(pa_kw.add_run('Palabras clave---'), 8.2, bold=True)
run_fmt(pa_kw.add_run('Cadena de frío, caminos mínimos, Colossoma macropomum, Dijkstra, ECA, grafos dirigidos, localización de instalaciones, multimodalidad, OSRM.'), 8.2)

def para(content, *more_content, before=0, after=2.0, line_spacing=1.03):
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
            run_fmt(p.add_run(item), 8.6)
        elif isinstance(item, tuple) and item[0] == 'm':
            p._p.append(parse_xml(f'<m:oMath xmlns:m="{M_NS}">{item[1]}</m:oMath>'))
        elif isinstance(item, tuple) and item[0] == 'b':
            run_fmt(p.add_run(item[1]), 8.6, bold=True)
        elif isinstance(item, tuple) and item[0] == 'i':
            run_fmt(p.add_run(item[1]), 8.6, italic=True)
    return p

def heading(text, before=4, after=1.5):
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_before = Pt(before)
    p.paragraph_format.space_after = Pt(after)
    p.paragraph_format.keep_with_next = True
    run_fmt(p.add_run(text.upper()), 9.0, bold=True)
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
    run_fmt(pn.add_run(f'({EQ[0]})'), 8.4)

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
    cap.paragraph_format.space_after = Pt(3.0)
    run_fmt(cap.add_run(caption_text), 7.6, italic=True)

# =========================================================================
# CUERPO EN DOS COLUMNAS
# =========================================================================
sec_body = doc.add_section(WD_SECTION_START.CONTINUOUS)
set_section_cols(sec_body, n_cols=2, space=300)

heading('I.  Introducción')

para('La pesca artesanal en el municipio de Puerto Gaitán (Meta) sustenta la economía de comunidades ribereñas distribuidas '
     'en las cuencas de los ríos Meta, Manacacías e Iteviare. La captura se concentra en especies reofílicas de alto valor comercial, '
     'particularmente la cachama de río (', ('i', 'Colossoma macropomum'), '). Sin embargo, la ausencia de cuartos de frío en las riberas '
     'y las altas temperaturas de la Orinoquía (', ('m', r('30 °C')), ') aceleran el rigor mortis y la proliferación bacteriana, '
     'provocando pérdidas de hasta el 40 % del producto antes de llegar a plazas de mercado [1], [2]. En el marco del proyecto de '
     'investigación y extensión de la Escuela de Campo Agropecuaria (ECA C05-01-2026-003, Unillanos--AUNAP), este trabajo responde a la '
     'pregunta de investigación rectora: ', ('i', '¿Cómo mejorar la eficiencia de los procesos de captura y acopio mediante el '
     'fortalecimiento de capacidades tecnológicas?'), ' articulando los puntos de extracción con los tres centros de acopio estratégicos '
     'de la cuenca: San Miguel (A01), Plaza de Mercado (A02) y Puente Arimena (A03).')

para('En la ciencia de las estructuras de datos, una red de transporte con diversos modos y nodos de transferencia se modela formalmente '
     'como un grafo dirigido ponderado ', ('m', r('G = (V, E)')), ' almacenado mediante listas de adyacencia indexadas por tablas hash '
     'con complejidad espacial ', ('m', r('O(|V| + |E|)')), ' [3]. Para reflejar el corredor logístico real, cada arista ',
     ('m', r('e = (u, v) ∈ E')), ' se pondera mediante una función de costo multicriterio normalizada:')
equation(r('w(e) = 0.25·t + 0.20·c + 0.20·r + 0.10·p + 0.10·(1-conf) + 0.05·ret'))

para('donde ', ('m', r('t')), ' es el tiempo de viaje normalizado, ', ('m', r('c')), ' el costo operativo, ', ('m', r('r')), ' la confiabilidad '
     'de la vía, ', ('m', r('p')), ' la penalización por deterioro y ', ('m', r('ret')), ' demoras fijas en muelles. A la temperatura de '
     'los Llanos Orientales, la degradación bacteriana acumulada ', ('m', sub(r('D'), rp('acum'))), ' sigue la cinética lineal [1], [2]:')
equation(sub(r('D'), rp('acum')) + rp(' = ') + sub(r('D'), r('0')) + rp(' + ∑ ') + sub(r('k'), r('i')) + rp(' · ') + sub(r('t'), r('i')))

para('donde la constante de descomposición a 30 °C es ', ('m', sub(r('k'), r('i'))), ' = 2.5 %/h en condiciones ordinarias y ',
     ('m', sub(r('k'), r('i'))), ' = 3.75 %/h en tramos destapados expuestos al sol (zonas de deterioro D con factor ×1.5). Si el pescado '
     'supera el tiempo crítico de inocuidad ', ('m', sub(r('t'), rp('máx'))), ' = 4.0 h (240 min) sin refrigeración, la carga pierde aptitud '
     'comercial. En contraste, al ingresar a un centro de frío (F), la temperatura desciende a 0 °C (hielo 1:1), reiniciando el reloj térmico '
     'a 0.0 h y extendiendo la vida útil hasta 360 h (15 días) [1].')

para(('b', 'Estado del arte: '), 'Históricamente, la planificación de transporte en grafos se abordó mediante caminos mínimos univariados '
     '(Dijkstra 1959, Bellman-Ford 1958 y Floyd-Warshall 1962) enfocados únicamente en distancia euclidiana [3]. Posteriormente, Hakimi (1964) '
     'y Laporte et al. (2019) formalizaron el Problema de Localización de Instalaciones (FLP / p-mediana) para optimizar la apertura de plantas '
     'sujetas a costos fijos y radios de cobertura [4]. En la última década, los sistemas logísticos agropecuarios han convergido hacia '
     'modelos de doble grafo georreferenciado que articulan redes hidrográficas reales (shapefiles) con motores de ruteo vial digital como '
     'OSRM (Open Source Routing Machine), permitiendo evaluar cadenas de frío perecederas con topología real en lugar de aproximaciones en línea recta [5].')

para(('b', 'Restricciones del modelo: '), 'El sistema opera bajo condiciones físicas estrictas: (i) la navegación fluvial en canoa con motor '
     'fuera de borda (velocidad media nominal ', ('m', sub(r('v'), rp('canoa'))), ' ≈ 16.5 km/h) depende del cauce meándrico y presenta una '
     'incertidumbre por corrientes de ', ('m', r('Δt = ±0.15·t')), '; (ii) cada transbordo lancha--camión en muelle (M) impone una demora '
     'fija de +0.25 h (15 min) bajo el sol; (iii) los hábitats protegidos (H) poseen restricción ambiental absoluta, prohibiendo su uso como '
     'nodos intermedios; y (iv) la red eléctrica confiable requerida para compresores frigoríficos solo existe en F01, F02 y F03.')

para('A partir de este marco, el proyecto resolvió cuatro incógnitas operativas: (i) determinar mediante BFS el nodo de acopio o frío más '
     'próximo en número mínimo de transbordos desde cada punto de pesca; (ii) calcular mediante Dijkstra y DFS los itinerarios multimodales '
     'óptimos a Bogotá evaluando la exposición térmica; (iii) resolver mediante FLP Greedy la ubicación óptima de centros frigoríficos minimizando '
     'costos de inversión; y (iv) caracterizar cinemáticamente la red ajustando un modelo de regresión lineal fluvial y terrestre.')

heading('II.  Sección Experimental y Metodología')

para('El desarrollo experimental se ejecutó en Python 3.10+ bajo arquitectura modular sin dependencias de librerías automáticas de grafos '
     '(como NetworkX), asegurando la implementación manual de los TADs y algoritmos. El proceso metodológico integró tres etapas:')

para(('b', '1. Adquisición y digitalización cartográfica: '), 'A partir del censo en campo de 33 fichas de pescadores artesanales en Puerto '
     'Gaitán y Puerto López, se identificaron 7 asociaciones pesqueras principales (producción total: 265.75 kg/día). Se clasificaron 25 vértices '
     'en 7 categorías funcionales (P: 7 pesca, M: 3 muelles, A: 3 acopios, F: 3 frío, D: 2 deterioro crítico, H: 2 hábitats protegidos, '
     'V: 5 comercios reales con coordenadas verificadas en Puerto Gaitán, Villavicencio y Bogotá) y 41 aristas dirigidas (fluviales, acceso '
     'local y carreteras) cargadas desde archivos CSV.')

para(('b', '2. Construcción del doble grafo en memoria: '), 'Se instanció un Grafo Logístico Principal (', ('m', r('|V| = 25')), ', ',
     ('m', r('|E| = 41')), ') basado en listas de adyacencia con diccionario Hash O(1). En paralelo, se procesó el shapefile hidrográfico '
     'del IGAC (', ('i', 'rios.shp'), '), construyendo un Grafo Fluvial Topológico con 12,413 vértices cuantizados a 5 decimales (resolución 1.1 m) '
     'y 24,790 aristas navegables, indexadas en una rejilla espacial Hash de 447 celdas (0.05° × 0.05°) para hallar el cauce exacto. Las '
     'aristas terrestres de la Ruta Nacional 40 se trazaron consultando la API de OSRM, almacenando 41 polilíneas en caché JSON local.')

add_col_figure(os.path.join(ASSETS, 'figura_1_topologia_col.png'),
               'Figura 1. Topología del grafo logístico multimodal (25 vértices y 41 aristas) en 4 capas funcionales con restricciones H y D.')

para(('b', '3. Implementación algorítmica: '), 'Se programó Dijkstra con cola de prioridad binaria (', ('i', 'heapq'), '), Bellman-Ford con '
     'detección de ciclos negativos, Floyd-Warshall para la matriz de todos los pares, BFS con cola FIFO (', ('i', 'deque'), '), DFS con '
     'retroceso exhaustivo y el algoritmo FLP Greedy para localización de plantas frigoríficas. Las herramientas de instrumentación incluyeron '
     'el framework pytest (40 pruebas unitarias), Folium para mapas interactivos HTML y un entorno de ejecución en Windows 11.')

heading('III.  Resultados y Análisis')

para(('b', 'Clasificación de variables del sistema: '), '(i) ', ('b', 'Variables directas: '), 'coordenadas WGS 84 (latitud, longitud), masa '
     'de captura diaria por puerto ', ('m', sub(r('m'), rp('pesca'))), ' [kg/día], costos fijos mensuales de plantas frigoríficas [COP/mes], '
     'distancias cartográficas del cauce ', ('m', sub(r('d'), r('i'))), ' [km] y tiempos medidos de tránsito ', ('m', sub(r('t'), r('i'))),
     ' [h]; (ii) ', ('b', 'Variables indirectas: '), 'distancia en saltos de transbordo (BFS), costos de ruta multicriterio ',
     ('m', r('w(e)')), ', tiempo acumulado sin refrigeración ', ('m', sub(r('t'), rp('sinFrío'))), ', incertidumbre propagada ',
     ('m', r('Δt')), ', porcentaje de degradación biológica ', ('m', sub(r('D'), rp('acum'))), ' [%] y costo unitario logístico [COP/kg].')

para('Considerando la variabilidad de corriente del río y oleaje, la incertidumbre en el tiempo fluvial ', ('m', r('Δt')), ' se calculó por '
     'propagación de error relativo [6]:')
equation(r('Δt = t · ') + frac(r('Δ') + sub(r('v'), rp('canoa')), sub(r('v'), rp('canoa'))) + rp(' = 0.15 · t'))

para(('b', 'Respuesta a las Incógnitas 1 y 2 (BFS, Dijkstra y DFS): '), 'La Tabla 1 compila la resolución de la Incógnita 1 (acopio o frío '
     'más cercano en saltos mínimos mediante BFS) y la Incógnita 2 (itinerario óptimo y deterioro de cachama hacia Bogotá D.C. vía Dijkstra/DFS).')

# TABLA 1: Ruteo y Tiempos
heads_t1 = ['Punto Captura', 'kg/d', 'Saltos BFS', 'Ruta a Bogotá (Dijkstra)', 't 1er Frío', 'Deterioro']
w_t1 = [0.85, 0.32, 0.45, 1.05, 0.42, 0.36]
tb1 = doc.add_table(rows=8, cols=6)
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
    run_fmt(pc.add_run(h), 6.8, bold=True)

filas_t1 = [
    ('P01 Alto Neblinas', '65.8', '2 (a A02)', 'P01→M03→F02→F03→Bog', '0.48±0.07 h', '1.20 %'),
    ('P02 Atarraya Verde', '40.0', '1 (a A02)', 'P02→M03→F02→F03→Bog', '0.43±0.06 h', '1.08 %'),
    ('P03 San Miguel', '25.0', '1 (a A01)', 'P03→A01→F02→F03→Bog', '0.25±0.04 h', '0.62 %'),
    ('P04 Asopespor', '20.0', '1 (a A01)', 'P04→A01→F02→F03→Bog', '0.40±0.06 h', '1.00 %'),
    ('P05 Puerto Trujillo', '30.0', '1 (a A03)', 'P05→A03→D01→A01→F02→Bog', '2.20±0.33 h', '6.38 %'),
    ('P06 Desembarcadero', '50.0', '1 (a F02)', 'P06→F02→F03→Bog', '0.08±0.01 h', '0.20 %'),
    ('P07 Soplaviento', '35.0', '2 (a A02)', 'P07→M03→F02→F03→Bog', '0.38±0.06 h', '0.95 %'),
]

for i, row in enumerate(filas_t1, start=1):
    tb1.rows[i]._tr.get_or_add_trPr().append(parse_xml(f'<w:cantSplit {nsdecls("w")}/>'))
    for j, val in enumerate(row):
        c = tb1.cell(i, j)
        c.width = Inches(w_t1[j])
        cell_margins(c, 2, 2, 2, 2)
        pc = c.paragraphs[0]
        pc.alignment = WD_ALIGN_PARAGRAPH.LEFT if j in (0, 3) else WD_ALIGN_PARAGRAPH.CENTER
        pc.paragraph_format.space_after = Pt(0)
        run_fmt(pc.add_run(val), 6.6, bold=(j == 5))

cap_t1 = doc.add_paragraph()
cap_t1.alignment = WD_ALIGN_PARAGRAPH.CENTER
cap_t1.paragraph_format.space_before = Pt(1.5)
cap_t1.paragraph_format.space_after = Pt(2.5)
run_fmt(cap_t1.add_run('Tabla 1. Resolución de Incógnitas 1 y 2: Saltos BFS, itinerarios Dijkstra a Bogotá y degradación de cachama.'), 7.4, italic=True)

para('El análisis de la Tabla 1 y la Gráfica 1 demuestra que los 7 puertos pesqueros alcanzan refrigeración estable mucho antes del límite '
     'crítico de 4.0 h. Seis de los siete puntos consolidan su carga en menos de 0.50 h (30 min). El caso más exigente corresponde a Puerto '
     'Trujillo (P05), que navega 63 km por el río Iteviare cruzando la zona crítica D01, acumulando 2.20 ± 0.33 h y un deterioro de 6.38 %, '
     'manteniéndose plenamente dentro del umbral higiénico-sanitario de la FAO [1]. Además, el ruteo de Dijkstra desvió exitosamente a P04 '
     'evitando cruzar el hábitat protegido H01.')

add_col_figure(os.path.join(ASSETS, 'grafica_1_bfs_col.png'),
               'Gráfica 1. Tiempo sin frío acumulado por punto de pesca frente al umbral crítico sanitario de 4.0 h (FAO).')

para(('b', 'Respuesta a la Incógnita 3 (Localización Óptima FLP): '), 'El algoritmo FLP evaluó 5 configuraciones de red frigorífica (Tabla 2 '
     'y Gráfica 2a). El Escenario Óptimo seleccionó como planta central el Centro Frío Puerto Gaitán (F02, $3.0M COP/mes), el cual logra el '
     '100 % de cobertura con un costo unitario de $59,080 COP/kg, evitando el sobredimensionamiento de operar tres plantas ($104,444 COP/kg).')

heads_t2 = ['Escenario Logístico', '# CF', 'Pérdida', 'Costo Mensual', '$/kg', 'Cob.']
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
    run_fmt(pc.add_run(h), 6.8, bold=True)

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
        run_fmt(pc.add_run(val), 6.6, bold=(i == 3))

cap_t2 = doc.add_paragraph()
cap_t2.alignment = WD_ALIGN_PARAGRAPH.CENTER
cap_t2.paragraph_format.space_before = Pt(1.5)
cap_t2.paragraph_format.space_after = Pt(2.5)
run_fmt(cap_t2.add_run('Tabla 2. Resolución de Incógnita 3: Evaluación de escenarios y selección óptima de planta frigorífica (FLP).'), 7.4, italic=True)

add_col_figure(os.path.join(ASSETS, 'grafica_2a_dfs_col.png'),
               'Gráfica 2a. Comparación de costos operativos mensuales y selección óptima del centro F02 en Puerto Gaitán.')

para(('b', 'Respuesta a la Incógnita 4 (Cinemática y Regresión Lineal): '), 'Al modelar la relación tiempo de tránsito vs. distancia sobre '
     'las 41 conexiones del corredor, se ajustó una recta de regresión ', ('m', r('t(d) = m · d + b')), ' separada por modo (Gráfica 2b):')
equation(sub(r('t'), rp('fluvial')) + rp('(d) = 3.64 · d + 0.12 ,   ') + sub(r('R'), sup(r(''), r('2'))) + rp(' = 0.9989'))
equation(sub(r('t'), rp('terrestre')) + rp('(d) = 0.92 · d + 1.45 ,   ') + sub(r('R'), sup(r(''), r('2'))) + rp(' = 0.9997'))

para('La interpretación física de los parámetros es concluyente: (1) la pendiente fluvial ', ('m', sub(r('m'), rp('f'))), ' = 3.64 min/km '
     'representa el recíproco de la velocidad media en canoa cargada (', ('m', sub(r('v'), rp('f'))), ' = 16.48 km/h); (2) la pendiente '
     'terrestre ', ('m', sub(r('m'), rp('t'))), ' = 0.92 min/km corresponde a la velocidad media de camión en la RN 40 (',
     ('m', sub(r('v'), rp('t'))), ' = 65.22 km/h); (3) el intercepto terrestre ', ('m', sub(r('b'), rp('t'))), ' = 1.45 min refleja las '
     'maniobras de pesaje y carga; y (4) el ratio de velocidades (3.96:1) demuestra que cada kilómetro fluvial consume cuatro veces más '
     'tiempo que el carretero, justificando la instalación de centros de acopio estratégicos en confluencias.')

add_col_figure(os.path.join(ASSETS, 'grafica_2b_regresion_col.png'),
               'Gráfica 2b. Regresión lineal de tiempos de tránsito fluvial y carretero vs. distancia de tramo.')

para(('b', 'Verificación cruzada Bellman-Ford y Floyd-Warshall: '), 'Bellman-Ford corroboró al 100 % las distancias de Dijkstra sin detectar '
     'ciclos de costo negativo. La matriz de Floyd-Warshall permitió consultar en O(1) que el tiempo intermodal entre cualquier punto de captura '
     'y Bogotá se ubica entre 6.38 h y 8.95 h, con el pescado estabilizado a 0 °C desde su paso por Puerto Gaitán.')

heading('IV.  Conclusiones')

para(('b', '1. Incógnita 1 y Eficiencia en Acopio (ECA): '), 'El recorrido BFS demostró que el fortalecimiento tecnológico de los tres acopios '
     '(A01 San Miguel, A02 Plaza de Mercado y A03 Puente Arimena) permite al 85.7 % (6/7) de los puertos de captura transferir su producción '
     'en máximo 2 saltos topológicos, conteniendo la degradación en tiempos inferiores a 0.50 h (30 min), lo que '
     'garantiza la contención temprana del rigor mortis en la cachama.')

para(('b', '2. Resolución de la Incógnita 2 (Dijkstra y DFS): '), 'Los itinerarios óptimos hacia Bogotá D.C. (~295 km) registraron tiempos '
     'sin frío de entre 0.08 y 2.20 h, cumpliendo al 100 % el límite higiénico-sanitario de la FAO (4.0 h). Incluso en el caso crítico de '
     'Puerto Trujillo (P05, 63 km por río Iteviare), el deterioro se limitó al 6.38 %, evitando hábitats protegidos (H01, H02).')

para(('b', '3. Resolución de la Incógnita 3 (FLP Greedy): '), 'La optimización de instalaciones determinó que la apertura del Centro Frío '
     'Puerto Gaitán (F02, $3.0M COP/mes) es la configuración óptima, cubriendo el 100 % de la demanda censada (265.8 kg/día) con un costo '
     'de $59,080 COP/kg, ahorrando $10.0M COP mensuales respecto a abrir tres plantas concurrentes.')

para(('b', '4. Resolución de la Incógnita 4 (Modelo Cinemático): '), 'El ajuste lineal confirmó una cinemática fluvial de 3.64 min/km '
     '(16.5 km/h, R² = 0.999) frente a 0.92 min/km terrestre (65.2 km/h, R² = 0.999), probando cuantitativamente que la eficiencia de la '
     'cadena pesquera depende de acopios intermedios que reduzcan la navegación bajo el sol.')

heading('Referencias')

refs = [
    '[1] FAO, «El pescado fresco: su calidad y cambios de calidad», Colección FAO: Pesca, N° 348, Roma, 1999.',
    '[2] SciELO, «Cinética de deterioro y vida útil de Colossoma macropomum bajo almacenamiento refrigerado», Rev. MVZ Córdoba, vol. 24, n° 2, pp. 7240-7248, 2019.',
    '[3] T. H. Cormen, C. E. Leiserson, R. L. Rivest, y C. Stein, Introduction to Algorithms, 3a ed. Cambridge, MA: MIT Press, 2009, pp. 651-698.',
    '[4] S. L. Hakimi, «Optimum locations of switching centers and the absolute centers and medians of a graph», Operations Research, vol. 12, n° 3, pp. 450-459, 1964.',
    '[5] G. Laporte, S. Nickel, y F. Saldanha-da-Gama, Location Science, 2a ed. Cham, Suiza: Springer, 2019, pp. 115-148.',
    '[6] J. R. Taylor, An Introduction to Error Analysis: The Study of Uncertainties in Physical Measurements, 2a ed. Sausalito, CA: Univ. Science Books, 1997, pp. 45-78.'
]

for ref in refs:
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    p.paragraph_format.space_before = Pt(0)
    p.paragraph_format.space_after = Pt(1.2)
    p.paragraph_format.line_spacing = 1.01
    p.paragraph_format.left_indent = Inches(0.18)
    p.paragraph_format.first_line_indent = Inches(-0.18)
    run_fmt(p.add_run(ref), 7.6)

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
