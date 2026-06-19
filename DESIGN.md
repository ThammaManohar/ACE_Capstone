# Design

## Theme

Light, restrained, paper-quiet. Mood: a quiet law library reading room — steady cobalt ink, brass-warm highlights used sparingly, generous margins. Not a SaaS dashboard, not a chatbot skin. Pure white surface; the brand lives in the primary color and typography, not in a tinted background.

**Strategy:** Restrained (tinted neutrals + one accent, accent ≤10% of surface).

## Palette (OKLCH)

```css
:root {
  --bg:        oklch(1.000 0.000 0);     /* pure white */
  --surface:   oklch(0.970 0.004 230);   /* faint cool-tinted panel */
  --border:    oklch(0.880 0.006 230);
  --ink:       oklch(0.200 0.010 230);   /* body text, ~14:1 on bg */
  --muted:     oklch(0.480 0.012 230);   /* secondary text, ~5.3:1 on bg */
  --primary:   oklch(0.450 0.086 230);   /* cobalt — brand, actions */
  --primary-ink: oklch(1.000 0.000 0);   /* text on primary fill */
  --accent:    oklch(0.550 0.130 70);    /* warm brass — sparing use: badges, highlights */
  --accent-ink: oklch(1.000 0.000 0);
  --danger:    oklch(0.470 0.150 25);
  --focus-ring: oklch(0.450 0.086 230 / 0.45);
}
```

Contrast checked: ink-on-bg ≈ 14:1, muted-on-bg ≈ 5.3:1, primary-ink-on-primary ≈ 6.8:1 (white text on mid-saturation cobalt, per the Helmholtz-Kohlrausch text rule).

## Typography

- Display/headings: **Fraunces** (soft, characterful serif with optical-size axis — scholarly without being stuffy; distinct from the generic-serif default). Weights 500/600, optical size set high for headings.
- Body/UI: **Work Sans** (humanist sans, warmer and more distinctive than Inter/system sans, still highly legible at small sizes).
- No third family. No monospace needed in the visible UI.
- Scale: 14 / 16 / 20 / 28 / 38px, ratio ≈1.3-1.4 between steps. Headings get weight contrast, not size alone.
- No uppercase body copy. No tracked eyebrows.

## Layout

- Centered column, max width ~760px for reading comfort (65-75ch body lines).
- Two top-level views via `st.tabs`: **Ask** (primary, opens by default) and **Upload a document** (secondary). No sidebar — sidebar reads as an app-admin pattern, not a calm reading tool.
- No cards-as-default. Panels are flat with a single 1px `--border`, never both border + soft shadow.
- Border radius: 8px on inputs/panels, full-pill only on small status badges.
- Sources/citations render as a quiet inline disclosure (`st.expander`) listing document labels and a short snippet — never raw similarity/distance numbers.

## Motion

- Minimal: a single subtle fade/slide-in (180ms, ease-out) on the answer panel appearing. Respects `prefers-reduced-motion` (falls back to instant).
- No loading spinners with personality copy ("AI is thinking..."); plain "Searching the indexed documents…" / "Reading the document…" status text.

## Components

- **Primary button**: solid `--primary` fill, `--primary-ink` text, 8px radius, no shadow.
- **Secondary/ghost button**: 1px `--border`, `--ink` text, transparent fill.
- **Status badge** (e.g. "Not in the indexed documents"): pill, `--surface` fill with `--border`, `--muted` text — calm, not alarming (no red unless it's a true error).
- **Error state** (e.g. unsupported file type): `--danger` text, no red background fill, plain sentence, no icon clutter.
- Focus states: 2px `--focus-ring` outline on all interactive elements (Streamlit's default focus is barely visible — must be reinforced via CSS).
