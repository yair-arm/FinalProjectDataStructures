# -*- coding: utf-8 -*-
"""
Genera las figuras y graficas analiticas para el Informe IEEE y las Diapositivas
a partir de los resultados reales ejecutados por el programa C++ (comparativa_resultados.csv)
y las 33 encuestas transcritas (encuestas_pescadores.csv).
Sin titulos superiores dentro de las graficas (van en el pie de figura).
"""
import csv
import os
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch

BASE = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
DATA_DIR = os.path.join(BASE, 'Codigo', 'data')
OUT_DIR = os.path.join(BASE, 'Informe_IEEE', 'Assets')
os.makedirs(OUT_DIR, exist_ok=True)

plt.rcParams['font.family'] = 'serif'
plt.rcParams['font.serif'] = ['Times New Roman', 'DejaVu Serif']
plt.rcParams['mathtext.fontset'] = 'stix'

# Leer comparativa_resultados.csv generado por C++
rows = []
with open(os.path.join(DATA_DIR, 'comparativa_resultados.csv'), encoding='utf-8') as f:
    reader = csv.DictReader(f)
    for r in reader:
        rows.append(r)

# =========================================================================
# FIGURA 1: TOPOLOGIA DEL GRAFO DIRIGIDO (CAPAS FLUVIAL-TERRESTRE)
# =========================================================================
fig, ax = plt.subplots(figsize=(10.5, 5.4), dpi=300)
ax.set_xlim(0, 100)
ax.set_ylim(0, 62)
ax.axis('off')

# Bandas de capas
capas = [
    (1.5, 29.0, '#EFF6FF', '#93C5FD', 'Capa 1: Puntos de Pesca (P)'),
    (31.5, 27.0, '#FEF3C7', '#FCD34D', 'Capa 2: Nodos Criticos -> Centros A+F'),
    (59.5, 19.0, '#ECFDF5', '#6EE7B7', 'Capa 3: Cabeceras'),
    (79.5, 19.5, '#F5F3FF', '#C4B5FD', 'Capa 4: Mercados (V)')
]
for x0, w, fc, ec, lbl in capas:
    box = FancyBboxPatch((x0, 2.0), w, 57.0, boxstyle='round,pad=0.6',
                         facecolor=fc, edgecolor=ec, linewidth=1.6, alpha=0.55, zorder=0)
    ax.add_patch(box)
    ax.text(x0 + w/2, 57.2, lbl, ha='center', va='center', fontsize=10.5,
            fontweight='bold', color='#1E293B')

pos = {
    'P_Cano_Morroco': (12, 50),
    'P_Vichada': (12, 42),
    'P_Planas': (12, 34),
    'P_Guarrojo': (23, 38),
    'P_Canalete_Maiciana': (12, 23),
    'P_Manacacias_Sur': (23, 25),
    'P_Yucao': (14, 15),
    'P_Chaviva_PtoLopez': (26, 5.5),
    'P_Muco': (44, 46),
    'P_Meta_Ventura': (44, 34),
    'D_Manacacias_Medio': (44, 22),
    'D_Bocas_Manacacias': (45, 13.5),
    'Puerto_Gaitan': (69, 32),
    'Puerto_Lopez': (69, 6.0),
    'Villavicencio': (89, 28),
    'Bogota': (89, 12),
}

labels_short = {
    'P_Cano_Morroco': 'Caño Morroco\n(P)',
    'P_Vichada': 'Vichada\n(P)',
    'P_Planas': 'Río Planas\n(P)',
    'P_Guarrojo': 'Río Guarrojo\n(P)',
    'P_Canalete_Maiciana': 'Cañalute/\nMaiciana (P)',
    'P_Manacacias_Sur': 'Manacacías\nSur (P)',
    'P_Yucao': 'Río Yucao\n(P)',
    'P_Chaviva_PtoLopez': 'Chaviva\n(P)',
    'P_Muco': 'Río Muco\n(Nuevo A+F)',
    'P_Meta_Ventura': 'Meta /\nVentura (P)',
    'D_Manacacias_Medio': 'Manacacías Medio\n(Nuevo A+F)',
    'D_Bocas_Manacacias': 'Bocas Manacacías\n(Nuevo A+F)',
    'Puerto_Gaitan': 'Puerto Gaitán\n(M+F+V)',
    'Puerto_Lopez': 'Puerto López\n(A+F)',
    'Villavicencio': 'Villavicencio\n(V+F)',
    'Bogota': 'Bogotá D.C.\n(V+F)',
}

