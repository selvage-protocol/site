#!/usr/bin/env python3
"""Derives `public/mark-header.png` from the owner's master, `public/mark-transparent.png`.

The nav bar paints the monogram at 32 CSS px, so the page fetches a 128×128 derivative of
the 800×800 master instead of the master itself (`scripts/check-weight.py` holds that). Until
now nothing in the tree made that derivative: it was built once by hand with
`magick -resize -gamma`, which left it impossible for anyone to reproduce, retune or verify.
This is the producer, and `--check` is the pin: the gate re-derives the file and fails when the
committed bytes are not what the master and the curve below produce.

The arithmetic, in the order the file is built in:

1. **Area-average the master down to `SIZE`, premultiplied by alpha.** Each destination pixel is
   the exact area-weighted mean of the source rectangle it covers (800 / 128 = 6.25 source pixels
   per side, so the boxes are fractional). Colour is accumulated premultiplied — `channel × alpha`
   — and divided by the accumulated alpha at the end. That is the only way an alpha image
   resamples correctly: the master's transparent field is white with alpha 0, so averaging the
   bare bytes drags that white into the glyph edges and the mark comes out haloed.
2. **Apply `MARK_GAMMA` to the colour channels**, through a 256-entry table built once. The
   result is a function of the byte rather than of a floating-point path, so the same input bytes
   give the same output bytes on any machine. Alpha is untouched: this levels the tones, it does
   not change the shapes.

Nothing is cropped, redrawn or re-framed: the derivative is the master's own pixels on a lighter
tone curve, at the size one surface paints.

    scripts/make-mark.py            # rewrite public/mark-header.png
    scripts/make-mark.py --check    # derive in memory; fail when the committed file differs
"""

from __future__ import annotations

import importlib.util
import math
import os
import struct
import sys
import zlib

# The derivative's side in pixels. The one surface paints it at 32 CSS px (`h-8` in
# `components/site-header.tsx`), so this covers a device pixel ratio to 4 without any surface
# upscaling it, and `scripts/check-weight.py` asserts the `<img>` declares the file's own size.
SIZE = 128

# The tone curve: `out = round(255 × (in/255)^(1/MARK_GAMMA))`, the same shape as ImageMagick's
# `-gamma`, applied to the colour channels after the resize. The master is a shaded wordmark whose
# dark stroke is invisible on the bar, so it has to be lifted before it can be read at all, and
# the lift goes no further than the non-text floor needs. Unlevelled (1.0) the derivative's median
# ink pixel measures 1.72:1 on `#1e1e2e`, below the 3.0:1 floor `scripts/check-contrast.py`
# asserts; at 2.4 — the curve the hand-built derivative carried — it measures 4.70:1, which spends
# 1.7:1 of headroom lifting the owner's own tones towards pale. 1.7 measures 3.25:1: clear of the
# floor with room for a later tweak, and the artwork's own colours kept as far as that floor
# allows. Re-derive with this script after changing the number; check-contrast will say where the
# new curve landed.
MARK_GAMMA = 1.7

HERE = os.path.dirname(os.path.abspath(__file__))
MASTER = os.path.join(HERE, "..", "public", "mark-transparent.png")
DERIVATIVE = os.path.join(HERE, "..", "public", "mark-header.png")

# The colour declaration the file this replaces carried, and the one it keeps: ImageMagick's
# sRGB `gAMA` (1/2.2) and `cHRM`. Writing them again is what makes the new file a drop-in for the
# old one rather than a file whose pixels a colour-managed browser may interpret differently.
PNG_GAMMA = 45455
PNG_CHRM = (31270, 32900, 64000, 33000, 30000, 60000, 15000, 6000)


def decode(path: str):
    """`check-contrast.png_pixels`, imported rather than copied.

    The tree already carries one standard-library PNG decoder, in `scripts/check-contrast.py`,
    where it reads this same mark's pixels to measure them. A producer with a second decoder
    would be a second opinion about what the master contains, and the two would drift.
    """
    checker = os.path.join(HERE, "check-contrast.py")
    spec = importlib.util.spec_from_file_location("check_contrast", checker)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {checker}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.png_pixels(path)


