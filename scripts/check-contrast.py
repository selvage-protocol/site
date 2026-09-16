#!/usr/bin/env python3
"""Fails the tree when the page's text contrast drops below WCAG AA.

Parses the theme tokens out of `style.css` and asserts the pairs the page
actually renders: body and muted prose, links (visited included), the button
label on its mauve fill, code blocks, the tinted badge and secondary button
(computed as alpha composites over the page background, the way the browser
composes them), and the worst case of the translucent glass card over every
stop of the hero gradient. Thresholds are WCAG 2.2 AA: 4.5:1 for normal text,
3.0:1 for the focus outline (non-text UI).

This is a floor, not an audit. It cannot see layout: touch-target sizes,
keyboard reachability, focus visibility and reduced-motion handling are read
against the code by a person (see the README's accessibility notes), because
no ratio proves a link can be tabbed to.

Exit 0 lists every asserted pair with its measured ratio. Exit 1 names the
pairs below threshold. Exit 2 means the check itself cannot run (a token it
needs is missing or unparsable): that is a failure, not a pass.

`STYLE_CSS` overrides the stylesheet under test, so a probe can run the check
against a deliberately broken copy: a gate that only ever sees passing tokens
proves nothing.
"""

from __future__ import annotations

import os
import re
import sys

TEXT_MIN = 4.5
NON_TEXT_MIN = 3.0
# The glass card's fill over the hero gradient (see style.css `.hero-glass`).
GLASS_ALPHA = 0.82


def lum(hexcode: str) -> float:
    rgb = [int(hexcode[i : i + 2], 16) / 255 for i in (1, 3, 5)]

    def channel(c: float) -> float:
        return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4

    return 0.2126 * channel(rgb[0]) + 0.7152 * channel(rgb[1]) + 0.0722 * channel(rgb[2])


def ratio(a: str, b: str) -> float:
    hi, lo = sorted((lum(a), lum(b)), reverse=True)
    return (hi + 0.05) / (lo + 0.05)


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


def hero_stops(css: str) -> list[str]:
    block = re.search(r"\.hero-visual\s*\{(.*?)\}", css, re.DOTALL)
    if block is None:
        return []
    return [h.lower() for h in re.findall(r"#[0-9a-fA-F]{6}", block.group(1))]


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
    need = ["bg", "fg", "muted", "link", "link-visited", "code-bg", "mantle"]
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
    link, visited, code_bg, mantle = (
        tok["link"],
        tok["link-visited"],
        tok["code-bg"],
        tok["mantle"],
    )
    checks: list[tuple[str, str, str, float]] = [
        ("body text", fg, bg, TEXT_MIN),
        ("muted prose", muted, bg, TEXT_MIN),
        ("link", link, bg, TEXT_MIN),
        ("visited link", visited, bg, TEXT_MIN),
        ("button label on mauve fill", bg, link, TEXT_MIN),
        ("code text", fg, code_bg, TEXT_MIN),
        ("muted text on code background", muted, code_bg, TEXT_MIN),
        ("badge text on badge fill", link, composite(link, bg, 0.10), TEXT_MIN),
        (
            "secondary button text on its fill",
            link,
            composite(link, bg, 0.15),
            TEXT_MIN,
        ),
        ("focus outline against the page", link, bg, NON_TEXT_MIN),
    ]
    stops = hero_stops(css)
    if not stops:
        print(
            "check-contrast: no gradient stops found under .hero-visual; "
            "the glass-card worst case cannot be computed",
            file=sys.stderr,
        )
        return 2
    for stop in stops:
        surface = composite(mantle, stop, GLASS_ALPHA)
        checks.append((f"glass card text over {stop}", fg, surface, TEXT_MIN))
        checks.append((f"glass card muted text over {stop}", muted, surface, TEXT_MIN))

    failures = 0
    for name, a, b, minimum in checks:
        measured = ratio(a, b)
        mark = "ok" if measured >= minimum else "FAIL"
        print(f"check-contrast: [{mark}] {name}: {a} on {b} = {measured:.2f}:1 (needs {minimum:.1f}:1)")
        if measured < minimum:
            failures += 1
    if failures:
        print(f"check-contrast: {failures} pair(s) below WCAG AA")
        return 1
    print(f"check-contrast: {len(checks)} pairs at or above WCAG AA")
    return 0


if __name__ == "__main__":
    sys.exit(main())
