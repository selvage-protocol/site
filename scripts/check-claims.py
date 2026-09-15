#!/usr/bin/env python3
"""Fails the shipped page on a phrase the project cannot back today.

This is a filter, not a proof. It matches a list of known wordings; a false claim written in
different words, a synonym, a superlative, a wrong number the corpus does not pin, or any
sentence that is merely unbacked all pass it. What it does guarantee is narrower and still
worth having: those known wordings do not appear, even when the page wraps them across lines or
encodes the characters as HTML entities.

Each entry below pairs a phrase the page must not carry with the reason it must not, and with a
sample that has to match it. The reasons are not this script's opinion: every one of them is a
claim the research record already checked and found false or unbacked, and the sample is what
keeps a pattern from quietly matching nothing — a check whose patterns are dead and a check that
scans no file both report a clean page, which is the failure this file exists to catch.

The scan normalises what it reads before it matches: HTML comments and tags are removed, entities
are decoded, unicode dashes become hyphens, and runs of whitespace (including the line breaks the
page wraps at) collapse to a single space. A phrase that only looks absent because it happened to
wrap, or because a hyphen was written as `&#45;`, would otherwise pass.

Run from anywhere; the repository root is resolved from this file's location. Arguments are paths
(files or directories) to scan instead of the whole checkout.

    scripts/check-claims.py              # every *.html in the checkout
    scripts/check-claims.py .tmp/empty   # reaches no file: that is a failure, not a pass

Exit 0 when the page is clean of every known wording, 1 when it carries one, 2 when the check
itself cannot run (a dead pattern, or nothing to scan).
"""

from __future__ import annotations

import html
import os
import re
import sys
from dataclasses import dataclass

# Directories that never hold the shipped page.
SKIP_DIRS = {".git", ".tmp", "node_modules"}

# A claimed corpus number that is not the one `specification/schema/validate.py` pins is a wrong
# number the page would otherwise show without failing anything. The lookahead is what makes the
# pinned value the only one that passes.
VEHICLE = r"\d[\d,]*"

