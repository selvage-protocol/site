#!/usr/bin/env python3
"""Fails the tree when the page's text contrast drops below WCAG AA.

Parses the theme tokens out of `style.css` and asserts the pairs the page
actually renders: body and muted prose, links, the button
label on its mauve fill, code blocks, the sample's own token colours, the
tinted badge and secondary button (computed as alpha composites over the page
background, the way the browser composes them), and the worst case of the
translucent glass card over every stop of the hero figure's own ground. The text
that is not a theme token — the window's line numbers, the card the page offers
but cannot sell yet, the repository descriptions — is read out of the rule that
paints it, so a pair cannot go on measuring a token the page stopped using there
(which is what the line-number pair did). The secondary
button's boundary is parsed out of `components/ui/button.tsx` (`border-mauve/*`)
and asserted at the non-text 3.0:1 floor too, so weakening the class fails the
build, and the ground a code sample is drawn on is parsed the same way: the
figure's own fill over the card's, rather than a constant that would measure a
surface nobody renders. Thresholds are WCAG 2.2 AA: 4.5:1 for normal text,
3.0:1 for non-text UI.

Each peer is three colours on the page and each is measured where it lands: the 2 px
caret bar and the badge fill are the peer's own colour over the surface they are
drawn on (non-text), the badge's label is a dark text on that fill (text), and
the selection is the peer's colour at the client's quarter alpha *behind* the
sample's text, so the pair that matters is the token the fill sits under — read
out of `components/room-visuals.tsx`, so moving the fill over a dimmer token
fails the build. A quarter-alpha tint cannot also clear the non-text floor (see
`TINT_MIN`), and the pair below says so rather than pretending otherwise.

The figures' one mark that is not a peer is the dot on the open file, in the text colour
its own rule declares; it is floored where it is drawn, on the figure's ground, so a
restyle that dims it below the non-text floor fails here rather than in a reader's eyes.

This is a floor, not an audit. It cannot see layout: touch-target sizes,
keyboard reachability, focus visibility and reduced-motion handling are read
against the code by a person (see the README's accessibility notes), because
no ratio proves a link can be tabbed to.

The one pair the floor cannot hold on this palette is the link against the body text
beside it, and that is asserted the other way round rather than dropped. WCAG 1.4.1
(Use of Color) asks for 3.0:1 between a link and its neighbours when colour is the only
thing distinguishing it, and WCAG 1.4.3 asks for 4.5:1 between the link text and its
background. Both cannot hold here: `--fg` is 11.34:1 on `--bg`, so a colour that just
clears 4.5:1 on the background is 11.34 / 4.5 = 2.52:1 from the prose, and any colour
3.0:1 from the prose is at most 11.34 / 3.0 = 3.78:1 on the background, below the text
floor. So the page carries 1.4.1's other allowed affordance — every prose link is
underlined — and this check reads the underline out of the stylesheet and asserts the
3.0:1 pair whenever it is missing. A link distinguished by colour alone therefore still
has to clear the floor, and a link that is underlined does not have to pretend it could.

Exit 0 lists every asserted pair with its measured ratio. Exit 1 names the
pairs below threshold. Exit 2 means the check itself cannot run (a token it
needs is missing or unparsable): that is a failure, not a pass.

The nav mark is the one mark on the page that is not a token: it is the owner's artwork, served
as pixels. It is a logotype, and WCAG 1.4.11 exempts logotypes from its 3.0:1 non-text
requirement, so the check does not hold it there: that floor is what had the derivative levelled
away from the owner's colours, and a mark the standard exempts should not have to change to clear
it. What the check does hold is the property the exemption leaves — the mark is ink, so its
typical pixel must be no darker than the ground the bar shows it on (`MARK_MIN`, the floor below
which no reader can see it). It reads `public/mark-header.png` itself, composites its own pixels
over that ground, and prints the measured ratio: 1.72:1 for the owner's own tones. A derivative
recoloured darker until it is a smudge on the bar fails here.

`STYLE_CSS` overrides the stylesheet under test, `BUTTON_TSX` the button
component, `ROOM_TSX` the figure component and `MARK_PNG` the nav mark, so a probe
can run the check against deliberately broken copies: a gate that only ever sees
passing tokens proves nothing.
"""

from __future__ import annotations

import os
import re
import struct
import sys
import zlib

TEXT_MIN = 4.5
NON_TEXT_MIN = 3.0

# A fifth of full coverage: a pixel less opaque than this is the antialiased fringe of a glyph
# rather than ink a reader reads as the mark. It is the threshold the nav mark's rule below uses
# to decide which pixels are the mark at all.
MARK_INK_ALPHA = 50

# A PNG the check cannot read is exit 2 rather than a skipped pair, the same way an unparsable
# token is: a mark nobody measured is not a mark that passed.
PNG_MAGIC = b"\x89PNG\r\n\x1a\n"
# Channel count by PNG colour type, for the two an 8-bit opaque or alpha image may use.
PNG_CHANNELS = {2: 3, 6: 4}

