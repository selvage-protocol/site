#!/usr/bin/env python3
"""Fails the tree when the page serves an image heavier or larger than the surface it paints.

The defect this exists for: the body mark is painted at 32 CSS px in the nav header, and it was
served as the owner's 800×800 master — 60,595 bytes, a quarter of everything the page transfers,
for a 20×9 px monogram. A browser resamples it silently, so nothing said so.

Two rules, both decided from the served HTML and the bytes on disk, so both hold without a
layout engine:

- **Weight.** Every image the page fetches out of `public/` is at most `BUDGET_BYTES`. The
  budget is a ceiling on what a surface this page actually paints may cost, not a total for the
  page: a check on the total would redden the gate for a framework upgrade that changes nothing
  a reader sees, which is the coupling the other checks refuse.
- **Declared size.** Where an `<img>` carries `width`/`height`, they are the file's own pixel
  size. Those attributes are the aspect ratio a browser reserves before the bytes arrive, so a
  swap that leaves them behind distorts the mark or shifts the layout, and neither shows up as a
  failed request.

The favicons are out of scope on purpose: they are Next file conventions, served out of
`.next/static/media` under a hashed name this check would have to read the build manifest to
resolve, and the build writes their `sizes` from the files. What is in scope is every image the
page body names, and the check fails when it reaches none of them rather than reporting a page
that carries no image.

Exit 0 prints what the page fetches and what it costs. Exit 1 names the file that broke a rule.
Exit 2 means the check itself cannot run — no served page, no image in it, a file it cannot read
— which is a failure, not a pass.

    scripts/check-weight.py [rendered.html]     # defaults to .tmp/rendered.html
"""

from __future__ import annotations

import os
import struct
import sys
from dataclasses import dataclass
from html.parser import HTMLParser

# A surface this page paints at 32 CSS px, so the largest reasonable derivative is a few
# hundred bytes of pixels per side. 16 KiB is roughly 2.5× the 128 px derivative and a quarter
# of the master it replaced: it fails on the master and leaves room for a denser mark.
BUDGET_BYTES = 16 * 1024

PNG_MAGIC = b"\x89PNG\r\n\x1a\n"
IMAGE_RELS = {"icon", "shortcut", "apple-touch-icon", "mask-icon"}


@dataclass(frozen=True)
class Fetched:
    """One image the served HTML makes the browser request."""

    element: str
    url: str
    declared: tuple[int, int] | None


class PageParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.images: list[Fetched] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        self._element(tag, {k.lower(): (v or "") for k, v in attrs})

    handle_startendtag = handle_starttag

    def _element(self, tag: str, attrs: dict[str, str]) -> None:
        if tag == "img":
            url = attrs.get("src", "")
            if url:
                declared = None
                if attrs.get("width", "").isdigit() and attrs.get("height", "").isdigit():
                    declared = (int(attrs["width"]), int(attrs["height"]))
                self.images.append(Fetched("<img>", url, declared))
            for candidate in (attrs.get("srcset") or "").split(","):
                candidate = candidate.strip().split(" ")[0]
                if candidate:
                    self.images.append(Fetched("<img srcset>", candidate, None))
            return
        if tag == "link" and (attrs.get("rel") or "").lower() in IMAGE_RELS:
            url = attrs.get("href", "")
            if url:
                self.images.append(Fetched(f'<link rel="{attrs.get("rel")}">', url, None))
            return
        if tag == "link" and (attrs.get("rel") or "").lower() == "preload":
            if (attrs.get("as") or "").lower() == "image" and attrs.get("href"):
                self.images.append(Fetched('<link rel="preload" as="image">', attrs["href"], None))


def images_of(html: str) -> list[Fetched]:
    parser = PageParser()
    parser.feed(html)
    parser.close()
    return parser.images


def png_size(path: str) -> tuple[int, int] | None:
    """The pixel size out of a PNG's IHDR, or None when the file is not one."""
    with open(path, "rb") as handle:
        header = handle.read(24)
    if len(header) < 24 or not header.startswith(PNG_MAGIC) or header[12:16] != b"IHDR":
        return None
    width, height = struct.unpack(">II", header[16:24])
    return width, height


def local_file(root: str, url: str) -> str | None:
    """The file under `public/` this URL names, or None when it is not one of the page's own."""
    path = url.split("#", 1)[0].split("?", 1)[0]
    if not path.startswith("/") or ".." in path:
        return None
    candidate = os.path.join(root, "public", path.lstrip("/"))
    return candidate if os.path.isfile(candidate) else None


