# DESIGN.md — Sistema Visual Híbrido: Dala Constellation × Apple Midnight Exhibition × ORYZO Editorial

## 1. Dirección de Arte y Fusión Estética
- **Lienzo de Grafos Interactivos (Inspiración Dala — *Constellation floating on black velvet*)**:
  - Superficie base en negro absoluto `--color-void: #000000` donde los 25 vértices y 41 aristas flotan junto a una constelación reactiva de partículas triangulares multicromáticas (`#8052ff` Electric Iris, `#ffb829` Saffron Spark, `#15846e` Deep Verdant, `#2997ff` Electric Link).
  - Botones primarios en píldora violeta `--color-electric-iris: #8052ff` (`border-radius: 24px`) y acentos de ruta óptima en `--color-saffron-spark: #ffb829`.
- **Módulos de Exposición, KPIs y Soluciones (Inspiración Apple — *Midnight Hardware Gallery*)**:
  - Bloques de exhibición sobre `--color-obsidian: #000000` y paneles `--color-carbon: #1d1d1f` con esquinas de `28px` (`--radius-cards: 28px`), contornos sutiles de `1px` (`--color-steel: #333336`) y cero sombras difusas (`box-shadow: none`).
  - Tipografía escultural en `--color-porcelain: #f5f5f7` y controles de acción en `--color-apple-blue: #0071e3` / `--color-electric-link: #2997ff`.
- **Voz Editorial y Separadores Estructurales (Inspiración ORYZO AI — *Darkroom Product Editorial*)**:
  - Acentos tipográficos cálidos en `--color-warm-cream: #ffedd7` y `--color-ember-accent: #dc5000` para créditos técnicos y sellos de ingeniería.
  - Divisores estructurales discontinuos de `1px dashed #40372e` (`--color-cork-border`) y etiqueta serial vertical en el margen derecho.

## 2. Tokens de Color
- `--color-void` / `--color-obsidian`: `#000000`
- `--color-graphite`: `#0e0e0e`
- `--color-carbon`: `#1d1d1f`
- `--color-steel`: `#333336`
- `--color-cork-border`: `#40372e`
- `--color-bone-white`: `#ffffff`
- `--color-porcelain`: `#f5f5f7`
- `--color-warm-cream`: `#ffedd7`
- `--color-silver-mist`: `#bdbdbd`
- `--color-ash`: `#86868b`
- `--color-electric-iris`: `#8052ff`
- `--color-saffron-spark`: `#ffb829`
- `--color-deep-verdant`: `#15846e`
- `--color-apple-blue`: `#0071e3`
- `--color-electric-link`: `#2997ff`
- `--color-ember-accent`: `#dc5000`

## 3. Tipografía y Escala
- **Familias**: `'PPNeueMontreal', 'SF Pro Display', 'Halyard Display', 'Söhne', 'Neue Haas Grotesk', system-ui, -apple-system, sans-serif` (nunca Inter/Roboto genéricos).
- **Monospace / Datos Tabulares**: `'JetBrains Mono', 'SF Mono', 'Cascadia Code', Consolas, monospace` con `font-variant-numeric: tabular-nums`.
- **Escala**:
  - Display / Hero: `48px`–`64px`, `font-weight: 400`, `line-height: 1.05`, `letter-spacing: -0.035em`.
  - Heading de Sección (`h1`/`h2`): `28px`–`36px`, `font-weight: 500`, `line-height: 1.12`, `letter-spacing: -0.025em`.
  - Subtítulo / Stat (`h3`): `20px`–`24px`, `font-weight: 500`, `line-height: 1.2`.
  - Cuerpo (`body` / `p`): `15px`–`17px`, `font-weight: 300`, `line-height: 1.5`.
  - Etiquetas de navegación y metadatos: `12px`–`14px`, `font-weight: 600`, `letter-spacing: 0.025em`, `text-transform: uppercase`.

## 4. Movimiento y Física (Emil Kowalski & Apple Fluid Design)
- Solo se animan `transform` y `opacity` en compositor GPU.
- Curvas personalizadas: `--ease-out: cubic-bezier(0.23, 1, 0.32, 1)`, `--ease-in-out: cubic-bezier(0.77, 0, 0.175, 1)`.
- Feedback táctil inmediato en controles interactivos: `transform: scale(0.97)` en `:active` (120ms).
- Transiciones por teclado (`←`/`→`, `1`–`8`, `R`, `Esc`) instantáneas (`0ms`).
- Soporte completo para `@media (prefers-reduced-motion: reduce)` y `@media (hover: hover) and (pointer: fine)`.
