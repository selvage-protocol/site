#!/usr/bin/env python3
"""Fails the shipped page on a phrase the project cannot back today.

This is a filter, not a proof. It matches a list of known wordings; a false claim written in
different words, a synonym, a superlative, a wrong number the corpus does not pin, or any
sentence that is merely unbacked all pass it. What it does guarantee is narrower and still
worth having: those known wordings do not appear, even when the page wraps them across lines or
encodes the characters as HTML entities.

Three claims are asserted in the positive instead, because a phrase list cannot reach them: the
image tag in the `docker run` the page hands a reader, the instance the demo section points at —
the address it gives an editor, the wire version that address speaks, and the page a guest is sent
to — and the disclosure of what the sealed relay still sees. The address half asks the path a
plain `GET` can reach, not the upgrade: see `demo_session_route`. Each is a fact with an artefact
behind it, and a wrong tag is a command that fails rather than a wording that lies. See
`PUBLISHED_IMAGE`, `DEMO_ORIGIN` and `RELAY_DISCLOSURE` below.

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

Run from anywhere; the repository root is resolved from this file's location. Arguments are paths
(files or directories) to scan instead of the whole checkout.

    scripts/check-claims.py              # every *.html in the checkout
    scripts/check-claims.py .tmp/empty   # reaches no file: that is a failure, not a pass

Exit 0 when the page is clean of every known wording and both pins hold up, 1 when it
carries a forbidden wording or a pin is wrong, 2 when the check itself cannot run (a dead
pattern, nothing to scan, a registry that cannot be asked, or a demo host that does not answer).
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
SITE_ORIGIN = r"selvage-protocol\.vercel\.app"

DASHES = re.compile("[\u2010-\u2015\u2212\ufe58\ufe63\uff0d]")

# The page's happy path is a `docker run` a reader pastes, so the tag in it is a claim with an
# artefact behind it: a wrong tag is `manifest unknown`, not a wording a phrase list can
# enumerate. It is therefore a *required* claim, pinned once here and asserted twice: every
# reference the rendered page carries must name this version, and the registry must serve it.
#
# The registry half is the one that reaches the artefact, and it holds the distinction that
# matters: a platform entry in an image index proves only that a slot is *labelled* arm64.
# `selvaged:0.1.1` published one, and both its legs carried the amd64 binary — every layer
# digest identical across the two per-platform manifests. `0.1.0` and `0.1.1` are the two
# versions a page must never name; `0.1.2` was correct and is simply superseded. The check
# compares those digests and fails when they are the same set, which is what a mislabelled leg
# looks like, and it pulls them with no credential in the request, because no account is the
# point of the command the page hands over.
PUBLISHED_IMAGE = "ghcr.io/selvage-protocol/selvaged"
PINNED_IMAGE_VERSION = "0.2.0"
IMAGE_REFERENCE = re.compile(r"ghcr\.io/selvage-protocol/selvaged(?::([\w][\w.+-]*))?")
REGISTRY_HOST = "ghcr.io"
REGISTRY_REPOSITORY = PUBLISHED_IMAGE.split("/", 1)[1]
REQUEST_TIMEOUT_SECONDS = 20

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
DEMO_HOST = "selvage.dontblameme.dev"
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
RELAY_DISCLOSURE = (
    (
        "the room's existence",
        re.compile(r"\b(?:room|session)s?\b[^.]{0,40}\bexists?\b", re.IGNORECASE),
    ),
    (
        "its membership",
        re.compile(
            r"\bwho is in (?:it|one|the room|a room)\b|\bmembership\b|\bwho (?:has )?joined\b",
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
# A link's destination lives in an attribute, and the visible text carries only its label, so both
# are scanned: an anchor labelled with the demo host can point somewhere else entirely.
DESTINATION = re.compile(r"\b(?:href|src|action)\s*=\s*(?:\"([^\"]*)\"|'([^']*)')", re.IGNORECASE)
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
        r"salvage/1",
        "the wire version is salvage/1",
        "the wire version is `selvage/1`; 'salvage' is the near-homophone the full protocol "
        "title exists to defend against",
    ),
    Phrase(
        r"\bnobody (?:else )?can read\b"
        r"|\bonly (?:you|the (?:people|two) in the room)\b"
        r"|\bthe server learns nothing\b"
        r"|\bfully encrypted\b"
        r"|\bzero[- ]knowledge\b",
        "nobody else can read the room",
        "the relay is sealed, not omniscient: it still reads the room's existence, membership, "
        "display names, sizes and timing, and the keys are in the link a human pastes",
        (
            "nobody else can read it",
            "only the people in the room can read it",
            "the server learns nothing",
            "fully encrypted",
            "zero-knowledge relay",
        ),
        (
            "The server relays ciphertext, and cannot tell who is host.",
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
            "browse selvage-protocol.vercel.app in your browser",
            "selvage is available in your browser at selvage-protocol.vercel.app",
            "selvage-protocol.vercel.app is where a guest joins",
        ),
        (
            "The browser page joins the same room from a tab, with the invite link a host copies.",
            "A guest works in the page at https://selvage.dontblameme.dev with nothing installed.",
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
        # to contain it is describing an artefact, not claiming a frozen release. The published
        # image is `0.2.0` today, which carries no `1.0` substring at all, so the fixture below
        # is synthetic rather than the live pin; the lookbehind still has to hold for whatever
        # version a future pin carries. A 1.0 that stands on its own still matches.
        r"(?<![\d.])v?1\.0\b|production[- ]ready|production[- ]grade|battle[- ]tested|stable release",
        "the stable release, version 1.0",
        "the wire version is `selvage/1`; no shape is frozen. "
        "`0.2.0` is the version of the image that is published, not a 1.0",
        ("we are at v1.0", "the stable rele<!-- -->ase, version 1.0"),
        ("ghcr.io/selvage-protocol/selvaged:0.2.0", "0.2.0", "version 0.2.0", "tool:2.1.0"),
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
        "the host's file contents travel through the server to the peers that ask for them, and "
        "they are sealed in `selvage/2` but still leave the machine; 'only the people in the "
        "room' is false whatever the version, because whoever holds the link can read the room, "
        "its fragment included",
    ),
    Phrase(
        # The relay is sealed, so "the server cannot read" is backed only when the thing it
        # cannot read is named and is sealed material. Bare, or with the room or its membership
        # as the object, it is the overclaim the page's own paragraph refutes.
        r"\bthe server (?:cannot|can't) (?:read|see)\b"
        r"(?!\s+(?:(?:the|any|its|your|our|a|their|all|of)\s+){0,3}"
        r"(?:(?:sealed|encrypted)\s+|\w+['\u2019]s\s+)*"
        r"(?:text|ciphertext|documents?|cursors?|file ?names?|roles?|listings?|bytes|"
        r"contents?|keystrokes?)\b)"
        # Host is a peer's signed claim the server cannot make, so that one reading is backed.
        # It stays exempt only while it is the whole clause: an "or who is in the room" after it
        # is the membership claim the relay does see, and is not exempt.
        r"|\bthe server (?:cannot|can't) (?:tell|know) who\b"
        r"(?!\s+(?:is\s+(?:the\s+)?host|the\s+host\s+is)\b"
        r"(?!\s*(?:[,;:]|[-\u2013\u2014])?\s*(?:\b(?:and|or|nor|but)\b)?\s*"
        r"(?:who\b|(?:the\s+)?(?:rooms?|members?|membership|people|participants)\b)))",
        "the server cannot read anything",
        "the relay is sealed, not omniscient: it reads no text, no cursor, no file name and no "
        "role, and it cannot forge, mis-attribute or replay a frame, but it still reads a room's "
        "existence, its membership, the display names and the sizes and timing of what moves, "
        "and it can drop, delay or end any room. 'It cannot read' or 'it cannot read the room' "
        "without naming sealed material is the unqualified form, and 'it cannot tell who is in "
        "the room' is the membership claim it does see; the readings that stay legal are a "
        "claim about named, sealed material and the peer's signed claim that it cannot tell who "
        "is host",
        (
            "the server can't see anything",
            "the server cannot read",
            "the server cannot read the room",
            "the server cannot tell who is in the room",
            "the server cannot tell who is host or who is in the room",
        ),
        (
            "The documents are sealed, so the server cannot read the text.",
            "The server relays ciphertext, and cannot tell who is host.",
            "The server cannot tell who the host is.",
            (
                "It still sees that a room exists, who is in it, their names, and the sizes "
                "and timing of what moves."
            ),
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
            "A demo instance runs at https://selvage.dontblameme.dev.",
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
        "`PROTOCOL.md` §10 states the rule in force for `selvage/1`: same major alone. No corpus "
        "line puts the design at 0.x; the compatibility clause names 0.x only for a future major "
        "0, which is not this one",
    ),
    Phrase(
        rf"\b(?!34858\b){VEHICLE}\s+frame[- ]checks?\b",
        "34857 frame checks",
        "the pinned number is 34858 frame checks (`specification/schema/validate.py`); a different "
        "number is a claim the corpus disproves",
        clean=("34858 frame checks",),
    ),
    Phrase(
        rf"\b(?!31\b){VEHICLE}\s+(?:\w+\s+){{0,2}}vectors?\b",
        "30 conformance vectors",
        "the pinned number is 31 vectors (`specification/schema/validate.py`); a different number "
        "is a claim the corpus disproves, and the count is pinned wherever the word sits — the "
        "page writes both 'conformance vectors' and 'wire vectors'",
        clean=("31 conformance vectors", "the 31 wire vectors"),
    ),
    Phrase(
        rf"\b(?!8642\b){VEHICLE}\s+assertions?\b",
        "8641 assertions",
        "the pinned number is 8642 assertions (`specification/schema/validate.py`); a different "
        "number is a claim the corpus disproves",
        clean=("8642 assertions",),
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


def demo_meta() -> tuple[str, tuple[str, ...]]:
    """What the instance reports about itself from `/meta`: its name, and its wire versions.

    The request names itself rather than going out as the interpreter's default signature: the
    host is behind Cloudflare, whose bot list answers `403` (error 1010) to `Python-urllib`, and
    a check that cannot read the instance cannot assert anything about it.
    """
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
    return name, tuple(offered)


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


def page_names(version: str, pages: list[Scanned]) -> bool:
    """Whether the page's visible text carries this wire version as a name of its own.

    The needle comes from the instance, so a page that names none of what the instance offers is
    the failure this reports rather than a scan that quietly looked for nothing. The lookarounds
    keep `selvage/1` from being satisfied by `selvage/12`.
    """
    pattern = re.compile(rf"(?<![\w/]){re.escape(version)}(?![\w/])")
    return any(pattern.search(page.text) for page in pages)


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


def check_relay_disclosure(pages: list[Scanned]) -> int:
    """The page's statement of what the sealed relay still sees, required rather than permitted.

    The `clean` fixtures above only prove the phrase pattern does not reject those sentences;
    they do not make the page carry one. Each fact the paragraph states has a pattern of its
    own, so a rewritten paragraph that keeps the facts passes and one that drops a fact fails.
    Deleting the paragraph fails too, and the sizes-and-timing fact is the one nothing else on
    the page states. Returns 0 when a scanned page carries all four and 1 when none does; it
    asks no network.
    """
    root = root_of_this_checkout()
    failures: list[tuple[str, list[str]]] = []
    for page in pages:
        absent = [
            label for label, pattern in RELAY_DISCLOSURE if not pattern.search(page.text)
        ]
        if not absent:
            print(
                "check-claims: the page states what the sealed relay still sees — the room's "
                "existence, its membership, the display names and the sizes and timing of "
                "what moves"
            )
            return 0
        failures.append((os.path.relpath(page.path, root), absent))
    for where, absent in failures:
        print(
            f"check-claims: {where} does not state what the sealed relay still sees: it is "
            f"missing {', '.join(absent)}. The page's server section carries that disclosure, "
            "so a page with a fact dropped from it claims more than the relay does",
            file=sys.stderr,
        )
    return 1


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
        for evasion in phrase.evasions:
            if not pattern.search(normalise(evasion)[0]):
                print(
                    f"check-claims: the pattern {phrase.pattern!r} does not match its evasion "
                    f"sample {evasion!r}; the claim is written in a shape the pattern misses",
                    file=sys.stderr,
                )
                return 2
        for wording in phrase.clean:
            if pattern.search(normalise(wording)[0]):
                print(
                    f"check-claims: the pattern {phrase.pattern!r} matches its clean fixture "
                    f"{wording!r}; honest wording is a false positive",
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
    scanned: list[Scanned] = []
    for path in paths:
        with open(path, encoding="utf-8") as handle:
            raw = handle.read()
        text, line_of = normalise(raw)
        scanned.append(
            Scanned(
                path=path,
                text=text,
                line_of=line_of,
                destinations=destinations(raw),
            )
        )
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

    for check in (check_relay_disclosure, check_pinned_image, check_demo_instance):
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
