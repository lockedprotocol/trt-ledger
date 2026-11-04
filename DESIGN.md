---
name: TRT Ledger
description: Free, independent price guide that turns TRT clinic prices into sourced first-year totals.
colors:
  periwinkle: "#9cbcff"
  periwinkle-light: "#bfd3ff"
  navy: "#13284d"
  navy-deep: "#0a1a36"
  link-blue: "#1d4fae"
  night-bg: "#0a111e"
  night-surface: "#111a2b"
  night-surface-raised: "#172238"
  night-tint: "#121d33"
  night-ink: "#e9eef7"
  night-muted: "#9ba7bd"
  night-line: "#233049"
  night-control: "#5f6c85"
  night-accent-soft: "#1b2a47"
  night-band: "#172a52"
  night-bar: "#3a4761"
  mist-bg: "#f5f7fb"
  paper: "#ffffff"
  mist-surface-raised: "#eef2f8"
  mist-tint: "#e6eefa"
  navy-ink: "#0f1d36"
  slate-muted: "#55617a"
  mist-line: "#dde4ee"
  slate-control: "#8c97ab"
  mist-accent-soft: "#e3eaf6"
  mist-bar: "#c2cbd9"
  confirmed-green: "#11734f"
  confirmed-green-soft: "#dff3e9"
  night-confirmed-green: "#4fc98f"
  night-confirmed-green-soft: "#12301f"
  check-amber: "#865100"
  check-amber-soft: "#fdf0d6"
  night-check-amber: "#f0b357"
  night-check-amber-soft: "#2e2412"
  error-red: "#b42318"
  night-error-red: "#f2847b"
typography:
  display:
    fontFamily: "Archivo, -apple-system, BlinkMacSystemFont, Segoe UI, sans-serif"
    fontSize: "clamp(38px, 5.6vw, 68px)"
    fontWeight: 850
    lineHeight: 0.98
    letterSpacing: "-0.015em"
    fontVariation: "\"wdth\" 72"
  headline:
    fontFamily: "Archivo, -apple-system, BlinkMacSystemFont, Segoe UI, sans-serif"
    fontSize: "clamp(30px, 3.8vw, 44px)"
    fontWeight: 850
    lineHeight: 1.02
    letterSpacing: "-0.01em"
    fontVariation: "\"wdth\" 75"
  title:
    fontFamily: "Archivo, -apple-system, BlinkMacSystemFont, Segoe UI, sans-serif"
    fontSize: "21px"
    fontWeight: 800
    lineHeight: 1.15
    letterSpacing: "-0.01em"
    fontVariation: "\"wdth\" 85"
  figure:
    fontFamily: "Archivo, -apple-system, BlinkMacSystemFont, Segoe UI, sans-serif"
    fontSize: "34px"
    fontWeight: 850
    lineHeight: 1.1
    letterSpacing: "-0.01em"
    fontFeature: "\"tnum\" 1"
    fontVariation: "\"wdth\" 75"
  body:
    fontFamily: "Archivo, -apple-system, BlinkMacSystemFont, Segoe UI, sans-serif"
    fontSize: "16px"
    fontWeight: 400
    lineHeight: 1.6
    fontVariation: "\"wdth\" 100"
  label:
    fontFamily: "Archivo, -apple-system, BlinkMacSystemFont, Segoe UI, sans-serif"
    fontSize: "13.5px"
    fontWeight: 550
    lineHeight: 1.4
    fontVariation: "\"wdth\" 100"
  tag:
    fontFamily: "Archivo, -apple-system, BlinkMacSystemFont, Segoe UI, sans-serif"
    fontSize: "12.5px"
    fontWeight: 600
    lineHeight: 1.5
    fontVariation: "\"wdth\" 100"
rounded:
  sm: "12px"
  md: "20px"
  lg: "28px"
  lg-mobile: "24px"
  pill: "999px"
spacing:
  xs: "6px"
  sm: "8px"
  md: "12px"
  lg: "16px"
  xl: "24px"
  card: "22px"
  hero: "56px"
  section: "80px"
  section-mobile: "56px"