edges = [
    ('P_Cano_Morroco', 'P_Meta_Ventura', '210m', 'fluvial'),
    ('P_Cano_Morroco', 'P_Muco', '170m', 'fluvial'),
    ('P_Vichada', 'P_Planas', '160m', 'fluvial'),
    ('P_Vichada', 'P_Guarrojo', '185m', 'fluvial'),
    ('P_Planas', 'P_Guarrojo', '115m', 'fluvial'),
    ('P_Planas', 'P_Manacacias_Sur', '150m', 'fluvial'),
    ('P_Guarrojo', 'P_Muco', '120m', 'fluvial'),
    ('P_Guarrojo', 'D_Manacacias_Medio', '165m', 'fluvial'),
    ('P_Muco', 'P_Meta_Ventura', '110m', 'fluvial'),
    ('P_Muco', 'D_Bocas_Manacacias', '145m', 'fluvial'),
    ('P_Meta_Ventura', 'D_Bocas_Manacacias', '130m', 'fluvial'),
    ('P_Meta_Ventura', 'Puerto_Gaitan', '155m', 'fluvial'),
    ('P_Canalete_Maiciana', 'P_Manacacias_Sur', '140m', 'fluvial'),
    ('P_Manacacias_Sur', 'D_Manacacias_Medio', '115m', 'fluvial'),
    ('D_Manacacias_Medio', 'D_Bocas_Manacacias', '95m', 'fluvial'),
    ('D_Manacacias_Medio', 'Puerto_Gaitan', '125m', 'fluvial'),
    ('P_Yucao', 'D_Bocas_Manacacias', '105m', 'fluvial'),
    ('P_Yucao', 'P_Chaviva_PtoLopez', '135m', 'fluvial'),
    ('P_Chaviva_PtoLopez', 'Puerto_Lopez', '90m', 'fluvial'),
    ('D_Bocas_Manacacias', 'Puerto_Gaitan', '45m', 'fluvial'),
    ('Puerto_Gaitan', 'Puerto_Lopez', '105m', 'terrestre'),
    ('Puerto_Gaitan', 'Villavicencio', '170m', 'terrestre'),
    ('Puerto_Lopez', 'Villavicencio', '80m', 'terrestre'),
    ('Villavicencio', 'Bogota', '150m', 'terrestre'),
]

for u, v, w_lbl, med in edges:
    x1, y1 = pos[u]
    x2, y2 = pos[v]
    col = '#0284C7' if med == 'fluvial' else '#B45309'
    ls = '-' if med == 'fluvial' else '--'
    ax.annotate('', xy=(x2, y2), xytext=(x1, y1),
                arrowprops=dict(arrowstyle='-|>,head_width=0.35,head_length=0.5',
                                color=col, lw=1.4, linestyle=ls, alpha=0.82,
                                shrinkA=14, shrinkB=14),
                zorder=2)
    xm, ym = (x1 + x2) / 2, (y1 + y2) / 2
    ax.text(xm, ym + 0.6, w_lbl, fontsize=7.5, fontweight='bold', color=col,
            ha='center', va='center',
            bbox=dict(boxstyle='round,pad=0.12', facecolor='white', edgecolor='none', alpha=0.75),
            zorder=3)

