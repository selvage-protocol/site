#!/usr/bin/env python3
"""Fails the shipped page on a phrase the project cannot back today.

This is a filter, not a proof. It matches a list of known wordings; a false claim written in
different words, a synonym, a superlative, a wrong number the corpus does not pin, or any
sentence that is merely unbacked all pass it. What it does guarantee is narrower and still
worth having: those known wordings do not appear, even when the page wraps them across lines or
encodes the characters as HTML entities.

Facts are asserted in the positive instead, because a phrase list cannot reach them: the image tag
in the `docker run` the page hands a reader, the instance the demo section points at — the address
it gives an editor and the page a guest is sent to — the wire the tag and that address each speak,
held together and to no version this protocol does not have, the disclosures the page owes a reader
of what the sealed relay still sees and of the terms `selvaged` is under, and the identity the
extension is published under with the two
registries the release publishes it to and what an
install is and is not. The address half asks the
path a plain `GET` can reach, not the upgrade: see `demo_session_route`. Each is a fact with an
artefact behind it, and a wrong tag is a command that fails rather than a wording that lies. See
`PUBLISHED_IMAGE`, `DEMO_ORIGIN`, `RELAY_DISCLOSURE`, `FSL_DISCLOSURE`, `PUBLISHED_EXTENSION` and
`check_wire_binding` below.

Each entry below pairs a phrase the page must not carry with the reason it must not, and with a
sample that has to match it. The reasons are not this script's opinion: every one of them is a
claim the research record already checked and found false or unbacked, and the sample is what
keeps a pattern from quietly matching nothing — a check whose patterns are dead and a check that
scans no file both report a clean page, which is the failure this file exists to catch.

The scan normalises what it reads before it matches: inline markup (spans, links, comments)
is removed without a trace, so a phrase split by a tag is still the same phrase; `script` and
`style` elements are skipped whole, so the rendered page's framework runtime never scans as
prose; block markup
leaves a single space, so a phrase ending one block and starting the next is two phrases, not
one written across a boundary. Entities are decoded, unicode dashes become hyphens, and runs of whitespace (including the line breaks the
page wraps at) collapse to a single space. A phrase that only looks absent because it happened to
wrap, or because a hyphen was written as `&#45;`, would otherwise pass.

Prose the page carries in a `meta` attribute is scanned beside its body text, because a link unfurl
prints that prose verbatim and a claim written there is a claim: `description`, `og:*` and
`twitter:*` are read as text of their own. Tags are stripped otherwise, so without that half a
page could carry an overclaim only the unfurl and no reader's eye would meet.

Run from anywhere; the repository root is resolved from this file's location. Arguments are paths
(files or directories) to scan instead of the whole checkout.

    scripts/check-claims.py              # every *.html in the checkout
    scripts/check-claims.py .tmp/empty   # reaches no file: that is a failure, not a pass

Exit 0 when the page is clean of every known wording and the positive claims hold up, 1 when it
carries a forbidden wording or a positive claim is wrong, 2 when the check itself cannot run (a
dead pattern, nothing to scan, a registry that cannot be asked, or a demo host that does not
answer).
"""

from __future__ import annotations

import html
import json
import os
import re
import sys
import urllib.error
import urllib.request
from dataclasses import dataclass

# Directories that never hold the shipped page.
SKIP_DIRS = {".git", ".tmp", "node_modules"}

# A claimed corpus number that is not the one `specification/schema/validate.py` pins is a wrong
# number the page would otherwise show without failing anything. The lookahead is what makes the
# pinned value the only one that passes. There are two layers and each is pinned on its own — the
# wire corpus's 24 vectors, 33,760 frame checks and 8,387 assertions, and the peer corpus's 26
# vectors, 221 checks and 74 assertions — so a number before one of those nouns has to be that
# layer's pin, and the peer layer's count is written with the layer named ('26 peer vectors').
#
# The wire layer's two largest counts are written with their thousands separated on the page,
# because a reader has to read them; `33,?760` accepts either spelling so a count written without
# the separator is still recognised rather than read as a number that is missing.
VEHICLE = r"\d[\d,]*"

# The address the project's own landing page is served at. The browser entry holds a claim that
# this origin is a place to join a room: the demo instance is where a page can be opened now, and
# the site is not a client.
SITE_ORIGIN = r"selvage\.dontblameme\.dev"

DASHES = re.compile("[\u2010-\u2015\u2212\ufe58\ufe63\uff0d]")

# The page's happy path is a `docker run` a reader pastes, so the tag in it is a claim with an
# artefact behind it: a wrong tag is `manifest unknown`, not a wording a phrase list can
# enumerate. It is therefore a *required* claim, pinned once here and asserted twice: every
# reference the rendered page carries must name this tag, and the registry must serve it.
#
# The tag is one the release publishes rather than a version, because a version written into a
# reader's command goes stale the moment the page's copy of it does. `latest` resolves to a built
# artefact all the same, which is what the registry half reaches, and any other tag on the page
# fails the first half rather than passing as a live command.
#
# The registry half is the one that reaches the artefact, and it holds the distinction that
# matters: a platform entry in an image index proves only that a slot is *labelled* arm64.
# `selvaged:0.1.1` published one, and both its legs carried the amd64 binary — every layer
# digest identical across the two per-platform manifests, the same defect `0.1.0` carries. The check
# compares those digests and fails when they are the same set, which is what a mislabelled leg
# looks like, and it pulls them with no credential in the request, because no account is the
# point of the command the page hands over.
PUBLISHED_IMAGE = "ghcr.io/selvage-protocol/selvaged"
PUBLISHED_IMAGE_TAG = "latest"
IMAGE_REFERENCE = re.compile(r"ghcr\.io/selvage-protocol/selvaged(?::([\w][\w.+-]*))?")
REGISTRY_HOST = "ghcr.io"
REGISTRY_REPOSITORY = PUBLISHED_IMAGE.split("/", 1)[1]
REQUEST_TIMEOUT_SECONDS = 20

# The wire version this protocol has, and which wire the tag the page hands a reader speaks. The
# page hands a reader an artefact whose wire is a fact about the artefact, not a wording: under this
# version the room's bytes reach the server sealed, so a page that puts the sealing claim over a
# command yielding a relay that cannot seal is a silent downgrade. The map is a constant rather
# than a measurement because nothing on a registry answers what wire version a binary speaks: an
# index will say `linux/arm64` and nothing about the frames inside. A tag with no entry fails the
# check instead of defaulting, so a release that points a tag at a different wire has to declare it
# in the same wave — this map, `PUBLISHED_IMAGE_TAG` and the page's sentence about it move
# together, and `check_wire_binding` is what holds the last of the three to the first two.
#
# The entry is keyed by the tag, not by a version, and the tag is a moving name: the protocol has
# one wire version, so every release that tag can resolve to speaks it, and what the entry refuses
# is a tag whose wire nobody has declared rather than a tag that has moved.
WIRE = "selvage/2"
IMAGE_WIRE_BY_TAG = {
    "latest": WIRE,
}
WIRE_VERSION = re.compile(r"\bselvage/\d+\b")

# The demo section points at a running instance, a claim with an artefact behind it in the same
# way the `docker run` is. Four sentences around it are checkable here: an instance of the server
# runs at that host, the address the section hands an editor hosts a room on it, that editor
# speaks a wire version the instance offers, and the browser row's guest page is served there. A
# host that has moved, a box that is down, or a box that answers only part of that is a false
# sentence, and no phrase list can enumerate those.
#
# What is deliberately no longer asserted is which release the box runs. The page named one and
# the check compared it; the page stopped naming it, because a visitor has no use for the version
# of an endpoint they will never call. `PUBLISHED_IMAGE_TAG` is still asserted, against the
# registry, as the tag the `docker run` hands a reader.
DEMO_HOST = "selvage-demo.dontblameme.dev"
DEMO_ORIGIN = "https://" + DEMO_HOST
# Every reference the page may carry to that host: the instance's own origin, and its terms page.
# The session address is the origin as well, with no path. The clients append the endpoint path
# themselves (`sessionUrl` in the engines both clients vendor), so the two forms are not
# interchangeable: an address already carrying the path gets a second one appended and the socket
# is refused, which is why the full form is not an allowed reference.
DEMO_REFERENCES = (DEMO_ORIGIN, DEMO_ORIGIN + "/terms", "wss://" + DEMO_HOST)
DEMO_URL = re.compile(r"(?:https?|wss?)://[^\s\"'<>)]+")
# The endpoint path the clients append to whatever server address they are given, so the address
# the page hands a reader names this path's parent.
SESSION_PATH = "/session"
# The name the server artefact reports from `/meta`, and the artefact the page's own `docker run`
# pulls. The page's sentence is that an instance of the server runs at that host, so a `/meta`
# that does not name this is a different thing answering on the same host.
SERVER_NAME = re.compile(r"selvaged/\S+")
# The host card's own element in the shell the client serves: `web_client`'s `public/index.html`
# writes it into the markup rather than building it in script, so it is in the bytes `/` answers
# with whatever the browser is and whether or not the bundle's script has run. It is the artefact
# behind the page's sentence that a session can be started from the demo's page: a bundle older
# than the one that added the card carries no such element, and the sentence would be about a page
# that cannot start one.
HOST_CARD = re.compile(r'id="host-wrap"')
# The page's statement of what the sealed relay still sees is a claim the gate has to *require*,
# not just permit: the `clean` fixtures above only prove the pattern does not reject those
# sentences, and an editor who deleted the statement would leave every one of them green. What is
# required is the facts, one pattern each, so a rewrite that keeps them passes and a page that
# drops one fails. The panel carries them in two shapes: the chips name three of them a line at a
# time, and the fourth is the heading's "What the server can still see" read with the chip under it
# that completes it.
#
# Two of the four are phrased as the panel's own statement rather than as a bare subject and verb,
# because the page states those two a second time in *The session layer is written down*: "Which
# rooms exist, who is in one, ...", which is a sentence about what every collaborative tool
# decides for itself and not a statement of relay visibility at all. Loosely matched, that
# paragraph would supply existence and membership for a page whose statement had been deleted, and
# a rewrite that dropped the two facts while keeping "their names" and "sizes and timing" would
# pass with them gone. `who is in it` is the panel's wording and `who is in one` is the donor's;
# the existence fact is the heading's "still see" with the chip's clause after it, not the bare
# "rooms exist" the donor paragraph writes.
RELAY_DISCLOSURE = (
    (
        "the room's existence",
        re.compile(
            r"\bsees that an? (?:room|session)s? exists?\b"
            r"|\bstill (?:sees|reads)\b[^.]{0,40}\b(?:room|session)s?\b[^.]{0,24}\bexists?\b"
            r"|\bstill see\b[^.]{0,120}\bthat an? (?:room|session)s? exists?\b",
            re.IGNORECASE,
        ),
    ),
    (
        "its membership",
        re.compile(
            r"\bwho is in (?:it|the room)\b|\bmembership\b|\bwho (?:has )?joined\b",
            re.IGNORECASE,
        ),
    ),
    (
        "the display names",
        re.compile(
            r"\bdisplay names?\b|\btheir names\b|\b(?:members?|participants?)'? names\b",
            re.IGNORECASE,
        ),
    ),
    (
        "the sizes and timing of what moves",
        re.compile(r"\bsizes?\b[^.]{0,32}\btiming\b", re.IGNORECASE),
    ),
)
# The disclosure the page owes a reader of the server's licence, required the way the relay's is:
# the `open source` entry forbids one false wording, and this holds the page to the truth a reader
# must meet instead. Each part is a pattern of its own, so a rewrite that keeps the facts passes
# and a page that drops or contradicts a part fails. The identifier bound to `selvaged`, the
# source-available term, the OSI denial, the grant for non-competing use and the MIT conversion
# are read together from one page: the disclosure is one claim, and a page that states four of
# its five parts has not stated it.
FSL_DISCLOSURE = (
    (
        "that `selvaged` is FSL-1.1-MIT",
        re.compile(
            r"\bselvaged\b[^.]{0,64}\bFSL-1\.1-MIT\b|\bFSL-1\.1-MIT\b[^.]{0,64}\bselvaged\b",
            re.IGNORECASE,
        ),
    ),
    (
        "that it is source-available",
        re.compile(r"\bsource[-\s]available\b", re.IGNORECASE),
    ),
    (
        "that it is not OSI-approved",
        re.compile(r"\bnot\b[^.]{0,40}\bOSI[-\s]?approved\b", re.IGNORECASE),
    ),
    (
        "that it is free for non-competing use",
        # A `not` in front of the grant or inside it denies it rather than stating it.
        re.compile(
            r"(?<!\bnot )(?<!n't )\bfree\b(?:(?!\bnot\b)[^.]){0,64}\bnon[-\s]?competing\b",
            re.IGNORECASE,
        ),
    ),
    (
        "that it converts to MIT two years after each release",
        re.compile(r"\bMIT\b[^.]{0,64}\b(?:two|2)\s+years\b", re.IGNORECASE),
    ),
)
# The corpus and every count the page could show for it, and the file that pins each count: the
# wire layer's 24 vectors, 33,760 frame checks and 8,387 assertions, and the peer layer's 26
# vectors, 221 checks and 74 assertions are all constants in `specification/schema/validate.py`.
# The page shows none of them, because they move as the corpus grows, and names the file
# instead, which is where a reader reads the current ones. A number the page hands a reader with
# no file beside it is one the reader cannot check, so a count that comes back is held to the same
# citation.
# Where a sentence ends in the visible text. A bare `.` is not one: the file this check reads
# for is `schema/validate.py`, and cutting a window at the period before its `py` truncated the
# citation out of the very sentence that carries it.
SENTENCE_END = re.compile(r"\.(?=\s|$)")
CORPUS_COUNTS = (
    # Both spellings the forbidden-number rules accept: `24 conformance vectors` and `24 wire
    # vectors` are the same pin, and a citation rule that matched only one of them would leave
    # the other wording unguarded — the count would not be seen at all, so nothing would ask it
    # for a file.
    (re.compile(r"\b24 (?:conformance|wire) vectors\b"), "the 24 wire vectors"),
    (re.compile(r"\b33,?760 frame[- ]checks\b"), "33,760 frame checks"),
    (re.compile(r"\b8,?387 assertions\b"), "8,387 assertions"),
    (re.compile(r"\b26 peer vectors\b"), "26 peer vectors"),
    (re.compile(r"\b221 peer checks\b"), "221 peer checks"),
    (re.compile(r"\b74 peer assertions\b"), "74 peer assertions"),
)
# The page's name for the corpus, in both spellings the counts above accept.
CORPUS_MENTION = re.compile(r"\b(?:conformance|wire) vectors\b")
CORPUS_FILE = re.compile(r"\b(?:specification/)?schema/validate\.py\b")
USER_AGENT = "selvage-site-check/1.0"