DASHES = re.compile("[\u2010-\u2015\u2212\ufe58\ufe63\uff0d]")


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
        "there is no encryption layer in version 1: frames travel through the server as "
        "unencrypted bytes, and this slice has no transport security either",
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
        "the room carries no file mutations: nothing on the wire adds, renames or removes a "
        "path, and nothing writes to the host's working copy",
    ),
    Phrase(
        r"file (?:creat|renam|delet)\w*",
        "file creation",
        "the room carries no file mutations: nothing on the wire adds, renames or removes a "
        "path, and nothing writes to the host's working copy",
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
        "the wire version is `selvage/1`; nothing has been released and no shape is frozen",
    ),
    Phrase(
        r"second implementation|interoperab\w*",
        "a second implementation exists",
        "there is no second implementation: the Neovim client drives a byte-identical copy of "
        "the same engine, so nothing yet shows a client built from the prose alone agreeing "
        "byte for byte with this one",
    ),
    Phrase(
        r"marketplace|open ?vsx|\bgallery\b",
        "install it from the extension gallery",
        "the extension is unpublished, and publishing it is a non-goal until it works with a "
        "friend; the path in is a checkout and `npm run package`",
    ),
    Phrase(
        r"read[- ]only|view[- ]only",
        "guests have view-only access",
        "the design inverts this: read-only scopes the host's filesystem, never the shared "
        "buffer, and every holder of the invite edits the session CRDT",
    ),
    Phrase(
        r"never leaves|never reaches|leaves? your machine|stays? on your machine"
        r"|only the people in the room",
        "your code never leaves your machine",
        "the host's file contents travel through the server to the peers that ask for them and "
        "there is no encryption layer in version 1; the relay is payload-opaque but plaintext, "
        "so its operator can read a frame as it passes",
    ),
    Phrase(
        r"server (?:cannot|can't|can not) (?:read|see)",
        "the server cannot read what a room is editing",
        "the relay is payload-opaque, not confidential: it holds no document text, but it can "
        "read a frame as it routes it and there is no transport security in this slice",
    ),
    Phrase(
        r"\btrusted by\b|testimonial|case stud|\bscreenshot|\blogo\b",
        "trusted by teams at",
        "there is no social proof to show and no logo to show it with: no image, no logo, no "
        "screenshot and no user exists anywhere in this project",
    ),
    Phrase(
        r"\bin production\b|used in production"
        r"|\d[\d,.]*(?:\s+\w+){0,3}\s+(?:developers|users|teams|companies|downloads|stars"
        r"|subscribers)\b",
        "used in production by 40 engineering teams",
        "no user count exists. The only numbers this project can show are the corpus counts its "
        "own validator pins (23 vectors, 806 frame checks, 192 assertions)",
    ),
    Phrase(
        r"\bfirst\b",
        "the first protocol to specify the session layer",
        "a claim of priority no source supports: the design record surveys prior art (Eclipse "
        "Open Collaboration Tools et al.), and the project's own claim is that the session layer "
        "is unspecified, not that this is first",
    ),
    Phrase(
        r"(?:try|open|visit|see|browse) the (?:live |public |free )?demo|\blive demo\b",
        "try the live demo",
        "there is no demo instance: the only server that has ever run is a local debug build, "
        "and standing one up means a VPS, an external account and money — an owner decision",
    ),
    Phrase(
        r"design[^.]{0,20}0\.x",
        "the design is at 0.x",
        "`PROTOCOL.md` §10 states the rule in force for `selvage/1`: same major alone. No corpus "
        "line puts the design at 0.x; the compatibility clause names 0.x only for a future major "
        "0, which is not this one",
    ),
    Phrase(
        rf"\b(?!806\b){VEHICLE}\s+frame[- ]checks?\b",
        "804 frame checks",
        "the pinned number is 806 frame checks (`specification/schema/validate.py`); a different "
        "number is a claim the corpus disproves",
    ),
    Phrase(
        rf"\b(?!23\b){VEHICLE}\s+vectors?\b",
        "22 vectors",
        "the pinned number is 23 vectors (`specification/schema/validate.py`); a different "
        "number is a claim the corpus disproves",
    ),
    Phrase(
        rf"\b(?!192\b){VEHICLE}\s+assertions?\b",
        "190 assertions",
        "the pinned number is 192 assertions (`specification/schema/validate.py`); a different "
        "number is a claim the corpus disproves",
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


def _blank_keep_newlines(match: re.Match[str]) -> str:
    return "".join("\n" if char == "\n" else " " for char in match.group(0))


def normalise(text: str) -> tuple[str, list[int]]:
    """The page's visible text, with the source line of every character.

    Comments and tags are not rendered, so they are not claims: both are blanked. Entities are
    decoded after the tags are gone, so an escaped angle bracket in the prose is not mistaken for
    a tag. Dashes are flattened and whitespace collapsed, because a phrase split across the
    page's ~90-column wrapping is not absent — it is the same phrase with a line break in it.
    """
    text = re.sub(r"<!--.*?-->", _blank_keep_newlines, text, flags=re.DOTALL)
    text = re.sub(r"<[^>]*>", _blank_keep_newlines, text)
    visible: list[str] = []
    line_of: list[int] = []
    for number, line in enumerate(text.splitlines(), 1):
        line = html.unescape(line)
        line = DASHES.sub("-", line)
        line = re.sub(r"\s+", " ", line).strip()
        if not line:
            continue
        for char in line:
            visible.append(char)
            line_of.append(number)
        visible.append(" ")
        line_of.append(number)
    return "".join(visible), line_of


def main() -> int:
    compiled: list[tuple[Phrase, re.Pattern[str]]] = []
    for phrase in FORBIDDEN:
        pattern = re.compile(phrase.pattern, re.IGNORECASE)
        if not pattern.search(normalise(phrase.sample)[0]):
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
            text, line_of = normalise(handle.read())
        for phrase, pattern in compiled:
            for match in pattern.finditer(text):
                hits += 1
                print(
                    f"{os.path.relpath(path, root)}:{line_of[match.start()]}: "
                    f"forbidden phrase {match.group(0)!r}\n"
                    f"    {phrase.reason}"
                )

    if hits:
        print(f"check-claims: {hits} forbidden phrase(s) in {len(paths)} file(s)")
        return 1

    print(
        f"check-claims: {len(compiled)} known wordings alive over {len(paths)} file(s), none "
        "found. This is a filter, not a proof: a false claim in other words passes it"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