components:
  button-primary:
    backgroundColor: "{colors.periwinkle}"
    textColor: "{colors.night-bg}"
    rounded: "{rounded.pill}"
    padding: "11px 22px"
    height: "46px"
  button-primary-hover:
    backgroundColor: "{colors.periwinkle-light}"
  button-primary-light:
    backgroundColor: "{colors.navy}"
    textColor: "{colors.paper}"
    rounded: "{rounded.pill}"
    padding: "11px 22px"
    height: "46px"
  button-primary-light-hover:
    backgroundColor: "{colors.navy-deep}"
  button-secondary:
    backgroundColor: "{colors.night-surface}"
    textColor: "{colors.night-ink}"
    rounded: "{rounded.pill}"
    padding: "10px 18px"
    height: "44px"
  button-secondary-hover:
    backgroundColor: "{colors.night-surface-raised}"
  button-small:
    backgroundColor: "{colors.periwinkle}"
    textColor: "{colors.night-bg}"
    rounded: "{rounded.pill}"
    padding: "8px 16px"
    height: "38px"
  input:
    backgroundColor: "{colors.night-surface}"
    textColor: "{colors.night-ink}"
    rounded: "{rounded.sm}"
    padding: "10px 14px"
    height: "46px"
  search-pill:
    backgroundColor: "{colors.night-surface}"
    textColor: "{colors.night-ink}"
    rounded: "{rounded.pill}"
    padding: "7px 7px 7px 18px"
  card:
    backgroundColor: "{colors.night-surface}"
    textColor: "{colors.night-ink}"
    rounded: "{rounded.md}"
    padding: "{spacing.card}"
  hero-panel:
    backgroundColor: "{colors.night-tint}"
    textColor: "{colors.night-ink}"
    rounded: "{rounded.lg}"
    padding: "{spacing.hero}"
  tag-lowest:
    backgroundColor: "{colors.night-confirmed-green}"
    textColor: "{colors.night-bg}"
    typography: "{typography.tag}"
    rounded: "{rounded.pill}"
    padding: "3px 10px"
  tag-confirmed:
    backgroundColor: "{colors.night-confirmed-green-soft}"
    textColor: "{colors.night-confirmed-green}"
    typography: "{typography.tag}"
    rounded: "{rounded.pill}"
    padding: "3px 10px"
  tag-check:
    backgroundColor: "{colors.night-check-amber-soft}"
    textColor: "{colors.night-check-amber}"
    typography: "{typography.tag}"
    rounded: "{rounded.pill}"
    padding: "3px 10px"
  tag-neutral:
    backgroundColor: "{colors.night-surface-raised}"
    textColor: "{colors.night-muted}"
    typography: "{typography.tag}"
    rounded: "{rounded.pill}"
    padding: "3px 10px"
  chip-selected:
    backgroundColor: "{colors.night-accent-soft}"
    textColor: "{colors.night-ink}"
    rounded: "{rounded.pill}"
    padding: "6px 14px"
    height: "40px"
  alert-band:
    backgroundColor: "{colors.night-band}"
    textColor: "{colors.paper}"
    rounded: "{rounded.lg}"
    padding: "44px"
---

# Design System: TRT Ledger

## Overview

**Creative North Star: "The Open Ledger"**

TRT Ledger is a price guide that shows its working. The system is the category standard for consumer health comparison, executed at full craft: large rounded panels, pill controls, one confident ink color, and condensed heavy numerals that make a first-year total the loudest thing on any surface it appears on. Every visual decision serves one act: reading a sourced number, seeing how sure the site is of it, and acting on it.

The default first visit is **dark**: a deep blue-black ground with periwinkle actions. A stored choice from the header sun/moon switch can flip the site to the light world of soft blue-gray grounds and navy ink; both themes are full peers built from the same custom properties, and every generated state, city and partner page applies the same pre-paint theme script. Density is moderate: comparison cards carry a lot of facts, so the system spends its contrast on totals and status, and keeps everything else quiet in muted ink.

Imagery is limited to one authored stroke-icon set and the logo mark. There are no photographs, stock people, or illustrations.

**Key Characteristics:**
- Dark by default; light is a stored opt-in with identical structure.
- Archivo variable throughout: condensed extra-bold for display and figures, regular width for UI.
- Tabular figures on every price.
- Pills for every control and status tag; large-radius panels for every container.
- Three status colors with fixed meanings: green confirmed/savings, amber check, red errors.
- One authored motion moment; everything else is a short state transition.

## Colors

A cool blue-navy family carrying one action color, with three semantic hues that each mean exactly one thing. Every color is a custom property in the shared stylesheet; the dark set redefines the same names, so components never name a theme.

