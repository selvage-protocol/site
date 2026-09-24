#!/usr/bin/env python3
"""Fails the shipped page on a phrase the project cannot back today.

This is a filter, not a proof. It matches a list of known wordings; a false claim written in
different words, a synonym, a superlative, a wrong number the corpus does not pin, or any
sentence that is merely unbacked all pass it. What it does guarantee is narrower and still
worth having: those known wordings do not appear, even when the page wraps them across lines or
encodes the characters as HTML entities.

Facts are asserted in the positive instead, because a phrase list cannot reach them: the image tag
in the `docker run` the page hands a reader, the instance the demo section points at — the address
it gives an editor, the wire version that address speaks, and the page a guest is sent to — the
wire version the page says each artefact it hands a reader speaks, the two disclosures the page
owes a reader: what the sealed relay still sees, and that a guest who opens the room server's own
page trusts that server for the client code as well as for the relay, and the identity the
extension is published under with the two registries the release publishes it to and what an
install is and is not. The address half asks the
path a plain `GET` can reach, not the upgrade: see `demo_session_route`. Each is a fact with an
artefact behind it, and a wrong tag is a command that fails rather than a wording that lies. See
`PUBLISHED_IMAGE`, `DEMO_ORIGIN`, `RELAY_DISCLOSURE`, `PUBLISHED_EXTENSION` and
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
# pinned value the only one that passes.
VEHICLE = r"\d[\d,]*"

# The address the project's own landing page is served at. The browser entry holds a claim that
# this origin is a place to join a room: the demo instance is where a page can be opened now, and
# the site is not a client.
SITE_ORIGIN = r"selvage\.dontblameme\.dev"

DASHES = re.compile("[\u2010-\u2015\u2212\ufe58\ufe63\uff0d]")

# The page's happy path is a `docker run` a reader pastes, so the tag in it is a claim with an
# artefact behind it: a wrong tag is `manifest unknown`, not a wording a phrase list can
# enumerate. It is therefore a *required* claim, pinned once here and asserted twice: every
# reference the rendered page carries must name this version, and the registry must serve it.
#
# The registry half is the one that reaches the artefact, and it holds the distinction that
# matters: a platform entry in an image index proves only that a slot is *labelled* arm64.
# `selvaged:0.1.1` published one, and both its legs carried the amd64 binary — every layer
# digest identical across the two per-platform manifests, the same defect `0.1.0` carries. The check
# compares those digests and fails when they are the same set, which is what a mislabelled leg
# looks like, and it pulls them with no credential in the request, because no account is the
# point of the command the page hands over.
PUBLISHED_IMAGE = "ghcr.io/selvage-protocol/selvaged"
PINNED_IMAGE_VERSION = "0.4.1"
IMAGE_REFERENCE = re.compile(r"ghcr\.io/selvage-protocol/selvaged(?::([\w][\w.+-]*))?")
REGISTRY_HOST = "ghcr.io"
REGISTRY_REPOSITORY = PUBLISHED_IMAGE.split("/", 1)[1]
REQUEST_TIMEOUT_SECONDS = 20

# The wire version this protocol has, and which wire the pinned `selvaged` release speaks. The
# page hands a reader an artefact whose wire is a fact about the artefact, not a wording: under this
# version the room's bytes reach the server sealed, so a page that puts the sealing claim over a
# command yielding a relay that cannot seal is a silent downgrade. The map is a constant rather
# than a measurement because nothing on a registry answers what wire version a binary speaks: an
# index will say `linux/arm64` and nothing about the frames inside. A pin with no entry fails the
# check instead of defaulting, so a release that moves the pin has to declare the new tag's wire in
# the same wave — this map, `PINNED_IMAGE_VERSION` and the page's sentence about it move together,
# and `check_wire_binding` is what holds the last of the three to the first two.
WIRE = "selvage/2"
IMAGE_WIRE_BY_TAG = {
    "0.4.1": WIRE,
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
# of an endpoint they will never call. `PINNED_IMAGE_VERSION` is still asserted, against the
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
# The page's paragraph about the sealed relay is a claim the gate has to *require*, not just
# permit: the `clean` fixtures above only prove the pattern does not reject those sentences, and
# an editor who deletes the paragraph would leave every one of them green. What is required is
# the paragraph's facts, one pattern each, so a rewrite that keeps the facts passes and a page
# that drops one fails. The sizes-and-timing fact is the one only this paragraph carries.
#
# Two of the four are phrased as the disclosure's own sentence rather than as a subject and a verb,
# because the page states three of them twice: *The session layer has no specification* writes
# "Which rooms exist, who is in one, ...", which is a sentence about what every collaborative tool
# decides for itself and not a disclosure of relay visibility at all. Loosely matched, that
# paragraph would supply existence and membership for a page whose disclosure had been deleted, and
# a rewrite that dropped the two facts while keeping "their names" and "sizes and timing" would
# pass with them gone. `who is in it` is the disclosure's wording; `who is in one` is the donor's.
RELAY_DISCLOSURE = (
    (
        "the room's existence",
        re.compile(
            r"\bsees that an? (?:room|session)s? exists?\b"
            r"|\bstill (?:sees|reads)\b[^.]{0,40}\b(?:room|session)s?\b[^.]{0,24}\bexists?\b",
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
USER_AGENT = "selvage-site-check/1.0"

# The second disclosure the page owes a reader, and the one the plan forbids leaving implied: the
# browser guest is served the client by the room's own server, so that server supplies the program
# that reads the fragment as well as the relay that carries the frames, and a page that says the
# server cannot read must say so out loud (the desktop clients are installed artefacts and are not
# in that position). Required the way `RELAY_DISCLOSURE` is, so one edit cannot quietly drop it.
BROWSER_TRUST_DISCLOSURE = (
    (
        "the guest's trust in the server that serves it the page",
        re.compile(r"\btrusts?\b[^.]{0,64}\bfor the client code\b", re.IGNORECASE),
    ),
    (
        "the clients that are not in that position",
        re.compile(r"\bnot in that position\b", re.IGNORECASE),
    ),
)

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
# What the row has to state about the install itself, required the way the disclosures are: a
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

# The two sentences that bind the page's sealing claim to the wire version it is true of: which
# wire the pinned image speaks, and which wire the demo speaks. `check_wire_binding` reads both.
WIRE_OF_PINNED = re.compile(
    r"\bthe (?:published |pinned )?(?:image|container)\b"
    r"[^.]{0,80}?\bspeaks?\b[^.]{0,40}?\b(selvage/\d+)\b",
    re.IGNORECASE,
)
WIRE_OF_DEMO = re.compile(
    r"\b(?:the demo|the instance)\b[^.]{0,80}?\bspeaks?\b[^.]{0,40}?\b(selvage/\d+)\b",
    re.IGNORECASE,
)
# How a page says the sealing is not what a reader can obtain yet. There is no version to say it of:
# the protocol has one wire version and the pinned release speaks it, so the sentence is false — it
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
        r"\b(?:nobody|no[ -]?one)\b[^.]{0,24}\bcan\b[^.]{0,16}"
        r"\b(?:read|see|open|decrypt|view)\b"
        r"|\bonly\b[^.]{0,32}\bcan\b[^.]{0,16}\b(?:read|see|open|decrypt|view)\b"
        r"|\bthe (?:server|relay|box|binary|instance)\b[^.]{0,24}"
        r"\b(?:learns|knows|sees|reads)\b[^.]{0,12}\bnothing\b"
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
        # to contain it is describing an artefact, not claiming a frozen release. The pin is
        # `0.4.1`, which carries no `1.0` substring at all, so the fixture below is synthetic
        # rather than the live pin; the lookbehind still has to hold for whatever version a future
        # pin carries. A 1.0 that stands on its own still matches.
        r"(?<![\d.])v?1\.0\b|production[- ]ready|production[- ]grade|battle[- ]tested|stable release",
        "the stable release, version 1.0",
        "the wire version is `selvage/2`; no shape is frozen. "
        "`0.4.1` is the version of the image the page hands a reader, not a 1.0",
        ("we are at v1.0", "the stable rele<!-- -->ase, version 1.0"),
        ("ghcr.io/selvage-protocol/selvaged:0.4.1", "0.4.1", "version 0.4.1", "tool:2.1.0"),
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
        "own validator pins (31 vectors, 34858 frame checks, 8642 assertions)",
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
        r"design[^.]{0,20}0\.x",
        "the design is at 0.x",
        "`PROTOCOL.md` §10 states the rule in force: `v` has one value, `selvage/2`, and a frame "
        "naming another is `bad_message`. No corpus "
        "line puts the design at 0.x; the compatibility clause names 0.x only for a future major "
        "0, which is not this one",
    ),
    Phrase(
        rf"\b(?!33760\b){VEHICLE}\s+frame[- ]checks?\b",
        "33759 frame checks",
        "the pinned number is 33760 frame checks (`specification/schema/validate.py`); a different "
        "number is a claim the corpus disproves",
        clean=("33760 frame checks",),
    ),
    Phrase(
        rf"\b(?!24\b){VEHICLE}\s+(?:\w+\s+){{0,2}}vectors?\b",
        "23 conformance vectors",
        "the pinned number is 24 vectors (`specification/schema/validate.py`); a different number "
        "is a claim the corpus disproves, and the count is pinned wherever the word sits — the "
        "page writes both 'conformance vectors' and 'wire vectors'",
        clean=("24 conformance vectors", "the 24 wire vectors"),
    ),
    Phrase(
        rf"\b(?!8387\b){VEHICLE}\s+assertions?\b",
        "8386 assertions",
        "the pinned number is 8387 assertions (`specification/schema/validate.py`); a different "
        "number is a claim the corpus disproves",
        clean=("8387 assertions",),
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


def pinned_tag_legs() -> dict[str, tuple[str, ...]]:
    """{platform: layer digests} for the pinned tag, read from the per-platform manifests.

    The tag's own document is an index that points at those; the layers live in the manifests
    it names, which is why the index alone cannot answer what this asks. Attestation entries
    carry `platform: unknown/unknown` and are skipped by the `os` filter.
    """
    token = anonymous_pull_token()
    index = _registry_json(f"{REGISTRY_REPOSITORY}/manifests/{PINNED_IMAGE_VERSION}", token)
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


def check_pinned_image(pages: list[Scanned]) -> int:
    """The page's version against the pin, and the pin against the registry.

    Returns 0 when both hold, 1 when either does not, 2 when the registry cannot be asked.
    """
    root = root_of_this_checkout()
    reference = f"{PUBLISHED_IMAGE}:{PINNED_IMAGE_VERSION}"
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
            f"reference, and the pin is {reference!r}: the page's happy path is where it is "
            "handed to a reader, so a scan that never reaches it is not checking the pin",
            file=sys.stderr,
        )
        return 1
    if wrong:
        for where in wrong:
            print(
                f"check-claims: the page hands a reader {where}, and the pinned image is "
                f"{reference!r}",
                file=sys.stderr,
            )
        return 1

    try:
        legs = pinned_tag_legs()
    except (urllib.error.URLError, OSError, ValueError, KeyError) as error:
        print(
            f"check-claims: cannot ask {REGISTRY_HOST} for {reference} ({error}); the pin "
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
        f"check-claims: the pinned image {reference} pulls anonymously and is not one "
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

    if not any(page_names(one, pages) for one in offered):
        print(
            f"check-claims: {DEMO_ORIGIN} offers the wire versions {', '.join(offered)} and the "
            "page names none of them: a client refuses a server that does not offer its wire "
            "version, so an editor set to that address is a session the page cannot open",
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


def first_page_stating(
    pages: list[Scanned], facts
) -> tuple[Scanned | None, list[tuple[str, list[str]]]]:
    """The first page that states every fact, and every page's missing ones.

    A disclosure is required, not permitted: a `clean` fixture proves a pattern does not reject a
    sentence, never that the page carries one. What is required is the facts, one pattern each, so
    a rewritten paragraph that keeps them passes and one that drops a fact fails.
    """
    root = root_of_this_checkout()
    failures: list[tuple[str, list[str]]] = []
    for page in pages:
        absent = [label for label, pattern in facts if not pattern.search(page.text)]
        if not absent:
            return page, []
        failures.append((os.path.relpath(page.path, root), absent))
    return None, failures


def check_relay_disclosure(pages: list[Scanned]) -> int:
    """The page's statement of what the sealed relay still sees, required rather than permitted.

    The facts are the paragraph's, and they are read from the visible text: a fact stated only in
    a link unfurl is not on the page a reader reads. Each fact has a pattern of its own, so a
    rewritten paragraph that keeps them passes and one that drops a fact fails. Two of the four
    have to be phrased as the disclosure's own sentence, because the page states the same two
    nouns a second time in *The session layer has no specification*, about what every
    collaborative tool decides for itself; matched loosely that paragraph supplied them for a
    page whose disclosure had been deleted, and a rewrite that dropped those two while keeping
    "their names" and "sizes and timing" passed with them gone. Returns 0 when a scanned page
    carries all four and 1 when none does; it asks no network.
    """
    page, failures = first_page_stating(pages, RELAY_DISCLOSURE)
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
            f"missing {', '.join(absent)}. The page's server section carries that disclosure, "
            "so a page with a fact dropped from it claims more than the relay does",
            file=sys.stderr,
        )
    return 1


def check_browser_trust(pages: list[Scanned]) -> int:
    """The page's statement that a browser guest trusts the room's own server for the client code.

    The E2EE plan's §2 closing paragraph (`selvage-protocol/ai_notes`,
    `docs/studies/e2ee-plan.md`) forbids leaving this implied by a page that claims the
    server cannot read: the fragment is never sent, but the program that reads it is, and it is
    served by the same server as the relay, so a pwned one can hand the guest a client that uses
    its own key. The mitigation the plan names first — an origin the room's server does not
    control — is not the shape the page describes, so the second half has to be said out loud,
    including which clients are installed artefacts rather than fetched ones. Required the way the
    visibility facts are, so an edit that keeps every phrase pattern green cannot drop it.
    """
    page, failures = first_page_stating(pages, BROWSER_TRUST_DISCLOSURE)
    if page is not None:
        print(
            "check-claims: the page states that a guest who opens the page the room's own "
            "server serves trusts that server for the client code as well as for the relay, and "
            "that the installed clients are not in that position"
        )
        return 0
    for where, absent in failures:
        print(
            f"check-claims: {where} does not state what the browser guest trusts: it is "
            f"missing {', '.join(absent)}. The page hands a guest the page its own server "
            "serves and says the server cannot read the room, which is the combination the plan "
            "forbids leaving implied",
            file=sys.stderr,
        )
    return 1


def check_published_extension(pages: list[Scanned]) -> int:
    """The page's install row against the identity and the registries the release publishes to.

    Required rather than permitted, for the reason the disclosures are: a `clean` fixture proves a
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


