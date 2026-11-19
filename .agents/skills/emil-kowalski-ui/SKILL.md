---
name: emil-kowalski-ui
description: >-
  Aplica principios avanzados de Emil Kowalski para micro-interacciones, animaciones de interfaz,
  física de resortes (spring physics), transiciones de layout fluidas, curvas cubic-bezier naturales
  y feedback háptico/táctil en frontend (CSS, Tailwind, Framer Motion/Motion, React, Vanilla JS).
---

# Emil Kowalski UI & Motion Principles

Usa esta guía al construir, estilizar o animar componentes web, botones, modales, drawers, listas o menús interactivos.

## 1. Física de Resortes (Spring Physics) vs Curvas Duracionales
- **Resortes para componentes interactivos (arrastre, drawers, toggles)**:
  - Framer Motion / Motion:
    ```typescript
    // Interacciones rápidas / botones / toggles:
    transition: { type: "spring", stiffness: 400, damping: 30, mass: 1 }
    // Modales suaves / drawers / hojas deslizantes:
    transition: { type: "spring", stiffness: 300, damping: 32 }
    ```
- **CSS Transitions y Bezier cuando no hay motor de física**:
  - Salida exponencial natural (snappy): `cubic-bezier(0.16, 1, 0.3, 1)` (out-expo).
  - Deslizamiento suave (smooth sheet): `cubic-bezier(0.32, 0.72, 0, 1)`.
  - **Evitar**: `ease-in-out` estándar o `linear` para movimientos de entrada/salida.

## 2. Duraciones Clave y Regla Asimétrica
- **Micro-interacciones (hover, focus, active)**: `120ms – 180ms`.
- **Componentes medianos (menús desplegables, tooltips, toasts)**: `180ms – 250ms`.
- **Transiciones grandes (modales, drawers, cambios de vista)**: `300ms – 400ms`.
- **Regla Asimétrica de Salida**: Las animaciones de cierre o desaparición **deben ser entre un 30% y un 50% más rápidas** que las de entrada. Si un modal entra en 300ms, debe cerrarse en 180ms–200ms.

## 3. Principio de Feedback Inmediato (Tactile Feel)
- Botones interactivos deben tener respuesta inmediata en `:active`:
  ```css
  button:active {
    transform: scale(0.97);
    transition-duration: 80ms;
  }
  ```
- Al soltar el clic, el elemento rebota a `scale(1)` con elasticidad natural.

## 4. Animaciones de Layout y Rendimiento
- **Propiedades compuestas**: Animar exclusivamente `transform` (`translate`, `scale`, `rotate`) y `opacity`.
- **Evitar animar directamente**: `width`, `height`, `top`, `left`, `margin`, `padding` porque disparan reflows del navegador en cada fotograma.
- **Staggering (cascada escalonada)**:
  - En listas o rejillas de elementos, retrasar cada ítem entre `30ms` y `50ms`.
  - No escalonar más de 6–8 elementos a la vez para no retrasar la percepción de velocidad de la interfaz.