### Primary
- **Periwinkle** (dark default action): primary buttons, the header "Find clinics" pill, links, focus rings, the selected-tab count, and the "Ledger" half of the wordmark.
- **Periwinkle Light**: hover state of every periwinkle action.
- **Ledger Navy** (light-theme action): the same roles in the light theme, and the fill of the price-alert band in light.
- **Navy Deep**: hover state of navy actions.
- **Link Blue**: inline links and focus outlines in the light theme, kept separate from navy so links read as links on navy-adjacent surfaces.

### Secondary (status)
- **Confirmed Green / Night Confirmed Green**: a clinic confirmed for the visitor's state, the "Lowest first-year cost" tag and rank badge, savings amounts, the visitor's own bar in the overpaying chart, and the "Lowest first-year cost confirmed for [state]" line on the hero price card. Soft variants back the "confirmed" tags and the included-tick in inclusion lists.
- **Check Amber / Night Check Amber**: "Check state", "Unverified price", stale-price and "not stated" marks, always on its soft ground. The calculator's "check your numbers" note uses the soft amber ground with normal ink.
- **Error Red / Night Error Red**: invalid inputs (border), error messages, and form error text.

### Neutral
- **Night BG / Mist BG**: page ground.
- **Night Surface / Paper**: cards, panels, inputs, the header search pill, the footer.
- **Night Surface Raised / Mist Surface Raised**: hover fill for secondary pills, neutral tags, inclusion-list pills, rank badges, the segmented-tab track.
- **Night Tint / Mist Tint**: base of the hero panel, under a soft radial glow (blue top-right; in light also a faint green bottom-left).
- **Night Ink / Navy Ink**: headings, figures, body copy.
- **Night Muted / Slate Muted**: labels, notes, source lines, secondary facts.
- **Night Line / Mist Line**: 1px hairlines on cards, panels, dividers, trust-bar rules.
- **Night Control / Slate Control**: the stronger 1px border of form fields and the search pill, so inputs read as inputs against cards.
- **Accent Soft (night / mist)**: selected chips and toggles, focus halo around fields, text selection.
- **Night Band**: the price-alert band in dark (navy in light), with white text and pale blue-gray secondary text.
- **Bar (night / mist)**: the comparison bars for other clinics in the overpaying chart.

### Named Rules
**The Three Meanings Rule.** Green means confirmed for your state or money saved; amber means check this; red means something is wrong with input. No status color is ever decoration. The build currently also tints the "not included" cross in clinic inclusion lists red; that use is under review and is not a pattern to extend.

**The Confirmed-Only Green Rule.** "Lowest first-year cost" and its green treatment go only to a clinic confirmed to serve the visitor's state. A clinic that does not publish its states gets amber "Check state", never green.

**The One Action Color Rule.** Periwinkle (dark) or navy (light) is the only action fill. Secondary actions are surface-colored pills with a hairline, not a second accent.

## Typography

**Display Font:** Archivo variable (wdth 62–125, wght 400–900, from Google Fonts), with -apple-system, Segoe UI, sans-serif fallback
**Body Font:** Archivo at regular width (wdth 100)

**Character:** One family doing two jobs through its width axis. Condensed and extra-bold, it is a dense, confident headline and price voice; at full width and normal weight it is a calm, legible UI face.

### Hierarchy
- **Display** (850, clamp 38–68px, line-height 0.98, wdth 72): the home hero headline and the overpaying result's large number (68px, 54px on phones). State and city page titles use the same voice at clamp 34–56px, wdth 75.
- **Headline** (850, clamp 30–44px, line-height 1.02, wdth 75): section heads and the alert band heading; guide-page section heads use clamp 24–32px at wdth 80.
- **Title** (800, 17–22px, wdth 85–88): clinic names on cards (21px, wdth 88), summary and group heads (18–22px, wdth 85), the hero price card's clinic name (26px, 850, wdth 80).
- **Figure** (850, 32–40px, wdth 75, tabular): every first-year total, lab total and summary stat. The hero price card total is 40px (34px on phones); trust-bar figures are 22px at 800, wdth 80.
- **Body** (400, 16px, line-height 1.6, wdth 100): paragraphs and lists; ledes at 17–18.5px in muted ink, capped at about 560px or 72ch.
- **Label** (550, 13.5px): form labels, notes, source and "checked" lines, all in muted ink. Strong text inside copy is 650.
- **Tag** (600, 12.5px): pill tags and count badges.