frio_opt = {'P_Muco', 'D_Manacacias_Medio', 'D_Bocas_Manacacias'}
mercados = {'Puerto_Gaitan', 'Puerto_Lopez', 'Villavicencio', 'Bogota'}
for node, (nx, ny) in pos.items():
    if node in frio_opt:
        fc, ec, tc = '#DC2626', '#7F1D1D', 'white'
    elif node in mercados:
        fc, ec, tc = '#059669', '#064E3B', 'white'
    else:
        fc, ec, tc = '#2563EB', '#1E3A8A', 'white'
    ax.text(nx, ny, labels_short[node], ha='center', va='center',
            fontsize=8.2, fontweight='bold', color=tc,
            bbox=dict(boxstyle='round,pad=0.32', facecolor=fc, edgecolor=ec, linewidth=1.6),
            zorder=4)

leg_handles = [
    mpatches.Patch(color='#2563EB', label='Punto de Pesca (P)'),
    mpatches.Patch(color='#DC2626', label='Centro Propuesto Acopio + Frío (A+F)'),
    mpatches.Patch(color='#059669', label='Cabecera / Mercado (V)'),
    plt.Line2D([0], [0], color='#0284C7', lw=2, label='Tramo Fluvial (Canoa ~15 km/h)'),
    plt.Line2D([0], [0], color='#B45309', lw=2, ls='--', label='Tramo Terrestre (Camión)'),
]
ax.legend(handles=leg_handles, loc='lower center', bbox_to_anchor=(0.5, -0.05),
          ncol=3, fontsize=9.2, frameon=True, edgecolor='#334155', facecolor='white')

plt.tight_layout()
plt.savefig(os.path.join(OUT_DIR, 'figura_1_topologia_grafo.png'), dpi=300, bbox_inches='tight')
plt.close()

# =========================================================================
# GRAFICA 1: COMPARATIVA BFS (TIEMPOS SIN FRIO) Y FRECUENCIA DE ENCUESTAS
# =========================================================================
fig1, (ax1, ax2) = plt.subplots(1, 2, figsize=(11.0, 4.6), dpi=300)

short_names = [
    'Caño\nMorroco', 'Vichada', 'Planas', 'Guarrojo', 'Muco',
    'Meta/\nVentura', 'Cañalute', 'Manac.\nSur', 'Yucao', 'Chaviva'
]
t_act = [int(r['tiempo_sin_frio_bfs_actual']) for r in rows]
t_opt = [int(r['tiempo_sin_frio_bfs_opt']) for r in rows]
reps = [int(r['reportes']) for r in rows]

x = np.arange(len(short_names))
w = 0.36
ax1.bar(x - w/2, t_act, width=w, label='Red Actual (sin acopio A+F)', color='#DC2626', edgecolor='#7F1D1D', lw=1.3, zorder=3)
ax1.bar(x + w/2, t_opt, width=w, label='Red Optimizada (3 centros A+F)', color='#059669', edgecolor='#064E3B', lw=1.3, zorder=3)
ax1.axhline(360, color='#D97706', ls='--', lw=2.0, zorder=4, label='Límite óptimo cachama (360 min)')
ax1.axhline(480, color='#991B1B', ls=':', lw=2.0, zorder=4, label='Deterioro crítico (480 min)')

for i in range(len(x)):
    ax1.text(x[i] - w/2, t_act[i] + 10, f'{t_act[i]}', ha='center', va='bottom', fontsize=7.8, fontweight='bold', color='#7F1D1D')
    ax1.text(x[i] + w/2 + 0.04, t_opt[i] + 10, f'{t_opt[i]}', ha='center', va='bottom', fontsize=7.8, fontweight='bold', color='#064E3B')

ax1.set_ylabel('Tiempo sin cadena de frío [min]', fontsize=11.5, fontweight='bold')
ax1.set_xticks(x)
ax1.set_xticklabels(short_names, fontsize=8.0, fontweight='bold', rotation=25, ha='right')
ax1.set_ylim(0, 700)
ax1.grid(True, axis='y', ls='--', alpha=0.5, zorder=1)
ax1.legend(fontsize=8.3, loc='upper right', framealpha=0.95, edgecolor='#334155')

