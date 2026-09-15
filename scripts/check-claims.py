#!/usr/bin/env python3
"""Fails the shipped page on a phrase the project cannot back today.

Each entry below pairs a phrase the page must not carry with the reason it must not, and with
a sample that has to match it. The reasons are not this script's opinion: every one of them is
a claim the research record already checked and found false or unbacked, and the sample is what
keeps a pattern from quietly matching nothing — a check whose patterns are dead and a check
that scans no file both report a clean page, which is the failure this file exists to catch.

Run from anywhere; the repository root is resolved from this file's location. Arguments are
paths (files or directories) to scan instead of the whole checkout.

    scripts/check-claims.py            # every *.html in the checkout
    scripts/check-claims.py .tmp/empty   # reaches no file: that is a failure, not a pass

Exit 0 when the page is clean, 1 when it carries a forbidden phrase, 2 when the check itself
cannot run (a dead pattern, or nothing to scan).
"""

from __future__ import annotations

import os
import re
import sys
from dataclasses import dataclass

# Directories that never hold the shipped page.
SKIP_DIRS = {".git", ".tmp", "node_modules"}


@dataclass(frozen=True)
class Phrase:
    pattern: str
    sample: str
    reason: str


FORBIDDEN: list[Phrase] = [
    Phrase(
        r"open[- ]sourc\w*",
        "the server is open source",
        "the server binary `selvaged` is FSL-1.1-MIT: source-available, not OSI-approved. Name "
        "the licences instead; 'open source' is false of the server and of the project as a whole",
    ),
    Phrase(
        r"\bSSP\b",
        "the SSP wire",
        "the abbreviation is taken, by stack-smashing protection and by supply-side platforms; "
        "the protocol is the Selvage Session Protocol, written out at least once per paragraph",
    ),
    Phrase(
        r"salvage/1",
        "the wire version is salvage/1",
        "the wire version is `selvage/1`; 'salvage' is the near-homophone the full protocol "
        "title exists to defend against",
    ),
    Phrase(
        r"end[- ]to[- ]end|\be2ee\b",
        "end-to-end encrypted",
        "there is no encryption layer in version 1: the reference server routes document "
        "payloads as bytes and holds them in memory for the life of the room",
    ),
    Phrase(
        r"\bbrowser\b",
        "it runs in the browser",
        "there is no client that runs in a web page. Both clients are editor plugins, and the "
        "one in-page route ever tried needed the arm64 `vsda` module moved aside by hand",
    ),
    Phrase(
        r"\b(?:create|rename|delete)\w*\s+(?:files?|folders?|directories|paths)",
        "delete files in the host's folder",
        "the room carries no file mutations: nothing adds, renames or removes a path in the "
        "host's folder, and nothing writes to the host's working copy",
    ),
    Phrase(
        r"file (?:creat|renam|delet)\w*",
        "file creation",
        "the room carries no file mutations: nothing adds, renames or removes a path in the "
        "host's folder, and nothing writes to the host's working copy",
    ),
    Phrase(
        r"\bdocker\b|compose file|one[- ]command",
        "docker compose up",
        "no Dockerfile, compose file or service unit exists in any repository; the documented "
        "way to run the server is `cargo run -p selvaged -- --listen ...`",
    ),
    Phrase(
        r"\bv?1\.0\b|production[- ]ready|production[- ]grade|battle[- ]tested|stable release",
        "the stable release, version 1.0",
        "the wire version is `selvage/1` while the design is at 0.x: same major and, at 0.x, "
        "same minor. Nothing has been released and nothing here promises a fixed shape",
    ),
    Phrase(
        r"second implementation|interoperab\w*",
        "a second implementation exists",
        "there is no second implementation: the Neovim client drives a byte-identical copy of "
        "the same engine, so nothing yet shows a client built from the prose alone agreeing "
        "byte for byte with this one",
    ),
    Phrase(
        r"marketplace|open ?vsx",
        "install it from the marketplace",
        "the extension is unpublished, and publishing it is a non-goal until it works with a "
        "friend; the path in is a checkout and `npm run package`",
    ),
    Phrase(
        r"read[- ]only",
        "guests are read-only",
        "the design inverts this: read-only scopes the host's filesystem, never the shared "
        "buffer, and every holder of the invite edits the session CRDT",
    ),
    Phrase(
        r"never leaves|leaves? your machine|stays? on your machine",
        "your code never leaves your machine",
        "the host's file contents travel through the server to the peers that ask for them and "
        "there is no encryption layer in version 1. What is bounded is the grant: the paths the "
        "host enumerates and the reads it serves from inside the granted root",
    ),
    Phrase(
        r"\btrusted by\b|testimonial|case stud|\bscreenshot|\blogo\b",
        "trusted by teams at",
        "there is no social proof to show and no logo to show it with: no image, no logo, no "
        "screenshot and no user exists anywhere in this project",
    ),
    Phrase(
        r"\d[\d,.]*\s+(?:developers|users|teams|companies|downloads|stars|subscribers)\b",
        "10,000 developers",
        "no user count exists. The only numbers this project can show are the corpus counts its "
        "own validator pins (23 vectors, 806 frame checks, 192 assertions)",
    ),
    Phrase(
        r"(?:try|open|visit|see|browse) the (?:live |public |free )?demo|\blive demo\b",
        "try the live demo",
        "there is no demo instance: the only server that has ever run is a local debug build, "
        "and standing one up means a VPS, an external account and money — an owner decision",
    ),
]


def root_of_this_checkout() -> str:
    here = os.path.dirname(os.path.abspath(__file__))
    return os.path.dirname(here)


def html_files(under: list[str]) -> list[str]:
    found: list[str] = []
    for start in under:
        if os.path.isfile(start):
            if start.endswith(".html"):
                found.append(start)
            continue
        for directory, subdirs, names in os.walk(start):
            subdirs[:] = [d for d in subdirs if d not in SKIP_DIRS and not d.startswith(".")]
            for name in names:
                if name.endswith(".html"):
                    found.append(os.path.join(directory, name))
    return sorted(set(found))


def main() -> int:
    compiled: list[tuple[Phrase, re.Pattern[str]]] = []
    for phrase in FORBIDDEN:
        pattern = re.compile(phrase.pattern, re.IGNORECASE)
        if not pattern.search(phrase.sample):
            print(
                f"check-claims: the pattern {phrase.pattern!r} does not match its own sample "
                f"{phrase.sample!r}; a pattern that matches nothing passes everything",
                file=sys.stderr,
            )
            return 2
        compiled.append((phrase, pattern))

    root = root_of_this_checkout()
    os.chdir(root)
    targets = sys.argv[1:] or ["."]
    paths = html_files(targets)
    if not paths:
        print(
            f"check-claims: reached no .html file under {targets}; a scan that finds nothing "
            "would report a clean page, so this is a failure rather than a pass",
            file=sys.stderr,
        )
        return 2

    hits = 0
    for path in paths:
        with open(path, encoding="utf-8") as handle:
            for number, line in enumerate(handle, 1):
                for phrase, pattern in compiled:
                    for match in pattern.finditer(line):
                        hits += 1
                        print(
                            f"{os.path.relpath(path, root)}:{number}: "
                            f"forbidden phrase {match.group(0)!r}\n"
                            f"    {phrase.reason}"
                        )

    if hits:
        print(f"check-claims: {hits} forbidden phrase(s) in {len(paths)} file(s)")
        return 1

    print(
        f"check-claims: {len(compiled)} phrases alive, {len(paths)} file(s) scanned, "
        "no forbidden phrase found"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
