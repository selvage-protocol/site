# Accessibility: the WCAG AA floor

The page holds itself to WCAG 2.2 AA. Ratios are computed from the colours the page paints — the
theme tokens in `style.css`, the colour a rule declares where a pair is not a token, and, for the
one mark that is artwork rather than a token, the pixels of `public/mark-header.png` — never
eyeballed; `scripts/check-contrast.py` asserts them in the gate, so a regression fails the build
instead of waiting for a look. Measured today:

| Pair | Ratio | Needs |
|---|---|---|
| body text on page | 11.34:1 | 4.5:1 |
| muted prose on page | 7.37:1 | 4.5:1 |
| link on page | 8.07:1 | 4.5:1 |
| button label on its mauve fill | 8.07:1 | 4.5:1 |
| peer badge label on its mauve fill (the first peer's name in the window; the label is read from the badge's own rule rather than taken to be the page's colour) | 9.23:1 | 4.5:1 |
| peer badge label on its teal fill (the second peer's name in the window) | 12.59:1 | 4.5:1 |
| peer badge label on its peach fill (the third peer's name in the sample) | 10.59:1 | 4.5:1 |
| code comment on the sample's ground (the editor theme's `comment`) | 6.64:1 | 4.5:1 |
| code keyword on the sample's ground (`keyword`, the mauve the page already uses) | 9.23:1 | 4.5:1 |
| code string on the sample's ground (`string`) | 12.61:1 | 4.5:1 |
| code number on the sample's ground (`number`) | 10.59:1 | 4.5:1 |
| code type on the sample's ground (`type`) | 14.76:1 | 4.5:1 |
| code function on the sample's ground (`fn`, the browser client's own function colour) | 8.91:1 | 4.5:1 |
| the room window's line numbers, over the ground the hero figure actually paints, the glow included (the window's fill and the radial wash's centre, the lighter of the two; the colour the window's own rule paints, read from the stylesheet rather than taken from a token the window does not use there) | 4.58:1 | 4.5:1 |
| the not-yet-available card's number and its planned row, on the band the card is transparent over (the band's own fill, read from its rule) | 4.75:1 | 4.5:1 |
| the repository description on the repository card, on the card's hover fill, and on the page itself | 6.22:1 / 5.81:1 / 5.81:1 | 4.5:1 |
| the peers' caret bars and badge fills on the sample's ground (the figure's fill over the card's over the page) | 9.23:1 / 12.59:1 / 10.59:1 | 3.0:1 |
| the peers' caret bars and badge fills on the room window, over the ground the hero figure is drawn on | 8.55:1 / 11.67:1 / 9.82:1 | 3.0:1 |
| code type under a peer's selection fill, on the sample's ground | 7.92:1 | 4.5:1 |
| code type under a peer's selection fill, on the window | 7.20:1 | 4.5:1 |
| the selection tint itself, at the client's quarter alpha (mauve / teal, on the window: 1.70:1 / 1.90:1) | 1.67:1 / 1.86:1 | 1.5:1 |
| code text on code background | 12.14:1 | 4.5:1 |
| muted text on code background | 7.89:1 | 4.5:1 |
| badge text on its fill (the primitive's default chip, computed as the palette's mauve over its own 10% wash; the page's own badges are the pills the cards carry, measured in the groups below) | 6.63:1 | 4.5:1 |
| secondary-button text on its fill, the primitive's own (the page renders the `outline` variant, so this pair is the component's; hover state, the worst of rest `15` at 5.98:1) | 5.32:1 | 4.5:1 |
| ghost-button text on its hover fill (`bg-surface0/60`; the variant is parsed from the component, and the page carries no ghost button) | 9.75:1 | 4.5:1 |
| secondary button boundary, the primitive's own (`border-mauve/60`, parsed from the component) | 3.82:1 | 3.0:1 |
| outline button boundary on the page (`border-surface1`, parsed from the component; below the 3.0:1 a boundary that *identifies* a control would need and above the floor a reader loses it at — the button's own label and focus ring identify it) | 1.80:1 | 1.5:1 |
| focus outline against the page | 8.07:1 | 3.0:1 |
| window text on the window, over the ground the hero figure is drawn on | 12.02:1 (muted 7.81:1) | 4.5:1 |
| hero figure text on the figure's own ground (the figure sits on the page, so its ground is `--bg`) | 11.34:1 (muted 7.37:1) | 4.5:1 |
| the nav mark's median ink pixel on the header's ground (the owner's artwork, a decorative logotype: 1.4.11 measures graphical objects *required to understand the content*, which a mark with `alt=""` beside the link's own `Selvage` label is not, and the standard's logotype clause — text that is part of a logo or brand name has no contrast requirement — is SC 1.4.3's rather than 1.4.11's; its own pixels read out of `public/mark-header.png` and composited over `--bg`) | 1.88:1 | 1.5:1 |

WCAG 1.4.1 is the one criterion measured the other way round, because both of its floors cannot hold
at once here. It asks for 3.0:1 between a link and the text beside it when colour is the only thing
distinguishing the two, and the link's own text is separately floored at 4.5:1 against its
background. `--fg` is 11.34:1 on `--bg`, so a colour that just clears the text floor is 11.34 / 4.5
= 2.52:1 from the prose, and a colour 3.0:1 from the prose is at most 3.78:1 on the page, below the
text floor. The page takes 1.4.1's other allowed affordance instead: every prose link is underlined
(`text-decoration-line` named in `style.css`, because preflight's `text-decoration: inherit` had
left every link colour-only, which is why the thickness and offset already there drew nothing).
`scripts/check-contrast.py` reads that declaration out of the stylesheet and asserts the 3.0:1 pair
whenever it is missing, so a colour-only link scheme fails the gate: the stylesheet as it stood
before the underline went in measures 1.40:1 against the prose beside it and fails the check.

A link wears one colour, `--link`, in every state, a followed link included: the underline is the
affordance, so nothing about a link's state is carried by colour, and two links that differ only in
whether they have been visited do not read as two different things.

Four groups the check does not parse are computed the same way, from the colours the browser
composites, and are re-measured whenever the fills around them move: inline code text on its chip
fill (`--color-surface0`) 8.69:1; the small text on the page's own ground — the try cards' numbers,
their footnote, the invite strip's label and the host the copy control hands over — 7.37:1; the card
body text on the card fill (`#181825`) 7.89:1; and the client chips 12.97:1 on the figure band they
are drawn on, with the planned client's chip at 6.64:1 and the open-list chip at 5.07:1 on the same
band. The status pills the cards carry are the same shape — their own colour over their own wash, on
the card each one sits in — and the lowest of them is 6.38:1 (the specification's mauve on a hovered
repository card). The two overlay tones are used only where they clear the floor of the ground they
are painted on: `--color-overlay1` carries the copy control's own label on the card fill (4.75:1)
and the open-list chip on the figure band (5.07:1), and `--color-overlay2` carries the terminal's
comments on the terminal's fill, and the planned client's chip on the figure band (all 6.64:1), as
well as the repository grid's open-list note on the page (5.81:1), where `--color-subtext1` carries
that strip's lead (9.26:1). The washes the page paints its own marks over are measured the same way:
the panels' chips sit at 9.50:1 (green) and 8.10:1 (peach) on their own washes, the highlighted row
of the comparison card at 10.70:1, and the open file's row in the window at 10.42:1. The section
hairlines sit at 1.30:1 against the page on purpose: they are decorative separators, they carry no
state, and nothing is identified by them. The panel and card borders the design draws in
`--color-surface1` are 1.80:1, which is below the 3.0:1 a boundary that *identifies* something would
need, and the page does not use one to identify anything; the one such boundary on a control is the
outline hero button, which the check measures and holds to that same visibility floor rather than to
a floor the design's own tone cannot clear.

The selection tint is the one colour on the page that cannot clear the floor it would be given as a
mark, and the check says so rather than pretending. It wears the alpha the client itself builds for
a selection (`translucent(colour, 0.25)`, `web_client/src/bridge/cursors.ts`), which measures 1.67:1
mauve and 1.86:1 teal against the sample's ground and 1.70:1 / 1.90:1 against the window's; the
alpha that would reach the non-text 3.0:1 is about a half, and at that alpha the sample's own text
on it falls below 4.5:1. The two floors cannot both hold for a translucent fill, so the fill is
asserted where it matters — the token it sits under, read out of `components/room-visuals.tsx` so
that moving it over the dimmer comment colour fails the build — and its own pair is a floor of
1.5:1, which only fails a tint nobody can see. The opaque caret bar is what carries a peer at 3.0:1.

What no ratio proves is read against the code by a person on every change:

- **Visible focus.** Every link and button carries a 2 px mauve `:focus-visible` outline at a 2 px
  offset; the `Button` primitive repeats it as a utility, so both spellings agree. Verified in the
  browser: the first three tabs land on the nav's own anchors with that ring.
- **Keyboard.** Every control is a native anchor or button; the page carries no form, no scripted
  widget and no fold. The sticky header slides away on scroll-down but carries
  `focus-within:translate-y-0`, so a tabbed-to link is never focused off-screen. That slide is the
  `SiteHeader` client boundary running, so it is only as true as the page's scripts being permitted.
  [The Content-Security-Policy](content-security-policy.md) records the interval in which they were
  not, and the gate step that now fails if it happens again. No skip link: the page is one route, so
  there is no repeated block to bypass.
- **Reduced motion.** Four things move and all four stand down under `prefers-reduced-motion`: the
  line the hero's window types (under `reduce` it is written whole and never restarts), the caret's
  blink (an `animation: none` in the `reduce` block), the 2 px hover lift on the figure cards, and
  the header's slide (a `motion-reduce:transition-none` utility, so `transition-property` is `none`
  and the bar still hides and returns, without the slide). `scroll-behavior: smooth` goes to `auto`
  in the same block, and the buttons' own lift is a `motion-safe:` utility. Verified in the browser:
  under emulated `reduce` the typed line is 27 characters on the first frame and still 27 a second
  later, the caret's `animation-name` is `none`, the header's `transition-property` is `none`, and
  `scroll-behavior` is `auto`.
- **Touch targets.** Nav links are `text-sm` (20 px line box) with `py-1`, for 28 px of target
  height against the 24 px minimum; buttons are 32–44 px tall. In-prose links are inline and exempt.
- **Decorative only.** The hero figure and the cards' drawings are `aria-hidden`: the window and its
  glow, the guest's tree, one open file, the carets and the invite chip. Their worst-case ratios
  still clear AA (above), and each drawing is followed by the sentence that describes the room
  rather than four lines of code.
- **The figure grid is a list.** Each card's drawing is followed by a bold lead and a sentence, so
  the four claims are readable as a list before they are readable as a picture.
- **Client links.** The routes, the repositories and the specification are links drawn as controls —
  a tab, a card with a border and a fill, a `Source` or `Marketplace` label with an arrow — and the
  stylesheet takes the prose underline off that group (`.repo`, `.demo-link`, `.spec-link`,
  `.source-link`, `.try-link`, `.cta`), because their affordance is the control's own shape. Every link in running
  prose keeps it, so a link there is not told apart by its colour and monospace face alone; the
  focus outline is unchanged.