def names_wire(text: str, version: str) -> bool:
    """Whether this text names the wire version as a name of its own, not as `selvage/21`."""
    return re.search(rf"(?<![\w/]){re.escape(version)}(?![\w/])", text) is not None


def page_names(version: str, pages: list[Scanned]) -> bool:
    """Whether the page's visible text carries this wire version as a name of its own.

    The needle comes from the instance, so a page that names none of what the instance offers is
    the failure this reports rather than a scan that quietly looked for nothing. The lookarounds
    keep `selvage/2` from being satisfied by `selvage/21`.
    """
    return any(names_wire(page.text, version) for page in pages)


def wire_binding_problems(
    page: Scanned, offered: tuple[str, ...], pinned_wire: str
) -> list[str]:
    """What this page says about the wire that the artefacts behind it do not support."""
    problems: list[str] = []
    pinned = WIRE_OF_PINNED.search(page.text)
    if pinned is None:
        problems.append(
            "it never says which wire the image under the `docker run` speaks (that release "
            f"is {pinned_wire})"
        )
    elif pinned.group(1) != pinned_wire:
        problems.append(
            f"it says the pinned image speaks {pinned.group(1)!r}, and the pin "
            f"{PINNED_IMAGE_VERSION} speaks {pinned_wire}"
        )
    demo = WIRE_OF_DEMO.search(page.text)
    if demo is None:
        problems.append("it never says which wire the demo speaks")
    elif demo.group(1) not in offered:
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
    if not names_wire(page.text, WIRE):
        problems.append(f"it never names {WIRE}, the one wire version this protocol has")
    unreleased = WIRE_UNRELEASED.search(page.text)
    if unreleased is not None:
        problems.append(
            f"it calls the wire unreleased ({unreleased.group(0)!r}), and the pinned release "
            f"{PINNED_IMAGE_VERSION} speaks it (`IMAGE_WIRE_BY_TAG`)"
        )
    return problems