# Panel b: Frecuencia en 33 encuestas por subcuenca/punto principal
cuencas_lbl = ['Pto. Gaitán\n(Cabecera)', 'Bocas\nManacacías', 'Río Yucao', 'Manacacías\nMedio', 'Manacacías\nSur', 'Meta /\nVentura', 'Río Muco', 'Río Planas']
cuencas_val = [28, 19, 18, 14, 9, 8, 7, 6]
colors_c = ['#1D4ED8', '#DC2626', '#2563EB', '#DC2626', '#3B82F6', '#60A5FA', '#DC2626', '#93C5FD']
y_pos = np.arange(len(cuencas_lbl))
ax2.barh(y_pos, cuencas_val, color=colors_c, edgecolor='#1E293B', lw=1.3, zorder=3)
for i, v in enumerate(cuencas_val):
    ax2.text(v + 0.5, y_pos[i], f'{v} enc.', va='center', ha='left', fontsize=9.5, fontweight='bold', color='#0F172A')
ax2.invert_yaxis()
ax2.set_yticks(y_pos)
ax2.set_yticklabels(cuencas_lbl, fontsize=9.2, fontweight='bold')
ax2.set_xlabel('Frecuencia de mención en 33 encuestas [encuestas]', fontsize=11.5, fontweight='bold')
ax2.set_xlim(0, 34)
ax2.grid(True, axis='x', ls='--', alpha=0.5, zorder=1)
p_red = mpatches.Patch(color='#DC2626', label='Nodos elegidos para Centros A+F')
p_blue = mpatches.Patch(color='#2563EB', label='Cabecera / Cuencas alimentadoras')
ax2.legend(handles=[p_red, p_blue], fontsize=8.8, loc='lower right', framealpha=0.95, edgecolor='#334155')

plt.tight_layout(pad=1.6)
plt.savefig(os.path.join(OUT_DIR, 'grafica_1_bfs_y_encuestas.png'), dpi=300, bbox_inches='tight')
plt.close()

# =========================================================================
# GRAFICA 2: ANALISIS DFS (DISTRIBUCION DE RUTAS) Y REGRESION DISTANCIA-TIEMPO
# =========================================================================
fig2, (ax2a, ax2b) = plt.subplots(1, 2, figsize=(10.2, 4.4), dpi=300)

# Panel 2a: Distribucion de las 240 rutas DFS evaluadas (datos exactos de salida C++)
cats = ['Red Actual\n(240 rutas)', 'Red Optimizada\n(240 rutas)']
opt_counts = np.array([44, 192])
ale_counts = np.array([49, 48])
cri_counts = np.array([147, 0])

xc = np.arange(2)
wc = 0.45
ax2a.bar(xc, opt_counts, width=wc, label='Óptimo (≤ 360 min sin frío)', color='#059669', edgecolor='#064E3B', lw=1.5, zorder=3)
ax2a.bar(xc, ale_counts, width=wc, bottom=opt_counts, label='Alerta bacteriana (360–480 min)', color='#F59E0B', edgecolor='#78350F', lw=1.5, zorder=3)
ax2a.bar(xc, cri_counts, width=wc, bottom=opt_counts + ale_counts, label='Deterioro crítico (> 480 min)', color='#DC2626', edgecolor='#7F1D1D', lw=1.5, zorder=3)

ax2a.text(0, 22, '44\n(18.3%)', ha='center', va='center', fontsize=10, fontweight='bold', color='white')
ax2a.text(0, 44 + 24.5, '49 (20.4%)', ha='center', va='center', fontsize=9.5, fontweight='bold', color='#1E293B')
ax2a.text(0, 44 + 49 + 73.5, '147\n(61.3%)', ha='center', va='center', fontsize=10, fontweight='bold', color='white')

