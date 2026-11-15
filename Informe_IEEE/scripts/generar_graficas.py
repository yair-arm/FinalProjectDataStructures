# -*- coding: utf-8 -*-
"""
Genera las figuras analiticas para el Informe IEEE doble columna (ancho ~3.25 in)
y para las Diapositivas PPTX basandose en el modelo de 25 vertices y 41 aristas de Harold.
"""
import os
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch

BASE = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
OUT_DIR = os.path.join(BASE, 'Informe_IEEE', 'Assets')
os.makedirs(OUT_DIR, exist_ok=True)

plt.rcParams['font.family'] = 'serif'
plt.rcParams['font.serif'] = ['Times New Roman', 'DejaVu Serif']
plt.rcParams['mathtext.fontset'] = 'stix'

# =========================================================================
# 1. FIGURA 1 VERTICAL: TOPOLOGIA DEL GRAFO LOGISTICO (1 COLUMNA IEEE)
# =========================================================================
fig_v, ax_v = plt.subplots(figsize=(5.6, 7.8), dpi=300)
ax_v.set_xlim(0, 100)
ax_v.set_ylim(0, 100)
ax_v.axis('off')

# Capas funcionales
capas_v = [
    (81, 17, '#EFF6FF', '#93C5FD', 'Capa 1: Puntos de Captura Fluvial (P)'),
    (58, 20, '#FEF3C7', '#FCD34D', 'Capa 2: Muelles (M) y Acopios Rurales (A)'),
    (34, 21, '#ECFDF5', '#6EE7B7', 'Capa 3: Centros Frigorificos (F) / Zonas D y H'),
    (5, 26, '#F5F3FF', '#C4B5FD', 'Capa 4: Mercados Mayoristas y Minoristas (V)')
]
for y0, h, fc, ec, lbl in capas_v:
    box = FancyBboxPatch((2, y0), 96, h, boxstyle='round,pad=0.5',
                         facecolor=fc, edgecolor=ec, linewidth=1.3, alpha=0.55, zorder=0)
    ax_v.add_patch(box)
    ax_v.text(50, y0 + h - 2.8, lbl, ha='center', va='center', fontsize=9.0,
              fontweight='bold', color='#1E293B')

pos_v = {
    # Puntos de pesca (Capa 1)
    'P01': (12, 88), 'P02': (27, 88), 'P07': (42, 88),
    'P03': (58, 88), 'P04': (73, 88), 'P05': (88, 88),
    'P06': (50, 77),
    # Muelles y Acopios (Capa 2)
    'M03': (22, 67), 'A02': (38, 67),
    'M01': (62, 67), 'A01': (76, 67), 'A03': (89, 67),
    # Frío y Críticos (Capa 3)
    'F01': (18, 44), 'F02': (48, 44), 'F03': (78, 44),
    'D01': (88, 51), 'D02': (65, 51), 'H01': (68, 38), 'H02': (32, 38),
    # Mercados (Capa 4)
    'V_PG1': (18, 16), 'V_PG2': (36, 16),
    'V_VLL': (60, 16), 'V_BOG1': (78, 16), 'V_BOG2': (90, 16)
}

labels_v = {
    'P01': 'P01\nNeblinas', 'P02': 'P02\nAtarraya', 'P07': 'P07\nSoplav.',
    'P03': 'P03\nSan Mig.', 'P04': 'P04\nAsopesp.', 'P05': 'P05\nTrujillo',
    'P06': 'P06 Desemb.',
    'M03': 'M03 (Muelle)', 'A02': 'A02 Acopio',
    'M01': 'M01', 'A01': 'A01 Acopio', 'A03': 'A03',
    'F01': 'F01 Neblinas', 'F02': 'F02 Pto. Gaitán', 'F03': 'F03 Pto. López',
    'D01': 'D01 (×1.5)', 'D02': 'D02', 'H01': 'H01 [Restr]', 'H02': 'H02 [Restr]',
    'V_PG1': 'V_PG1\nLlanofish', 'V_PG2': 'V_PG2\nEl Pavón',
    'V_VLL': 'V_VLL\nVillavic.', 'V_BOG1': 'V_BOG1\nBuceo', 'V_BOG2': 'V_BOG2\nBogotá'
}

edges_sample = [
    ('P01', 'M03', 'fluvial'), ('P01', 'A02', 'fluvial'),
    ('P02', 'M03', 'fluvial'), ('P02', 'A02', 'local'),
    ('P07', 'M03', 'fluvial'), ('P07', 'A02', 'fluvial'),
    ('P03', 'M01', 'fluvial'), ('P03', 'A01', 'local'),
    ('P04', 'M01', 'fluvial'), ('P04', 'A01', 'local'),
    ('P05', 'A03', 'fluvial'), ('P06', 'F02', 'local'),
    ('M03', 'F02', 'local'), ('A02', 'F02', 'local'),
    ('M01', 'A01', 'local'), ('A01', 'F02', 'carretera'),
    ('A03', 'D01', 'local'), ('D01', 'A01', 'local'),
    ('F01', 'F02', 'carretera'), ('F02', 'F03', 'carretera'),
    ('F02', 'V_PG1', 'local'), ('F02', 'V_PG2', 'local'),
    ('F03', 'V_VLL', 'carretera'), ('F03', 'V_BOG1', 'carretera'),
    ('F03', 'V_BOG2', 'carretera'),
]