# A peer's selection is a background and not a mark, and it wears the alpha the client
# itself builds for one (`translucent(colour, 0.25)`, web_client/src/bridge/cursors.ts).
# That tint cannot reach the non-text floor: over the page's code ground a mauve fill
# measures 1.70:1 and a teal one 1.90:1, and the alpha that would reach 3.0:1 — about a
# half — drags the sample's own text below 4.5:1 on it. The two floors cannot both hold
# for a translucent fill, so the text one is asserted (it is the one a reader reads) and
# this one only fails a tint nobody can see at all. The mark that carries a peer at the
# non-text floor is their caret bar, opaque, asserted at 3.0:1 below.
TINT_MIN = 1.5

# The nav mark is a logotype, and WCAG 1.4.11 (Non-text Contrast) exempts logotypes from its
# 3.0:1 requirement for graphical objects, so this check does not hold the owner's monogram to
# `NON_TEXT_MIN`. It holds it to the floor a reader can still see it at — the same one the
# selection tint gets, and not a WCAG threshold — because the mark is ink drawn on a dark bar,
# and a mark darkened into that bar is the defect worth failing. The owner's own tones measure
# 1.72:1 there.
MARK_MIN = 1.5


def lum(hexcode: str) -> float:
    rgb = [int(hexcode[i : i + 2], 16) / 255 for i in (1, 3, 5)]

    def channel(c: float) -> float:
        return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4

    return 0.2126 * channel(rgb[0]) + 0.7152 * channel(rgb[1]) + 0.0722 * channel(rgb[2])


def ratio(a: str, b: str) -> float:
    hi, lo = sorted((lum(a), lum(b)), reverse=True)
    return (hi + 0.05) / (lo + 0.05)


class PngError(ValueError):
    """A PNG this check cannot read (not a PNG, interlaced, or another bit depth)."""


def png_pixels(path: str) -> tuple[int, int, int, bytes]:
    """An 8-bit RGB or RGBA PNG as (width, height, channels, raster), unfiltered.

    The page carries the mark as pixels, so the only way to measure the tone it paints is to
    read them; the standard library has no decoder, and reaching for ImageMagick would put a
    second toolchain in the gate for one file. The two shapes ImageMagick writes for this asset
    are the ones accepted, and anything else (16-bit, a palette, Adam7, an RGB image whose
    transparency is a `tRNS` chunk rather than a per-pixel alpha) is `PngError` rather than a
    guess.
    """
    try:
        with open(path, "rb") as handle:
            data = handle.read()
    except OSError as exc:
        raise PngError(str(exc)) from exc
    if not data.startswith(PNG_MAGIC):
        raise PngError("not a PNG")
    header = None
    compressed = bytearray()
    at = len(PNG_MAGIC)
    while at + 12 <= len(data):
        length = int.from_bytes(data[at : at + 4], "big")
        kind = data[at + 4 : at + 8]
        body = data[at + 8 : at + 8 + length]
        if kind == b"IHDR":
            header = body
        elif kind == b"IDAT":
            compressed += body
        elif kind == b"tRNS":
            # An RGB image can carry one transparent colour in a `tRNS` chunk, and this decoder
            # treats colour type 2 as opaque. Reading it as opaque would measure pixels the page
            # never paints, so the image is refused instead of guessed at: a mark this check
            # cannot decode is exit 2 rather than a pair it made up. (Colour type 6 carries its
            # alpha per pixel and has no `tRNS`.)
            raise PngError("it carries a tRNS chunk, which this decoder does not apply")
        elif kind == b"IEND":
            break
        at += 12 + length
    if header is None or len(header) < 13:
        raise PngError("no IHDR")
    width, height, depth, colour, _, _, interlace = struct.unpack(">IIBBBBB", header[:13])
    if depth != 8:
        raise PngError(f"bit depth {depth}, not 8")
    if colour not in PNG_CHANNELS:
        raise PngError(f"colour type {colour}, not RGB or RGBA")
    if interlace != 0:
        raise PngError("interlaced")
    channels = PNG_CHANNELS[colour]
    stride = width * channels
    try:
        raw = zlib.decompress(bytes(compressed))
    except zlib.error as exc:
        raise PngError(f"its IDAT does not decompress: {exc}") from exc
    if len(raw) != height * (stride + 1):
        raise PngError("the raster is not the size its header declares")
    raster = bytearray(height * stride)
    previous = bytearray(stride)
    at = 0
    for row in range(height):
        kind = raw[at]
        at += 1
        line = bytearray(raw[at : at + stride])
        at += stride
        if kind == 1:
            for i in range(channels, stride):
                line[i] = (line[i] + line[i - channels]) & 0xFF
        elif kind == 2:
            for i in range(stride):
                line[i] = (line[i] + previous[i]) & 0xFF
        elif kind == 3:
            for i in range(stride):
                left = line[i - channels] if i >= channels else 0
                line[i] = (line[i] + ((left + previous[i]) >> 1)) & 0xFF
        elif kind == 4:
            for i in range(stride):
                left = line[i - channels] if i >= channels else 0
                up = previous[i]
                corner = previous[i - channels] if i >= channels else 0
                estimate = left + up - corner
                to_left, to_up, to_corner = (
                    abs(estimate - left),
                    abs(estimate - up),
                    abs(estimate - corner),
                )
                if to_left <= to_up and to_left <= to_corner:
                    predictor = left
                elif to_up <= to_corner:
                    predictor = up
                else:
                    predictor = corner
                line[i] = (line[i] + predictor) & 0xFF
        elif kind != 0:
            raise PngError(f"filter {kind} on row {row}")
        raster[row * stride : (row + 1) * stride] = line
        previous = line
    return width, height, channels, bytes(raster)