def check_wire_binding(pages: list[Scanned]) -> int:
    """Which wire version the page says each artefact it hands a reader speaks.

    The page hands a reader one `docker run` and one instance address, there is one wire version,
    and it is the sealed one. A page that describes sealing without saying which version does
    which invites the failure a confidentiality feature cannot have: a reader pastes the command
    under the paragraph and gets a server that carries the room through it in the clear. So the
    page has to say which wire the pinned image speaks and which wire the demo speaks, and to
    name no other version: with one version a second name is a claim about a version this protocol
    does not have, and the plaintext one is what the reader of a sealing paragraph meets when the
    pin is a release that cannot seal. The demo's half is measured, against what `/meta` offers,
    where no wording can forge it; the image's half is read from `IMAGE_WIRE_BY_TAG`, because no
    registry says what wire a binary speaks, and a release that moves the pin has to declare the
    new tag's wire in the same wave. Both halves together are what make the page's own sentence
    about the pin and the sentence about the instance agree with what a reader will actually get.

    Returns 0, 1 when the page says something the artefacts disprove, 2 when the instance cannot
    be asked or this file cannot say what the pin speaks.
    """
    root = root_of_this_checkout()
    binding = [page for page in pages if WIRE_VERSION.search(page.text)]
    if not binding:
        print(
            f"check-claims: none of {len(pages)} scanned file(s) names a wire version, and the "
            "page hands a reader a server to run: a scan that reaches no version is not "
            "checking the version",
            file=sys.stderr,
        )
        return 1
    if PINNED_IMAGE_VERSION not in IMAGE_WIRE_BY_TAG:
        print(
            f"check-claims: the pin is {PINNED_IMAGE_VERSION} and nothing here says which "
            "wire version that release speaks (see `IMAGE_WIRE_BY_TAG`); a pin whose wire is "
            "unknown cannot be held to the page's sentence about it",
            file=sys.stderr,
        )
        return 2
    pinned_wire = IMAGE_WIRE_BY_TAG[PINNED_IMAGE_VERSION]
    try:
        offered = demo_meta()[1]
    except (urllib.error.URLError, OSError, ValueError, KeyError) as error:
        print(
            f"check-claims: cannot ask {DEMO_ORIGIN} which wire versions it offers ({error}); "
            "the page says which artefact speaks which version, and the half of that sentence "
            "about the instance cannot be checked without it",
            file=sys.stderr,
        )
        return 2

    failed: list[tuple[str, list[str]]] = []
    for page in binding:
        problems = wire_binding_problems(page, offered, pinned_wire)
        if problems:
            failed.append((os.path.relpath(page.path, root), problems))
    if failed:
        for where, problems in failed:
            print(
                f"check-claims: {where} does not bind what it says to the one wire version: "
                + "; ".join(problems),
                file=sys.stderr,
            )
        return 1
    print(
        f"check-claims: the page binds its sealing claim to the one wire version the artefacts "
        f"speak — the pin {PINNED_IMAGE_VERSION} as {pinned_wire}, the demo as "
        f"{', '.join(offered)} from `/meta` — names no other version, and does not call it "
        "unreleased"
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
        check_browser_trust,
        check_published_extension,
        check_pinned_image,
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