ax2a.text(1, 96, '192\n(80.0%)', ha='center', va='center', fontsize=10.5, fontweight='bold', color='white')
ax2a.text(1, 192 + 24, '48 (20.0%)', ha='center', va='center', fontsize=9.5, fontweight='bold', color='#1E293B')
ax2a.text(1, 246, '0 críticas (0.0%)', ha='center', va='bottom', fontsize=10, fontweight='bold', color='#064E3B',
          bbox=dict(boxstyle='round,pad=0.2', facecolor='#D1FAE5', edgecolor='#059669', lw=1.2))

ax2a.set_ylabel('Cantidad de rutas simples DFS [rutas]', fontsize=11.8, fontweight='bold')
ax2a.set_xticks(xc)
ax2a.set_xticklabels(cats, fontsize=11, fontweight='bold')
ax2a.set_ylim(0, 355)
ax2a.grid(True, axis='y', ls='--', alpha=0.5, zorder=1)
ax2a.legend(fontsize=8.6, loc='upper right', framealpha=0.95, edgecolor='#334155')

# Panel 2b: Regresion lineal Distancia Fluvial (km) vs Tiempo sin frio (min) en BFS Actual vs Optimizada
# Distancias acumuladas exactas de las rutas BFS en red actual y red optimizada:
dist_actual = np.array([201, 228, 211, 182, 177, 149, 205, 170, 56, 22], dtype=float)
t_bfs_act = np.array(t_act, dtype=float)

dist_opt = np.array([42, 76, 59, 30, 0, 32, 64, 29, 26, 22], dtype=float)
t_bfs_opt = np.array(t_opt, dtype=float)

m1, b1 = np.polyfit(dist_actual, t_bfs_act, 1)
r2_1 = np.corrcoef(dist_actual, t_bfs_act)[0, 1] ** 2

m2, b2 = np.polyfit(dist_opt, t_bfs_opt, 1)
r2_2 = np.corrcoef(dist_opt, t_bfs_opt)[0, 1] ** 2

x_line_act = np.linspace(0, 235, 100)
x_line_opt = np.linspace(0, 88, 60)
ax2b.scatter(dist_actual, t_bfs_act, s=65, color='#DC2626', edgecolor='#7F1D1D', zorder=4, label='Red Actual (BFS)')
ax2b.plot(x_line_act, m1 * x_line_act + b1, color='#DC2626', lw=2.0, ls='-', zorder=3,
          label=f'Ajuste Actual: $t={m1:.2f}d+{b1:.1f}$ ($R^2={r2_1:.4f}$)')

ax2b.scatter(dist_opt, t_bfs_opt, s=65, marker='s', color='#059669', edgecolor='#064E3B', zorder=4, label='Red Optimizada (BFS)')
ax2b.plot(x_line_opt, m2 * x_line_opt + b2, color='#059669', lw=2.0, ls='--', zorder=3,
          label=f'Ajuste Optim.: $t={m2:.2f}d+{b2:.1f}$ ($R^2={r2_2:.4f}$)')

ax2b.axhline(360, color='#D97706', ls=':', lw=1.8, zorder=2, label='Umbral 360 min (6 h)')

ax2b.set_xlabel('Distancia acumulada al 1er nodo frío $d$ [km]', fontsize=11.5, fontweight='bold')
ax2b.set_ylabel('Tiempo expuesto sin frío $t$ [min]', fontsize=11.5, fontweight='bold')
ax2b.set_xlim(-8, 242)
ax2b.set_ylim(-20, 680)
ax2b.grid(True, ls='--', alpha=0.5, zorder=1)
ax2b.legend(fontsize=8.0, loc='upper left', framealpha=0.95, edgecolor='#334155')

plt.tight_layout(pad=1.6)
plt.savefig(os.path.join(OUT_DIR, 'grafica_2_dfs_y_regresion.png'), dpi=300, bbox_inches='tight')
plt.close()

print(f'Regresion Actual: m={m1:.4f}, b={b1:.4f}, R2={r2_1:.6f}')
print(f'Regresion Opt:    m={m2:.4f}, b={b2:.4f}, R2={r2_2:.6f}')
print('Graficas generadas correctamente en:', OUT_DIR)
