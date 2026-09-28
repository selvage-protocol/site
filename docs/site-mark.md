# The site mark

The page serves the owner's raster mark at every size from the owner's own pixels: `public/` carries
the transparent 800×800 PNG export byte-identical (its checksum matches the owner's file) and never
hotlinked, and every surface that paints the mark is a derivative of it or of its opaque twin. The
one surface that carries the page-body mark is dark, and the opaque export's baked `#1e1e2e` base
would draw a visible chip inside it, so the transparent glyphs are the ones that sit on the surface:

| Surface | File | Why |
|---|---|---|
| Nav header on dark Mocha | `public/mark-header.png` | the bar is translucent Mocha over the page; the opaque export's baked `#1e1e2e` base would draw a visible box against it, while the transparent glyphs sit straight on the bar. The bar paints it at 30 CSS px, which is what the file is sized for (see below). The export's glyphs are dark — a shaded wordmark whose dark stroke is faint on a dark ground — and the mark is a decorative logotype — 1.4.11 measures graphical objects *required to understand the content*, which a mark with `alt=""` beside the link's own `Selvage` label is not, and the standard's logotype clause is SC 1.4.3's rather than 1.4.11's — so this derivative carries the owner's own tones unchanged; `scripts/check-contrast.py` reads the file's pixels and holds its median to a visibility floor instead |
| Favicon and social card | `app/icon1.png` / `app/icon.png` / `app/icon2.png` / `app/apple-icon.png` / `app/opengraph-image.png` | tab bars and link unfurls crop unpredictably, so these stay opaque: the four favicon sizes are the opaque export resized, the social card the full-size opaque export |

The hero panel used to be the second surface. It is now a figure of the product itself (see [the
product figures](product-figures.md)) and carries no mark: a watermark on a drawing of an editor
window is one more thing between the reader and the thing the drawing shows.

There is no vector favicon. `app/icon.svg` was one: the owner's Comfortaa Bold `svp` monogram
(Catppuccin mauve/teal/red on a Mocha base) with the live `<text>` converted to paths and Inkscape's
filter and clip markup kept. It was the first icon the page declared. Its `<clipPath>` contains a
`<use>` that points at a `<g>`, which contributes no shape to the clip, so both Chromium and librsvg
clip the glyph group away and the only thing an SVG-aware browser can draw from the file is the
baked `#1e1e2e` rect: a blank dark square at 16, 32 and 48 px, verified by rasterising the file in
both. (Which candidate a browser really paints in a tab is its own scoring of an SVG that declares
no `sizes`; the point is that one of the two icons was undrawable rather than merely small.) The
paths themselves were faithful to the owner's framing (at 2% fuzz their glyph box is the owner's
opaque export's own rectangle, 516×229+137+280 of 800), but the file still fell short of the
artwork: rasterised with Inkscape's shadow filter left in, the letters come out glowing (RMSE 8%
from the export at 800 px), and with the filter dropped they come out flat (11%), because the
export's dark stroke and soft shadow are baked into its pixels and not into the paths. A redraw is a
second copy of the artwork that nothing keeps in step with the first, and the owner's pixels are the
source of truth: it was removed rather than repaired.

The favicon set is the owner's own pixels at each size a browser asks for: `app/icon1.png` (16),
`app/icon.png` (32), `app/icon2.png` (48) and `app/apple-icon.png` (180) are the opaque 800×800
export resized with ImageMagick (`magick app/opengraph-image.png -resize <N>x<N>`), each verified
pixel-identical to a fresh resize (RMSE 0 at all four sizes) and rendered 1:1 by the browser, so no
surface is an upscale of another. The mark sits where the owner put it: its box is centred to within
1.5 px at every size, spanning 62–67% of the width and 25–29% of the height, because the export is a
wide wordmark on a square field. At 16 px that leaves the monogram 10×4 px, the smallest this
artwork gets and the reason the 180 px and the social card carry it best. Giving the tab more of the
mark would mean cropping the export's field, a re-framing of the owner's composition, so it is not
done here.

