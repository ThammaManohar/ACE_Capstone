# Design

## Theme

BigLaw firm-site register: light page, deep navy ink, monochrome restraint, institutional gravity through whitespace and type rather than color or decoration. Reference points: Cravath, Sullivan & Cromwell — minimal color, serif display headings, generous margins, understated interactive elements. No tinted header band, no second accent color, no SaaS-style filled CTAs.

**Strategy:** Restrained, monochrome (a single navy ink color carries headings, actions, and emphasis; distinction comes from weight and position, not hue).

## Palette (OKLCH)

```css
:root {
  --bg:        oklch(1.000 0.000 0);     /* pure white */
  --surface:   oklch(0.970 0.004 230);   /* faint cool-tinted panel, used sparingly */
  --border:    oklch(0.880 0.006 230);
  --border-strong: oklch(0.790 0.010 230);
  --ink:       oklch(0.180 0.014 230);   /* near-black navy, body text + headings */
  --muted:     oklch(0.480 0.012 230);   /* secondary text, ~5.3:1 on bg */
  --primary:   oklch(0.180 0.014 230);   /* same deep navy — the only brand color */
  --primary-ink: oklch(1.000 0.000 0);
  --danger:    oklch(0.470 0.150 25);
  --focus-ring: oklch(0.180 0.014 230 / 0.45);
}
```

No accent color. `--primary` and `--ink` are intentionally the same deep navy — one color, used consistently, with weight and underline/border doing the work that a second accent hue used to do.

## Typography

- Display/headings: **Fraunces** (soft, characterful serif with optical-size axis), weights 500/600.
- Body/UI: **Work Sans**.
- No third family. No monospace.
- Generous whitespace: wider margins and section gaps than a typical SaaS density — unhurried, institutional pacing.
- No uppercase body copy. No tracked eyebrows except the single masthead-less heading eyebrow already in place.

## Layout

- Centered column, max width ~760px.
- Plain white page, no tinted header band — the heading sits directly on the page background.
- Two top-level views: **Ask** (primary) and **Upload a document** (secondary). No sidebar.
- No cards-as-default. Panels are flat with a single 1px `--border`.
- Sources/citations render as a quiet inline disclosure listing document labels and a short snippet — never raw similarity/distance numbers.

## Motion

- Minimal: a single subtle fade/slide-in on the answer panel appearing. Respects `prefers-reduced-motion`.
- Plain status text ("Searching the indexed documents…"), no personality copy.

## Components

- **Primary button**: outlined/text-style — navy text, navy underline or 1px outline, transparent background. Not a filled SaaS CTA.
- **Active tab**: navy underline + bold weight, no color change.
- **Status badge / scope pill**: `--surface` fill, `--border` outline, navy dot/text — same single-color logic.
- **Citation marks**: navy, weight-differentiated from body text.
- **Error state**: `--danger` text only, no background fill.
- Focus states: 2px `--focus-ring` outline (navy-based) on all interactive elements.
