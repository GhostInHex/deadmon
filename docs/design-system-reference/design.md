# V7 Go — Design System

Canonical source of truth for UI in this project. Read before generating or editing
any component, page, or style.

Source of record: Paper file [`01M4P2QPPSW3J2G6YD5BPP14SA`](https://app.paper.design/file/01M4P2QPPSW3J2G6YD5BPP14SA)
("V7 Go — design system + homepage hero"). This file mirrors its token set. If the two
ever disagree, Paper wins and this file is the bug.

---

## Direction

**Industrial.** Precision-instrument register, not soft enterprise. Near-black ink on pure
white, one hot signal orange, hairline rules instead of boxed cards, monospace stamped
labels. Asymmetric scale contrast — very large serif display against small muted labels.

Mood reference points: machine shop, control panel, stamped specification plate.

**Deliberately avoided:** dark navy + electric purple/lime/teal (2019–2024 SaaS cliché),
warm off-white + terracotta, gradients, drop shadows on cards, purple anything.

---

## Tokens

Paste verbatim. Do not hand-rewrite these.

```css
:root {
  /* ---- Color ---- */
  --color-ink: #292929;          /* primary text, warm charcoal — never pure black on white */
  --color-ink-deep: #171717;     /* headlines, emphasis */
  --color-paper: #FFFFFF;        /* primary ground */
  --color-paper-warm: #F7F6F5;   /* secondary surface, alternating bands */
  --color-rule: #E4E2E0;         /* hairline borders — prefer over boxed cards */
  --color-rule-strong: #D1CFCE;  /* section dividers, outline buttons */
  --color-signal: #FF683D;       /* PRIMARY ACCENT — one per viewport, never a fill field */
  --color-signal-deep: #EC580A;  /* pressed/hover for signal */
  --color-signal-wash: #FFF1EB;  /* tinted accent callout surface */
  --color-mono: #737373;         /* muted mono labels, captions */
  --color-ink-muted: #6B6B6B;    /* secondary body — passes contrast on white */
  --color-ink-inverse: #FFFFFF;  /* text on dark or signal ground */

  /* ---- Type family ---- */
  --font-display: 'Instrument Serif';
  --font-body: 'Inter';
  --font-mono: 'DM Mono';

  /* ---- Type scale ---- */
  --text-2xs: 11px;   /* mono uppercase eyebrows only */
  --text-xs: 12px;    /* mono data labels, dense table cells */
  --text-sm: 14px;    /* nav links, captions, small body */
  --text-md: 16px;    /* default body */
  --text-lg: 20px;    /* lead paragraphs, card titles */
  --text-xl: 28px;    /* section headings */
  --text-2xl: 40px;   /* sub-headline */
  --text-3xl: 64px;   /* hero headline, desktop */
  --text-4xl: 88px;   /* display headline, hero only */

  /* ---- Weight ---- */
  --font-weight-regular: 400;
  --font-weight-medium: 500;
  --font-weight-semibold: 600;
  --font-weight-bold: 700;
  --font-weight-black: 900;

  /* ---- Tracking ---- */
  --tracking-display: -0.02em;   /* tight, large display type */
  --tracking-body: 0em;
  --tracking-mono: 0.08em;       /* open, uppercase mono labels */

  /* ---- Leading ---- */
  --leading-display: 100px;      /* for --text-4xl, near-solid editorial */
  --leading-heading: 36px;
  --leading-body: 26px;          /* generous, aids readability */
  --leading-tight: 20px;         /* for --text-sm */

  /* ---- Spacing ---- */
  --spacing-1: 4px;
  --spacing-2: 8px;
  --spacing-3: 12px;
  --spacing-4: 16px;
  --spacing-5: 24px;
  --spacing-6: 32px;
  --spacing-7: 48px;
  --spacing-8: 64px;
  --spacing-9: 96px;
  --spacing-10: 128px;
  --spacing-11: 160px;

  /* ---- Radius ---- */
  --radius-sm: 4px;
  --radius-md: 8px;
  --radius-lg: 12px;
  --radius-pill: 999px;          /* buttons and pill badges only */

  /* ---- Container ---- */
  --container-content: 1200px;   /* max page content, 64px gutters at 1440 */
  --container-prose: 680px;      /* max measure for body paragraphs */

  /* ---- Breakpoint ---- */
  --breakpoint-sm: 480px;
  --breakpoint-md: 768px;
  --breakpoint-lg: 1024px;
  --breakpoint-xl: 1280px;

  /* ---- Opacity ---- */
  --opacity-muted: 0.72;
  --opacity-faint: 0.4;
}
```

**Contrast floor:** text below 16px must clear WCAG AA against its actual background.
`--opacity-muted` and `--opacity-faint` are for de-emphasis and decoration only — never
for body copy.

---

## Usage rules

1. **No raw hex in components.** Every color, space, and radius is a token. This is what
   makes theming and dark mode possible later.
2. **Signal is scarce.** One `--color-signal` element per viewport. Two is a bug. It marks
   the single most important thing on screen — currently the italic half of the hero
   headline and one stat figure.
3. **Hairlines over cards.** Separate sections with `border-top: 1px solid var(--color-rule)`.
   Reserve boxed surfaces for genuinely distinct objects.
4. **Scale contrast over grid sameness.** A 88px display line beside a 11px mono label is
   the intended texture. Uniform mid-size everything is the failure mode.
5. **Whitespace is a feature.** Generous above the fold, tighter within related groups.

---

## Components

**Button — primary.** Ink ground, pill radius.
```css
font-family: var(--font-body); font-size: 15px; font-weight: 500;
padding: 15px 30px; border-radius: var(--radius-pill);
background: var(--color-ink); color: var(--color-paper);
```

**Button — accent.** Signal ground. Reserve for the single highest-intent action.

**Button — outline.** `border: 1px solid var(--color-rule-strong)`, ink text, transparent.

**Badge / pill.** Mono uppercase 11px, `letter-spacing: 0.08em`, `signal-wash` ground,
`signal-deep` text, optional 5px dot in `--color-signal`.

**Stat cell.** 44px Inter Bold `700`, `letter-spacing: -0.03em`, over an 11px mono uppercase
label in `--color-mono`. Exactly one figure per row may take `--color-signal`.

**Stat strip.** Full-bleed flex row, `border-top` hairline, 1px `--color-rule` dividers
between cells. First and last cells get asymmetric padding to meet the page gutter.

**Nav.** 76px tall, `padding: 0 64px`, hairline bottom border. Logo lockup left, five
Inter 14px links centered, "Log in" + ink pill CTA right.

---

## Paper-specific gotchas

Both of these were hit while building the source artboards. They will silently produce
broken output.

**1. `font-size` does not resolve `var()` tokens in Paper.**
Colors, spacing, and radius resolve correctly. Font sizes do not — `font-size: var(--text-sm)`
is stored as a literal unresolved string and renders at the default size. Use explicit px
for any font size written into a Paper node. CSS in a real codebase should use the tokens
normally.

**2. Rich text is flattened.**
`<span style="color: var(--color-signal)">Zero room for error.</span>` inside a headline
renders as a single text node and loses the span's styling entirely — the accent color
silently disappears.

To get a two-tone headline, use sibling text nodes in a flex row:
```html
<div style="display:flex; align-items:baseline; gap:16px;">
  <div style="font-family:'Instrument Serif'; font-size:88px; color:#171717;">Complex workflows.</div>
  <div style="font-family:'Instrument Serif'; font-size:88px; font-style:italic; color:#FF683D;">Zero room for error.</div>
</div>
```

**3. Artboard overflow.** Fixed heights clip content. Set `height: fit-content` rather than
guessing a new pixel height when a composition runs long.

---

## Build status

| Piece | Status |
|---|---|
| Token set (59) | Complete |
| Design System artboard | Complete, verified |
| Homepage desktop 1440 | Built; final section order inferred, not re-rendered |
| Homepage mobile 390 | Not started |
| Dark mode | Not started |

### Dark mode — not yet defined

The system is architected for it (semantic tokens only, no raw hex), but no dark ramp
exists. When defining one, note that a naive inversion fails:

- Ink and paper **do not swap roles**. `#292929` becomes the ground; body text needs to
  move *lighter* (toward `#EDEAE6`). Reusing ink for both is the standard failure.
- `--color-signal` `#FF683D` will likely vibrate on near-black and needs a lighter step
  (toward `#FF8A63`).
- Rules **invert direction** — `#E4E2E0` darkens on white; on dark it must lighten.
- Add a `[data-theme="dark"]` block that remaps the semantic layer only. Components should
  not change.