def mark_ink(path: str, ground: str) -> tuple[str, int, int]:
    """The mark's ink as the page paints it, over `ground`: (colour, ink pixels, alpha floor).

    The colour is the composited pixel of median luminance among the mark's own pixels, which
    is what "the mark" looks like to a reader rather than the file's average over its empty
    field: the artwork is a shaded wordmark, its dark stroke is invisible on a dark bar, and
    the mean of every pixel counts that stroke and the transparent field beside it. A mark
    whose typical pixel is dark is the defect this measures.
    """
    width, height, channels, raster = png_pixels(path)
    base = [int(ground[i : i + 2], 16) for i in (1, 3, 5)]
    ink: list[tuple[float, str]] = []
    for at in range(0, len(raster), channels):
        alpha = raster[at + 3] if channels == 4 else 255
        if alpha <= MARK_INK_ALPHA:
            continue
        pixel = [
            round(raster[at + i] * alpha / 255 + base[i] * (1 - alpha / 255)) for i in range(3)
        ]
        ink.append((lum("#%02x%02x%02x" % tuple(pixel)), "#%02x%02x%02x" % tuple(pixel)))
    if not ink:
        raise PngError(f"{width}×{height} with no pixel above alpha {MARK_INK_ALPHA}")
    ink.sort()
    return ink[len(ink) // 2][1], len(ink), MARK_INK_ALPHA


def composite(fg: str, bg: str, alpha: float) -> str:
    f = [int(fg[i : i + 2], 16) for i in (1, 3, 5)]
    b = [int(bg[i : i + 2], 16) for i in (1, 3, 5)]
    mixed = [round(f[i] * alpha + b[i] * (1 - alpha)) for i in range(3)]
    return "#%02x%02x%02x" % tuple(mixed)


def tokens(css: str) -> dict[str, str]:
    found = dict(re.findall(r"--([\w-]+)\s*:\s*(#[0-9a-fA-F]{6})", css))
    out: dict[str, str] = {}
    for key, value in found.items():
        # `@theme` pins `--color-mantle` where `:root` says `--code-bg`: strip the
        # prefix so both spellings resolve to the same token.
        out.setdefault(key.removeprefix("color-"), value.lower())
    return out


def rgba_fill(css: str, selector: str) -> tuple[str, float] | None:
    """The fill of the rule whose selector list contains `selector`, as (hex, alpha).

    A surface is the value the browser composites, so the check reads it instead of
    trusting a constant: a restyle that changes the alpha without touching the code
    would otherwise measure a surface nobody renders. Only an `rgba()` background
    counts — anything else (a hex, a gradient, a missing rule) is exit 2, not a pass.
    """
    rule = re.search(
        r"([^{}]*" + selector + r"[^{}]*)\{([^{}]*)\}",
        css,
        re.DOTALL,
    )
    if rule is None:
        return None
    fill = re.search(
        r"background\s*:\s*rgba\(\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)\s*,\s*([0-9.]+)\s*\)",
        rule.group(2),
    )
    if fill is None:
        return None
    red, green, blue = (int(fill.group(i)) for i in (1, 2, 3))
    try:
        alpha = float(fill.group(4))
    except ValueError:
        return None
    if not all(0 <= c <= 255 for c in (red, green, blue)):
        return None
    if not 0 < alpha <= 1:
        return None
    return "#%02x%02x%02x" % (red, green, blue), alpha


def declared_colour(css: str, selector: str, names: tuple[str, ...]) -> str | None:
    """A solid hex or palette variable one rule declares for `selector`, or None.

    The colour is read from the rule a browser reads, so a pair on text that is not a
    theme token — a line number, a card's number, a description drawn dimmer than the
    prose beside it — measures what is painted in that place rather than a token assumed
    to be in force there. A `var()` is resolved against the file's own palette, and
    anything this cannot read (a gradient, a `color-mix()`, a rule that is gone) is None:
    exit 2, not a pass.
    """
    css = re.sub(r"/\*.*?\*/", "", css, flags=re.DOTALL)
    value = None
    for rule in re.finditer(r"([^{}]+)\{([^{}]*)\}", css):
        if selector not in [s.strip() for s in rule.group(1).split(",")]:
            continue
        for declaration in rule.group(2).split(";"):
            name, separator, fill = declaration.partition(":")
            if separator and name.strip() in names:
                value = fill.strip()
    if value is None:
        return None
    variable = re.fullmatch(r"var\(\s*--([\w-]+)\s*\)", value)
    if variable:
        palette = dict(re.findall(r"--([\w-]+)\s*:\s*([^;{}]+)", css))
        value = palette.get(variable.group(1), "").strip()
    if not re.fullmatch(r"#[0-9a-fA-F]{6}", value):
        return None
    return value.lower()


def solid_fill(css: str, selector: str) -> str | None:
    """Read a solid hex background or palette variable; unsupported fills fail closed."""
    return declared_colour(css, selector, ("background", "background-color"))


def text_colour(css: str, selector: str) -> str | None:
    """The colour one rule paints its text in; unsupported values fail closed."""
    return declared_colour(css, selector, ("color",))


def glass_fill(css: str) -> tuple[str, float] | None:
    """The `.hero-glass` fill as (hex, alpha), or None when unusable."""
    return rgba_fill(css, r"\.hero-glass")


def selection_fill(css: str, tone: str) -> tuple[str, float] | None:
    """The `.selected-<tone>` fill a peer's selection is drawn in, as (hex, alpha)."""
    return rgba_fill(css, rf"\.selected-{tone}")


def hero_stops(css: str) -> list[str]:
    block = re.search(r"\.hero-visual\s*\{(.*?)\}", css, re.DOTALL)
    if block is None:
        return []
    return [h.lower() for h in re.findall(r"#[0-9a-fA-F]{6}", block.group(1))]


class FillError(ValueError):
    """A `bg-mauve` fill the check cannot measure."""


def variant_classes(tsx: str, name: str) -> str:
    """The class string of one cva variant, or raise `FillError`."""
    match = re.search(rf"{name}:\s*\"([^\"]*)\"", tsx)
    if match is None:
        raise FillError(f"no {name} variant")
    return match.group(1)


def fill_alphas(tsx: str) -> list[int]:
    """Every `bg-mauve` fill alpha in the button component, as percentages.

    On this dark-only page a stronger fill sits closer to the mauve label, so
    the worst state is the maximum: any darkened or lightened fill that drops
    the pair fails the build. A bare `bg-mauve` is opaque (100). Anything the
    check cannot measure raises `FillError` — an omitted state must fail the
    build rather than pass it quietly.
    """
    alphas: list[int] = []
    for match in re.finditer(r"bg-mauve(?:/([^\s\"']*))?(?![\w-])", tsx):
        modifier = match.group(1)
        if modifier is None:
            alphas.append(100)
        elif re.fullmatch(r"\d{1,3}", modifier) and 0 <= int(modifier) <= 100:
            alphas.append(int(modifier))
        else:
            raise FillError(f"unsupported bg-mauve modifier {modifier!r}")
    return alphas


def boundary_alphas(tsx: str) -> list[int]:
    """Every `border-mauve/*` alpha in the button component, as percentages.

    The weakest boundary is the one that has to clear the non-text floor, so
    the check asserts the minimum: any weakened `border-mauve` class anywhere
    in the component fails the build.
    """
    return [int(a) for a in re.findall(r"border-mauve/(\d+)", tsx)]


def selected_kinds(tsx: str) -> list[str]:
    """Every token class the sample draws inside a `<Selected>` span, `body` for the text
    that carries no token of its own.

    The fill is a background, so the pair that matters is the text it sits under, and the
    component is where that is written down: a check that guessed a token would measure a
    surface nobody renders, and one that measured all five would fail a page that is
    right. Reading the spans keeps the pair on what is drawn — moving the fill over the
    comment colour, which clears neither floor, fails the build.
    """
    spans = re.findall(r"<Selected\b[^>]*>(.*?)</Selected>", tsx, re.DOTALL)
    if not spans:
        raise FillError("no <Selected> span in the component")
    kinds: list[str] = []
    for body in spans:
        found = re.findall(r'kind="(\w+)"', body)
        kinds.extend(found if found else ["body"])
    return kinds


def underlines(css: str, selector: str) -> bool:
    """Whether the rule for `selector` puts an underline on a link.

    This is the affordance WCAG 1.4.1 allows instead of a 3.0:1 colour difference, and it
    is a declaration the stylesheet has to make: Tailwind's preflight sets
    `a { text-decoration: inherit }`, so a rule naming only the thickness and the offset
    draws nothing. Both spellings count, the shorthand and `text-decoration-line`; a rule
    that is missing, or that sets `none`, is read as no affordance.
    """
    css = re.sub(r"/\*.*?\*/", "", css, flags=re.DOTALL)
    found = False
    for rule in re.finditer(r"([^{}]+)\{([^{}]*)\}", css):
        if selector not in [s.strip() for s in rule.group(1).split(",")]:
            continue
        for declaration in rule.group(2).split(";"):
            name, separator, value = declaration.partition(":")
            if separator and name.strip() in ("text-decoration", "text-decoration-line"):
                found = "underline" in value
    return found


def main() -> int:
    here = os.path.dirname(os.path.abspath(__file__))
    path = os.environ.get("STYLE_CSS", os.path.join(here, "..", "style.css"))
    try:
        with open(path, encoding="utf-8") as handle:
            css = handle.read()
    except OSError as exc:
        print(f"check-contrast: cannot read {path}: {exc}", file=sys.stderr)
        return 2
    tok = tokens(css)
    need = [
        "bg",
        "fg",
        "muted",
        "link",
        "code-bg",
        "mantle",
        # A peer's own colour: the caret bar, the badge fill, and the ground the badge's
        # label sits on. Two peers hold a selection and the third does not, which is why the
        # selection pairs below name their tones rather than walking this list.
        "teal",
        "peach",
        # The sample's token colours: each one is a pair below, and a missing token would
        # leave the code in one colour without failing anything.
        "code-comment",
        "code-keyword",
        "code-fn",
        "code-string",
        "code-number",
        "code-type",
    ]
    missing = [n for n in need if n not in tok]
    if missing:
        print(
            f"check-contrast: style.css has no --{', --'.join(missing)}; "
            "a contrast check that cannot find its tokens passes everything",
            file=sys.stderr,
        )
        return 2
    bg, fg, muted = tok["bg"], tok["fg"], tok["muted"]
    # The Tailwind classes and the plain CSS must agree on the palette: the check
    # asserts pairs from `:root`, but `text-subtext` renders from `@theme`.
    for theme_key, var_key in (
        ("base", "bg"),
        ("mantle", "code-bg"),
        ("text", "fg"),
        ("subtext", "muted"),
        ("mauve", "link"),
    ):
        if tok.get(theme_key) != tok.get(var_key):
            print(
                f"check-contrast: --color-{theme_key} ({tok.get(theme_key)}) disagrees "
                f"with --{var_key} ({tok.get(var_key)}); the asserted pairs do not "
                "describe what the classes render",
                file=sys.stderr,
            )
            return 2
    link, code_bg, mantle = (
        tok["link"],
        tok["code-bg"],
        tok["mantle"],
    )
    # The peer badges' label is read off the rule that paints it rather than taken to be the
    # page's own pair: the badge wore the page's background once and wears the palette's crust
    # now, and a pair that assumed either would go on measuring the colour it replaced.
    peer_label = text_colour(css, ".peer-badge")
    if peer_label is None:
        print(
            "check-contrast: no usable colour on .peer-badge; the peer badges' label cannot "
            "be measured",
            file=sys.stderr,
        )
        return 2
    checks: list[tuple[str, str, str, float]] = [
        ("body text", fg, bg, TEXT_MIN),
        ("muted prose", muted, bg, TEXT_MIN),
        ("link", link, bg, TEXT_MIN),
        ("button label on mauve fill", bg, link, TEXT_MIN),
        ("code text", fg, code_bg, TEXT_MIN),
        ("muted text on code background", muted, code_bg, TEXT_MIN),
        # The badge primitive's own chip: the mauve label over its own 10% wash. The page's
        # badges are the pills its cards colour row by row, so this pair is kept for the
        # primitive the way the ghost button's is, and the pills are measured by hand in the
        # accessibility notes rather than parsed here.
        ("badge text on badge fill", link, composite(link, bg, 0.10), TEXT_MIN),
        # A peer's name wears the glyph-margin badge's pair, in all three tones: the label's
        # own colour on the peer's own colour, the same pair the default button's label is
        # measured on.
        ("peer badge label on mauve fill", peer_label, link, TEXT_MIN),
        ("peer badge label on teal fill", peer_label, tok["teal"], TEXT_MIN),
        ("peer badge label on peach fill", peer_label, tok["peach"], TEXT_MIN),
        ("focus outline against the page", link, bg, NON_TEXT_MIN),
    ]
    tsx_path = os.environ.get(
        "BUTTON_TSX", os.path.join(here, "..", "components", "ui", "button.tsx")
    )
    try:
        with open(tsx_path, encoding="utf-8") as handle:
            tsx = handle.read()
    except OSError as exc:
        print(f"check-contrast: cannot read {tsx_path}: {exc}", file=sys.stderr)
        return 2
    alphas = boundary_alphas(tsx)
    if not alphas:
        print(
            f"check-contrast: no border-mauve/* class in {tsx_path}; "
            "a boundary check that cannot find its boundary passes everything",
            file=sys.stderr,
        )
        return 2
    weakest = min(alphas)
    checks.append(
        (
            f"secondary button boundary (border-mauve/{weakest})",
            composite(link, bg, weakest / 100),
            bg,
            NON_TEXT_MIN,
        )
    )
    fills: list[int] = []
    try:
        # Only the secondary variant pairs a mauve label with a mauve fill;
        # the default variant's bare `bg-mauve` carries a dark label and is
        # covered by the token pair, so including it here would fail a
        # passing page.
        fills = fill_alphas(variant_classes(tsx, "secondary"))
    except FillError as exc:
        print(f"check-contrast: {exc}; a fill the check cannot measure is a failure, not a pass", file=sys.stderr)
        return 2
    if not fills:
        print(
            f"check-contrast: no bg-mauve/* class in {tsx_path}; "
            "a fill check that cannot find its fill passes everything",
            file=sys.stderr,
        )
        return 2
    strongest = max(fills)
    checks.append(
        (
            f"secondary button text on its fill (bg-mauve/{strongest})",
            link,
            composite(link, bg, strongest / 100),
            TEXT_MIN,
        )
    )
    # The ghost variant's hover state is the one pair on the page the two checks above do not
    # reach: a `text-text` label over a `bg-surface0` wash. Its resting label is
    # `text-subtext`, which is the muted-prose pair already. The page carries no ghost button
    # at present, and the variant's own pairs are measured from the component anyway, so a
    # `ghost` button that comes back on the page is one whose worst state is already checked.
    # Both halves are read out of the component rather than named here, and anything this
    # cannot read is exit 2, as everywhere else in this file.
    try:
        ghost = variant_classes(tsx, "ghost")
    except FillError as exc:
        print(
            f"check-contrast: {exc}; a hover state the check cannot measure is a failure, "
            "not a pass",
            file=sys.stderr,
        )
        return 2
    hover_fill = re.search(r"hover:bg-([\w-]+)/(\d+)", ghost)
    hover_label = re.search(r"hover:text-([\w-]+)", ghost)
    if hover_fill is None or hover_label is None:
        print(
            "check-contrast: the ghost variant carries no `hover:bg-<token>/<n>` and "
            "`hover:text-<token>` pair, so the state the ghost variant is drawn in has "
            "nothing to measure it from",
            file=sys.stderr,
        )
        return 2
    hover_token, hover_strength = hover_fill.group(1), int(hover_fill.group(2))
    hover_fill_hex, hover_label_hex = tok.get(hover_token), tok.get(hover_label.group(1))
    if hover_fill_hex is None or hover_label_hex is None or not 1 <= hover_strength <= 100:
        print(
            f"check-contrast: the ghost variant's hover state names "
            f"{hover_token!r} at {hover_strength} and {hover_label.group(1)!r}, and the "
            "palette does not carry both as tokens in that range",
            file=sys.stderr,
        )
        return 2
    checks.append(
        (
            f"ghost button label on its hover fill (bg-{hover_token}/{hover_strength})",
            hover_label_hex,
            composite(hover_fill_hex, bg, hover_strength / 100),
            TEXT_MIN,
        )
    )
    stops = hero_stops(css)
    if not stops:
        print(
            "check-contrast: no gradient stops found under .hero-visual; "
            "the glass-card worst case cannot be computed",
            file=sys.stderr,
        )
        return 2
    fill = glass_fill(css)
    if fill is None:
        print(
            "check-contrast: no usable rgba() background on .hero-glass; "
            "the glass-card worst case cannot be computed",
            file=sys.stderr,
        )
        return 2
    glass_rgb, glass_alpha = fill
    # The samples sit on two grounds, and both are read out of the stylesheet rather than
    # restated: the glass card over the panel's gradient, and the code figure inside a card
    # of the prose column, which is the figure's own fill over the card's over the page.
    # A light colour is at its worst on the lightest surface it can sit on, so the sample's
    # own colours are asserted there rather than on every stop.
    figure = rgba_fill(css, r"\.prose-body pre\.fig-code")
    card = rgba_fill(css, r"\.prose-body ul\.cards > li")
    if figure is None or card is None:
        print(
            "check-contrast: no usable rgba() background on the code figure or on the card "
            "it sits in; the ground the sample's own colours are measured against cannot "
            "be computed",
            file=sys.stderr,
        )
        return 2
    figure_ground = composite(figure[0], composite(card[0], bg, card[1]), figure[1])
    worst_glass = max((composite(glass_rgb, stop, glass_alpha) for stop in stops), key=lum)
    for token, colour in (
        ("comment", tok["code-comment"]),
        ("keyword", tok["code-keyword"]),
        ("function", tok["code-fn"]),
        ("string", tok["code-string"]),
        ("number", tok["code-number"]),
        ("type", tok["code-type"]),
    ):
        checks.append((f"code {token} on the code figure", colour, figure_ground, TEXT_MIN))
        checks.append((f"code {token} on the glass card", colour, worst_glass, TEXT_MIN))
    # The page's line numbers are the ones in the room window, and its own rule paints them
    # in a colour of their own: reading `muted` here measured a token the window does not use
    # for them, which is the way this pair goes blind to a dimmed number. The ground is the
    # window's, the glass over the figure's fill.
    room_num = text_colour(css, ".room-num")
    if room_num is None:
        print(
            "check-contrast: no usable colour on .room-num; the room window's line "
            "numbers cannot be measured",
            file=sys.stderr,
        )
        return 2
    checks.append(("room window line numbers", room_num, worst_glass, TEXT_MIN))
    # The card the page offers but cannot sell yet is drawn on the band rather than on a card
    # of its own, so its number and its planned row are floored on the band's own fill.
    band = solid_fill(css, ".band")
    if band is None:
        print(
            "check-contrast: no usable solid background on .band; the ground the "
            "not-yet-available card is drawn on cannot be computed",
            file=sys.stderr,
        )
        return 2
    for label, selector in (
        ("not-yet-available card number", ".try-card-planned .try-num"),
        ("not-yet-available card row", ".planned-row"),
    ):
        colour = text_colour(css, selector)
        if colour is None:
            print(
                f"check-contrast: no usable colour on {selector}; the text the "
                "not-yet-available card draws cannot be measured",
                file=sys.stderr,
            )
            return 2
        checks.append((f"{label} on the band", colour, band, TEXT_MIN))
    # A peer's caret bar and the fill of their badge are one colour, opaque, drawn on both
    # grounds: a mark nobody can see is not a caret, so every tone is floored as non-text UI
    # on both grounds.
    for tone, colour in (("mauve", link), ("teal", tok["teal"]), ("peach", tok["peach"])):
        checks.append(
            (f"{tone} caret bar and badge fill on the code figure", colour, figure_ground, NON_TEXT_MIN)
        )
        checks.append(
            (f"{tone} caret bar and badge fill on the glass card", colour, worst_glass, NON_TEXT_MIN)
        )
    room_tsx_path = os.environ.get(
        "ROOM_TSX", os.path.join(here, "..", "components", "room-visuals.tsx")
    )
    try:
        with open(room_tsx_path, encoding="utf-8") as handle:
            room_tsx = handle.read()
    except OSError as exc:
        print(f"check-contrast: cannot read {room_tsx_path}: {exc}", file=sys.stderr)
        return 2
    try:
        kinds = selected_kinds(room_tsx)
    except FillError as exc:
        print(
            f"check-contrast: {exc} in {room_tsx_path}; the ground a peer's selection puts "
            "its text on cannot be computed",
            file=sys.stderr,
        )
        return 2
    token_colours = {
        "comment": tok["code-comment"],
        "keyword": tok["code-keyword"],
        "string": tok["code-string"],
        "number": tok["code-number"],
        "type": tok["code-type"],
        "body": fg,
    }
    # The peers who hold a selection: the third peer is drawn with a caret and a badge and no
    # fill of their own, so this is the pair list the stylesheet has the rules for.
    for tone, colour in (("mauve", link), ("teal", tok["teal"])):
        spec = selection_fill(css, tone)
        if spec is None:
            print(
                f"check-contrast: no usable rgba() background on .selected-{tone}; "
                "a peer's selection fill cannot be measured",
                file=sys.stderr,
            )
            return 2
        peer_rgb, peer_alpha = spec
        if peer_rgb != colour:
            print(
                f"check-contrast: .selected-{tone} is {peer_rgb} where that peer's own colour "
                f"is {colour}; the fill is not the colour the caret wears",
                file=sys.stderr,
            )
            return 2
        for ground_name, ground in (("code figure", figure_ground), ("glass card", worst_glass)):
            filled = composite(peer_rgb, ground, peer_alpha)
            checks.append(
                (f"{tone} selection tint over the {ground_name}", filled, ground, TINT_MIN)
            )
            for kind in kinds:
                checks.append(
                    (
                        f"{tone} selection fill under the code {kind} on the {ground_name}",
                        token_colours[kind],
                        filled,
                        TEXT_MIN,
                    )
                )
    # The nav mark is the one surface that paints the owner's artwork as pixels rather than as a
    # token, so it is measured from the file the page fetches. It is a logotype, which WCAG 1.4.11
    # exempts, so it is held to `MARK_MIN` (a reader can see it at all) and not to the non-text
    # floor every token-drawn mark gets; the measured ratio is printed with the pair. Two things
    # make this pair the bar's own: the bar is `bg-base/85` over a page whose ground is the same
    # `bg-base`, so a translucent bar over it composites to that colour exactly; and the mark in
    # the HTML is `h-8 w-auto`, 32 CSS px of a 128 px file, which resampling does not change the
    # tone of. The median is the typical ink pixel rather than the brightest one, so a mark that
    # is dark except for a highlight does not pass.
    mark_path = os.environ.get(
        "MARK_PNG", os.path.join(here, "..", "public", "mark-header.png")
    )
    try:
        mark_ink_colour, mark_pixels, ink_alpha = mark_ink(mark_path, bg)
    except PngError as exc:
        print(
            f"check-contrast: cannot read the nav mark {mark_path}: {exc}; "
            "a mark that cannot be read is a failure, not a pass",
            file=sys.stderr,
        )
        return 2
    checks.append(
        (
            f"nav header mark (a logotype, exempt from the non-text floor), the median of "
            f"{mark_pixels} ink pixels above alpha {ink_alpha}",
            mark_ink_colour,
            bg,
            MARK_MIN,
        )
    )
    dot_fill = solid_fill(css, ".open-dot")
    if dot_fill is None:
        print(
            "check-contrast: no usable solid background on .open-dot; "
            "the open-file mark cannot be measured",
            file=sys.stderr,
        )
        return 2
    for stop in stops:
        surface = composite(glass_rgb, stop, glass_alpha)
        checks.append((f"glass card text over {stop}", fg, surface, TEXT_MIN))
        checks.append((f"glass card muted text over {stop}", muted, surface, TEXT_MIN))
        # The glass is composited over the figure's own fill, and that fill is a ground the
        # page paints text on too, so it carries the pair as well as the surface above it.
        checks.append((f"hero figure text over {stop}", fg, stop, TEXT_MIN))
        checks.append((f"hero figure muted text over {stop}", muted, stop, TEXT_MIN))
    # The open file's dot is drawn in the card's own figure band, not on the hero figure, so
    # it is floored on the ground it is painted on. Its fill is read rather than assumed, so a
    # stylesheet change cannot silently bypass the non-text floor.
    checks.append(("open-file dot on the code figure", dot_fill, figure_ground, NON_TEXT_MIN))
    # The repository descriptions are the page's other small text on a surface of its own. The
    # card's hover state lightens that surface to the page's own colour, which is the worst of
    # the two, and the planned card carries one on the page itself.
    repo_desc = text_colour(css, ".repo-desc")
    repo_fill = solid_fill(css, ".prose-body .repo")
    repo_hover = solid_fill(css, ".prose-body .repo:hover")
    if repo_desc is None or repo_fill is None or repo_hover is None:
        print(
            "check-contrast: no usable colour on .repo-desc or on the repository card it "
            "sits in; the description cannot be measured",
            file=sys.stderr,
        )
        return 2
    checks.append(("repository description on the repository card", repo_desc, repo_fill, TEXT_MIN))
    checks.append(
        ("repository description on the hovered card", repo_desc, repo_hover, TEXT_MIN)
    )
    checks.append(("planned card description on the page", repo_desc, bg, TEXT_MIN))

    # WCAG 1.4.1, and the pair this check went blind to: a link judged against the page's
    # background and never against the prose beside it. The two floors cannot both hold on
    # this palette (see the module docstring), so the pair is asserted where colour is the
    # lone affordance, read out of the stylesheet rather than assumed.
    notes: list[str] = []
    if underlines(css, ".prose-body a"):
        notes.append(
            f"prose links are underlined, the non-colour affordance WCAG 1.4.1 allows "
            f"instead of 3.0:1 against the text beside them ({link} on {fg} would be "
            f"{ratio(link, fg):.2f}:1)"
        )
    else:
        checks.append(("link vs body text, colour alone", link, fg, NON_TEXT_MIN))

    failures = 0
    for name, a, b, minimum in checks:
        measured = ratio(a, b)
        mark = "ok" if measured >= minimum else "FAIL"
        print(f"check-contrast: [{mark}] {name}: {a} on {b} = {measured:.2f}:1 (needs {minimum:.1f}:1)")
        if measured < minimum:
            failures += 1
    for note in notes:
        print(f"check-contrast: [ok] {note}")
    if failures:
        print(
            f"check-contrast: {failures} pair(s) below their floor; the lines above name each "
            f"pair's own floor — WCAG AA, or the logotype nav mark's visibility floor"
        )
        return 1
    print(
        f"check-contrast: {len(checks)} pairs at or above their floors — WCAG AA for the "
        f"{len(checks) - 1} pairs drawn from the palette and the rules that paint it, a "
        f"visibility floor for the logotype nav mark "
        f"(glass {glass_rgb} at alpha {glass_alpha} parsed from .hero-glass, "
        f"sample ground {figure_ground} parsed from the code figure)"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
