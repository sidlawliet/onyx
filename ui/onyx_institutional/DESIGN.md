---
name: Onyx Institutional
colors:
  surface: '#12131a'
  surface-dim: '#12131a'
  surface-bright: '#383941'
  surface-container-lowest: '#0d0e15'
  surface-container-low: '#1a1b22'
  surface-container: '#1e1f26'
  surface-container-high: '#292931'
  surface-container-highest: '#33343c'
  on-surface: '#e3e1ec'
  on-surface-variant: '#c8c5ca'
  inverse-surface: '#e3e1ec'
  inverse-on-surface: '#2f3038'
  outline: '#919095'
  outline-variant: '#47464a'
  surface-tint: '#c8c6c8'
  primary: '#c8c6c8'
  on-primary: '#313032'
  primary-container: '#09090b'
  on-primary-container: '#7a787b'
  inverse-primary: '#5f5e60'
  secondary: '#adc6ff'
  on-secondary: '#002e6a'
  secondary-container: '#0566d9'
  on-secondary-container: '#e6ecff'
  tertiary: '#cec4c4'
  on-tertiary: '#352f2f'
  tertiary-container: '#0c0808'
  on-tertiary-container: '#7f7777'
  error: '#ffb4ab'
  on-error: '#690005'
  error-container: '#93000a'
  on-error-container: '#ffdad6'
  primary-fixed: '#e5e1e4'
  primary-fixed-dim: '#c8c6c8'
  on-primary-fixed: '#1c1b1d'
  on-primary-fixed-variant: '#474649'
  secondary-fixed: '#d8e2ff'
  secondary-fixed-dim: '#adc6ff'
  on-secondary-fixed: '#001a42'
  on-secondary-fixed-variant: '#004395'
  tertiary-fixed: '#ebe0df'
  tertiary-fixed-dim: '#cec4c4'
  on-tertiary-fixed: '#1f1a1a'
  on-tertiary-fixed-variant: '#4c4545'
  background: '#12131a'
  on-background: '#e3e1ec'
  surface-variant: '#33343c'
typography:
  display:
    fontFamily: Inter
    fontSize: 32px
    fontWeight: '600'
    lineHeight: 40px
    letterSpacing: -0.02em
  headline-sm:
    fontFamily: Inter
    fontSize: 18px
    fontWeight: '600'
    lineHeight: 24px
    letterSpacing: -0.01em
  body-md:
    fontFamily: Inter
    fontSize: 14px
    fontWeight: '400'
    lineHeight: 20px
  body-sm:
    fontFamily: Inter
    fontSize: 13px
    fontWeight: '400'
    lineHeight: 18px
  mono-label:
    fontFamily: Geist
    fontSize: 12px
    fontWeight: '500'
    lineHeight: 16px
    letterSpacing: 0.02em
  table-data:
    fontFamily: Inter
    fontSize: 13px
    fontWeight: '450'
    lineHeight: 16px
rounded:
  sm: 0.125rem
  DEFAULT: 0.25rem
  md: 0.375rem
  lg: 0.5rem
  xl: 0.75rem
  full: 9999px
spacing:
  unit: 8px
  container-padding: 24px
  gutter: 16px
  component-gap-sm: 4px
  component-gap-md: 8px
  row-height-dense: 32px
  row-height-standard: 40px
---

## Brand & Style
The design system is engineered for high-stakes institutional investment operations. It prioritizes **precision, auditability, and cognitive efficiency**. The brand personality is "Silent Power"—sophisticated and authoritative without being loud.

The aesthetic follows a **Modern Corporate / Minimalist** path with a heavy emphasis on data density. It draws inspiration from developer-centric tools, utilizing a "Dark Mode First" strategy to reduce eye strain during prolonged analysis. The interface relies on structural integrity, high-contrast borders, and a total absence of decorative flourishes like glassmorphism or aggressive gradients. Every pixel must serve a functional purpose in the decision-making workflow.