# The extension's published identity and the registries the release publishes that one `.vsix`
# to. `selvage-protocol.selvage` is the `publisher` and `name` in `vscode_client/package.json`,
# and the two registries are the two publish steps in that repository's `release.yml`; the page
# hands a reader an install, so these are facts with artefacts behind them rather than wordings.
#
# The entry this replaces forbade the words "marketplace", "open vsx" and "gallery" outright,
# because publishing the extension was a non-goal (`DESIGN.md` §11: "marketplace publication
# until it works with a friend"). The owner retired that non-goal and the extension is published
# on both registries, so the rule runs the other way now: naming the two is required, and what is
# forbidden is a registry the project does not publish to — or "the extension gallery" without
# naming one, which is a channel the page cannot point at.
PUBLISHED_EXTENSION = "selvage-protocol.selvage"
PUBLISHED_REGISTRIES = (
    (
        "the VS Code Marketplace",
        re.compile(r"\b(?:VS ?Code|Visual Studio)\s+Marketplace\b", re.IGNORECASE),
    ),
    ("Open VSX", re.compile(r"\bOpen\s*VSX\b", re.IGNORECASE)),
)
# The two listings, and the identity is inside both. They are not *required* links: the page's
# own link check reaches every URL it carries, and the Marketplace's listing URL answers 404
# until the release that publishes the extension has run, so requiring one here would redden the
# gate for a release that has not been dispatched. What is checked is the other direction — a
# page that links a listing has to link one of these two, so a link to the retired
# `selvage-protocol.selvage-client`, which still exists on the Marketplace, fails on the
# destination rather than on the label.
EXTENSION_LISTINGS = (
    "https://marketplace.visualstudio.com/items?itemName=" + PUBLISHED_EXTENSION,
    "https://open-vsx.org/extension/" + PUBLISHED_EXTENSION.replace(".", "/"),
)
REGISTRY_LISTING = re.compile(
    r"marketplace\.visualstudio\.com/items\b|open-vsx\.org/extension/",
    re.IGNORECASE,
)
# Registry-shaped words. Every one the page carries has to be part of one of the two names above,
# so a page that also offers the extension from somewhere else — "the extension gallery", the
# JetBrains or Eclipse marketplace, another editor's store — fails instead of passing on the two
# names it carries as well. A bare "registry" is deliberately not here: `ghcr.io` is one, and the
# image section may name it.
REGISTRY_WORD = re.compile(
    r"\bmarketplaces?\b|\bgaller(?:y|ies)\b|\bopen\s*vsx\b"
    r"|\b(?:extension|plugin|add-?on)s?\s+stores?\b|\b(?:extension|plugin)s?\s+registr(?:y|ies)\b",
    re.IGNORECASE,
)
# What the row has to state about the install itself, required the way the disclosure is: a
# `clean` fixture only proves a pattern does not reject a sentence, so a page that keeps the two
# registry names and drops what the install is would leave a reader thinking a gallery install is
# a session. "on a server you run" is not the sentence to read — the hero carries that one — so
# the limitation is phrased as what an install is and is not, and as the client's own binary.
EXTENSION_INSTALL_LIMITATION = (
    (
        "that an install is the client and not a server",
        re.compile(
            r"\bclient\b[^.]{0,32}\bnot a server\b"
            r"|\bnot a server\b"
            r"|\bno server\b"
            r"|\bclient only\b"
            r"|\bserver is not part of\b",
            re.IGNORECASE,
        ),
    ),
    (
        "that a session needs a `selvaged` the reader runs",
        re.compile(
            r"\bselvaged\b[^.]{0,32}\byou run\b|\byou run\b[^.]{0,32}\bselvaged\b",
            re.IGNORECASE,
        ),
    ),
)
EXTENSION_PUBLICATION = (
    (
        "the extension's published identity",
        re.compile(rf"\b{re.escape(PUBLISHED_EXTENSION)}\b", re.IGNORECASE),
    ),
    *(
        (f"{name} as a registry it is published on", pattern)
        for name, pattern in PUBLISHED_REGISTRIES
    ),
    *EXTENSION_INSTALL_LIMITATION,
)

# How a page that says which wire an artefact speaks is read: which wire the image under the
# `docker run` speaks, and which wire the demo speaks. A page is no longer required to say
# either, so `check_wire_binding` reads them where they are written and holds each to the
# artefact it names.
WIRE_OF_IMAGE = re.compile(
    r"\bthe (?:published |pinned )?(?:image|container)\b"
    r"[^.]{0,80}?\bspeaks?\b[^.]{0,40}?\b(selvage/\d+)\b",
    re.IGNORECASE,
)
WIRE_OF_DEMO = re.compile(
    r"\b(?:the demo|the instance)\b[^.]{0,80}?\bspeaks?\b[^.]{0,40}?\b(selvage/\d+)\b",
    re.IGNORECASE,
)
# How a page says the sealing is not what a reader can obtain yet. There is no version to say it of:
# the protocol has one wire version and the published tag speaks it, so the sentence is false — it
# tells a guest their room is plaintext when it is not. `check_wire_binding` forbids it rather than
# requiring it, which is the direction it had while a version was still unpublished.
WIRE_UNRELEASED = re.compile(
    r"\bnot in a published release\b|\bno published release\b"
    r"|\bnot (?:yet )?(?:published|released|shipped)\b",
    re.IGNORECASE,
)
# A link's destination lives in an attribute, and the visible text carries only its label, so both
# are scanned: an anchor labelled with the demo host can point somewhere else entirely.
DESTINATION = re.compile(r"\b(?:href|src|action)\s*=\s*(?:\"([^\"]*)\"|'([^']*)')", re.IGNORECASE)
# Prose an attribute carries rather than the body. A `meta` element's `content` is what a link
# unfurl prints, which is the surface a person deciding whether to paste the link meets before the
# page renders; the tags themselves are stripped from the visible text, so this prose is invisible
# to every pattern above unless it is read as text of its own.
META_ELEMENT = re.compile(r"<meta\b[^>]*>", re.IGNORECASE)
META_KEY = re.compile(r"\b(?:name|property)\s*=\s*(?:\"([^\"]*)\"|'([^']*)')", re.IGNORECASE)
META_CONTENT = re.compile(r"\bcontent\s*=\s*(?:\"([^\"]*)\"|'([^']*)')", re.IGNORECASE)
# `description` alone, and the two prefixed families. `og:image` and friends are URLs rather than
# prose and are not read here: a URL is checked where it is a destination, not as a sentence.
META_PROSE_KEYS = ("description",)
META_PROSE_PREFIXES = ("og:", "twitter:")
MANIFEST_TYPES = (
    "application/vnd.oci.image.index.v1+json",
    "application/vnd.docker.distribution.manifest.list.v2+json",
    "application/vnd.oci.image.manifest.v1+json",
    "application/vnd.docker.distribution.manifest.v2+json",
)


@dataclass(frozen=True)
class Scanned:
    """One rendered file, as the scan read it.

    `text` and `line_of` are the visible page — what a reader sees, which is what a phrase claim
    is made of. `destinations` are the URL-bearing attributes with the line each sits on, because
    a link's destination is not visible: `<a href="https://elsewhere.example">selvage.example</a>`
    renders as the label alone.
    """

    path: str
    text: str
    line_of: list[int]
    destinations: list[tuple[str, int]]
    # The bytes the scan read, kept so a fact that has to be read out of an element's own
    # markup — a grid row whose name, description, pill and destination are one claim — can be
    # read from where it sits rather than from the page's flattened text.
    raw: str
    # Prose carried in attributes rather than in the body: one normalised stream per `meta`
    # element, each with the source line of every character. Scanned beside `text`, never
    # instead of it, so a claim in a link unfurl fails the same way one in a paragraph does.
    prose: list[tuple[str, list[int]]]


@dataclass(frozen=True)
class Phrase:
    pattern: str
    sample: str
    reason: str
    # Spellings of the same claim that must match too: the wording with markup inside its
    # tokens, which the browser joins and this scan does not, and a reworded version that
    # evades a bounded window or another verb. Each one has to match — an evasion that slips
    # through is an overclaim the filter passes.
    evasions: tuple[str, ...] = ()
    # Honest wordings the pattern must not match. Each one has to stay clean: a broadening
    # that reintroduces a false positive fails the gate instead of passing everything.
    clean: tuple[str, ...] = ()
    # Wordings the pattern matches that are backed all the same, because one of these matches a
    # sentence the hit sits in. Written this way the exemption is about what the sentence names
    # rather than about the shape of the determiners in front of the verb, so a true sentence
    # survives whatever order it puts its nouns in, and a false one cannot borrow an unrelated
    # noun from a sentence away because the window is the sentence around the hit.
    permitted_when: tuple[str, ...] = ()
    # Wordings that cancel a permit: the sentence names the permitted material and denies it, so
    # the name is not the disclosure the permit exists to read. "The relay learns no membership"
    # names membership and asserts the opposite of what the permit is for, and the pattern is
    # written against the permit's own noun rather than against negation in general — "the
    # server cannot read the text" is an honest sentence with a negative in it, and it stays one.
    voided_when: tuple[str, ...] = ()