The header mark is sized the same way the favicons are, and it is the one surface that carries the
owner's own tones with nothing applied to them. The nav bar paints it at 30 CSS px, so
`public/mark-header.png` is the 128×128 derivative `scripts/make-mark.py` builds: the master cropped
to the square holding its ink, area-averaged down to 128, premultiplied by alpha so the transparent
field's white cannot bleed into the glyph edges, and no colour change after that. The crop is what
the mark needed. The export is a wide wordmark on a field far larger than its glyphs — its ink is
36,531 of 640,000 pixels — and averaging the whole canvas spent the derivative's own pixels on the
field: at 30 CSS px the glyph drew **20×9 px** inside the 30 px box, the same size the master draws
resampled directly, which is what the derivative was. Cropped, the glyph spans the frame's width,
the ink covers **20%** of the box rather than 10%, and the same 30 CSS px draw it at **30×14 px**.
The crop is squared around the ink rather than stretched to a square, because a square average of
the ink's own rectangle would draw the letters 2.26 times as tall as they are: the frame's
proportions are the master's, and the width is what a wordmark fills. The favicons keep the export's
field, where it is what centres the mark in a square; the header is the surface that paints the mark
in a box of its own, so the field there is only empty pixels and a smaller glyph. It is derived from
the master's own alpha on every run rather than written down, so `--check` re-derives it with
everything else. 128 covers a device pixel ratio to 4. The master is 60,595 bytes; served there it
was 26% of everything the page transferred, and a browser resampled it silently. The export is a
shaded wordmark whose glyph tones sit between `#2d111e` and `#7cc9c0`, so on `#1e1e2e` the
derivative's median ink pixel measures **1.88:1**: the wordmark's dark stroke is faint on a dark
bar. Nothing is done about that here. WCAG 1.4.11's 3.0:1 non-text floor is asserted on every mark
this page draws from a token, and it does not reach the nav mark: it measures graphical objects
*required to understand the content*, and this one is `alt=""` beside the link's own `Selvage`
label. The standard's logotype clause — text that is part of a logo or brand name has no contrast
requirement — is SC 1.4.3's, not 1.4.11's, and it is where a wordmark's own tones are excused, so
lifting the derivative to clear a floor that does not apply to it would be recolouring the owner's
own work to pass a rule that is not the one in question. A lighter plate behind the mark is the
change that would keep both the artwork's colours and a 3.0:1 mark. The file is 7,948 bytes. `scripts/check-contrast.py`
composites its own pixels over `--bg` and holds the median to a visibility floor of **1.5:1** — the
floor below which a reader cannot see it, and not a WCAG threshold — printing the measured 1.88:1,
so a derivative recoloured darker until it is a smudge on the bar fails the gate.

The derivative had no producer until now: it was built once by hand with ImageMagick, so nothing in
the tree could reproduce or verify it. [`scripts/make-mark.py`](../scripts/make-mark.py) is the
producer, and [`scripts/ci-local.sh mark`](../scripts/ci-local.sh) re-derives the file from the
master inside the gate and fails when the committed pixels are not what the master produces. The pin
compares pixels rather than bytes: a zlib release may compress the same raster differently, and the
raster is the claim. With no curve between them the two resamples still agree to within a level or
three: at 30 px, resampling the derivative and resampling the square of the master it was made from
differ on 188 of 900 pixels, 170 of them by one level in a channel and none by more than three, a
mean of 0.1 levels over the clip, which is the rounding of a second averaging step and nothing else.

What the producer does not reproduce is ImageMagick's resample. `-resize` defaults to a Mitchell
window, which reaches past the box each destination pixel covers and rings a little; the producer
averages exactly that box, which is the one definition of a downscale that needs no knobs of its
own. A derivative built with the window instead of the box would differ from this one on its edge
tones, not in the artwork's colours.

The alternative the review offered — dropping the mark and keeping the wordmark alone — was not
taken because the mark is the page's only image-body surface and `scripts/check-weight.py` is
written around it: a page that fetches no image at all is an exit 2 there rather than a pass, so
removing the mark would have retired a check about image weight instead of answering a question
about tone.

`public/mark-transparent.png` stays in the tree at full size: another repository pins its bytes, so
it is the source of truth rather than a fetched asset. Only the surfaces that paint the mark are
listed above, and `scripts/check-weight.py` holds every image the page body fetches to a budget so a
master cannot come back to one of them by accident.