## Colors
The palette is rooted in a "Deep Slate" spectrum to provide a stable, low-distraction environment. 

- **Canvas & Surfaces:** The primary background is a true dark neutral to ensure maximum contrast for white text. Surfaces use subtle shifts in gray to indicate nesting and hierarchy rather than shadows.
- **Accents:** Professional Blue (#3B82F6) is reserved strictly for primary interactive elements, focus states, and progress indicators. 
- **Data States:** Semantic colors (Emerald, Amber, Crimson) are used with restraint. In high-density tables, these should often be represented by small pips or subtle text tints to prevent "color fatigue."

## Typography
This design system utilizes **Inter** for its neutral, highly legible character, and **Geist** for technical labels and data points to provide a clean, monospaced feel where precision matters.

- **Data Density:** Use `body-sm` (13px) as the default for sidebars and secondary meta-data. 
- **Tabular Data:** `table-data` uses a slightly tighter line-height to allow more rows to be visible above the fold. 
- **Emphasis:** Avoid bolding large blocks of text; use font-weight `500` or `600` for headers to maintain a clean, thin-stroke aesthetic.

## Layout & Spacing
The layout adheres to a **Strict 8px Grid**. Alignment is the primary tool for creating a sense of order in complex views.

- **Modular Panels:** Use a fixed-width left navigation (240px) and a flexible main content area. Side drawers for deep-dive analysis should occupy 400px-600px of the right viewport.
- **Data Tables:** Implement a "Density Toggle." High-density views use 32px row heights with 4px cell padding; standard views use 40px.
- **Breakpoints:** 
  - Desktop: 1440px+ (Full 12-column grid)
  - Laptop: 1024px (Collapsed sidebar to icons)
  - Tablet/Mobile: Not prioritized for this system; use responsive stacking for critical monitoring only.

## Elevation & Depth
Elevation is communicated through **Tonal Layering** and **1px Borders** rather than traditional shadows. 

- **Level 0 (Canvas):** #09090B. The base layer.
- **Level 1 (Cards/Panels):** #18181B with a 1px border of #27272A.
- **Level 2 (Popovers/Modals):** #18181B with a 1px border of #3F3F46. Use a very subtle, 10% opacity black shadow to slightly lift the element from the background.
- **Active States:** Use a 1px Blue (#3B82F6) border to indicate focus or active selection in a grid or list.

## Shapes
The shape language is **Technical and Sharp**. 

- **Standard Elements:** Buttons, inputs, and cards use a 4px (0.25rem) radius. This provides just enough softness to feel modern without losing the precision of a professional tool.
- **Strict Elements:** Data pips and status indicators may use 2px radius for a more "pixel-perfect" look.
- **Interactive States:** Hover states should be represented by a background color shift to #27272A rather than a change in shape or size.

## Components
- **Data Tables:** Columns must be sortable and resizable. Use "Skeleton" loaders during AI data fetches. Statuses are shown as a text label preceded by a 6px solid circle pip in the semantic color.
- **Command Palette:** A center-aligned modal (Cmd+K) with a search input and grouped results (Actions, Navigation, Help). Use `mono-label` for keyboard shortcuts.
- **KPI Cards:** Small-format cards containing a label, a large value, and a "Sparkline" (small-multiple chart) in the bottom third. The sparkline color should match the trend (Green for up, Red for down).
- **Workflow Timelines:** A vertical or horizontal track using thin 1px lines. Completed steps use the Blue accent; pending steps use a dashed border circle.
- **Input Fields:** Flat background (#09090B) with a 1px border (#27272A). On focus, the border changes to Blue (#3B82F6) with no outer glow.
- **Buttons:** 
  - *Primary:* Solid Blue (#3B82F6) with white text.
  - *Secondary:* Transparent background with 1px border (#3F3F46).
  - *Ghost:* No border/background until hover. Used for table actions.