def area_average(raster: bytes, width: int, height: int, size: int) -> bytearray:
    """The master as an RGBA `size`×`size` raster, each pixel the mean of the box it covers.

    Premultiplied by alpha, so a partly transparent destination pixel is the colour of the ink
    that covers it and not a blend of that ink with the transparent field's white.
    """
    out = bytearray(size * size * 4)
    for dy in range(size):
        top = dy * height / size
        bottom = (dy + 1) * height / size
        for dx in range(size):
            left = dx * width / size
            right = (dx + 1) * width / size
            sums = [0.0, 0.0, 0.0, 0.0]
            area = 0.0
            for sy in range(int(top), min(math.ceil(bottom), height)):
                cover_y = min(sy + 1, bottom) - max(sy, top)
                if cover_y <= 0:
                    continue
                for sx in range(int(left), min(math.ceil(right), width)):
                    cover_x = min(sx + 1, right) - max(sx, left)
                    if cover_x <= 0:
                        continue
                    cover = cover_x * cover_y
                    at = (sy * width + sx) * 4
                    alpha = raster[at + 3]
                    for channel in range(3):
                        sums[channel] += raster[at + channel] * alpha / 255 * cover
                    sums[3] += alpha * cover
                    area += cover
            mean_alpha = sums[3] / area
            pixel = [0, 0, 0]
            if mean_alpha > 0:
                for channel in range(3):
                    value = sums[channel] / area * 255 / mean_alpha
                    pixel[channel] = max(0, min(255, round(value)))
            at = (dy * size + dx) * 4
            out[at : at + 3] = bytes(pixel)
            out[at + 3] = max(0, min(255, round(mean_alpha)))
    return out


def gamma_table(gamma: float) -> bytes:
    """`out = round(255 × (in/255)^(1/gamma))`, one entry per byte a PNG channel can hold.

    A table rather than the expression applied per pixel: the curve is then a function of the
    byte, the same byte gives the same byte everywhere, and the number above is the one thing
    to change.
    """
    return bytes(
        max(0, min(255, round(255 * (value / 255) ** (1.0 / gamma)))) for value in range(256)
    )


def derive(raster: bytes, width: int, height: int) -> bytes:
    """The derivative's RGBA raster: the master area-averaged to `SIZE`, then levelled."""
    levelled = area_average(raster, width, height, SIZE)
    table = gamma_table(MARK_GAMMA)
    for at in range(0, len(levelled), 4):
        for channel in range(3):
            levelled[at + channel] = table[levelled[at + channel]]
    return bytes(levelled)


def filter_row(kind: int, line: bytes, above: bytes, bpp: int) -> bytes:
    """One PNG scan line under filter `kind` (0 none, 1 sub, 2 up, 3 average, 4 paeth)."""
    out = bytearray(len(line))
    for i, value in enumerate(line):
        left = line[i - bpp] if i >= bpp else 0
        up = above[i]
        corner = above[i - bpp] if i >= bpp else 0
        if kind == 0:
            predictor = 0
        elif kind == 1:
            predictor = left
        elif kind == 2:
            predictor = up
        elif kind == 3:
            predictor = (left + up) >> 1
        else:
            estimate = left + up - corner
            to_left, to_up, to_corner = (
                abs(estimate - left),
                abs(estimate - up),
                abs(estimate - corner),
            )
            predictor = left if to_left <= to_up and to_left <= to_corner else (
                up if to_up <= to_corner else corner
            )
        out[i] = (value - predictor) & 0xFF
    return bytes(out)


def chunk(kind: bytes, body: bytes) -> bytes:
    return (
        struct.pack(">I", len(body))
        + kind
        + body
        + struct.pack(">I", zlib.crc32(kind + body) & 0xFFFFFFFF)
    )