FORBIDDEN: list[Phrase] = [
    Phrase(
        r"open[- ]sourc\w*",
        "the server is open source",
        "the server binary `selvaged` is FSL-1.1-MIT: source-available, not OSI-approved. Name "
        "the licences instead; 'open source' is false of the server and of the project as a whole",
        ("the server is o<!-- -->pen source", "the server is open <em>so</em>urce",
         "the server is o<span title=\">\">pen source", "the server is o<!--\n-->pen source"),
    ),
    Phrase(
        r"\bSSP\b",
        "the SSP wire",
        "the abbreviation is taken, by stack-smashing protection and by supply-side platforms; "
        "the protocol is the Selvage Session Protocol, written out at least once per paragraph",
        ("the S<!-- -->SP wire",),
    ),
    Phrase(
        r"salvage/1|salvage/2",
        "the wire version is salvage/1",
        "the wire version is `selvage/2`; 'salvage' is the near-homophone the full protocol "
        "title exists to defend against",
        ("the wire version is s<!-- -->alvage/2",),
    ),
    Phrase(
        # The overclaim family the project's E2EE plan refutes
        # (`selvage-protocol/ai_notes`, `docs/studies/e2ee-plan.md` §2), and the one a reader
        # writes first: "no one else can see it" is the same claim as "nobody else can read it", and
        # "the server knows nothing" is the same one with the sentence turned round. The subject,
        # the verb and the word order are all alternated for that reason; pinning any of them to
        # one spelling is what let four paraphrases through in the review's probe.
        #
        # The window between the subject and the verb is the sentence's, not a word's: a page
        # that writes "the server relays the room as ciphertext and learns nothing" states the
        # claim 35 characters after its subject, which a 24-character window passed. There is no
        # permit on this entry — naming what the relay still reads does not make the overclaim
        # true — so the wider window is what closes it.
        r"\b(?:nobody|no[ -]?one)\b[^.]{0,24}\bcan\b[^.]{0,16}"
        r"\b(?:read|see|open|decrypt|view)\b"
        r"|\bonly\b[^.]{0,32}\bcan\b[^.]{0,16}\b(?:read|see|open|decrypt|view)\b"
        r"|\bthe (?:server|relay|box|binary|instance)\b[^.]{0,64}"
        r"\b(?:learns|knows|sees|reads)\b[^.]{0,24}\bnothing\b"
        r"|\bfully encrypted\b"
        r"|\bzero[- ]knowledge\b",
        "nobody else can read the room",
        "the relay is sealed, not omniscient: it still reads the room's existence, membership, "
        "display names, sizes and timing, and the keys are in the link a human pastes. Whoever "
        "holds that link can read the room, its fragment included",
        (
            "nobody else can read it",
            "no one else can read it",
            "nobody else can see it",
            "only the people in the room can read it",
            "only the two of you can read the room",
            "only your peers can read the room",
            "the server learns nothing",
            "the server knows nothing about your code",
            "the server sees nothing",
            "fully encrypted",
            "zero-knowledge relay",
            "the server relays the room as ciphertext and learns nothing",
            "the relay carries the room and sees nothing of what is in it",
        ),
        (
            # The link's holder is inside the threat model and not outside it, so this sentence
            # is the honest one the page carries beside the claim; a pattern that forbade it
            # would push the page back to the sentence the claim wanted.
            "Whoever holds the invite can read the room, its fragment included.",
            (
                "It still sees that a room exists, who is in it, their names, and the sizes "
                "and timing of what moves."
            ),
        ),
    ),
    Phrase(
        # The browser client is published now and it hosts: on Chrome or Edge a page its own
        # server serves starts a room from a folder the person picks, which is the demo's shape
        # and needs no editor at all. The page may therefore name a route a reader can follow and
        # say a room can be started from a page. What survives is what is still false: hosting in
        # a browser the reader may not be holding (Firefox and Safari have no directory picker,
        # so they join and cannot host, which is the claim the unqualified "host a session in the
        # browser" makes); joining without the invite link a host copies; the stale denial that
        # nothing runs in a page, which the page once carried; and the claim that the project's
        # own landing page is a place to join a room, the route-shaped overclaim left now that a
        # real route exists.
        r"\bnothing runs? in a (?:web page|tab|browser)\b"
        r"|no clients? (?:to|that|which)? ?(?:runs?|open)\w* in a (?:web page|tab|browser)"
        r"|\b(?:host|start|create|mint)\w*\s+(?:a|the|your)\s+(?:room|session)\s+"
        r"(?:in|from|with|on)\s+(?:a|the|your)?\s*(?:browser|web page|tab)\b"
        r"|\b(?:open|visit|browse)\w*\b[^.]{0,24}\b(?:page|browser|tab)\b[^.]{0,24}"
        r"\bstart typing\b"
        r"|\bwithout (?:an )?invite\b|\binvite[- ]free\b"
        r"|" + SITE_ORIGIN + r"[^.]{0,48}\b(?:browser|client|room|join|edit)\w*\b"
        r"|\b(?:browser|client|room|join|edit)\w*\b[^.]{0,48}" + SITE_ORIGIN,
        "open the page in your browser and start typing",
        "the browser page joins a room from a link in any browser, and Chrome or Edge can start "
        "one from a folder on a page the room's own server serves, which the demo is. What is "
        "false is the unqualified form: Firefox and Safari have no directory picker, a page no "
        "server serves cannot host, joining needs the invite link a host copies, and the "
        "project's own site is a landing page rather than a client",
        (
            "nothing runs in a web page",
            "there is no client to open in a tab",
            "host a session in the browser",
            "browse selvage.dontblameme.dev in your browser",
            "selvage is available in your browser at selvage.dontblameme.dev",
            "selvage.dontblameme.dev is where a guest joins",
        ),
        (
            "The browser page joins the same room from a tab, with the invite link a host copies.",
            "A guest works in the page at https://selvage-demo.dontblameme.dev with nothing installed.",
            "On Chrome or Edge, a page its own server serves starts a session from a folder you pick.",
            "The page starts a room in Chrome or Edge, and only where its own server serves it.",
            "Chrome or Edge can start a session from the page instead.",
        ),
    ),
    Phrase(
        r"\b(?:create|rename|delete)\w*\s+(?:files?|folders?|directories|paths)",
        "delete files in the host's folder",
        "the room carries no file mutations: nothing on the wire adds, renames or removes a "
        "path, and the only write to the host's working copy is the host's own. A guest's "
        "keystroke reaches the folder through the host's client, which is what writes out the "
        "text the room settled on",
    ),
    Phrase(
        r"file (?:creat|renam|delet)\w*",
        "file creation",
        "the room carries no file mutations: nothing on the wire adds, renames or removes a "
        "path, and the only write to the host's working copy is the host's own, so a guest "
        "cannot create, rename or delete a file in it",
    ),
    Phrase(
        # This entry used to forbid the word `docker`, on the reason that no Dockerfile, compose
        # file or service unit existed. All three exist today, so those wordings are truth and
        # the pattern was enforcing the opposite of it. What it holds now is the denial those
        # artefacts refute, which is the sentence the page carried until this was corrected:
        # `reference_server/Dockerfile`, `reference_server/compose.yaml`,
        # `reference_server/packaging/systemd/selvaged.service` and the anonymously pullable
        # `ghcr.io/selvage-protocol/selvaged:0.2.0` are all in the repositories.
        r"\bno (?:image|container) to pull\b|\bnothing to install on the server\b"
        r"|\bno compose (?:file|configuration)\b|\bno systemd (?:service|unit)\b",
        "there is no image to pull and no service unit to install in any repository yet",
        "the server image is published (`ghcr.io/selvage-protocol/selvaged:0.2.0`) and pulls "
        "with no account, `reference_server/compose.yaml` runs it, and "
        "`reference_server/packaging/systemd/selvaged.service` installs the binary: a page "
        "saying none of that exists states the opposite of the truth",
        ("there is no im<!-- -->age to pull", "no conta<span></span>iner to pull",
         "there is no comp<!-- -->ose file", "there is no systemd <span>u</span>nit"),
        ("the published image pulls with no account and no login",
         "the image is published, so there is nothing to clone"),
    ),
    Phrase(
        # The lookbehind is what keeps a version-inside-a-version out of a pattern about a 1.0
        # claim: a tag like `2.1.0` carries `1.0` as a substring, and naming a tag that happens
        # to contain it is describing an artefact, not claiming a frozen release. The tag the
        # page carries is `latest`, which carries no `1.0` substring at all, so the fixture below
        # is synthetic rather than the live tag; the lookbehind still has to hold for whatever
        # tag a future release publishes under. A 1.0 that stands on its own still matches.
        r"(?<![\d.])v?1\.0\b|production[- ]ready|production[- ]grade|battle[- ]tested|stable release",
        "the stable release, version 1.0",
        "the wire version is `selvage/2`; no shape is frozen, and a release tag is a version of "
        "an artefact rather than a claim that 1.0 exists",
        ("we are at v1.0", "the stable rele<!-- -->ase, version 1.0"),
        ("ghcr.io/selvage-protocol/selvaged:0.4.5", "0.4.5", "version 0.4.5", "tool:2.1.0"),
    ),
    Phrase(
        r"second implementation|interoperab\w*",
        "a second implementation exists",
        "there is no second implementation: the Neovim client drives a byte-identical copy of "
        "the same engine, so nothing yet shows a client built from the prose alone agreeing "
        "byte for byte with this one",
    ),
    Phrase(
        # The direction that is false now. Publication used to be a non-goal and the page said as
        # much (`DESIGN.md` §11); the owner retired that, and the extension is published under
        # both registries, so the denial is what a rewrite would reach for and what this forbids.
        # The registries themselves are the other half of the rule, in
        # `check_published_extension`: this one only stops the page saying there are none.
        r"\bunpublished\b|\bnot (?:yet )?published\b|\bnothing published\b"
        r"|\bno published (?:extension|listin\w+|build)\b",
        "the extension is unpublished",
        "the extension is published as `selvage-protocol.selvage` on the VS Code Marketplace "
        "and on Open VSX, so a page saying it is not is false about the whole distribution "
        "channel; the retired wording — that publishing was a non-goal until it worked with a "
        "friend — is the decision this wave replaces",
        (
            "the extension is un<!-- -->published",
            "it is not yet published",
            "the extension is not yet publ<span></span>ished",
            "there is no published extension",
        ),
        (
            "It is published as `selvage-protocol.selvage` on the VS Code Marketplace and on "
            "Open VSX.",
            "A checkout and `npm run package` is the other way in.",
        ),
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
        "the host's file contents travel through the server to the peers that ask for them, and "
        "they are sealed in `selvage/2` but still leave the machine; 'only the people in the "
        "room' is false whatever the version, because whoever holds the link can read the room, "
        "its fragment included",
    ),
    Phrase(
        # "End-to-end encrypted" is the promise that plan's §2 refutes in one phrase: the
        # ordinary reading is that only the endpoints know anything, and a pwned relay knows the
        # nine things that section lists. It is not forbidden outright — a sentence that says
        # what stays visible beside it is the honest form, and the permit reads that — but it is
        # not permitted either, which is what dropping the entry left: "Selvage is end-to-end
        # encrypted" alone, or "the relay is blind", walked past every pattern the gate had.
        r"\bend[- ]to[- ]end\b|\be2ee\b"
        r"|\b(?:server|relay|box)\b[^.]{0,12}\b(?:is|stays?|remains?|goes)\b[^.]{0,8}"
        r"\b(?:blind|oblivious)\b",
        "Selvage is end-to-end encrypted.",
        "the seal covers the room's text and not its shape: the relay still reads a room's "
        "existence, its membership, the display names, the sizes and timing of what moves, the "
        "epoch, how many documents and files a room has and when one is fetched, and it can "
        "drop, delay, reorder, refuse or end a room. An unqualified 'end-to-end encrypted' or "
        "'the relay is blind' claims the shape too",
        (
            "Selvage is end-to-end encrypted.",
            "The room is encrypted end to end.",
            "Your code is encrypted end-to-end, so the relay is blind.",
            "The relay is blind.",
            "It is end-to-end encrypted.",
            "Selvage is end-to-end encrypted, so the relay learns no membership and no names.",
        ),
        (
            (
                "In `selvage/2` the room is end-to-end encrypted under keys the fragment "
                "carries, and the relay still sees a room's existence, its membership, the "
                "display names and the sizes and timing of what moves."
            ),
        ),
        (
            # What stays visible, named in the same sentence, is what makes the claim specific.
            # 180 lines away is not beside the claim: the fact has to sit in the sentence.
            r"\bstill (?:sees|reads|learns|knows)\b"
            r"|\b(?:existence|membership)\b"
            r"|\b(?:their|display|member|participant) names\b"
            r"|\bsizes?\b[^.]{0,32}\btiming\b",
        ),
        (
            # The permit is an honest sentence naming what the relay still reads. A sentence
            # that names it and denies it reads the same noun the other way round — "the relay
            # learns no membership" — and is the unqualified claim the permit exists to tell
            # apart from this one.
            r"\b(?:no|not|never|without|nothing|neither|nor)\b[^.]{0,16}"
            r"\b(?:existence|membership|names?)\b",
        ),
    ),
    Phrase(
        # The relay is sealed, so "the server cannot read" is backed when the thing it cannot read
        # is named and is sealed material, and it is the overclaim the page's own paragraph refutes
        # when it is bare or has the room as its object. The subject is alternated because the
        # page's own author already writes a different one — "the box … carries bytes it cannot
        # read" — and `it` is in the list because its absence is how "It cannot read the room"
        # passed: `it` is the server in one sentence and the host's own client in the next, and
        # only the object tells them apart. The modality and the verb are alternated for the same
        # reason, and `decrypt` is the verb a page about sealing reaches for first.
        r"\b(?:the\s+(?:server|relay|box|binary|instance|daemon)|selvaged|your\s+server|it)\b"
        r"[^.]{0,24}\b(?:cannot|can't|can not|never|has no way to|is unable to)\b"
        r"[^.]{0,20}\b(?:read|see|open|decrypt|view)\w*\b",
        "the relay cannot read anything",
        "the relay is sealed, not omniscient: it reads no text, no cursor, no file name and no "
        "role, and it cannot forge, mis-attribute or replay a frame, but it still reads a room's "
        "existence, its membership, the display names and the sizes and timing of what moves, "
        "and it can drop, delay, reorder or refuse frames and end any room. 'It cannot read' or "
        "'it cannot read the room' without naming sealed material is the unqualified form, and "
        "naming the material is what makes the sentence specific: the sentence the hit sits in "
        "has to name what stays unread, in whatever order it puts the two",
        (
            "the server can't see anything",
            "the server cannot read",
            "the server cannot read the room",
            "the relay cannot read anything",
            "the relay cannot read the room",
            "the box cannot see who is in the room",
            "selvaged cannot read the room",
            "your server cannot read the room",
            "it cannot read the room",
            "the server has no way to read the room",
            "the server never sees your code",
            "the server cannot decrypt the room",
            "The server cannot see anything, not even your text.",
        ),
        (
            "The documents are sealed, so the server cannot read the text.",
            "The server cannot read a character of text.",
            "The server cannot read what a room is editing.",
            "The server cannot read the document payloads.",
            "The server cannot read the text.",
            "The server cannot read the file names.",
            "The server cannot read the room's listing.",
            "The server cannot read the roles the host signed.",
            "The box — and whoever holds it — carries bytes it cannot read.",
            "The server never reads the fragment, which a browser does not send.",
        ),
        (
            # What it cannot read, named in the same sentence: sealed material by name, or the
            # material the fragment carries, which a user agent never puts in a request. A
            # sentence naming none of them is the unqualified claim, whatever its subject is.
            r"\b(?:sealed|encrypted|ciphertext)\b"
            r"|\b(?:text|documents?|cursors?|file ?names?|roles?|listings?|bytes|contents?|"
            r"keystrokes?|characters?|lines?|words?|titles?|selections?|edits?|editing|"
            r"fragments?|invite link)\b",
        ),
        (
            # A permit reads the material the sentence names. `anything` is the object that
            # names none of it: "the server cannot see anything, not even your text" names text
            # and claims everything besides, which is the unqualified form.
            r"\b(?:anything|everything|nothing)\b",
        ),
    ),
    Phrase(
        # `CANONICAL.md` §6.1 puts `kind` in the clear — it is the AEAD's associated data — and
        # `PROTOCOL.md` §7.1 makes `kind = 1` the room state the host publishes, so a relay that
        # routes a room's frames reads one clear byte and knows which connection is the host. It
        # reads membership whether or not it reads anything else. Both readings are therefore
        # false, whatever else the sentence says about sealed material, which is why this phrase
        # has no permit: the host is a peer's signed claim, and `PROTOCOL.md` §1.2 puts what the
        # server cannot do the other way round — it seats nobody as anything, and the host is
        # whoever holds the private half of the key the invite's fragment names.
        r"\b(?:the\s+(?:server|relay|box|binary|instance|daemon)|selvaged|your\s+server|it)\b"
        r"[^.]{0,24}\b(?:cannot|can't|can not|never|has no way to|is unable to)\b"
        r"[^.]{0,16}\b(?:tell|know|learn|say)\b[^.]{0,12}\b(?:who|which)\b",
        "the server cannot tell who is in the room",
        "the relay reads the cleartext `kind` byte of every frame, and `kind = 1` is the room "
        "state the host publishes (`CANONICAL.md` §6.1, `PROTOCOL.md` §7.1), so it can tell "
        "which connection is the host; it reads membership besides. The role is a peer's signed "
        "claim and the page may say that: the server cannot seat a host, prove one, or take the "
        "role",
        (
            "the server cannot tell who is host",
            "the server cannot tell who the host is",
            "the server cannot tell who is in the room",
            "the server cannot know who is hosting the room",
            "the relay can't tell who is host",
            "the server cannot tell who is host or who is in the room",
        ),
        (
            "The host is a peer's signed claim: the server cannot seat a host, prove one, or take the role.",
            "The host is whoever holds the private half of the room's host key; the server seats nobody as anything.",
        ),
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
        "own validator pins (24 vectors, 33,760 frame checks, 8,387 assertions)",
    ),
    Phrase(
        r"\bfirst\b",
        "the first protocol to specify the session layer",
        "a claim of priority no source supports: the design record surveys prior art (Eclipse "
        "Open Collaboration Tools et al.), and the project's own claim is that the session layer "
        "is unspecified, not that this is first",
    ),
    Phrase(
        # The instance is live, so this entry no longer denies it; pointing at the demo is truth
        # and the page's own heading says so. What it holds is the overclaim that replaced the
        # denial: a demo described as a service. Its rooms are in memory on one small box, it
        # keeps no work, it is not promised to be up, and it is not sized for a team.
        r"\b(?:live|free) demo\b"
        r"|\bdemo\b[^.]{0,48}\b(?:always (?:up|on|available)|unlimited|persist\w*|stored"
        r"|backed up|production|guarantee\w*|reliab\w*|at scale|(?:your|a|our|the) team)\b"
        r"|\b(?:at scale|(?:your|a|our|the) team)\b[^.]{0,32}\bdemo\b",
        "try the free demo, it is always up and your rooms are saved",
        "the demo is one small box with in-memory rooms: a restart ends every one of them, it "
        "keeps no work, nothing promises it is up, and it is not sized for a team. The terms "
        "also gate it to personal and evaluation use, so the shape of a free tier of a service "
        "is a claim about a product that does not exist",
        (
            "the free demo never goes down",
            "the demo persists your rooms",
            "the demo is always available",
            "run your team's sessions on the demo",
        ),
        (
            "A demo instance runs at https://selvage-demo.dontblameme.dev.",
            "The demo's rooms live in memory: a restart ends every one of them.",
            "Rooms on the demo are not kept; run your own server for that.",
        ),
    ),
    Phrase(
        # The instance carries a non-commercial term and the software does not. The workspace
        # and clients are MIT OR Apache-2.0, `crates/selvaged` is FSL-1.1-MIT, and the
        # specification's prose, schema and vectors are CC-BY-4.0, so moving the instance's
        # term onto the software claims a licence nobody granted.
        r"\bnon-?commercial licen[cs]e\b"
        r"|\b(?:licen[cs]e|software|project|selvage|selvaged|workspace|clients?|source)\b"
        r"[^.]{0,12}\b(?:is|are|stays?|remains?|becomes?)\b[^.]{0,8}\bnon-?commercial\b",
        "the non-commercial licence covers the project",
        "the demo instance's terms are non-commercial and the software's licences are not: the "
        "workspace and the clients are MIT OR Apache-2.0, `crates/selvaged` is FSL-1.1-MIT, "
        "which reserves commercial hosting for its licensor, and the specification's prose, "
        "schema and vectors are CC-BY-4.0",
        (
            "Selvage is non-commercial software",
            "the project is non-commercial",
            "selvaged has a non-commercial licence",
        ),
        (
            "The demo instance is non-commercial and for personal and evaluation use.",
            "Those terms cover the demo's one box, not the software.",
        ),
    ),
    Phrase(
        # The hero's chip about the specification and this heading said opposite things to a
        # skimmer. What the page means is that the session layer is the part nobody writes
        # down — every collaborative tool decides it for itself — and this project writes it
        # down; a heading that reads as a denial of the page's own first fact is the
        # contradiction, whatever the section argues below it.
        r"\bsession layer\b[^.]{0,24}\b(?:has|with) no specification\b"
        r"|\bno specification\b[^.]{0,24}\bsession layer\b",
        "the session layer has no specification",
        "the page's own fact says the opposite: the session layer is written down as a "
        "specification, with JSON Schema and conformance vectors, and the section carries it. "
        "The layer every collaborative tool decides for itself is the subject; a heading that "
        "denies the specification contradicts what a skimmer has just read",
        ("the sess<!-- -->ion layer has no specification",),
        ("The session layer is written down", "The session layer has a specification"),
    ),
    Phrase(
        r"design[^.]{0,20}0\.x",
        "the design is at 0.x",
        "`PROTOCOL.md` §10 states the rule in force: `v` has one value, `selvage/2`, and a frame "
        "naming another is `bad_message`. No corpus "
        "line puts the design at 0.x; the compatibility clause names 0.x only for a future major "
        "0, which is not this one",
    ),
    Phrase(
        rf"(?<![\d,])\b(?!33,?760\b){VEHICLE}\s+frame[- ]checks?\b",
        "33759 frame checks",
        "the wire corpus's pinned number is 33,760 frame checks "
        "(`specification/schema/validate.py`); a different number is a claim the corpus "
        "disproves. The peer layer's 221 are checks and are pinned by that entry",
        clean=("33,760 frame checks", "33760 frame checks"),
    ),
    Phrase(
        # The wire corpus and the peer corpus are two layers of one corpus and each is counted
        # and pinned on its own (`EXPECTED_WIRE_VECTORS` and `EXPECTED_PEER_VECTORS`,
        # `EXPECTED_PEER_CHECKS`). One number pinned wherever the word sits would read the peer
        # layer's count as the wire layer's — `26 peer vectors` is the peer layer's pin, not a
        # wrong count — so the wire entries exclude the shape the peer entries pin, exactly:
        # `26 peer vectors`, never `26 peer-ish vectors`. The window is `\S+` rather than `\w+`
        # for that: a hyphenated word between the number and the noun is still a word in front
        # of it, and `26 peer-ish vectors` was a rewrite the `\w+` window passed.
        rf"\b(?!24\b)(?!26\s+peer\s+vectors?\b){VEHICLE}\s+(?:\S+\s+){{0,2}}vectors?\b",
        "23 conformance vectors",
        "the wire corpus's pinned number is 24 vectors (`specification/schema/validate.py`); a "
        "different number is a claim the corpus disproves, and the count is pinned wherever the "
        "word sits — the page writes both 'conformance vectors' and 'wire vectors'. The peer "
        "layer's own count is a separate pin and is written '26 peer vectors'; any other number "
        "before that noun is still a failure",
        clean=("24 conformance vectors", "the 24 wire vectors", "26 peer vectors"),
    ),
    Phrase(
        rf"(?<![\d,])\b(?!8,?387\b){VEHICLE}\s+assertions?\b",
        "8386 assertions",
        "the wire corpus's pinned number is 8,387 assertions "
        "(`specification/schema/validate.py`); a different number is a claim the corpus "
        "disproves. The peer layer's count is its own pin and is written '74 peer assertions'",
        clean=("8,387 assertions", "8387 assertions", "74 peer assertions"),
    ),
    Phrase(
        rf"\b(?!26\b){VEHICLE}\s+peer\s+vectors?\b",
        "27 peer vectors",
        "the peer corpus's pinned number is 26 vectors and 221 checks "
        "(`EXPECTED_PEER_VECTORS` and `EXPECTED_PEER_CHECKS` in "
        "`specification/schema/validate.py`, where the validator prints 'peer vectors 26 files, "
        "19 frame, 7 decision, 221 checks, 74 assertion steps'); a different number is a claim "
        "the corpus disproves. The layer has to be named: `26 vectors` is read as the wire "
        "layer's count and fails on that entry",
        ("27 peer ve<!-- -->ctors",),
        clean=("26 peer vectors",),
    ),
    Phrase(
        rf"\b(?!221\b){VEHICLE}\s+peer\s+checks?\b",
        "220 peer checks",
        "the peer corpus's pinned count is 221 checks (`EXPECTED_PEER_CHECKS` in "
        "`specification/schema/validate.py`); a different number is a claim the corpus "
        "disproves. The wire layer's 33,760 are frame checks and are pinned by that entry",
        clean=("221 peer checks",),
    ),
    Phrase(
        rf"\b(?!74\b){VEHICLE}\s+peer\s+assertions?\b",
        "75 peer assertions",
        "the peer corpus's pinned number is 74 assertion steps (`EXPECTED_PEER_ASSERTIONS` in "
        "`specification/schema/validate.py`); a different number is a claim the corpus "
        "disproves. The wire layer's 8,387 are pinned by that entry",
        clean=("74 peer assertions",),
    ),
    Phrase(
        r"third[- ]part[^.]{0,24}sees?\b|no third[- ]part[^.]{0,24}saw\b",
        "No third party ever sees the room.",
        "the relay is sealed, not omniscient: the server's operator and the network path still "
        "see the room's existence, its membership, the display names and the sizes and timing of "
        "what moves, and the link's holder can read the room itself. Only the page's own weak "
        "reading ('no third party's cloud holding the room') is backed",
        ("No third-party ever sees the room.",),
    ),
    Phrase(
        r"no cloud[^.]{0,24}between",
        "no cloud in between",
        "the relay is sealed, not omniscient: the server's operator and the network path still "
        "see the room's existence, its membership, the display names and the sizes and timing of "
        "what moves, and the link's holder can read the room itself. Only the page's "
        "own weak reading ('no third party's cloud holding the room') is backed",
        ("no clo<!-- -->ud in between", "no cloud <em>in</em> between",
         "no cloud &#105;n between"),
    ),
    Phrase(
        r"\bno[ -]clouds?\b",
        "no account, no database, no cloud",
        "only the weak reading is backed (no third party's cloud holding the room): "
        "a self-hosted server can itself run on a cloud VM, so a bare 'no cloud' "
        "overclaims. The backed storage sentence is 'nothing written to disk'",
        ("no clo<!-- -->ud", "no-cloud"),
    ),
    Phrase(
        r"proven in one room|across editors too|(?:VS ?Code|Neovim|Vim|Emacs|editors?)\b[^.]{0,48}\bon one end and\b",
        "Proven in one room with VS Code on one end and Neovim on the other.",
        "the first cross-editor session has run, and the design notes' hand-run proof of it "
        "(`selvage-protocol/ai_notes`, `docs/proof-cross-editor.md`, 2026-09-17) records grant, "
        "cursors and follow in both directions passing while the concurrent-edit step falls short "
        "by one trailing newline byte. So a pairing across the two editors is demonstrated and "
        "byte-identical replicas are not: state what the clients are built to do rather than that "
        "it is proven",
        ("with VS Code on one end and Neovim on the other.",
         "with VS Code on one\nend and Neovim on the other."),
    ),
    Phrase(
        r"\binstant\b|\breal[- ]time\b|\blag[- ]free\b|\blightning[- ]fast\b|snappy",
        "Sessions feel instant, even on large projects.",
        "no performance data exists anywhere in the corpus: no speed, latency or fluency "
        "adjective is backed",
    ),
    Phrase(
        r"\b(?:self[- ]host(?:ing)?|setup|install(?:ation)?|deploy(?:ment)?)\b[^.]{0,24}\btakes? seconds\b"
        r"|(?:up(?: and running)?|ready|deploys?|installs?|setup|self[- ]hosts?)\b[^.]{0,24}\bin seconds\b(?!-)"
        r"|(?:server|selvaged|setup|install\w*|deploy\w*|build|app|site|page|service)\b[^.]{0,32}\b(?:starts?|runs?|boots?)\b[^.]{0,24}\bin seconds\b(?!-)"
        r"|one[- ]click|just works",
        "Self-hosting takes seconds on any machine you choose.",
        "the image, the compose file and the systemd unit all exist, and no ease claim around "
        "them is backed: no install time, start-up time or latency has been measured or "
        "recorded anywhere in the corpus",
        ("up and running in seconds.",
         "up and running in\nseconds.",
         "the server starts in seconds."),
        ("The countdown starts in seconds, then changes to minutes.",
         "The server starts in seconds-hand mode.",
         "The timeout runs in seconds.",
         "The render runs in seconds on this GPU.",
         "The editor starts a search in seconds."),
    ),
    Phrase(
        r"untouched by the network|\bonly machine\b[^.]{0,24}\b(?:your code|touches?)\b",
        "The machine you chose is the only machine your code touches.",
        "document payloads travel through the server to the peers that ask for them; the grant "
        "bounds which paths are listed and served, not which machines code touches",
        ("the only machine your code touches.",
         "the only machine your <em>code</em> touches."),
    ),
    Phrase(
        r"\bis live\b|\bnow live\b|\bnow available\b",
        "Selvage Session Protocol is now live.",
        "the image is published and pulls with no account, and one small demo instance runs. "
        "There is no hosted service and nothing was launched: a status reading 'live' or 'now "
        "available' sells the demo as a product. The honest status line names the release and "
        "the specification draft",
    ),
    Phrase(
        # The specification is a draft, and the phrase list already forbids selling the demo with a
        # `live` status; this is the same completion claim made of the protocol itself. The `1.0`
        # entry above catches a version claim, but `finished`, `released` and `stable` are titles
        # the draft has not reached, and a page could carry one with nothing else to say so.
        #
        # The copula is required between the subject and the word, and a `not` may not sit
        # between them, so an honest sentence — "the specification is a draft", "the specification
        # is not stable" — stays clean while a claim of completion does not. `released` is about
        # the protocol's own status and not about a release of an artefact, which the page states
        # elsewhere.
        r"\b(?:specification|protocol|session (?:layer|protocol))\b[^.]{0,32}"
        r"\b(?:is|are|was|were|has been|have been)\b(?:(?!\bnot\b)[^.]){0,12}"
        r"\b(?:finished|done|complete[d]?|finali[sz]ed|final|frozen|released|shipped|ratified|stable)\b",
        "The specification is finished.",
        (
            "the specification is a draft: the wire version is `selvage/2`, no shape is frozen and "
            "the corpus is still growing, so a page that calls the specification finished, released "
            "or stable claims a status the project has not reached"
        ),
        (
            "the specifi<!-- -->cation is finished",
            "The protocol has been released.",
        ),
        (
            "The specification is a draft.",
            "The specification is not stable.",
            "The release publishes the extension under `selvage-protocol.selvage`.",
            "The protocol is written down as a specification.",
        ),
    ),
    Phrase(
        r"\bsign[ -]?in\b|\bsign[ -]?up\b|\bget started\b|\bdownload\b|\bpricing\b",
        "Sign in to get started, then download the app.",
        "no accounts exist, so nothing can be signed into; no package exists to download and "
        "no price exists to show. The page offers the specification to read and a server to run",
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


# Tags whose rendering separates text: a phrase ending one block and starting the next is two
# phrases, not one written across a boundary. Anything else inline — spans, links, comments —
# renders nothing between its neighbours, so removing it must join them rather than split them.
# That join holds even for the line breaks inside the markup: a comment holding a newline still
# renders nothing, so the sides meet with no space. Reported hits still name source lines,
# because every visible character keeps the number of the line it came from.
BLOCK_TAGS = frozenset(
    "address article aside blockquote br dd details div dl dt fieldset figcaption figure"
    " footer form h1 h2 h3 h4 h5 h6 header hr li main nav ol p pre section table td th tr ul".split()
)


def _tag_end(text: str, start: int) -> int:
    """Index of the `>` closing the tag at `start`, or -1.

    Quote-aware: a `>` inside a single- or double-quoted attribute value does not end the tag,
    so `<span title=">">` is one tag rather than two fragments with `"` left over as prose.
    """
    quote = ""
    for i in range(start + 1, len(text)):
        char = text[i]
        if quote:
            if char == quote:
                quote = ""
        elif char in ("'", '"'):
            quote = char
        elif char == ">":
            return i
    return -1


def _element_end(text: str, tag_name: str, start: int) -> int:
    """Index just past the closing tag of the element opened before `start`, or -1.

    Only a real closer counts: the name must end at whitespace, `/` or `>`, so `</scripts>`
    does not close a `script` element. A closer whose `>` is never found is skipped rather
    than trusted.
    """
    pattern = re.compile(r"</\s*" + tag_name + r"(?=[\s>/])", re.IGNORECASE)
    pos = start
    while True:
        found = pattern.search(text, pos)
        if found is None:
            return -1
        end = _tag_end(text, found.start())
        if end != -1:
            return end + 1
        pos = found.start() + 1


def _visible(text: str) -> tuple[list[str], list[int], list[bool]]:
    """The page's visible characters, each with its source line.

    Tags and comments are skipped, so they contribute no text and no spacing — not even the
    line breaks inside them, which only advance the line count. A `script` or `style` element
    is skipped whole, closer included: the rendered page carries its framework runtime in
    `script` blocks, whose bytes would otherwise scan as prose. A `<` with no closing `>` is
    prose rather than markup and is kept. The third list marks each character that starts a
    fresh source line after a real line break, so joining can tell a wrap (a space, the way
    the browser collapses it) from markup that rendered nothing (no space).
    """
    chars: list[str] = []
    lines: list[int] = []
    fresh: list[bool] = []
    line = 1
    at_break = True
    i = 0
    while i < len(text):
        if text.startswith("<!--", i):
            end = text.find("-->", i + 4)
            skipped = text[i + 4 :] if end == -1 else text[i : end + 3]
            line += skipped.count("\n")
            i = len(text) if end == -1 else end + 3
            continue
        if text[i] == "<":
            end = _tag_end(text, i)
            if end == -1:
                chars.append("<")
                lines.append(line)
                fresh.append(at_break)
                at_break = False
                i += 1
                continue
            tag = text[i : end + 1]
            name = re.match(r"</?\s*([a-zA-Z][a-zA-Z0-9]*)", tag)
            tag_name = name.group(1).lower() if name is not None else ""
            if (
                tag_name in ("script", "style")
                and re.match(r"<\s*/", tag) is None
                and re.search(r"/\s*>$", tag) is None
            ):
                close = _element_end(text, tag_name, end + 1)
                if close != -1:
                    line += text.count("\n", i, close)
                    i = close
                    continue
            if tag_name in BLOCK_TAGS:
                # A block boundary is a text boundary; the space keeps the two sides apart
                # the way a line break in the source does.
                chars.append(" ")
                lines.append(line)
                fresh.append(at_break)
                at_break = False
            line += tag.count("\n")
            i = end + 1
            continue
        if text[i] in ("\r", "\n"):
            if text[i] == "\r" and text.startswith("\r\n", i):
                i += 1
            line += 1
            at_break = True
            i += 1
            continue
        chars.append(text[i])
        lines.append(line)
        fresh.append(at_break)
        at_break = False
        i += 1
    return chars, lines, fresh


def destinations(raw: str) -> list[tuple[str, int]]:
    """Every URL-bearing attribute the raw page carries, with the line each sits on.

    The visible text keeps a link's label and drops its destination, so this is the other half of
    what the page tells a reader. Values are unescaped the way the text is, so an `&amp;` is not a
    different URL; the line is the one the tag is on.
    """
    found: list[tuple[str, int]] = []
    for match in DESTINATION.finditer(raw):
        value = match.group(1) if match.group(1) is not None else match.group(2)
        if value:
            found.append((html.unescape(value), raw.count("\n", 0, match.start()) + 1))
    return found


def normalise(text: str) -> tuple[str, list[int]]:
    """The page's visible text, with the source line of every character.

    Comments, tags, scripts and styles are not rendered, so they are not claims: tags and
    comments are removed, and `script`/`style` elements are skipped whole — the rendered page
    carries its framework runtime in `script` blocks, whose bytes would otherwise scan as
    prose. Entities are
    decoded after the tags are gone, so an escaped angle bracket in the prose is not mistaken for
    a tag. Dashes are flattened and whitespace collapsed, because a phrase split across the
    page's ~90-column wrapping is not absent — it is the same phrase with a line break in it.
    A line break inside removed markup collapses differently: the markup rendered nothing, so
    its sides join with no space.
    """
    chars, lines, fresh = _visible(text)
    visible: list[str] = []
    line_of: list[int] = []
    word: list[str] = []
    word_line: list[int] = []

    def flush() -> None:
        segment = html.unescape("".join(word))
        segment = DASHES.sub("-", segment)
        segment = re.sub(r"\s+", " ", segment).strip()
        if segment:
            if visible:
                visible.append(" ")
                line_of.append(word_line[0])
            for char in segment:
                visible.append(char)
                line_of.append(word_line[0])
        word.clear()
        word_line.clear()

    for char, number, starts in zip(chars, lines, fresh):
        if char.isspace():
            if word and not word[-1].isspace():
                word.append(" ")
                word_line.append(number)
            continue
        if starts and word:
            flush()
        word.append(char)
        word_line.append(number)
    flush()
    if visible:
        visible.append(" ")
        line_of.append(line_of[-1])
    return "".join(visible), line_of


# How far either side of a hit a permit may sit before it stops being part of the same claim. The
# sentence is the bound; this only keeps a sentence with no full stop in it from becoming the whole
# page.
CLAUSE_WINDOW = 120


def clause_around(text: str, start: int, end: int) -> str:
    """The sentence a hit sits in, clipped to a window either side of it.

    A claim and the material it is about are written in one sentence; an exemption read from
    anywhere on the page is the one the review reproduced, where a paragraph 180 lines away
    supplied the fact. Clipping matters only for text that carries no full stop at all.
    """
    left = max(text.rfind(".", 0, start) + 1, start - CLAUSE_WINDOW)
    stop = text.find(".", end)
    right = len(text) if stop == -1 else min(stop + 1, end + CLAUSE_WINDOW)
    return text[left:right]


def hits(
    pattern: re.Pattern[str],
    permits: list[re.Pattern[str]],
    text: str,
    voiding: tuple[re.Pattern[str], ...] = (),
) -> list[re.Match[str]]:
    """Every match that is a hit: the pattern matched and no permit that stands matched its
    sentence.

    A phrase with no permits is its own matches, so this is the only path a hit takes. A permit
    that matched is not enough on its own: a `voiding` pattern cancels it when the sentence
    denies the material the permit names, which is a sentence the permit was never meant to
    rescue.
    """
    if not permits:
        return list(pattern.finditer(text))
    found: list[re.Match[str]] = []
    for match in pattern.finditer(text):
        clause = clause_around(text, match.start(), match.end())
        if any(void.search(clause) for void in voiding) or not any(
            permit.search(clause) for permit in permits
        ):
            found.append(match)
    return found


def meta_streams(raw: str) -> list[tuple[str, list[int]]]:
    """The prose a page carries in its `meta` attributes, normalised, with its source line.

    Each `content` is normalised on its own, because it is its own text: a sentence there is not a
    continuation of the body's prose, and joining the two would invent a phrase neither carries.
    The line is the tag's, which is where somebody reading the source finds it.
    """
    found: list[tuple[str, list[int]]] = []
    for tag in META_ELEMENT.finditer(raw):
        element = tag.group(0)
        key = META_KEY.search(element)
        if key is None:
            continue
        name = (key.group(1) or key.group(2) or "").lower()
        if name not in META_PROSE_KEYS and not name.startswith(META_PROSE_PREFIXES):
            continue
        content = META_CONTENT.search(element)
        if content is None:
            continue
        text, _ = normalise(html.unescape(content.group(1) or content.group(2) or ""))
        if text:
            line = raw.count("\n", 0, tag.start()) + 1
            found.append((text, [line] * len(text)))
    return found


def _registry_json(path: str, token: str | None = None) -> dict:
    request = urllib.request.Request(f"https://{REGISTRY_HOST}/v2/{path}")
    request.add_header("Accept", ", ".join(MANIFEST_TYPES))
    if token is not None:
        request.add_header("Authorization", f"Bearer {token}")
    with urllib.request.urlopen(request, timeout=REQUEST_TIMEOUT_SECONDS) as response:
        return json.loads(response.read())


def anonymous_pull_token() -> str:
    """The token a `docker pull` gets with no credentials: ghcr mints one to a bare GET."""
    with urllib.request.urlopen(
        f"https://{REGISTRY_HOST}/token?scope=repository:{REGISTRY_REPOSITORY}:pull"
        f"&service={REGISTRY_HOST}",
        timeout=REQUEST_TIMEOUT_SECONDS,
    ) as response:
        return json.loads(response.read())["token"]


def published_tag_legs() -> dict[str, tuple[str, ...]]:
    """{platform: layer digests} for the tag the page hands a reader, from the per-platform
    manifests.

    The tag's own document is an index that points at those; the layers live in the manifests
    it names, which is why the index alone cannot answer what this asks. Attestation entries
    carry `platform: unknown/unknown` and are skipped by the `os` filter.
    """
    token = anonymous_pull_token()
    index = _registry_json(f"{REGISTRY_REPOSITORY}/manifests/{PUBLISHED_IMAGE_TAG}", token)
    legs: dict[str, tuple[str, ...]] = {}
    for entry in index.get("manifests", []):
        platform = entry.get("platform", {})
        if platform.get("os") != "linux":
            continue
        manifest = _registry_json(f"{REGISTRY_REPOSITORY}/manifests/{entry['digest']}", token)
        layers = tuple(layer["digest"] for layer in manifest.get("layers", []))
        if layers:
            legs[f"linux/{platform.get('architecture')}"] = layers
    return legs


def check_published_image(pages: list[Scanned]) -> int:
    """The page's tag against the tag it may hand a reader, and that tag against the registry.

    Returns 0 when both hold, 1 when either does not, 2 when the registry cannot be asked.
    """
    root = root_of_this_checkout()
    reference = f"{PUBLISHED_IMAGE}:{PUBLISHED_IMAGE_TAG}"
    named = 0
    wrong: list[str] = []
    for page in pages:
        for match in IMAGE_REFERENCE.finditer(page.text):
            named += 1
            if match.group(0) != reference:
                where = os.path.relpath(page.path, root)
                wrong.append(f"{where}:{page.line_of[match.start()]}: {match.group(0)!r}")
    if not named:
        print(
            f"check-claims: none of {len(pages)} scanned file(s) carries a {PUBLISHED_IMAGE} "
            f"reference, and the tag the page may hand a reader is {reference!r}: the page's "
            "happy path is where it is handed over, so a scan that never reaches it is not "
            "checking the tag",
            file=sys.stderr,
        )
        return 1
    if wrong:
        for where in wrong:
            print(
                f"check-claims: the page hands a reader {where}, and the image it may name is "
                f"{reference!r}",
                file=sys.stderr,
            )
        return 1

    try:
        legs = published_tag_legs()
    except (urllib.error.URLError, OSError, ValueError, KeyError) as error:
        print(
            f"check-claims: cannot ask {REGISTRY_HOST} for {reference} ({error}); the tag "
            "cannot be checked against the artefact it names, so this is a failure rather "
            "than a pass",
            file=sys.stderr,
        )
        return 2

    absent = sorted({"linux/amd64", "linux/arm64"} - set(legs))
    if absent:
        print(
            f"check-claims: {reference} carries no manifest for {' or '.join(absent)}; the "
            "image commands the page hands a reader have to run on the machine they run it on",
            file=sys.stderr,
        )
        return 1
    amd64, arm64 = legs["linux/amd64"], legs["linux/arm64"]
    if amd64 == arm64:
        print(
            f"check-claims: the amd64 and arm64 manifests of {reference} carry identical "
            f"layers ({' '.join(amd64)}). A platform entry only labels a slot: an arm64 leg "
            "holding the other architecture's binary is the defect this asserts against",
            file=sys.stderr,
        )
        return 1
    print(
        f"check-claims: the published image {reference} pulls anonymously and is not one "
        f"binary twice — amd64 {' '.join(amd64)}, arm64 {' '.join(arm64)}"
    )
    return 0



def demo_host_of(reference: str) -> str:
    """The host of a URL, with any userinfo, port and path dropped; "" for one that names none.

    A destination can be relative (`#get-it-working`), which is this page and not the instance,
    so it answers with no host rather than failing.
    """
    if "://" not in reference:
        return ""
    authority = reference.split("://", 1)[1].split("/", 1)[0]
    return authority.rsplit("@", 1)[-1].split(":", 1)[0].lower()


# `/meta`, asked once per run however many checks read it. Two requests to a live box can answer
# differently, and a run whose halves disagree with each other checks nothing.
_META: list[tuple[str, tuple[str, ...]]] = []


def demo_meta() -> tuple[str, tuple[str, ...]]:
    """What the instance reports about itself from `/meta`: its name, and its wire versions.

    The request names itself rather than going out as the interpreter's default signature: the
    host is behind Cloudflare, whose bot list answers `403` (error 1010) to `Python-urllib`, and
    a check that cannot read the instance cannot assert anything about it.
    """
    if _META:
        return _META[0]
    request = urllib.request.Request(f"{DEMO_ORIGIN}/meta")
    request.add_header("Accept", "application/json")
    request.add_header("User-Agent", USER_AGENT)
    with urllib.request.urlopen(request, timeout=REQUEST_TIMEOUT_SECONDS) as response:
        body = json.loads(response.read())
    name = body["server"]
    if not isinstance(name, str) or not name:
        raise ValueError(f"/meta carried no usable `server` name ({name!r})")
    offered = body["wire_versions"]
    if not isinstance(offered, list) or not offered:
        raise ValueError(f"/meta carried no usable `wire_versions` ({offered!r})")
    if not all(isinstance(one, str) and one for one in offered):
        raise ValueError(f"/meta carried a wire version that is not a name ({offered!r})")
    _META.append((name, tuple(offered)))
    return _META[0]


def demo_session_route() -> tuple[int, str]:
    """What answers the instance's session path, as the status and media type of a plain GET.

    The page hands a reader a server address and the clients append `SESSION_PATH` to it, so the
    address is worth a sentence only if that path reaches the server. A plain GET is the request
    this check can make: a hand-rolled WebSocket upgrade from a runner's egress is answered `403`
    by the host's proxy, and a request the proxy refuses asserts nothing about the server. What
    answers the path is the assertion instead, and `session_path_reaches_the_server` is what
    decides it.
    """
    request = urllib.request.Request(f"{DEMO_ORIGIN}{SESSION_PATH}")
    request.add_header("User-Agent", USER_AGENT)
    try:
        with urllib.request.urlopen(request, timeout=REQUEST_TIMEOUT_SECONDS) as response:
            return response.status, response.headers.get_content_type()
    except urllib.error.HTTPError as error:
        return error.code, error.headers.get_content_type() if error.headers else ""


def session_path_reaches_the_server(status: int, media_type: str) -> bool:
    """Whether an answer to a plain GET on the session path came from the server.

    The server refuses a request that asks for no upgrade with its own JSON, so a **4xx JSON**
    answer is the server answering that path. Everything else is another conversation: a redirect
    or a 2xx (something else serving the path, `urlopen` having followed a redirect to it), a 5xx
    (the server failing rather than refusing), and a body that is not the server's JSON (the
    proxy's own page, which is `text/html`).

    Which 4xx the server chooses is its own business and not a sentence this page makes: pinning
    `404` would redden the site's gate for a change in `selvaged` that makes no claim on the page
    false, which is the coupling this file refuses elsewhere in the demo half.
    """
    return 400 <= status <= 499 and media_type == "application/json"


def demo_page_route() -> tuple[int, str, str]:
    """What the instance answers `/` with: its status, its media type, and the bytes it serves.

    The status is asked for as well as the media type, because the proxy's own `404` page is
    `text/html` too: a `/` that serves the guest page is a `200`, and anything else is that origin
    not serving it. The body comes back with them because one sentence on the page is about what
    the served bundle can do, and only the bytes say which bundle it is.
    """
    request = urllib.request.Request(f"{DEMO_ORIGIN}/")
    request.add_header("User-Agent", USER_AGENT)
    try:
        with urllib.request.urlopen(request, timeout=REQUEST_TIMEOUT_SECONDS) as response:
            return (
                response.status,
                response.headers.get_content_type(),
                response.read().decode("utf-8", "replace"),
            )
    except urllib.error.HTTPError as error:
        body = error.read().decode("utf-8", "replace") if error.headers else ""
        return error.code, error.headers.get_content_type() if error.headers else "", body


def demo_reference_allowed(reference: str) -> bool:
    """Whether the page may carry this reference to the instance.

    A trailing slash is the same URL to a browser, so it is the same reference here.
    """
    return any(reference.rstrip("/") == one.rstrip("/") for one in DEMO_REFERENCES)


def demo_references(page: Scanned) -> list[tuple[str, int]]:
    """Every reference to the demo host the page carries, in text and in attributes.

    The visible text is where a phrase claim lives, and an attribute is where a link's
    destination lives; both are scanned, because a label and the place it goes are two claims.
    """
    found: list[tuple[str, int]] = []
    for match in DEMO_URL.finditer(page.text):
        # The sentence's own punctuation ends the match: `wss://host;` is the reference with a
        # semicolon after it, not a reference with a semicolon in it.
        reference = match.group(0).rstrip(".,;:!?")
        if demo_host_of(reference) == DEMO_HOST:
            found.append((reference, page.line_of[match.start()]))
    for destination, line in page.destinations:
        if demo_host_of(destination) == DEMO_HOST:
            found.append((destination, line))
    return found


def check_demo_instance(pages: list[Scanned]) -> int:
    """The page's demo references against the host they name, and the host against the sentences.

    Returns 0 when they hold, 1 when a sentence the page carries is disproved, 2 when the
    instance cannot be asked.
    """
    root = root_of_this_checkout()
    followed = 0
    wrong: list[tuple[str, str, int]] = []
    for page in pages:
        where = os.path.relpath(page.path, root)
        for reference, line in demo_references(page):
            if demo_reference_allowed(reference):
                followed += 1
            else:
                wrong.append((where, reference, line))
    if not followed:
        print(
            f"check-claims: none of {len(pages)} scanned file(s) points at {DEMO_HOST!r}, and "
            "the instance is what this check asserts: a scan that never reaches the demo is not "
            "checking it",
            file=sys.stderr,
        )
        return 1
    if wrong:
        for where, reference, line in wrong:
            print(
                f"check-claims: the page points a reader at {where}:{line}: {reference!r}, and "
                f"the demo references are {', '.join(repr(one) for one in DEMO_REFERENCES)}",
                file=sys.stderr,
            )
        return 1
    if not any(
        destination.rstrip("/") == DEMO_ORIGIN
        for page in pages
        for destination, _ in page.destinations
    ):
        print(
            f"check-claims: no link on the page has a destination at {DEMO_ORIGIN}; the section "
            "points a reader at the instance, so the host its text names with nowhere to follow "
            "is the claim without the thing that makes it usable",
            file=sys.stderr,
        )
        return 1

    try:
        reported, offered = demo_meta()
        session_status, session_type = demo_session_route()
        page_status, media_type, page_body = demo_page_route()
    except urllib.error.HTTPError as error:
        answer = error.read(200).decode("utf-8", "replace").strip()
        print(
            f"check-claims: {DEMO_ORIGIN} answered {error.code} {error.reason} "
            f"({answer[:160]!r}); the instance the page points at is not answering the check, "
            "and a name nothing can read is a name nothing can confirm",
            file=sys.stderr,
        )
        return 2
    except (urllib.error.URLError, OSError, ValueError, KeyError) as error:
        print(
            f"check-claims: cannot ask {DEMO_ORIGIN} what it is serving ({error}); "
            "the sentences the page carries about the instance cannot be checked against the "
            "instance itself, so this is a failure rather than a pass",
            file=sys.stderr,
        )
        return 2

    if not SERVER_NAME.match(reported):
        print(
            f"check-claims: {DEMO_ORIGIN}/meta reports {reported!r} and the page says an "
            f"instance of the server runs there; the server the page's own `docker run` pulls "
            f"is {PUBLISHED_IMAGE.rsplit('/', 1)[-1]}, so this is a different thing answering "
            "on that host",
            file=sys.stderr,
        )
        return 1

    if not session_path_reaches_the_server(session_status, session_type):
        print(
            f"check-claims: {DEMO_ORIGIN}{SESSION_PATH} answered {session_status} "
            f"{session_type!r}, and the page hands a reader {DEMO_REFERENCES[-1]!r} as the "
            f"address to give an editor: the clients append {SESSION_PATH} to that address, so "
            "the server has to answer that path with a refusal of its own, and a redirect, a "
            "5xx or the proxy's page is something else answering it",
            file=sys.stderr,
        )
        return 1

    if page_status != 200 or media_type != "text/html":
        print(
            f"check-claims: {DEMO_ORIGIN}/ answers {page_status} {media_type!r}, and the browser "
            "row tells a guest the demo serves the page: a guest following an invite link there "
            "needs the page, and the proxy's own 404 is text/html as well, so a status that is "
            "not 200 is that origin not serving it",
            file=sys.stderr,
        )
        return 1

    if not HOST_CARD.search(page_body):
        print(
            f"check-claims: {DEMO_ORIGIN}/ serves a page whose shell carries no host card, and "
            "the browser row says Chrome or Edge can start a session from the demo's page: the "
            "card is what a bundle that can start one carries in its markup, so the bundle the "
            "instance serves is one that cannot",
            file=sys.stderr,
        )
        return 1

    print(
        f"check-claims: the demo instance {DEMO_ORIGIN} answers, reports {reported!r} offering "
        f"{', '.join(offered)}, answers {SESSION_PATH} with the server's own JSON "
        f"({session_status}), and serves a page whose shell carries the host card"
    )
    return 0


def disclosure_region(page: Scanned) -> str:
    """The page from its own `docker run` on: the text the relay's disclosure is read from.

    The paragraph sits under the packed command because a reader can take the claim and the
    command together, which is also what tells the paragraph apart from the hero. The hero used to
    state the same four facts above the command: reading the whole page let a hero line satisfy a
    check written to require the paragraph, and deleting the paragraph then passed. What is read is
    the page from its image's own reference onwards, so the hero cannot stand in for it —
    its chips name the same properties in a word each, and a hero line that states a fact in full
    would be the same defect again. Returns "" when the page carries no such reference, which the
    image half also fails on; this one names the absence rather than reporting four missing facts.
    """
    match = IMAGE_REFERENCE.search(page.text)
    return page.text[match.start():] if match else ""


def first_page_stating(
    pages: list[Scanned], facts, region_of=None
) -> tuple[Scanned | None, list[tuple[str, list[str]]]]:
    """The first page that states every fact, and every page's missing ones.

    A disclosure is required, not permitted: a `clean` fixture proves a pattern does not reject a
    sentence, never that the page carries one. What is required is the facts, one pattern each, so
    a rewritten paragraph that keeps them passes and one that drops a fact fails. `region_of`
    bounds where they may be read, for the one whose place is part of the claim (see
    `disclosure_region`); the default reads the whole page.
    """
    root = root_of_this_checkout()
    failures: list[tuple[str, list[str]]] = []
    for page in pages:
        text = page.text if region_of is None else region_of(page)
        absent = [label for label, pattern in facts if not pattern.search(text)]
        if not absent:
            return page, []
        failures.append((os.path.relpath(page.path, root), absent))
    return None, failures


def check_relay_disclosure(pages: list[Scanned]) -> int:
    """The page's statement of what the sealed relay still sees, required rather than permitted.

    The facts are the panel's, and they are read from the visible text: a fact stated only in
    a link unfurl is not on the page a reader reads. Each fact has a pattern of its own, so a
    rewritten panel that keeps them passes and one that drops a fact fails. Two of the four
    are read as the panel's own wording rather than as a bare subject and verb, because the page
    states the same two nouns a second time in *The session layer is written down*, about what
    every collaborative tool decides for itself; matched loosely that paragraph supplied them for
    a page whose statement had been deleted, and a rewrite that dropped those two while keeping
    "their names" and "sizes and timing" passed with them gone. The region is the page from the
    `docker run` that pulls the page's image onwards: the panel's place under that command is
    part of the claim, the chips and the heading over them state the facts a line at a time, and a
    hero line above the command is not where a reader is owed them. Returns 0 when a
    scanned page carries all four below its own command and 1 when none does; it asks no network.
    """
    if not any(IMAGE_REFERENCE.search(page.text) for page in pages):
        print(
            f"check-claims: none of {len(pages)} scanned file(s) carries a {PUBLISHED_IMAGE} "
            "reference, and what the relay still sees is read from the page's own `docker run` "
            "onwards: without that command the panel has nowhere its place puts it",
            file=sys.stderr,
        )
        return 1
    page, failures = first_page_stating(pages, RELAY_DISCLOSURE, disclosure_region)
    if page is not None:
        print(
            "check-claims: the page states what the sealed relay still sees — the room's "
            "existence, its membership, the display names and the sizes and timing of "
            "what moves"
        )
        return 0
    for where, absent in failures:
        print(
            f"check-claims: {where} does not state what the sealed relay still sees: it is "
            f"missing {', '.join(absent)}. That statement is read from the page's own "
            "`docker run` onwards, which is where the panel sits and where a hero line above "
            "the command does not reach, so a page that drops a fact from the panel claims more "
            "than the relay does",
            file=sys.stderr,
        )
    return 1


def check_fsl_disclosure(pages: list[Scanned]) -> int:
    """The server's licence disclosure, required rather than permitted.

    The page owes a reader of `selvaged` the terms it is under, and a phrase list can only forbid
    the false wording (`open source`): it can never require the true one. So each part of the
    disclosure is a required fact of its own, read from the page's visible text, and a rewrite
    that keeps the facts passes while a page that drops or contradicts one fails. The parts are
    the `FSL-1.1-MIT` identifier beside `selvaged`, source-available, not OSI-approved, free for
    non-competing use, and the conversion to MIT two years after each release.

    Returns 0 when a scanned page states every part and 1 when none does; it asks no network.
    """
    page, failures = first_page_stating(pages, FSL_DISCLOSURE)
    if page is not None:
        print(
            "check-claims: the page discloses the server's licence — `selvaged` is FSL-1.1-MIT: "
            "source-available, not OSI-approved, free for non-competing use, and MIT two years "
            "after each release"
        )
        return 0
    for where, absent in failures:
        print(
            f"check-claims: {where} does not disclose the server's licence: it is missing "
            f"{', '.join(absent)}. A reader is owed the terms `selvaged` is under, and a page "
            "that states some of them reads as if it stated all",
            file=sys.stderr,
        )
    return 1


def window_with_following_sentence(text: str, start: int, end: int) -> str:
    """The sentence a hit sits in and the one after it, from the visible text.

    A citation is read from where the number is: the page's own frame-count sentence names the
    counts and the sentence after it names the validator that prints them, which is the pair a
    reader reads together. A file named a section away is not what the number is checked against,
    so the window stops at the end of the following sentence — and a sentence ends at a period
    followed by whitespace, not at any period (see `SENTENCE_END`).
    """
    left = 0
    for stop in SENTENCE_END.finditer(text, 0, start):
        left = stop.end()
    ends = list(SENTENCE_END.finditer(text, end))
    right = len(text) if len(ends) < 2 else ends[1].end()
    return text[left:right]


def check_corpus_citation(pages: list[Scanned]) -> int:
    """The page's corpus names the file that prints its counts, and any count it shows does too.

    The page states no count: the corpus grows, and a number written into the page is stale as soon
    as it moves. What it hands a reader instead is the file, so the file is what is required, beside
    the corpus it counts: the window is the corpus's own sentence and the one after it (see
    `window_with_following_sentence`), and a scan that reaches no cited corpus fails rather than
    reporting a page that has stopped pointing anywhere as a page with nothing wrong.

    A count that does reach a page is held to the same window around the number, and every count
    in every scanned page is read: a check that returned on the first cited page would let a later
    page carry an uncited number, and one that returned on the first count would do the same within
    a page. Whether a count is the right one is the phrase list's business, which pins each of them.
    """
    root = root_of_this_checkout()
    cited = 0
    shown = 0
    uncited: list[tuple[str, str]] = []
    for page in pages:
        where = os.path.relpath(page.path, root)
        for match in CORPUS_MENTION.finditer(page.text):
            window = window_with_following_sentence(page.text, match.start(), match.end())
            if CORPUS_FILE.search(window):
                cited += 1
        for pattern, label in CORPUS_COUNTS:
            for match in pattern.finditer(page.text):
                shown += 1
                window = window_with_following_sentence(page.text, match.start(), match.end())
                if not CORPUS_FILE.search(window):
                    uncited.append((where, label))
    if cited == 0:
        print(
            f"check-claims: none of {len(pages)} scanned file(s) names {CORPUS_FILE.pattern} in "
            "the sentence that mentions the conformance vectors or the one after it. The page "
            "states no count, so that file is where a reader checks the corpus, and a rewrite that "
            "drops it leaves the corpus with nowhere to check it",
            file=sys.stderr,
        )
        return 1
    if not uncited:
        print(
            f"check-claims: the corpus is cited to {CORPUS_FILE.pattern} {cited} time(s), and all "
            f"{shown} corpus count(s) the scanned page(s) show name it beside them"
        )
        return 0
    for where, label in uncited:
        print(
            f"check-claims: {where} shows {label} with no file named in the sentence the number "
            "sits in or the one after it. Every count comes from a constant in "
            "`specification/schema/validate.py`, and a number with nowhere to check it is one a "
            "reader has to take on trust",
            file=sys.stderr,
        )
    return 1


def check_published_extension(pages: list[Scanned]) -> int:
    """The page's install row against the identity and the registries the release publishes to.

    Required rather than permitted, for the reason the disclosure is: a `clean` fixture proves a
    pattern does not reject a sentence, never that the page carries one, and this page could keep
    every fixture green while saying nothing about where the extension is installed from. Three
    things are asked of the scanned page:

    - the identity the release publishes under and both registries it publishes to, in the
      visible text — a reader installs from one of them, so a row that names neither is not an
      install row;
    - that every registry-shaped word on the page is part of one of those two names, so a page
      offering the extension from somewhere else — "the extension gallery", the JetBrains or
      Eclipse marketplace, another editor's store — fails rather than passing on the two names
      it also carries;
    - that any link the page does carry to a listing is one of the two, so a link to the retired
      ID's listing fails on the destination rather than on the label.

    What it does not do is ask the galleries. A listing is the release's fact — the two publish
    steps in `vscode_client/.github/workflows/release.yml` are what produce it — and a query here
    would redden the site's gate for a release that has not been dispatched yet, which is the
    ordering the release plan is the place for. The residual is stated rather than hidden: this
    proves the page agrees with the release workflow about the identity and the registries, not
    that either registry answers.

    Returns 0 when all of it holds and 1 when it does not; it asks no network.
    """
    root = root_of_this_checkout()
    page, failures = first_page_stating(pages, EXTENSION_PUBLICATION)
    if page is None:
        for where, absent in failures:
            print(
                f"check-claims: {where} does not say where the extension is published: it is "
                f"missing {', '.join(absent)}. The VS Code row is where a reader is handed an "
                "install, and a row that names a registry without saying what an install is and "
                "is not leaves it claiming more than the release delivers",
                file=sys.stderr,
            )
        return 1

    stray: list[str] = []
    for scanned in pages:
        allowed = [
            match.span()
            for _, pattern in PUBLISHED_REGISTRIES
            for match in pattern.finditer(scanned.text)
        ]
        for match in REGISTRY_WORD.finditer(scanned.text):
            covered = any(
                start <= match.start() and match.end() <= end for start, end in allowed
            )
            if not covered:
                stray.append(
                    f"{os.path.relpath(scanned.path, root)}:"
                    f"{scanned.line_of[match.start()]}: {match.group(0)!r}"
                )
    if stray:
        for where in stray:
            print(
                f"check-claims: the page names a registry at {where}, and the release publishes "
                f"to {' and '.join(name for name, _ in PUBLISHED_REGISTRIES)}. A registry the "
                "project does not publish to is a distribution channel it does not have, and "
                "\"the extension gallery\" names a channel without naming which",
                file=sys.stderr,
            )
        return 1

    missing = [
        f"{os.path.relpath(scanned.path, root)}:{line}: {destination!r}"
        for scanned in pages
        for destination, line in scanned.destinations
        if REGISTRY_LISTING.search(destination) and destination not in EXTENSION_LISTINGS
    ]
    if missing:
        for where in missing:
            print(
                f"check-claims: the page links a listing at {where}, and the extension is "
                f"published as `{PUBLISHED_EXTENSION}`; the listing on each registry is "
                f"{' and '.join(EXTENSION_LISTINGS)}. A link to a listing is a claim about "
                "which one, and the retired ID's listing is still there to be linked by "
                "mistake",
                file=sys.stderr,
            )
        return 1

    print(
        f"check-claims: the page hands a reader `{PUBLISHED_EXTENSION}` on "
        f"{' and '.join(name for name, _ in PUBLISHED_REGISTRIES)}, names no registry the "
        "project does not publish to, links no other listing, and says an install is the client "
        "and not a server"
    )
    return 0


# The card the page offers and does not have: a hosted tier the project would run for the reader.
# Its parts are one claim — the card, the status on it, the sentence saying who would run it, and
# the row that is a plan rather than a control — and each is a required fact of its own, so a
# rewrite that keeps the fact passes and a card that drops it fails.
#
# The status is stated once, in either of two spellings: the pill says the tier is not available
# yet and the row calls it planned. The pattern reads both rather than requiring both, because a
# card that states the same fact twice is the redundancy this replaced; a card that states it
# neither way is the absent status the check still catches. The facts are read from the card's own
# markup, not the page's text, so the same words elsewhere on the page — the grid's own plan wears
# them — cannot stand in for the status the card owes.
HOSTED_CARD_CLASS = "try-card-planned"
HOSTED_TIER_FACTS = (
    ("the card that offers it", re.compile(r"Rent a server", re.IGNORECASE)),
    (
        "that it is not available yet",
        # The note is drawn at the row's right edge by CSS, so its word joins the label in the
        # flattened text (`Hosted serversplanned`); the pattern reads the word without a leading
        # boundary for that reason, which is safe inside the card's own small region as long as
        # `unplanned` is not read as the word.
        re.compile(r"\bNot available yet\b|(?<!un)planned", re.IGNORECASE),
    ),
    ("who would run it", re.compile(r"\bWe run the server\b", re.IGNORECASE)),
)
# The row is where the card would offer a room the project cannot hand over, and the half a phrase
# cannot reach is the element it is written on: drawn on an anchor or a button, it reads as a
# control, and a reader who presses it asks for a room nobody can give them.
HOSTED_ROW_CLASS = "planned-row"
HOSTED_ROW_TEXT = re.compile(r"Hosted servers", re.IGNORECASE)
CONTROL_TAG = re.compile(r"<\s*(?:a|button)\b", re.IGNORECASE)

# The repository grid's rows are read from the page rather than listed here. The clients are
# the page's own list (`lib/clients.ts`), and a second hand-maintained list of names in this file
# would be the drift the grid's rule exists to catch: a client added to the page would be one
# this check never looked at. What is pinned below is the handful of facts that have to stay
# true of named rows whatever else the grid carries.
#
# A row's claim is its name, its description, its word and its destination together, read from
# the row's own markup: the pattern alone is not enough, because a swap of two rows' links leaves
# every name and every word still on the page.
GRID_PINNED_ROWS = (
    (
        "specification",
        "Prose, schema, vectors",
        "source of truth",
        re.compile(r"\bspecification[^.]{0,32}source of truth\b", re.IGNORECASE),
    ),
    (
        "vscode_client",
        "VS Code extension",
        "available",
        re.compile(r"\bvscode_client[^.]{0,32}available\b", re.IGNORECASE),
    ),
    (
        "reference_server",
        "selvaged",
        "available",
        re.compile(r"\breference_server[^.]{0,32}available\b", re.IGNORECASE),
    ),
    (
        "nvim_client",
        "Neovim plugin",
        "available",
        re.compile(r"\bnvim_client[^.]{0,32}available\b", re.IGNORECASE),
    ),
    (
        "web_client",
        "The browser page",
        "available",
        re.compile(r"\bweb_client[^.]{0,32}available\b", re.IGNORECASE),
    ),
)

# The row that is a plan rather than a repository a reader can open: a client nobody has written
# cannot be offered, so the row carries no destination and the word beside it says so. Its name,
# its description and that word are required the way a linked row's are, and read below without a
# destination, which is the half a linked row has no analogue for.
#
# It is named here so the page cannot quietly drop it: a plan that is not drawn at all satisfies
# every agreement rule below, and the one row the project writes down as planned is a fact about
# what the project has not written. `jetbrains_client` is that row.
GRID_PINNED_PLANS = (
    (
        "jetbrains_client",
        "JetBrains IDEs",
        "Not available yet",
        re.compile(
            r"\bjetbrains_client[^.]{0,32}JetBrains IDEs[^.]{0,32}Not available yet\b",
            re.IGNORECASE,
        ),
    ),
)

# The words the grid's rows carry. A row the page links states a repository a reader can open;
# a row it leaves unlinked is a plan and says so, in the hosted tier's words. The plan's words are
# the only ones an unlinked row may wear, and a linked row may not wear them, which is what keeps
# a plan from becoming a way to name a live repository without linking it.
GRID_LIVE_WORDS = ("available", "source of truth")
GRID_PLAN_WORD = "Not available yet"

# The key a surface carries for the client it draws. `lib/clients.ts` gives a client one `id`,
# and the grid's row, the chips and the install route each carry it, so the three can be read
# against each other without a list of client names here.
GRID_CLIENT = re.compile(r'\bdata-client="([\w-]+)"')

# The chips figure in *Clients share one protocol*, and the install routes' panels. A route's key
# is its panel's own id, which is the client's.
CHIPS_FIGURE = re.compile(
    r'<div\b[^>]*\bclass="[^"]*\bclients\b[^"]*"[^>]*>(.*?)</div>',
    re.DOTALL | re.IGNORECASE,
)

# The URL shape of a repository link. The grid's own rows are the list of names the page may
# carry, so a row's word and its destination cannot name two different repositories.
GRID_LINK = re.compile(r"https?://github\.com/selvage-protocol/([\w.-]+)")

GRID_HREF = re.compile(r'''href\s*=\s*"([^"]*)"''', re.IGNORECASE)
# The grid's own list, and one row of it. A row's whole claim is inside its list item, whatever
# shape that item takes, which is what keeps a sentence naming the repository from standing in
# for the row the page draws.
GRID_LIST = re.compile(r"<ul\b[^>]*\brepos\b[^>]*>(.*?)</ul>", re.DOTALL | re.IGNORECASE)
GRID_ITEM = re.compile(r"<li\b[^>]*>(.*?)</li>", re.DOTALL | re.IGNORECASE)

# One install route in the terminal: the strip's panels are siblings, each with an id of its own,
# so a panel is read from its id to the next panel's. The route that installs the extension is
# where the identity the release publishes under and the two registries it publishes to have to
# sit, and reading the panel rather than the page is what keeps them in that route.
INSTALL_PANEL_ID = re.compile(r'\bid="install-panel-([\w-]+)"')


@dataclass(frozen=True)
class GridRow:
    """One row of the repository grid, as the row's own markup reads it."""

    text: str
    linked: bool
    repository: str | None
    client: str | None


def grid_rows(raw: str) -> list[GridRow]:
    """Every row of the grid, from the list's own items.

    A row's repository comes from its `href` where it has one and its client from the key the
    surface carries, and its claim from the item whole, so one row cannot be satisfied by
    another row's words. A grid the page no longer draws answers with no rows, which fails where
    a row is required rather than passing quietly.
    """
    rows: list[GridRow] = []
    for grid in GRID_LIST.finditer(raw):
        for item in GRID_ITEM.finditer(grid.group(1)):
            body = item.group(0)
            href = GRID_HREF.search(body)
            repository = None
            if href is not None:
                named = GRID_LINK.match(html.unescape(href.group(1)))
                if named is not None:
                    repository = named.group(1)
            client = GRID_CLIENT.search(body)
            rows.append(
                GridRow(
                    text=normalise(body)[0],
                    linked=href is not None,
                    repository=repository,
                    client=client.group(1) if client else None,
                )
            )
    return rows


def chip_clients(raw: str) -> list[str]:
    """The client each chip in the *Clients share one protocol* figure names, in order.

    The figure is decoration drawn from the client list, so its chips are read from the figure's
    own markup rather than from the page's text. A page that no longer draws the figure answers
    with no clients, which fails where its chips are required rather than passing quietly.
    """
    clients: list[str] = []
    for figure in CHIPS_FIGURE.finditer(raw):
        clients.extend(match.group(1) for match in GRID_CLIENT.finditer(figure.group(1)))
    return clients


def install_panel_text(raw: str, panel: str) -> str | None:
    """One install route's own visible text, its panel read to the panel's own closer.

    Reading to the closer rather than to the next panel is what keeps the route whole wherever
    the strip puts it: the last panel would otherwise run to the end of the document and borrow
    whatever the page says after it. A page that no longer draws the terminal answers with None,
    which fails where a route is required rather than passing quietly.
    """
    opening = re.compile(
        rf'<(?P<tag>[a-z][\w-]*)\b[^>]*\bid="install-panel-{re.escape(panel)}"[^>]*>',
        re.IGNORECASE,
    )
    match = opening.search(raw)
    element = element_from(raw, match) if match is not None else None
    return normalise(element[1])[0] if element is not None else None


def element_by_class(raw: str, class_name: str) -> tuple[str, str] | None:
    """The first element whose `class` names `class_name`: its tag and its whole markup.

    The element is read to its own closer rather than the first inner one, so a card that holds a
    head, a body and a row ends where the card ends and not at its first `</div>`. A tag the
    markup never closes answers None rather than a fragment, so an element that cannot be read
    fails where one is required rather than passing quietly.
    """
    opening = re.compile(
        rf"<(?P<tag>[a-z][\w-]*)\b[^>]*\bclass=\"[^\"]*\b{re.escape(class_name)}\b[^\"]*\"[^>]*>",
        re.IGNORECASE,
    )
    match = opening.search(raw)
    return element_from(raw, match) if match is not None else None


def element_from(raw: str, match: re.Match[str]) -> tuple[str, str] | None:
    """The element whose opening tag `match` is, read to its own closer: its tag and its markup."""
    name = match.group("tag")
    scanner = re.compile(rf"<\s*(?P<close>/?)\s*{re.escape(name)}(?=[\s>/])", re.IGNORECASE)
    depth = 1
    pos = match.end()
    while depth and pos < len(raw):
        found = scanner.search(raw, pos)
        if found is None:
            return None
        end = _tag_end(raw, found.start())
        if end == -1:
            return None
        if found.group("close"):
            depth -= 1
        elif not raw[found.start():end + 1].rstrip().endswith("/>"):
            depth += 1
        pos = end + 1
    return name, raw[match.start():pos]


def hosted_card_region(page: Scanned) -> str:
    """The hosted tier's card text, the only region its facts are required to be stated in."""
    card = element_by_class(page.raw, HOSTED_CARD_CLASS)
    return normalise(card[1])[0] if card is not None else ""


def hosted_row_problem(card: str) -> str | None:
    """What is wrong with the hosted tier's row, or None when it is the plan the card draws.

    The row is where the card would offer a room the project cannot hand over, so what is required
    is that it is drawn on an element a reader cannot press and that it still names the tier. The
    control may be the row's own tag or an anchor wrapped around it, so the whole card is read for
    one; the page's flattened text cannot tell a plan from a link at all.
    """
    found = element_by_class(card, HOSTED_ROW_CLASS)
    if found is None:
        return "its row is gone, so the card no longer draws the tier it offers"
    _tag, row = found
    if not HOSTED_ROW_TEXT.search(row):
        return "its row no longer names the tier it is a plan for"
    if CONTROL_TAG.search(card):
        return "it draws a control, so it offers a room the project does not run"
    return None


def check_hosted_tier(pages: list[Scanned]) -> int:
    """The hosted tier the page offers and does not run yet.

    The card is the one place a reader can ask for something the project cannot give them, so
    what it says is read as a whole: it offers a server the project would run, it says that is
    not available yet, and the row under it is a plan rather than a control. Required rather than
    permitted, for the reason the disclosure is: a `clean` fixture proves a pattern does not
    reject a sentence, never that the page carries one. The status is read in either of its two
    spellings and from the card's own markup, so a card that states it once passes, one that
    states it nowhere fails, and one whose row is a control fails on the element the row is
    written on. The phrase list's `now available` entry can only catch the opposite direction — a
    page that dropped the status would read as an offer with nothing saying it cannot be taken,
    and nothing else here would notice.

    Returns 0 when a scanned page carries every part of the card and 1 when none does; it asks no
    network.
    """
    root = root_of_this_checkout()
    page, failures = first_page_stating(pages, HOSTED_TIER_FACTS, hosted_card_region)
    if page is not None:
        card = element_by_class(page.raw, HOSTED_CARD_CLASS)
        problem = hosted_row_problem(card[1]) if card is not None else None
        if problem is not None:
            print(
                f"check-claims: {os.path.relpath(page.path, root)} offers a hosted tier and "
                f"{problem}. The card is where a reader can ask for a server the project does "
                "not run yet, so its row has to stay a plan rather than a control",
                file=sys.stderr,
            )
            return 1
        print(
            "check-claims: the page offers a hosted tier and says it is not available yet — the "
            "card, its status, who would run it, and the row that is a plan rather than a control"
        )
        return 0
    for where, absent in failures:
        print(
            f"check-claims: {where} does not say what the hosted tier's card offers: it is "
            f"missing {', '.join(absent)}. The page offers a server the project does not run "
            "yet, and a card without that status reads as something a reader can ask for",
            file=sys.stderr,
        )
    return 1


def check_repository_grid(pages: list[Scanned]) -> int:
    """The repository grid, against its own rows and against the surfaces that draw a client.

    The grid is the page's own account of what exists. A row names a repository, describes it in
    a word or two, says one word about it and links it, and a reader who follows the row lands on
    the code the word is about. Five things hold that together, and all five are required rather
    than permitted, for the reason the disclosure is:

    - a row that links wears one of the words a live row may wear, and a row that does not link
      is a plan and says so. A plan is a client nobody has written, so a reader who follows the
      row reaches nothing, and a row that links nowhere hands the reader nothing to check;
    - a row's repository, its own text and its destination are one claim, read from inside the
      row, so a row that links a different repository fails even though the page still carries
      every name and every word;
    - every repository the page links is one a row of the grid links too, so no row and no source
      link beside the terminal points at a repository the project does not have;
    - the client each row draws, each chip in *Clients share one protocol* and each install route
      in the terminal are read from the key the surface carries, and all three have to name the
      same clients. A client added to the page's own list appears on every surface at once; a
      surface written out by hand is the half-added client this catches;
    - the chips are the leading clients in the grid's own order. The figure caps how many it
      names and rolls the rest into its last chip, so what it may leave out is a suffix of the
      list rather than a scatter, which is what stops a chip standing for a client the grid has
      not got.

    What is pinned by name is the handful of facts that have to stay true of named rows whatever
    else the grid carries: the specification is the source of truth, the extension's row is the
    one a reader is also handed an install for, and the plan is the one row that must not link.
    Nothing else about the grid is a list in this file: the clients are the page's own list, and
    a client added there is one this function reads rather than one it has to be told about.

    The extension's row is the one whose repository a reader is also handed an install for, and
    the install is where the identity the release publishes under and the two registries it
    publishes to live: the VS Code route in the terminal. So the row and that route are read as
    one claim — this function reads the word beside the repository from the grid and the install
    from the route's own panel, and `check_published_extension` reads the same identity and
    registries from the page as a whole. A route that lost the identity or a registry fails here
    even though the page still carries the row, which is what keeps the word `available` about
    the extension from standing alone.

    What it does not do is ask GitHub whether any of them answers. A repository's existence is
    the organisation's fact; what is read here is the page's own consistency about it.

    Returns 0 when all of it holds and 1 when it does not; it asks no network.
    """
    root = root_of_this_checkout()
    pinned = GRID_PINNED_ROWS + GRID_PINNED_PLANS
    facts = [(f"the {name} row", pattern) for name, _desc, _status, pattern in pinned]
    page, failures = first_page_stating(pages, facts)
    if page is None:
        for where, absent in failures:
            print(
                f"check-claims: {where} does not carry the repository grid: it is missing "
                f"{', '.join(absent)}. The grid is the page's own account of what exists, and "
                "a row that loses its word is a claim about a repository that nothing beside "
                "it supports",
                file=sys.stderr,
            )
        return 1

    rows = grid_rows(page.raw)
    if not rows:
        print(
            "check-claims: the page carries no repository grid, so no row can be read; a grid "
            "the check cannot see is not a grid that passed",
            file=sys.stderr,
        )
        return 1

    # The extension's row is the one row here whose repository a reader is handed an install for,
    # so the word beside the row is backed by that install: the identity the release publishes
    # under and both registries it publishes to, read from the route that hands the extension
    # over rather than from anywhere on the page. The row and the install are one claim, so a
    # route that lost the identity or a registry fails even though the row still says the client
    # is available.
    install = install_panel_text(page.raw, "vscode")
    missing = [
        label
        for label, pattern in PUBLISHED_REGISTRIES
        if install is None or not pattern.search(install)
    ]
    identity = install is not None and PUBLISHED_EXTENSION in install
    if install is None or not identity or missing:
        status = next(
            status for name, _desc, status, _ in GRID_PINNED_ROWS if name == "vscode_client"
        )
        absent = (
            ["the install route itself"]
            if install is None
            else ([f"the identity `{PUBLISHED_EXTENSION}`"] if not identity else []) + missing
        )
        print(
            f"check-claims: the grid says the extension's repository is {status}, and the VS "
            f"Code route in the terminal is missing {', '.join(absent)}, so the row offers a "
            "client the page does not say where to install. The word beside the row and the "
            "install a reader follows are one claim",
            file=sys.stderr,
        )
        return 1

    # The three surfaces that draw a client, read from the keys they carry rather than from a
    # list of names here.
    client_rows = [row.client for row in rows if row.client]
    clients = set(client_rows)
    chips = chip_clients(page.raw)
    routes = [match.group(1) for match in INSTALL_PANEL_ID.finditer(page.raw)]

    # Every rule below is about a chip and something else, so a figure that is not drawn at all
    # satisfies the lot of them: an empty list is a subset of every set, and it is the prefix of
    # the grid's clients. The figure is one of the two drawings of the client list, so reaching
    # no chip fails here rather than passing on the grid alone.
    if not chips:
        print(
            "check-claims: the page draws no client chips, so the figure cannot be read against "
            "the grid; the chips are one of the two drawings of the client list, and a figure "
            "the check cannot see is not a figure that passed",
            file=sys.stderr,
        )
        return 1

    for client in sorted(set(chips) - clients):
        print(
            f"check-claims: the chips name the client {client!r} and no row of the grid draws "
            "it. The chips and the grid are two drawings of one list, so a client on one and "
            "not the other is half a client",
            file=sys.stderr,
        )
    for client in sorted(set(routes) - clients):
        print(
            f"check-claims: the terminal carries an install route for {client!r} and no row of "
            "the grid draws that client. A route installs something the page's own account of "
            "what exists has to name, so a reader following it reaches a client the grid has "
            "not got",
            file=sys.stderr,
        )
    if chips != client_rows[: len(chips)]:
        kept = next(
            (
                client
                for at, client in enumerate(client_rows)
                if at >= len(chips) and client in chips
            ),
            None,
        )
        print(
            "check-claims: the chips name "
            f"{', '.join(repr(client) for client in chips)} and the grid draws "
            f"{', '.join(repr(client) for client in client_rows)}. The figure caps how many "
            "clients it names and rolls the rest into its last chip, so what it leaves out is "
            "the tail of the grid's own list"
            + (f", and {kept!r} is named past a client it does not name" if kept else ""),
            file=sys.stderr,
        )
    if (set(chips) - clients) or (set(routes) - clients) or chips != client_rows[: len(chips)]:
        return 1

    # Each row's own claim, and the rule that decides which of the two shapes it has: a row the
    # page links is a repository a reader can open, and one it does not is a plan and says so.
    linked_repos: set[str] = set()
    for row in rows:
        if not row.linked:
            if GRID_PLAN_WORD not in row.text:
                print(
                    f"check-claims: the grid row {row.text!r} links nothing and does not say it "
                    "is not available yet. A row is either a repository a reader can open or a plan, and "
                    "an unlinked row that says neither reads as a mistake",
                    file=sys.stderr,
                )
                return 1
            continue
        if row.repository is None:
            print(
                f"check-claims: the grid row {row.text!r} links somewhere that is not a "
                "repository under the organisation. A linked row hands a reader the code the "
                "word beside it is about",
                file=sys.stderr,
            )
            return 1
        linked_repos.add(row.repository)
        if row.repository not in row.text:
            print(
                f"check-claims: the grid row {row.text!r} links {row.repository!r} and does not "
                "name it. A row is a claim about one repository, and a reader who follows it "
                "has to land on the code the row is about",
                file=sys.stderr,
            )
            return 1
        if GRID_PLAN_WORD in row.text or not any(
            word in row.text for word in GRID_LIVE_WORDS
        ):
            print(
                f"check-claims: the grid row {row.text!r} links {row.repository!r} and does "
                f"not wear one of {', '.join(repr(word) for word in GRID_LIVE_WORDS)}"
                + (f" (it says {GRID_PLAN_WORD!r})" if GRID_PLAN_WORD in row.text else "")
                + ". A row the page links states a repository a reader can open, and the plan's "
                "word is the one it cannot wear",
                file=sys.stderr,
            )
            return 1

    stray = [
        f"{os.path.relpath(scanned.path, root)}:{line}: {destination!r}"
        for scanned in pages
        for destination, line in scanned.destinations
        for match in [GRID_LINK.match(destination)]
        if match and match.group(1) not in linked_repos
    ]
    if stray:
        for where in stray:
            print(
                f"check-claims: the page links a repository at {where}, and the grid links "
                f"{', '.join(sorted(linked_repos))}. A link is a claim that a repository is "
                "there to read, and a row that is a plan does not name one",
                file=sys.stderr,
            )
        return 1

    # A row's repository, its own text and its destination are one claim about one repository.
    # The rules above prove the shape of every row, not that a named row is still there; these
    # three hold the facts that have to stay true of the rows the page has always carried.
    for name, desc, status, _pattern in GRID_PINNED_ROWS:
        owner = next(
            (
                row.text
                for row in rows
                if row.repository == name
                and name in row.text
                and desc in row.text
                and status in row.text
            ),
            None,
        )
        if owner is not None:
            continue
        beside = next((row.text for row in rows if row.repository == name), None)
        detail = (
            f"The row whose destination names {name} reads {beside!r}"
            if beside is not None
            else f"The page links nothing whose destination names {name}"
        )
        print(
            f"check-claims: the {name} row does not join its name, its description ({desc!r}), "
            f"its pill ({status!r}) and its own link. {detail}. A row is a claim about one "
            "repository, and a reader who follows it has to land on the code the word beside it "
            "is about",
            file=sys.stderr,
        )
        return 1

    # A row that is a plan has no destination to be held against, so its own list item is what
    # carries the claim. The row's text is read whole, which is what keeps a sentence naming the
    # repository from standing in for the row the page draws.
    for name, desc, status, _pattern in GRID_PINNED_PLANS:
        if any(
            not row.linked and name in row.text and desc in row.text and status in row.text
            for row in rows
        ):
            continue
        print(
            f"check-claims: the {name} row does not join its name, its description ({desc!r}) "
            f"and its pill ({status!r}) in one row. Such a row is the page's own statement that "
            "it is a plan rather than something a reader can open, and a word about it loose on "
            "the page is not that statement",
            file=sys.stderr,
        )
        return 1

    print(
        f"check-claims: the grid draws {len(rows)} rows, {len(linked_repos)} of them linked, "
        f"and its {len(client_rows)} clients, its {len(chips)} chips and its {len(routes)} "
        "install routes name the same ones. Each row joins its own name, description and word "
        "to its own link, every repository the page links is one the grid links, the plan is "
        f"the one row left unlinked, and the extension is handed over in a VS Code install "
        f"route that names `{PUBLISHED_EXTENSION}` on both registries it is published to"
    )
    return 0


def wire_binding_problems(
    page: Scanned, offered: tuple[str, ...], image_wire: str
) -> list[str]:
    """What this page says about the wire that the artefacts behind it do not support.

    Nothing here has to be said: the page names no wire version and binds no artefact to one. Each
    rule reads what a page does say and holds it to the thing it names, so a sentence that comes
    back is checked the moment it is written rather than passing unread.
    """
    problems: list[str] = []
    image = WIRE_OF_IMAGE.search(page.text)
    if image is not None and image.group(1) != image_wire:
        problems.append(
            f"it says the image under the `docker run` speaks {image.group(1)!r}, and the "
            f"tag {PUBLISHED_IMAGE_TAG} speaks {image_wire}"
        )
    demo = WIRE_OF_DEMO.search(page.text)
    if demo is not None and demo.group(1) not in offered:
        problems.append(
            f"it says the demo speaks {demo.group(1)!r}, and {DEMO_ORIGIN}/meta offers "
            f"{', '.join(offered)}"
        )
    # One wire version, so every version the page names is the one this protocol has. A second
    # name is a claim about a version that does not exist, and it is how the plaintext wire's own
    # sentence would outlive it: a page that still tells a reader which wire to avoid is a reader
    # who pastes the command under the paragraph and meets the version they were warned about.
    strangers = sorted({match.group(0) for match in WIRE_VERSION.finditer(page.text)} - {WIRE})
    if strangers:
        problems.append(
            f"it names {', '.join(strangers)}, and this protocol has one wire version, {WIRE}"
        )
    unreleased = WIRE_UNRELEASED.search(page.text)
    if unreleased is not None:
        problems.append(
            f"it calls the wire unreleased ({unreleased.group(0)!r}), and the tag the page "
            f"hands a reader ({PUBLISHED_IMAGE_TAG}) speaks it (`IMAGE_WIRE_BY_TAG`)"
        )
    return problems


def check_wire_binding(pages: list[Scanned]) -> int:
    """Which wire version the page says each artefact it hands a reader speaks.

    The page hands a reader one `docker run` and one instance address, there is one wire version,
    and it is the sealed one. It no longer has to say which: what is read here is what it says
    about the wire, and behind that the two artefacts against each other, which is the fact the
    sentence used to carry. The wire the tag speaks is read from `IMAGE_WIRE_BY_TAG`, because no
    registry answers what wire a binary speaks and a tag the map does not name has to declare its
    wire in the same wave; the instance's half is measured, from `/meta`, where no wording can
    forge it. A tag the instance does not offer, or a version the page names that this protocol
    does not have, is a reader pasting the command under the sealing paragraph and getting a
    server that carries the room through it in the clear — the failure a confidentiality feature
    cannot have, and the one the pairing of the command and the paragraph is for.

    Returns 0, 1 when a page says something the artefacts disprove, 2 when the instance cannot
    be asked or this file cannot say what the tag speaks.
    """
    root = root_of_this_checkout()
    if PUBLISHED_IMAGE_TAG not in IMAGE_WIRE_BY_TAG:
        print(
            f"check-claims: the page hands a reader the tag {PUBLISHED_IMAGE_TAG} and nothing "
            "here says which wire version that tag speaks (see `IMAGE_WIRE_BY_TAG`); a tag "
            "whose wire is unknown cannot be held to what the page hands over beside it",
            file=sys.stderr,
        )
        return 2
    image_wire = IMAGE_WIRE_BY_TAG[PUBLISHED_IMAGE_TAG]
    try:
        offered = demo_meta()[1]
    except (urllib.error.URLError, OSError, ValueError, KeyError) as error:
        print(
            f"check-claims: cannot ask {DEMO_ORIGIN} which wire versions it offers ({error}); "
            "the page hands a reader that address and this file cannot say what a client meets "
            "there without it",
            file=sys.stderr,
        )
        return 2

    # The two artefacts the page hands over are one protocol, and that is the half of the
    # sentence that does not depend on the page saying it: the command a reader pastes and the
    # address a reader points an editor at have to deliver the same wire, or the page's own happy
    # path ends in a server the reader's client refuses.
    if image_wire not in offered:
        print(
            f"check-claims: the page hands a reader the tag {PUBLISHED_IMAGE_TAG}, which speaks "
            f"{image_wire}, and {DEMO_ORIGIN}/meta offers {', '.join(offered)}: the command and "
            "the address on the page are not the same protocol, so a reader who follows both "
            "meets a version one of the two does not have",
            file=sys.stderr,
        )
        return 1

    failed: list[tuple[str, list[str]]] = []
    for page in pages:
        problems = wire_binding_problems(page, offered, image_wire)
        if problems:
            failed.append((os.path.relpath(page.path, root), problems))
    if failed:
        for where, problems in failed:
            print(
                f"check-claims: {where} says something about the wire the artefacts do not "
                "support: " + "; ".join(problems),
                file=sys.stderr,
            )
        return 1
    named = sorted(
        {match.group(0) for page in pages for match in WIRE_VERSION.finditer(page.text)}
    )
    print(
        "check-claims: "
        + (f"the page names {', '.join(named)}" if named else "the page names no wire version")
        + f"; the tag {PUBLISHED_IMAGE_TAG} speaks {image_wire} and {DEMO_ORIGIN}/meta offers "
        f"{', '.join(offered)}, so the two artefacts the page hands a reader speak the same "
        "version, and nothing here names another one or calls the wire unreleased"
    )
    return 0


def main() -> int:
    compiled: list[
        tuple[Phrase, re.Pattern[str], list[re.Pattern[str]], tuple[re.Pattern[str], ...]]
    ] = []
    for phrase in FORBIDDEN:
        pattern = re.compile(phrase.pattern, re.IGNORECASE)
        permits = [re.compile(one, re.IGNORECASE) for one in phrase.permitted_when]
        voiding = tuple(
            re.compile(one, re.IGNORECASE) for one in phrase.voided_when
        )
        if not hits(pattern, permits, normalise(phrase.sample)[0], voiding):
            print(
                f"check-claims: the pattern {phrase.pattern!r} does not match its own sample "
                f"{phrase.sample!r}; a pattern that matches nothing passes everything",
                file=sys.stderr,
            )
            return 2
        for evasion in phrase.evasions:
            if not hits(pattern, permits, normalise(evasion)[0], voiding):
                print(
                    f"check-claims: the pattern {phrase.pattern!r} does not match its evasion "
                    f"sample {evasion!r}; the claim is written in a shape the pattern misses",
                    file=sys.stderr,
                )
                return 2
        for wording in phrase.clean:
            if hits(pattern, permits, normalise(wording)[0], voiding):
                print(
                    f"check-claims: the pattern {phrase.pattern!r} matches its clean fixture "
                    f"{wording!r}; honest wording is a false positive",
                    file=sys.stderr,
                )
                return 2
        compiled.append((phrase, pattern, permits, voiding))

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

    found_hits = 0
    scanned: list[Scanned] = []
    for path in paths:
        with open(path, encoding="utf-8") as handle:
            raw = handle.read()
        text, line_of = normalise(raw)
        prose = meta_streams(raw)
        scanned.append(
            Scanned(
                path=path,
                text=text,
                line_of=line_of,
                destinations=destinations(raw),
                raw=raw,
                prose=prose,
            )
        )
        where = os.path.relpath(path, root)
        for phrase, pattern, permits, voiding in compiled:
            for stream, lines in [(text, line_of), *prose]:
                for match in hits(pattern, permits, stream, voiding):
                    found_hits += 1
                    print(
                        f"{where}:{lines[match.start()]}: forbidden phrase "
                        f"{match.group(0)!r}\n    {phrase.reason}"
                    )

    if found_hits:
        print(f"check-claims: {found_hits} forbidden phrase(s) in {len(paths)} file(s)")
        return 1

    for check in (
        check_relay_disclosure,
        check_fsl_disclosure,
        check_corpus_citation,
        check_published_extension,
        check_hosted_tier,
        check_repository_grid,
        check_published_image,
        check_demo_instance,
        check_wire_binding,
    ):
        status = check(scanned)
        if status != 0:
            return status

    print(
        f"check-claims: {len(compiled)} known wordings alive over {len(paths)} file(s), none "
        "found. This is a filter, not a proof: a false claim in other words passes it"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