def self_test() -> str | None:
    """The rules, on fixtures that have to reach them.

    A check whose parser stopped recognising an `<img>` reports a page that carries none: the
    fixture below is what keeps that from being a pass, and the budget is exercised on a file
    that is over it rather than on one that happens to be small.
    """
    html = (
        '<img src="/a.png" width="32" height="32">'
        '<img srcset="/b.png 1x, /c.png 2x">'
        '<link rel="preload" as="image" href="/a.png">'
        '<link rel="icon" href="/icon.png">'
        '<link rel="preload" as="script" href="/x.js">'
    )
    found = images_of(html)
    urls = sorted(f.url for f in found)
    if urls != ["/a.png", "/a.png", "/b.png", "/c.png", "/icon.png"]:
        return f"the parser read {urls} out of its own fixture"
    if found[0].declared != (32, 32):
        return f"the declared size of its own fixture read {found[0].declared}"
    if found[1].declared is not None:
        return "an <img> with no width/height was given a declared size"
    if images_of("<p>prose</p>"):
        return "a document with no image element produced one"
    for name, size, budget, expected in (
        ("under the budget", BUDGET_BYTES - 1, BUDGET_BYTES, False),
        ("at the budget", BUDGET_BYTES, BUDGET_BYTES, False),
        ("over the budget", BUDGET_BYTES + 1, BUDGET_BYTES, True),
    ):
        if over_budget(size, budget) != expected:
            return f"the budget rule answered the wrong way for a file {name}"
    for name, declared, pixels, expected in (
        ("a matching size", (32, 32), (32, 32), False),
        ("a mismatched size", (800, 800), (128, 128), True),
        ("no declared size", None, (128, 128), False),
    ):
        if size_mismatch(declared, pixels) != expected:
            return f"the declared-size rule answered the wrong way for {name}"
    return None


def over_budget(size: int, budget: int) -> bool:
    return size > budget


def size_mismatch(declared: tuple[int, int] | None, pixels: tuple[int, int]) -> bool:
    return declared is not None and declared != pixels


def main(argv: list[str]) -> int:
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    dead = self_test()
    if dead is not None:
        print(f"check-weight: {dead}; a check that cannot decide passes everything", file=sys.stderr)
        return 2

    page = argv[1] if len(argv) > 1 else os.path.join(root, ".tmp", "rendered.html")
    try:
        with open(page, encoding="utf-8") as handle:
            html = handle.read()
    except OSError as exc:
        print(
            f"check-weight: cannot read {page}: {exc}. A check that reaches no page reports a "
            "page that weighs nothing, so build and serve it first (scripts/ci-local.sh weight)",
            file=sys.stderr,
        )
        return 2

    failures: list[str] = []
    measured: dict[str, tuple[int, tuple[int, int]]] = {}
    seen: set[str] = set()
    for image in images_of(html):
        path = local_file(root, image.url)
        if path is None:
            continue
        if path not in measured:
            try:
                pixels = png_size(path)
                if pixels is None:
                    print(f"check-weight: {path} is not a PNG this check can read", file=sys.stderr)
                    return 2
                measured[path] = (os.path.getsize(path), pixels)
            except OSError as exc:
                print(f"check-weight: cannot read {path}: {exc}", file=sys.stderr)
                return 2
        size, pixels = measured[path]
        where = os.path.relpath(path, root)
        if path not in seen:
            seen.add(path)
            print(
                f"check-weight: {where}: {size} bytes, {pixels[0]}×{pixels[1]} px, serves "
                f"{image.element} — budget {BUDGET_BYTES}"
            )
            if over_budget(size, BUDGET_BYTES):
                failures.append(
                    f"{where} is {size} bytes and is served to the page body; the budget for an "
                    f"image this page paints is {BUDGET_BYTES}. Resize the derivative for the "
                    "surface it lands on rather than serving the master"
                )
        if size_mismatch(image.declared, pixels):
            failures.append(
                f"{where} is {pixels[0]}×{pixels[1]} px and {image.element} declares "
                f"{image.declared[0]}×{image.declared[1]}, which is the aspect ratio a browser "
                "reserves before the bytes arrive"
            )
    if not seen:
        print(
            f"check-weight: {os.path.relpath(page, root)} names no image under public/, so this "
            "check decided nothing; a page whose images moved is not a page this passes",
            file=sys.stderr,
        )
        return 2
    if failures:
        for line in failures:
            print(f"check-weight: {line}")
        return 1
    print(
        f"check-weight: {len(seen)} image(s) the page body fetches from public/, "
        f"{sum(size for size, _ in measured.values())} bytes total, each at most "
        f"{BUDGET_BYTES} bytes and declaring its own pixel size. The "
        "favicons are file conventions and are not in scope"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