### Named Rules
**The Width Axis Rule.** Hierarchy is carried by width and weight together: display and figures sit between wdth 72 and 85 at 800–850; UI text stays at wdth 100. Never set body copy condensed, and never set a total at regular width.

**The Tabular Price Rule.** Every price, count, distance and stat uses tabular figures so columns of totals align.

**The Sentence Case Rule.** No uppercase labels, tracked-out eyebrows or kickers above headings. A heading starts the section.

## Layout

A single centered column of 1160px maximum with 24px side padding (16px on phones). Sections breathe at 80px vertical padding (56px on phones); a "band" section sits on the surface color between hairlines. The sticky 66px header is translucent page-ground with a 14px backdrop blur and a hairline below.

The home hero is one large tinted panel split about 1.35 : 1, copy and ZIP search left, price card right, with 56px internal padding; under 960px it stacks to one column (price card follows the search), and under 720px the header nav becomes a horizontally scrolling pill row under the logo. A four-fact trust bar sits below the hero panel between hairlines, dropping to two columns on smaller screens.

Clinic comparison is a vertical list of full-width cards, not a grid: identity and tags on the left, the cost block pinned right in a 190px column; on phones the cost block moves under the name with the "Visit site" button beside the total. Labs and in-person chains use auto-fill grids (196px and 300px minimums). Directory tables collapse to labelled stacked rows on phones.

Breakpoints: 960px (stack two-column layouts) and 720px (phone layout, 44px minimum touch targets on every control).

## Elevation & Depth

Depth is soft and mostly tonal. In light, cards and panels lift with a two-part ambient shadow (a 1–2px contact shadow plus a long, low-opacity navy drop), and the hero price card uses a deeper version. In dark, shadows collapse to a 1px contact shadow and separation comes from stepped surfaces (ground, surface, raised surface) and hairlines. Nothing uses hard offset shadows.

### Shadow Vocabulary
- **Rest** (`--shadow`): every card, panel, lab tile, summary block, the ZIP search pill, and the selected segmented tab.
- **Lifted** (`--shadow-lg`): only the hero price card, so the live number reads as the object on top.
- **Focus halo** (3–4px accent-soft ring): fields and the search pill on focus, in place of a shadow change.

### Named Rules
**The Quiet Lift Rule.** Shadows are ambient and the same at rest everywhere; there is no hover lift on cards. State is shown by color and border, not by elevation.

## Shapes

Two families: pills and large-radius rectangles. Every button, tag, chip, toggle, nav link, select in the hero, segmented control and count badge is a full pill. Every container is a soft rectangle: 20px for cards, panels and tiles; 28px for the hero panel and the alert band (24px on phones); 12px for form fields, the assumptions disclosure and inline notes. Borders are 1px hairlines throughout; the only dashed border is the "doesn't publish prices" callout. Rank badges and inclusion-list status marks are circles.