# Dibujar aristas
for u, v, tipo in edges_sample:
    if u in pos_v and v in pos_v:
        x1, y1 = pos_v[u]
        x2, y2 = pos_v[v]
        dx = x2 - x1
        dy = y2 - y1
        if tipo == 'fluvial':
            col, ls, lw = '#0284C7', '-', 1.2
        elif tipo == 'local':
            col, ls, lw = '#64748B', ':', 1.1
        else:
            col, ls, lw = '#B45309', '--', 1.3
        ax_v.annotate('', xy=(x2, y2), xytext=(x1, y1),
                      arrowprops=dict(arrowstyle='-|>', color=col, lw=lw, ls=ls,
                                      mutation_scale=8, shrinkA=8, shrinkB=8), zorder=1)

# Dibujar nodos
colores_tipo = {
    'P': ('#1E3A8A', '#DBEAFE', 's'),
    'M': ('#0284C7', '#BAE6FD', 'o'),
    'A': ('#D97706', '#FEF3C7', 'o'),
    'F': ('#059669', '#D1FAE5', 'h'),
    'D': ('#DC2626', '#FEE2E2', 'v'),
    'H': ('#16A34A', '#DCFCE7', 'X'),
    'V': ('#7C3AED', '#EDE9FE', 'D'),
}

for nid, (x, y) in pos_v.items():
    prefix = nid[0]
    if nid.startswith('V_'):
        prefix = 'V'
    edge_c, face_c, mark = colores_tipo.get(prefix, ('#334155', '#F1F5F9', 'o'))
    ax_v.plot(x, y, marker=mark, markersize=13, markeredgecolor=edge_c,
              markerfacecolor=face_c, markeredgewidth=1.4, zorder=3)
    ax_v.text(x, y - 2.8, labels_v.get(nid, nid), ha='center', va='top',
              fontsize=6.8, fontweight='bold', color='#0F172A', zorder=4)

leg_v = [
    mpatches.Patch(color='#1E3A8A', label='Pesca (P)'),
    mpatches.Patch(color='#0284C7', label='Muelle (M)'),
    mpatches.Patch(color='#D97706', label='Acopio (A)'),
    mpatches.Patch(color='#059669', label='Frío (F)'),
    mpatches.Patch(color='#DC2626', label='Deterioro (D)'),
    mpatches.Patch(color='#16A34A', label='Hábitat (H)'),
    mpatches.Patch(color='#7C3AED', label='Mercado (V)'),
]
ax_v.legend(handles=leg_v, loc='lower center', bbox_to_anchor=(0.5, -0.01),
            ncol=4, fontsize=7.5, frameon=True, edgecolor='#334155', facecolor='white')

plt.tight_layout()
plt.savefig(os.path.join(OUT_DIR, 'figura_1_topologia_col.png'), dpi=300, bbox_inches='tight')
plt.close()

# =========================================================================
# 2. GRAFICA 1: TIEMPOS SIN FRIO POR PUNTO DE PESCA (1 COLUMNA IEEE)
# =========================================================================
fig_g1, ax_g1 = plt.subplots(figsize=(5.2, 3.8), dpi=300)
puntos = ['P01\nNeblinas', 'P02\nAtarraya', 'P03\nSan Mig.', 'P04\nAsopesp.',
          'P05\nTrujillo', 'P06\nDesemb.', 'P07\nSoplav.']
t_sin_frio_h = [0.48, 0.43, 0.25, 0.40, 2.20, 0.08, 0.38]
t_sin_frio_min = [h * 60 for h in t_sin_frio_h]

x = np.arange(len(puntos))
ax_g1.bar(x, t_sin_frio_min, width=0.45, color='#0284C7', edgecolor='#0369A1', lw=1.3, zorder=3, label='Tiempo al 1er Frío/Acopio')
ax_g1.axhline(240, color='#DC2626', ls='--', lw=1.8, zorder=4, label='Límite Máximo Inocuidad (4 h / 240 min)')
ax_g1.axhline(60, color='#059669', ls=':', lw=1.5, zorder=4, label='Meta Operativa Excelente (< 1 h)')

for i in range(len(x)):
    ax_g1.text(x[i], t_sin_frio_min[i] + 5, f'{t_sin_frio_min[i]:.0f} min\n({t_sin_frio_h[i]:.2f}h)',
               ha='center', va='bottom', fontsize=7.2, fontweight='bold', color='#0F172A')

ax_g1.set_ylabel('Tiempo sin frío acumulado [min]', fontsize=9.2, fontweight='bold')
ax_g1.set_xticks(x)
ax_g1.set_xticklabels(puntos, fontsize=7.8, fontweight='bold')
ax_g1.set_ylim(0, 280)
ax_g1.grid(True, axis='y', ls='--', alpha=0.5, zorder=1)
ax_g1.legend(fontsize=7.5, loc='upper left', framealpha=0.95, edgecolor='#334155')

