# -*- coding: utf-8 -*-
"""
Genera las figuras analiticas para:
1) El Informe IEEE doble columna (imagenes optimizadas para ancho de 1 columna ~3.25 in).
2) Las Diapositivas PPTX (imagenes panoramicas de alta resolucion).
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

rows = []
with open(os.path.join(DATA_DIR, 'comparativa_resultados.csv'), encoding='utf-8') as f:
    for r in csv.DictReader(f):
        rows.append(r)

short_names = [
    'Caño\nMorroco', 'Vichada', 'Planas', 'Guarrojo', 'Muco',
    'Meta/\nVentura', 'Cañalute', 'Manac.\nSur', 'Yucao', 'Chaviva'
]
t_act = [int(r['tiempo_sin_frio_bfs_actual']) for r in rows]
t_opt = [int(r['tiempo_sin_frio_bfs_opt']) for r in rows]

# =========================================================================
# 1. FIGURA 1 VERTICAL (AJUSTADA A 1 COLUMNA IEEE)
# =========================================================================
fig_v, ax_v = plt.subplots(figsize=(5.6, 7.8), dpi=300)
ax_v.set_xlim(0, 100)
ax_v.set_ylim(0, 100)
ax_v.axis('off')

# Bandas de capas verticales (Flujo de arriba hacia abajo)
capas_v = [
    (80, 18, '#EFF6FF', '#93C5FD', 'Capa 1: Puntos de Pesca (P)'),
    (54, 24, '#FEF3C7', '#FCD34D', 'Capa 2: Confluencias Críticas / Centros A+F'),
    (28, 24, '#ECFDF5', '#6EE7B7', 'Capa 3: Cabeceras de Desembarque'),
    (2, 24, '#F5F3FF', '#C4B5FD', 'Capa 4: Mercados Regional / Nacional (V)')
]
for y0, h, fc, ec, lbl in capas_v:
    box = FancyBboxPatch((2, y0), 96, h, boxstyle='round,pad=0.5',
                         facecolor=fc, edgecolor=ec, linewidth=1.4, alpha=0.55, zorder=0)
    ax_v.add_patch(box)
    ax_v.text(50, y0 + h - 2.8, lbl, ha='center', va='center', fontsize=9.2,
              fontweight='bold', color='#1E293B')

pos_v = {
    'P_Cano_Morroco': (14, 87),
    'P_Vichada': (38, 87),
    'P_Planas': (62, 87),
    'P_Canalete_Maiciana': (86, 87),
    'P_Guarrojo': (38, 72),
    'P_Manacacias_Sur': (78, 72),
    'P_Yucao': (14, 63),
    'P_Chaviva_PtoLopez': (14, 46),
    'P_Muco': (38, 62),
    'P_Meta_Ventura': (58, 62),
    'D_Manacacias_Medio': (80, 62),
    'D_Bocas_Manacacias': (48, 44),
    'Puerto_Gaitan': (76, 44),
    'Puerto_Lopez': (26, 34),
    'Villavicencio': (38, 14),
    'Bogota': (72, 14),
}

labels_v = {
    'P_Cano_Morroco': 'Caño Morroco\n(P)',
    'P_Vichada': 'Vichada (P)',
    'P_Planas': 'Río Planas\n(P)',
    'P_Canalete_Maiciana': 'Cañalute\n(P)',
    'P_Guarrojo': 'Río Guarrojo\n(P)',
    'P_Manacacias_Sur': 'Manacacías Sur\n(P)',
    'P_Yucao': 'Río Yucao\n(P)',
    'P_Chaviva_PtoLopez': 'Chaviva (P)',
    'P_Muco': 'Río Muco\n[A+F]',
    'P_Meta_Ventura': 'Meta/Ventura\n(P)',
    'D_Manacacias_Medio': 'Manac. Medio\n[A+F]',
    'D_Bocas_Manacacias': 'Bocas Manac.\n[A+F]',
    'Puerto_Gaitan': 'Puerto Gaitán\n(M+F+V)',
    'Puerto_Lopez': 'Puerto López\n(A+F)',
    'Villavicencio': 'Villavicencio\n(V+F)',
    'Bogota': 'Bogotá D.C.\n(V+F)',
}

edges_v = [
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

for u, v, w_lbl, med in edges_v:
    x1, y1 = pos_v[u]
    x2, y2 = pos_v[v]
    col = '#0284C7' if med == 'fluvial' else '#B45309'
    ls = '-' if med == 'fluvial' else '--'
    ax_v.annotate('', xy=(x2, y2), xytext=(x1, y1),
                  arrowprops=dict(arrowstyle='-|>,head_width=0.32,head_length=0.45',
                                  color=col, lw=1.2, linestyle=ls, alpha=0.82,
                                  shrinkA=13, shrinkB=13),
                  zorder=2)

frio_opt = {'P_Muco', 'D_Manacacias_Medio', 'D_Bocas_Manacacias'}
mercados = {'Puerto_Gaitan', 'Puerto_Lopez', 'Villavicencio', 'Bogota'}
for node, (nx, ny) in pos_v.items():
    if node in frio_opt:
        fc, ec, tc = '#DC2626', '#7F1D1D', 'white'
    elif node in mercados:
        fc, ec, tc = '#059669', '#064E3B', 'white'
    else:
        fc, ec, tc = '#2563EB', '#1E3A8A', 'white'
    ax_v.text(nx, ny, labels_v[node], ha='center', va='center',
              fontsize=7.8, fontweight='bold', color=tc,
              bbox=dict(boxstyle='round,pad=0.28', facecolor=fc, edgecolor=ec, linewidth=1.4),
              zorder=4)

leg_v = [
    mpatches.Patch(color='#2563EB', label='Punto Pesca (P)'),
    mpatches.Patch(color='#DC2626', label='Centro A+F'),
    mpatches.Patch(color='#059669', label='Mercado (V)'),
    plt.Line2D([0], [0], color='#0284C7', lw=1.8, label='Fluvial Canoa'),
    plt.Line2D([0], [0], color='#B45309', lw=1.8, ls='--', label='Terrestre'),
]
ax_v.legend(handles=leg_v, loc='lower center', bbox_to_anchor=(0.5, -0.01),
            ncol=3, fontsize=8.2, frameon=True, edgecolor='#334155', facecolor='white')

plt.tight_layout()
plt.savefig(os.path.join(OUT_DIR, 'figura_1_topologia_col.png'), dpi=300, bbox_inches='tight')
plt.close()

# =========================================================================
# 2. GRAFICA 1 INDIVIDUAL: BFS TIEMPOS SIN FRIO (1 COLUMNA IEEE)
# =========================================================================
fig_g1, ax_g1 = plt.subplots(figsize=(5.2, 3.8), dpi=300)
x = np.arange(len(short_names))
w = 0.36
ax_g1.bar(x - w/2, t_act, width=w, label='Red Actual', color='#DC2626', edgecolor='#7F1D1D', lw=1.2, zorder=3)
ax_g1.bar(x + w/2, t_opt, width=w, label='Red Optimizada', color='#059669', edgecolor='#064E3B', lw=1.2, zorder=3)
ax_g1.axhline(360, color='#D97706', ls='--', lw=1.8, zorder=4, label='Límite óptimo (360 min)')
ax_g1.axhline(480, color='#991B1B', ls=':', lw=1.8, zorder=4, label='Deterioro crítico (480 min)')

for i in range(len(x)):
    ax_g1.text(x[i] - w/2, t_act[i] + 10, f'{t_act[i]}', ha='center', va='bottom', fontsize=7.0, fontweight='bold', color='#7F1D1D')
    ax_g1.text(x[i] + w/2 + 0.04, t_opt[i] + 10, f'{t_opt[i]}', ha='center', va='bottom', fontsize=7.0, fontweight='bold', color='#064E3B')

ax_g1.set_ylabel('Tiempo sin frío [min]', fontsize=9.5, fontweight='bold')
ax_g1.set_xticks(x)
ax_g1.set_xticklabels(short_names, fontsize=7.5, fontweight='bold', rotation=30, ha='right')
ax_g1.set_ylim(0, 690)
ax_g1.grid(True, axis='y', ls='--', alpha=0.5, zorder=1)
ax_g1.legend(fontsize=7.5, loc='upper right', framealpha=0.95, edgecolor='#334155')

plt.tight_layout()
plt.savefig(os.path.join(OUT_DIR, 'grafica_1_bfs_col.png'), dpi=300, bbox_inches='tight')
plt.close()

# =========================================================================
# 3. GRAFICA 2 INDIVIDUAL: DFS DISTRIBUCION DE RUTAS (1 COLUMNA IEEE)
# =========================================================================
fig_g2, ax_g2 = plt.subplots(figsize=(5.2, 3.6), dpi=300)
cats = ['Red Actual\n(240 rutas)', 'Red Optimizada\n(240 rutas)']
opt_counts = np.array([44, 192])
ale_counts = np.array([49, 48])
cri_counts = np.array([147, 0])

xc = np.arange(2)
wc = 0.42
ax_g2.bar(xc, opt_counts, width=wc, label='Óptimo (≤ 360 min)', color='#059669', edgecolor='#064E3B', lw=1.4, zorder=3)
ax_g2.bar(xc, ale_counts, width=wc, bottom=opt_counts, label='Alerta (360–480 min)', color='#F59E0B', edgecolor='#78350F', lw=1.4, zorder=3)
ax_g2.bar(xc, cri_counts, width=wc, bottom=opt_counts + ale_counts, label='Crítico (> 480 min)', color='#DC2626', edgecolor='#7F1D1D', lw=1.4, zorder=3)

ax_g2.text(0, 22, '44 (18.3%)', ha='center', va='center', fontsize=8.5, fontweight='bold', color='white')
ax_g2.text(0, 44 + 24.5, '49 (20.4%)', ha='center', va='center', fontsize=8.0, fontweight='bold', color='#1E293B')
ax_g2.text(0, 44 + 49 + 73.5, '147 (61.3%)', ha='center', va='center', fontsize=8.5, fontweight='bold', color='white')

ax_g2.text(1, 96, '192 (80.0%)', ha='center', va='center', fontsize=9.0, fontweight='bold', color='white')
ax_g2.text(1, 192 + 24, '48 (20.0%)', ha='center', va='center', fontsize=8.0, fontweight='bold', color='#1E293B')
ax_g2.text(1, 246, '0 críticas (0.0%)', ha='center', va='bottom', fontsize=8.5, fontweight='bold', color='#064E3B',
           bbox=dict(boxstyle='round,pad=0.2', facecolor='#D1FAE5', edgecolor='#059669', lw=1.1))

ax_g2.set_ylabel('Rutas simples DFS', fontsize=9.5, fontweight='bold')
ax_g2.set_xticks(xc)
ax_g2.set_xticklabels(cats, fontsize=9.2, fontweight='bold')
ax_g2.set_ylim(0, 345)
ax_g2.grid(True, axis='y', ls='--', alpha=0.5, zorder=1)
ax_g2.legend(fontsize=7.8, loc='upper left', framealpha=0.95, edgecolor='#334155')

plt.tight_layout()
plt.savefig(os.path.join(OUT_DIR, 'grafica_2a_dfs_col.png'), dpi=300, bbox_inches='tight')
plt.close()

# =========================================================================
# 4. GRAFICA 3 INDIVIDUAL: REGRESION LINEAL DISTANCIA-TIEMPO (1 COLUMNA IEEE)
# =========================================================================
fig_reg, ax_reg = plt.subplots(figsize=(5.2, 3.6), dpi=300)
dist_actual = np.array([201, 228, 211, 182, 177, 149, 205, 170, 56, 22], dtype=float)
t_bfs_act = np.array(t_act, dtype=float)
dist_opt = np.array([42, 76, 59, 30, 0, 32, 64, 29, 26, 22], dtype=float)
t_bfs_opt = np.array(t_opt, dtype=float)

m1, b1 = np.polyfit(dist_actual, t_bfs_act, 1)
r2_1 = np.corrcoef(dist_actual, t_bfs_act)[0, 1] ** 2

m2, b2 = np.polyfit(dist_opt, t_bfs_opt, 1)
r2_2 = np.corrcoef(dist_opt, t_bfs_opt)[0, 1] ** 2

x_act = np.linspace(0, 235, 100)
x_opt = np.linspace(0, 85, 60)

ax_reg.scatter(dist_actual, t_bfs_act, s=45, color='#DC2626', edgecolor='#7F1D1D', zorder=4, label='Red Actual')
ax_reg.plot(x_act, m1 * x_act + b1, color='#DC2626', lw=1.8, ls='-', zorder=3,
            label=f'Actual: $t={m1:.2f}d+{b1:.1f}$ ($R^2={r2_1:.3f}$)')

ax_reg.scatter(dist_opt, t_bfs_opt, s=45, marker='s', color='#059669', edgecolor='#064E3B', zorder=4, label='Red Optimizada')
ax_reg.plot(x_opt, m2 * x_opt + b2, color='#059669', lw=1.8, ls='--', zorder=3,
            label=f'Optim.: $t={m2:.2f}d+{b2:.1f}$ ($R^2={r2_2:.3f}$)')

ax_reg.axhline(360, color='#D97706', ls=':', lw=1.6, zorder=2, label='Umbral 360 min')

ax_reg.set_xlabel('Distancia acumulada al 1er frío $d$ [km]', fontsize=9.2, fontweight='bold')
ax_reg.set_ylabel('Tiempo sin frío $t$ [min]', fontsize=9.2, fontweight='bold')
ax_reg.set_xlim(-6, 240)
ax_reg.set_ylim(-15, 660)
ax_reg.grid(True, ls='--', alpha=0.5, zorder=1)
ax_reg.legend(fontsize=7.4, loc='upper left', framealpha=0.95, edgecolor='#334155')

plt.tight_layout()
plt.savefig(os.path.join(OUT_DIR, 'grafica_2b_regresion_col.png'), dpi=300, bbox_inches='tight')
plt.close()

print('Graficas individuales de una columna generadas exitosamente en:', OUT_DIR)