The logo (chosen 2026-11-04, "Price drop") is a 34px navy tile (#13284d, 18/64 corner radius, a faint periwinkle hairline so it holds on the dark ground) holding three rounded columns that step down from left to right, the first two in periwinkle at 50% and 85%, the last and lowest in confirmed green, with a white arrow following the fall. It reads as "find the lower price" and echoes the overpaying chart. The mark uses fixed colors in both themes. Beside it the wordmark sets "TRT" in ink and "Ledger" in the link color (periwinkle on dark, link blue on light) at 800 and wdth 88, so green stays reserved for confirmed and savings. The same mark is the favicon (assets/favicon.svg).

## Components

### Buttons
Confident and round.
- **Shape:** full pill (999px), 46px minimum height (44px for secondary, 38px for small, raised to 44px on phones).
- **Primary:** periwinkle with night-ground text in dark, navy with white text in light, 650 weight. Used for "Find clinics", form submits and the header nav CTA.
- **Hover / Active:** fill moves to the lighter periwinkle (dark) or deeper navy (light) over 0.15s; pressing nudges down 1px. Focus is a 2px link-colored outline offset 2px.
- **Secondary:** surface-colored pill with a hairline border and ink text (14.5px); hover fills with the raised surface. Used for map links and secondary actions.
- **Small:** primary-colored pill at 14px, 8px 16px padding, for "Visit site" on cards and "Email us" on partner offers; it carries the outbound arrow icon.

### Chips and tags
- **Tags:** 12.5px, 600, pill, 3px 10px, color-only (no border). Variants: solid green "Lowest first-year cost"; soft green "confirmed"; soft amber "Check state" and stale-price; raised-surface muted for model and "Estimate".
- **Filter chips and toggles:** surface pill with a hairline and a native checkbox in the accent color; checked state takes an accent border and accent-soft fill.
- **Segmented tabs:** a raised-surface pill track holding transparent pill buttons; the selected tab becomes a surface pill with the rest shadow and its count badge turns accent.

### Cards / Containers
- **Corner Style:** 20px.
- **Background:** surface on page ground; on band sections, panels drop to page ground with no shadow.
- **Shadow Strategy:** Rest shadow (see Elevation & Depth).
- **Border:** 1px hairline. The confirmed-lowest card swaps it for a 1px green border plus a green ring.
- **Internal Padding:** 18–22px; the clinic card reserves a 226px right column for its pinned cost block.

### Inputs / Fields
- **Style:** 46px minimum, 12px radius, surface fill, 1px control-colored border, 16px text so phones never zoom.
- **Focus:** border turns link-colored with a 3px accent-soft halo; hover darkens the border to ink.
- **Error:** border turns red and the message below turns red; messages are written as a fix ("Enter a 5-digit ZIP code.").

### Navigation
Sticky translucent header: logo left, pill nav links (14.5px, 550) right with a raised-surface hover, the first link as a primary pill, and a 44px circular theme switch showing a sun or moon stroke icon. Guide pages add muted breadcrumb links above the title.

### Icons
One authored set of stroke icons on a 24px grid: 2px stroke (1.8px on the search pin and theme switch), round caps and joins, no fill, inheriting the text color and sized to 1em inline. The set: outbound arrow, right arrow, tick, cross, question mark, map pin, sun, moon. Disclosure chevrons are drawn from two CSS borders. New icons are drawn to the same stroke; no emoji, icon fonts or text glyphs stand in for icons.

### Hero price card (signature)
The live answer in the first viewport: a surface card with the Lifted shadow inside the hero panel. Its head pairs the clinic name with a 40px tabular total, over a green line that reads "Lowest first-year cost confirmed for [state]" (or "among clinics that publish their states" before a state is known). Below, a hairline, the itemized lines (label in muted ink, amount in ink, estimates marked), a "Checked [date] · Source" line, and a "Compare all [n] confirmed for [state]" link with the right-arrow icon. When no clinic is confirmed for the state, the card says so plainly instead of showing a price.

### Clinic comparison card (signature)
Rank circle, clinic name, a row of pill tags, the pinned cost block (muted label, 34px total, per-month line, "Visit site" small button, checked date and source link), then a row of inclusion pills each led by a small circular status mark: green tick, amber question mark, or cross. A disclosure opens the cost breakdown and fine print.

### Overpaying chart and the one motion moment
Horizontal bars, one per clinic, sorted against what the visitor pays; the visitor's bar is green, unsure prices are outlined rather than filled, and a tooltip shows detail on hover. When the first result appears, the large number settles in from a slight blur and offset (0.7s) and the bars grow from the left (0.8s, lightly staggered), both on a long ease-out. It runs once per idle-to-result change and is switched off entirely, with every other transition, under Reduce Motion.

### Price-alert band
A 28px-radius band in navy (light) or night band (dark) with a condensed headline, pale secondary text, a pill email field and a white pill button with navy text.

## Do's and Don'ts

### Do:
- **Do** treat dark as the default first visit and design every new surface in both themes from the shared custom properties.
- **Do** make the first-year total the largest, most condensed text on any card (850, wdth 75, tabular).
- **Do** pair every price with its "Checked [date]" and a Source link with the outbound icon.
- **Do** use amber "Check state" for any clinic that does not publish its states, and reserve "Lowest first-year cost" and its green for a clinic confirmed for the visitor's state.
- **Do** keep every control a pill at 44px or taller on phones.
- **Do** draw any new icon to the existing 24px, 2px round-cap stroke.

### Don't:
- **Don't** add a second accent color or use green, amber or red decoratively.
- **Don't** use photographs, stock people, clinic imagery or illustrations.
- **Don't** add eyebrows, kickers or uppercase tracked labels above headings.
- **Don't** use hard offset shadows or hover lifts on cards.
- **Don't** add motion beyond the overpaying result's settle-in; state changes are 0.15s color transitions.
- **Don't** use emoji or text glyphs as icons.