plt.tight_layout()
plt.savefig(os.path.join(OUT_DIR, 'grafica_1_bfs_col.png'), dpi=300, bbox_inches='tight')
plt.close()

# =========================================================================
# 3. GRAFICA 2A: COMPARATIVA DE EVALUACION DE ESCENARIOS (1 COLUMNA IEEE)
# =========================================================================
fig_g2, ax_g2 = plt.subplots(figsize=(5.2, 3.6), dpi=300)
escenarios = ['Sin Frío', 'F01 (Nebl.)', 'F02 (P.Gaitán)*', 'F03 (P.López)', '3 Centros']
costos_m = [8.02, 9.70, 13.02, 13.02, 23.02]
perdidas = [17.1, 17.0, 17.1, 17.1, 17.1]

xe = np.arange(len(escenarios))
ax_g2.bar(xe, costos_m, width=0.45, color='#3B82F6', edgecolor='#1D4ED8', lw=1.3, zorder=3, label='Costo Total Mensual (M COP)')
ax_g2.set_ylabel('Costo Mensual [Millones COP]', fontsize=9.2, fontweight='bold', color='#1D4ED8')
ax_g2.set_xticks(xe)
ax_g2.set_xticklabels(escenarios, fontsize=7.8, fontweight='bold', rotation=15)
ax_g2.set_ylim(0, 28)
ax_g2.grid(True, axis='y', ls='--', alpha=0.5, zorder=1)

for i in range(len(xe)):
    ax_g2.text(xe[i], costos_m[i] + 0.6, f'${costos_m[i]:.1f}M', ha='center', va='bottom',
               fontsize=7.5, fontweight='bold', color='#1E293B')

ax_g2.text(2, 13.02 + 3.0, 'ÓPTIMO FLP\n(100% Cobertura)', ha='center', va='bottom',
           fontsize=7.2, fontweight='bold', color='#065F46',
           bbox=dict(boxstyle='round,pad=0.2', facecolor='#D1FAE5', edgecolor='#059669', lw=1.1))

plt.tight_layout()
plt.savefig(os.path.join(OUT_DIR, 'grafica_2a_dfs_col.png'), dpi=300, bbox_inches='tight')
plt.close()

# =========================================================================
# 4. GRAFICA 2B: REGRESION LINEAL DISTANCIA-TIEMPO POR MODO (1 COLUMNA IEEE)
# =========================================================================
fig_reg, ax_reg = plt.subplots(figsize=(5.2, 3.6), dpi=300)

# Datos reales de aristas fluviales y terrestres
d_fluvial = np.array([5.5, 4.0, 6.5, 4.5, 7.0, 8.0, 3.5, 5.0, 6.0, 4.2])
t_fluvial = d_fluvial / 16.5  # v_canoa ~ 16.5 km/h

d_terrestre = np.array([2.5, 8.5, 12.0, 18.0, 21.5, 35.0, 63.0, 126.0, 170.0, 290.0])
t_terrestre = d_terrestre / 65.0  # v_camion ~ 65 km/h

m_f, b_f = np.polyfit(d_fluvial, t_fluvial * 60, 1)
r2_f = np.corrcoef(d_fluvial, t_fluvial * 60)[0, 1] ** 2

m_t, b_t = np.polyfit(d_terrestre, t_terrestre * 60, 1)
r2_t = np.corrcoef(d_terrestre, t_terrestre * 60)[0, 1] ** 2

ax_reg.scatter(d_fluvial, t_fluvial * 60, s=40, color='#0284C7', edgecolor='#0369A1', zorder=4, label='Fluvial (Canoa)')
x_f_line = np.linspace(0, 15, 50)
ax_reg.plot(x_f_line, m_f * x_f_line + b_f, color='#0284C7', lw=1.8,
            label=f'Fluvial: $t={m_f:.2f}d$ min/km ($R^2={r2_f:.3f}$)')

ax_reg.scatter(d_terrestre, t_terrestre * 60, s=40, marker='s', color='#B45309', edgecolor='#78350F', zorder=4, label='Terrestre (RN 40)')
x_t_line = np.linspace(0, 300, 50)
ax_reg.plot(x_t_line, m_t * x_t_line + b_t, color='#B45309', lw=1.8, ls='--',
            label=f'Terrestre: $t={m_t:.2f}d$ min/km ($R^2={r2_t:.3f}$)')

ax_reg.set_xlabel('Distancia del tramo $d$ [km]', fontsize=9.2, fontweight='bold')
ax_reg.set_ylabel('Tiempo de tránsito $t$ [min]', fontsize=9.2, fontweight='bold')
ax_reg.grid(True, ls='--', alpha=0.5, zorder=1)
ax_reg.legend(fontsize=7.4, loc='upper left', framealpha=0.95, edgecolor='#334155')

plt.tight_layout()
plt.savefig(os.path.join(OUT_DIR, 'grafica_2b_regresion_col.png'), dpi=300, bbox_inches='tight')
plt.close()

print('Graficas actualizadas generadas exitosamente en:', OUT_DIR)