def encode_png(size: int, raster: bytes) -> bytes:
    """An 8-bit RGBA PNG of `raster`, standard library only.

    The row filter is chosen per line by the sum of the filtered bytes read as signed — the
    heuristic the format's own documentation suggests — so the mostly transparent field
    compresses without a compressor that would have to be installed beside this script.
    """
    header = struct.pack(">IIBBBBB", size, size, 8, 6, 0, 0, 0)
    raw = bytearray()
    stride = size * 4
    above = bytes(stride)
    for y in range(size):
        line = raster[y * stride : (y + 1) * stride]
        best = None
        for kind in (0, 1, 2, 3, 4):
            filtered = filter_row(kind, line, above, 4)
            score = sum(min(value, 256 - value) for value in filtered)
            if best is None or score < best[0]:
                best = (score, kind, filtered)
        raw.append(best[1])
        raw += best[2]
        above = line
    return (
        b"\x89PNG\r\n\x1a\n"
        + chunk(b"IHDR", header)
        + chunk(b"gAMA", struct.pack(">I", PNG_GAMMA))
        + chunk(b"cHRM", struct.pack(">8I", *PNG_CHRM))
        + chunk(b"IDAT", zlib.compress(bytes(raw), 9))
        + chunk(b"IEND", b"")
    )


def compare(derived: bytes, path: str) -> int:
    """Fail when the committed derivative is not `derived`; a raster that cannot be read is 2."""
    try:
        size, height, channels, committed = decode(path)
    except Exception as exc:  # PngError, and anything the import itself raises
        print(
            f"make-mark: cannot read {path}: {exc}; a derivative that cannot be read is a "
            "failure, not a pass",
            file=sys.stderr,
        )
        return 2
    if (size, height, channels) != (SIZE, SIZE, 4):
        print(
            f"make-mark: {path} is {size}×{height} with {channels} channel(s), not "
            f"{SIZE}×{SIZE} RGBA",
            file=sys.stderr,
        )
        return 1
    differing = [i for i in range(len(derived)) if derived[i] != committed[i]]
    if differing:
        worst = max(differing, key=lambda i: abs(derived[i] - committed[i]))
        print(
            f"make-mark: {path} is not the derivation of {os.path.relpath(MASTER, HERE)} at "
            f"gamma {MARK_GAMMA}: {len(differing)} of {len(derived)} channels differ",
            file=sys.stderr,
        )
        print(
            f"make-mark: worst at pixel {worst // 4 % SIZE},{worst // 4 // SIZE} channel "
            f"{worst % 4}: committed {committed[worst]}, derived {derived[worst]}",
            file=sys.stderr,
        )
        print(
            f"make-mark: run {os.path.relpath(os.path.abspath(__file__))} to rebuild it",
            file=sys.stderr,
        )
        return 1
    print(
        f"make-mark: {os.path.relpath(path)} is the master area-averaged to {SIZE}×{SIZE} and "
        f"levelled at gamma {MARK_GAMMA}: {len(derived)} channels match, "
        f"{os.path.getsize(path)} bytes"
    )
    return 0


def main(argv: list[str]) -> int:
    unknown = [one for one in argv if one != "--check"]
    if unknown:
        print(f"usage: {os.path.basename(__file__)} [--check]", file=sys.stderr)
        return 2
    try:
        width, height, channels, raster = decode(MASTER)
    except Exception as exc:
        print(f"make-mark: cannot read {MASTER}: {exc}", file=sys.stderr)
        return 2
    if channels != 4:
        print(
            f"make-mark: {MASTER} has {channels} channels; the premultiplied average needs "
            "an alpha channel",
            file=sys.stderr,
        )
        return 2
    derived = derive(raster, width, height)
    if "--check" in argv:
        return compare(derived, DERIVATIVE)
    with open(DERIVATIVE, "wb") as handle:
        handle.write(encode_png(SIZE, derived))
    print(
        f"make-mark: wrote {os.path.relpath(DERIVATIVE)} from the {width}×{height} master: "
        f"{SIZE}×{SIZE}, gamma {MARK_GAMMA}, {os.path.getsize(DERIVATIVE)} bytes"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
