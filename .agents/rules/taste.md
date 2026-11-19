# Reglas Globales de Criterio Visual y Taste (Anti-Slop UI)

Aplica estas directrices en cualquier interfaz web, componente interactivo, dashboard o maquetación:

## 1. Anti-Slop (Eliminación de clichés genéricos de IA)
- **Cero gradientes púrpuras/cian inflados**: No uses fondos negros con manchas circulares de `blur-3xl` moradas y cian a menos que sea una identidad de marca explícita.
- **Sin bordes sobre-redondeados sin jerarquía**: No pongas `rounded-3xl` o `rounded-[32px]` a botones o tarjetas densas en datos. Reserva radios grandes (16px–24px) para contenedores modales principales y radios pequeños (6px–10px) para controles y botones.
- **Micro-bordes sutiles en vez de sombras toscas**: Usa bordes de 1px con baja opacidad (`border border-white/[0.08]` en modo oscuro o `border-neutral-200/80` en modo claro). No apliques `shadow-2xl` genéricas; usa elevaciones por capas de superficie (`bg-neutral-900`, `bg-neutral-800`, `bg-neutral-700`).

## 2. Tipografía y Datos
- **Números tabulares**: Todo dato cuantitativo, métrica, contador, precio o coordenada debe usar `font-variant-numeric: tabular-nums` o clase `font-mono`.
- **Contraste intencional**:
  - Texto principal (títulos, valores clave): 90%–100% luminosidad / `text-neutral-100` o `text-neutral-900`.
  - Texto secundario (etiquetas, metadatos): 60% luminosidad / `text-neutral-400` o `text-neutral-500`.
  - Divisores y bordes: 10%–15% luminosidad relativa. Nunca dejes texto gris claro sobre fondo blanco o gris oscuro sobre fondo negro que no cumpla WCAG AA (mínimo 4.5:1).

## 3. Composición y Ritmo
- **Espacio en blanco con propósito**: El espacio no es vacío a rellenar, sino delimitador de grupos semánticos.
- **Densidad de información balanceada**: En dashboards y herramientas profesionales (como mapas, grafos o analítica), prioriza la densidad compacta legible sobre espacios inflados vacíos.
