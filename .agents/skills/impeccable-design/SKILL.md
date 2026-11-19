---
name: impeccable-design
description: >-
  Sistema de diseño de precisión (Impeccable): cuadrícula base de 4px/8px, escala modular
  de tipografía, emparejamiento de line-heights, proporciones armónicas de color (60-30-10)
  y consistencia en sistemas de diseño frontend.
---

# Impeccable Design: Tipografía, Espaciado y Jerarquía

Usa esta habilidad para estructurar interfaces limpias, proporcionadas y con rigor matemático en diseño.

## 1. Cuadrícula de Espaciado Sistemático (Base 4px / 8px)
Todo valor de `padding`, `margin`, `gap`, `width` y `height` debe adherirse a múltiplos de 4px / 8px:

| Token | Píxeles | Tailwind | Uso típico |
| :--- | :--- | :--- | :--- |
| **space-1** | 4px | `p-1`, `gap-1` | Padding de tags compactos, separación entre icono y texto corto |
| **space-2** | 8px | `p-2`, `gap-2` | Padding interior de botones pequeños, espacio entre inputs y labels |
| **space-3** | 12px | `p-3`, `gap-3` | Padding estándar de botones, separación de ítems de lista |
| **space-4** | 16px | `p-4`, `gap-4` | Padding estándar de tarjetas, separación entre secciones internas |
| **space-6** | 24px | `p-6`, `gap-6` | Padding de paneles y modales principales |
| **space-8** | 32px | `p-8`, `gap-8` | Separación de bloques grandes en layout |
| **space-12** | 48px | `p-12`, `gap-12` | Márgenes verticales de páginas y secciones destacadas |

## 2. Escala Tipográfica Modular y Alturas de Línea
La altura de línea (`line-height` / `leading`) debe estar emparejada exactamente para evitar saltos ópticos:

- **Micro (`text-xs` / 12px)** → `leading-4` (16px). Para insignias, metadata secundaria y pies de foto.
- **Base Pequeña (`text-sm` / 14px)** → `leading-5` (20px). Texto de apoyo en tarjetas, tablas densas y navegación.
- **Cuerpo (`text-base` / 16px)** → `leading-6` (24px). Párrafos principales y lectura continua.
- **Subtítulo (`text-lg` / 18px)** → `leading-7` (28px). Encabezados de tarjetas y secciones medianas.
- **Título Seccional (`text-xl` / 20px)** → `leading-7` (28px). Encabezados de paneles.
- **Título Principal (`text-2xl` / 24px)** → `leading-8` (32px, `tracking-tight`). Títulos de vista.
- **Display (`text-4xl+` / 36px+)** → `leading-none` o `leading-tight` con `tracking-tighter`.

## 3. Regla Cromática 60-30-10
- **60% Superficie / Fondo**: Un tono neutro cohesivo (p. ej., `bg-neutral-950` en oscuro o `bg-neutral-50` en claro).
- **30% Estructura y Texto**: Superficies elevadas (`bg-neutral-900`/`bg-white`), bordes tenues y texto legible.
- **10% Acento y Estado**: Reservado exclusivamente para acciones clave (botón primario, selección activa, estados de éxito o alerta). Si todo resalta, nada resalta.
