#!/usr/bin/env python3
"""Fails the shipped page on a phrase the project cannot back today.

This is a filter, not a proof. It matches a list of known wordings; a false claim written in
different words, a synonym, a superlative, a wrong number the corpus does not pin, or any
sentence that is merely unbacked all pass it. What it does guarantee is narrower and still
worth having: those known wordings do not appear, even when the page wraps them across lines or
encodes the characters as HTML entities.

Facts are asserted in the positive instead, because a phrase list cannot reach them: the images
the section's `docker run`s hand a reader and which of the two sits on which run, the
instance the demo section points at — the address
it gives an editor and the page a guest is sent to — the wire the tags and that address each speak,
held together and to no version this protocol does not have, the disclosures the page owes a reader
of what the sealed relay still sees and of the terms `selvaged` is under, and the identity the
extension is published under with the two
registries the release publishes it to and what an
install is and is not, and the JetBrains plugin's listing, which the Marketplace has to say is
public. The address half asks the path a plain `GET` can reach and the upgrade the clients open on
it: the path has to reach the server with the server's own JSON, and a `4xx` that is not that is the
edge in front of the demo refusing the check's own egress rather than the server answering, which a
run records instead of asserting (see `demo_session_route` and `demo_upgrade_route`). Each is a
fact with an artefact behind it, and a wrong tag is a command that fails rather than a wording that
lies. See
`PUBLISHED_IMAGES`, `DEMO_ORIGIN`, `RELAY_DISCLOSURE`, `FSL_DISCLOSURE`, `PUBLISHED_EXTENSION`,
`JETBRAINS_LISTING`, `check_run_section_command`, `check_run_section_address`,
`check_command_prompt_selection`, `check_wire_binding` and `check_jetbrains_listing` below.

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
dead pattern, nothing to scan, a registry that cannot be asked, or a demo host or the JetBrains
Marketplace that does not answer).
"""

from __future__ import annotations

import ast
import base64
import hashlib
import html
import json
import os
import re
import socket
import ssl
import sys
import traceback
import urllib.error
import urllib.request
from collections.abc import Callable, Iterable
from dataclasses import dataclass
from urllib.parse import urlsplit

# Directories that never hold the shipped page.
SKIP_DIRS = {".git", ".tmp", "node_modules"}

# A claimed corpus number that is not the one `specification/schema/validate.py` pins is a wrong
# number the page would otherwise show without failing anything. The lookahead is what makes the
# pinned value the only one that passes. There are two layers and each is pinned on its own — the
# wire corpus's 25 vectors, 33,784 frame checks and 8,394 assertions, and the peer corpus's 27
# vectors, 232 checks and 74 assertions — so a number before one of those nouns has to be that
# layer's pin, and the peer layer's count is written with the layer named ('27 peer vectors').
#
# The wire layer's two largest counts are written with their thousands separated on the page,
# because a reader has to read them; `33,?784` accepts either spelling so a count written without
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
# reference the rendered page carries must be one of the two below, and the registry must serve
# it.
#
# Two packages are involved, and a reader needs both: the server is the room, and the page image
# is the browser client, which reaches that room across the network the two containers share. Each
# has a tag of its own, so a page that names one of the two where the other belongs fails on the
# reference that is missing rather than passing on the one it got right.
#
# The tag is one the release publishes rather than a version, because a version written into a
# reader's command goes stale the moment the page's copy of it does. `latest` resolves to a built
# artefact all the same, which is what the registry half reaches, and any other tag on the page
# fails the first half rather than passing as a live command.
#
# The registry half is the one that reaches the artefact, and it holds the distinction that
# matters: a platform entry in an image index proves only that a slot is *labelled* arm64.
# The check compares the layer digests of the two per-platform manifests and fails when they are
# the same set, which is what a mislabelled leg
# looks like, and it pulls them with no credential in the request, because no account is the
# point of the command the page hands over. It runs per package, so the page half of the command
# is held to the same proof as the server half.
PUBLISHED_IMAGES = (
    "ghcr.io/selvage-protocol/selvaged",
    "ghcr.io/selvage-protocol/selvage-web",
)
PUBLISHED_IMAGE_TAG = "latest"
# The two references the page may print, in the order its commands name them. `SERVER_IMAGE` is
# the artefact the demo instance reports from `/meta`; `PAGE_IMAGE` is the one that relays to it.
SERVER_IMAGE, PAGE_IMAGE = PUBLISHED_IMAGES
IMAGE_REFERENCES = tuple(f"{image}:{PUBLISHED_IMAGE_TAG}" for image in PUBLISHED_IMAGES)
# The same pair as the section prints them, tag and all: the section prints the repository alone, because
# a bare repository is the tag above, and what the section's own reading compares is the reference.
SERVER_REFERENCE, PAGE_REFERENCE = IMAGE_REFERENCES
# Every reference under the project's own namespace, so a typo, another tag or a package the
# project does not publish is read and refused rather than passed over for naming nothing. The
# tag cannot end on a dot, which is how a sentence ends.
IMAGE_REFERENCE = re.compile(
    r"ghcr\.io/selvage-protocol/[\w-]+(?:\.[\w-]+)*(?::[\w](?:[\w.+-]*[\w+-])?)?"
)


def with_default_tag(reference: str) -> str:
    """A reference with no tag written as the `:latest` docker reads it as.

    The section prints the repository alone — `ghcr.io/selvage-protocol/selvaged` — because docker
    reads a bare repository as `:latest` and the shorter string is the one a reader reads. The
    reference is what is compared, so both spellings are read as the same one and any other tag is
    still a reference this project does not publish. The tag has one home: `PUBLISHED_IMAGE_TAG`
    above.
    """
    _, _, tail = reference.rpartition("/")
    return reference if ":" in tail else f"{reference}:{PUBLISHED_IMAGE_TAG}"


REGISTRY_HOST = "ghcr.io"
REQUEST_TIMEOUT_SECONDS = 20

# The Run section hands a reader three commands, one line each, and this host has no Docker, so what
# is read is the shape of those commands rather than the run itself: the network the two containers
# share is created in the first, before either run names it, and the server and the page are started
# in the others; every run is detached,
# because one that is not holds the reader's terminal instead of returning their prompt; every run
# joins the network the first command creates, read as a whole name, because that is how the page
# reaches its server; the address the page container is given names the server container on that
# network, and sits on the run that publishes the port a reader opens; each of the two runs carries
# the reference the project publishes for it, the page image on the run the address is given to and
# the server's on the other, and the server's run publishes nothing, because the page's own `-p`
# would collide with it and the page would never start.
RUN_BLOCK_CLASS = "command"
# The section's printed blocks, in the order the page puts them: one command each, so a reader who
# selects one does not take the next with it. The class is matched
# as a whole name rather than a prefix, or the `command-line` paragraphs inside a block would be
# read as blocks of their own.
COMMAND_BLOCK = re.compile(
    rf'<(?P<tag>[a-z][\w-]*)\b[^>]*\bclass="[^"]*(?<![\w-]){re.escape(RUN_BLOCK_CLASS)}(?![\w-])[^"]*"[^>]*>',
    re.IGNORECASE,
)
# One printed line of a block.
RUN_BLOCK_LINE = re.compile(
    r'<p\b[^>]*\bclass="[^"]*\bcommand-line\b[^"]*"[^>]*>(?P<line>.*?)</p>',
    re.IGNORECASE | re.DOTALL,
)
CONTAINER_NAME = re.compile(r"--name[=\s]+(?P<name>[^\s;|&]+)")
NETWORK_CREATE = re.compile(r"\bdocker\s+network\s+create\b")
# The network a run attaches its container to: the page reaches its server by that name, so a
# container on another network is one the page cannot reach.
NETWORK_FLAG = re.compile(r"--network[=\s]+(?P<name>[^\s;|&]+)")
# The address a container is pointed at its server with. The host in it is a claim of its own:
# the command has to give some container that name, on the network they share.
SERVER_ADDRESS = re.compile(r"-e\s+SELVAGE_SERVER=(?P<url>[^\s;|&]+)")
# The container a reader opens, which is the one that address belongs on: the page image serves
# that port and relays through it, so an address the command gives to another container is one
# the page never sees.
PUBLISHED_PORT = re.compile(r"(?:\s|^)(?:-p|--publish)[=\s]")
# The mapping that flag publishes, so the address on this machine can be read out of it and
# compared with the address the section prints. Docker's form is
# `[host-ip:][host-port:]container-port[/proto]`, and only the field before the last colon is a port
# on the host: `-p 8080` publishes the container's port on one docker picks, which is not an
# address a page can tell a reader to open. The host it names is read beside the port, because the
# section's own address is a claim about both: `-p 192.168.1.5:8080:8080` publishes the page where a
# browser sent to `http://127.0.0.1:8080/` never reaches it.
PUBLISHED_MAPPING = re.compile(r"(?:\s|^)(?:-p|--publish)[=\s](?P<mapping>[^\s;|&]+)")
# The loopback the section's own address may name, in the two spellings `RUN_OPENED_AT` accepts. A
# mapping that names one of these on its host side publishes where the address the section prints
# reaches; a mapping that names no host at all is left to docker and is read as naming none.
LOOPBACK_NAMES = ("127.0.0.1", "localhost")
# The address the section tells a reader to open, read out of the section's own text rather than off the
# command: the run's `-e SELVAGE_SERVER` is the address the page container relays to, and this is
# the one a browser opens. They are two copies of one fact, which is why they are compared. The
# lookahead is where the address ends rather than a character to consume — a slash, a space or a
# full stop after it is the prose around it, while a colon or a word character means what matched
# is not the address — so what the rule is handed is the address itself and not the space after it.
RUN_OPENED_AT = re.compile(r"http://(?:127\.0\.0\.1|localhost)(?::(?P<port>\d+))?(?![\w:])")
# Where the Run section is drawn: the page's own section between the band and the clients, the one
# that puts the three commands in it, above the terminal a reader installs one from.
RUN_SECTION_CLASS = "run-section"
# Where one command in a chain ends and the next begins: a block is one line the section prints, and
# a line may be several clauses.
COMMAND_SEPARATOR = re.compile(r";|&&")
DOCKER_RUN = re.compile(r"\bdocker\s+run\b")
# The detachment a run needs, alone or among bundled short flags. Without it the run holds the
# reader's terminal instead of returning their prompt.
DETACHED = re.compile(r"(?:\s|^)(?:-\w*d\w*|--detach)(?=\s|$)")

# The section prints two kinds of text that are not the command: the `$ ` prompt in front of a
# block's command, and the label above the block. Both sit inside the selection a reader makes
# over the section, so both have to be out of it — a `$ ` or a label pasted into a shell is a
# command that does not exist — and that is a property of the stylesheet the served page loads
# rather than of its markup: the prompt is drawn by a rule, and deleting the rule brings the
# pasted prompt back with nothing else in the tree to say so. The prompt's class is read out of
# the page's own markup, so a section that renames the prompt and its rule together still passes;
# the label's is named here, the way `command-line` is.
RUN_BLOCK_LABEL_CLASS = "command-label"
# An element that carries a class, with the names read as whole words, or `command-line` would
# answer for `command-label`.
CLASSED_ELEMENT = re.compile(
    r'<(?P<tag>[a-z][\w-]*)\b[^>]*\bclass="(?P<classes>[^"]*)"[^>]*>', re.IGNORECASE
)
# The innermost elements of a markup, with their attributes and their own text: the prompt is the
# element whose whole text is the `$ ` the section prints.
INNER_ELEMENT = re.compile(
    r'<(?P<tag>[a-z][\w-]*)\b(?P<attrs>[^>]*)>(?P<text>[^<]*)</(?P=tag)>', re.IGNORECASE
)
CLASS_ATTRIBUTE = re.compile(r'\bclass="(?P<classes>[^"]*)"', re.IGNORECASE)
# The stylesheet the served page loads, named in the page's own markup: the `rel` and the `href`
# of a `link` element. The build puts the files a browser is served under `static/`, which
# `next start` answers under the `/_next/static/` prefix, so that is the part of the build this
# reads and the part a page naming anything else is refused for.
STYLESHEET_LINK = re.compile(r"<link\b[^>]*>", re.IGNORECASE)
STYLESHEET_REL = re.compile(r"\brel=\"(?P<rel>[^\"]*)\"", re.IGNORECASE)
STYLESHEET_HREF = re.compile(r"\bhref=\"(?P<href>[^\"]*)\"", re.IGNORECASE)
BUILD_PREFIX = "/_next/static/"
# The declaration that keeps an element out of a selection, and the rule that has to carry it:
# the selector is read too, so a rule taking some other element out of a selection does not
# stand in for the class the page actually prints.
USER_SELECT_NONE = re.compile(r"(?:^|[\s;{])user-select\s*:\s*none\b", re.IGNORECASE)
CSS_RULE = re.compile(r"(?P<selectors>[^{}@]+)\{(?P<body>[^{}]*)\}", re.DOTALL)

# The section's command is read as a shape, and a shape read by matching is worth no more than what
# it is matched against, so every rule below carries its own fixture: one command in the shape the
# section prints, and a variant per rule `run_section_problems` can report, each pinning the fragment
# that rule emits so deleting the rule reddens the loop rather than leaving one nothing reads.
# They are written with names of their own rather than with the page's, so they are the shapes and
# not a second copy of the section, and `main` runs them before it scans anything: a rule that stops
# finding its shape, or that starts failing the correct one, fails the check itself rather than
# reporting a page clean. The rules about which of the two published references sits on which run
# name them in their fixtures, because a shape with names of its own says nothing about those.
#
# What is not fixtured this way is what is not a command string: the `$ ` prompt and label pin and
# the refusal to pass when a scanned page carries no Run section block read a served page and the
# stylesheet its build produced, so their fixture would be a page and a build rather than a line.
RUN_FIXTURE_NETWORK = "docker network create room"
RUN_FIXTURE_SERVER = (
    "docker run -d --rm --name server --network room example/server:1"
)
RUN_FIXTURE_PAGE = (
    "docker run -d --rm --name page --network room"
    " -p 127.0.0.1:8080:8080 -e SELVAGE_SERVER=http://server:8080 example/page:1"
)
RUN_FIXTURE_BLOCKS = (
    RUN_FIXTURE_NETWORK,
    RUN_FIXTURE_SERVER,
    RUN_FIXTURE_PAGE,
)


# The rules about which of the two references the page hands a reader sits on which run have
# nothing to read in a shape written with names of its own, because what they compare is those
# references. Their fixtures put them in, taken from the constants this file holds the page to
# rather than typed in, so a fixture cannot go stale against the command it is a variant of.
def with_project_images(server_reference: str, page_reference: str) -> tuple[str, ...]:
    """The fixture's blocks with the two published references in place of the example ones."""
    return (
        RUN_FIXTURE_NETWORK,
        RUN_FIXTURE_SERVER.replace("example/server:1", server_reference),
        RUN_FIXTURE_PAGE.replace("example/page:1", page_reference),
    )


RUN_FIXTURE_NAMED = with_project_images(SERVER_REFERENCE, PAGE_REFERENCE)
RUN_FIXTURE_SWAPPED = with_project_images(PAGE_REFERENCE, SERVER_REFERENCE)
# The section prints the two references without their tags, and docker reads a bare repository as
# `:latest`, so this is one of the correct shapes: it is the section's own, and the fixture below
# holds the reading that makes it the pinned reference.
RUN_FIXTURE_BARE = with_project_images(SERVER_IMAGE, PAGE_IMAGE)


def run_fixture(
    *edits: tuple[int, str, str],
    dropped: tuple[int, ...] = (),
    blocks: tuple[str, ...] = RUN_FIXTURE_BLOCKS,
) -> tuple[str, ...] | None:
    """The correct command with `edits` written into it, or None when one of them does not apply.

    An edit names a block, the text it replaces in it and what replaces it. The text has to be
    there: a fixture that no longer names the shape it is a variant of is reported rather than
    quietly becoming the correct command, which is how a rule stops being read. `dropped` leaves a
    whole block out, for the defects that are a block that should not be there, and `blocks` is the
    shape the edits are written into, for the variants of the one carrying the project's images.
    """
    lines = list(blocks)
    for block, before, after in edits:
        if block >= len(lines) or before not in lines[block]:
            return None
        lines[block] = lines[block].replace(before, after)
    return tuple(line for index, line in enumerate(lines) if index not in dropped)


# `(what, the blocks it runs, the fragment of the rule it has to be reported as)`, the fragment
# empty for the variants that are a correct command and have to come back clean.
RUN_FIXTURES: tuple[tuple[str, tuple[str, ...] | None, str], ...] = (
    (
        "a server container left in the foreground",
        run_fixture(
            (1, "docker run -d --rm --name server", "docker run --rm --name server")
        ),
        "runs a container without `-d`",
    ),
    (
        "a page container left off the network the server is on",
        run_fixture((2, "--name page --network room", "--name page --network other")),
        "runs a container that is not on room",
    ),
    (
        "a page container on a network the one the run creates starts with",
        run_fixture(
            (2, "--name page --network room", "--name page --network room-net")
        ),
        "runs a container that is not on room",
    ),
    (
        "a command that creates no network for the two containers",
        run_fixture((0, "docker network create room", "docker network inspect room")),
        "does not create the network the two containers share",
    ),
    (
        "a command that creates the network after the runs that join it",
        (
            RUN_FIXTURE_SERVER,
            RUN_FIXTURE_PAGE,
            RUN_FIXTURE_NETWORK,
        ),
        "runs a container before the command that creates room",
    ),
    (
        "a command that gives no container the relay address",
        run_fixture((2, " -e SELVAGE_SERVER=http://server:8080", "")),
        "gives no container `-e SELVAGE_SERVER`",
    ),
    (
        "an address that names a container nothing else is named",
        run_fixture(
            (2, "SELVAGE_SERVER=http://server:8080", "SELVAGE_SERVER=http://other:8080")
        ),
        "gives no other container the name 'other'",
    ),
    (
        "an address whose host is the start of a container the run does name",
        run_fixture(
            (1, "--name server --network room", "--name server-net --network room")
        ),
        "gives no other container the name 'server'",
    ),
    # The empty name is what both readings answer when there is nothing to read, and two of those
    # compared equal: the address `http://:8080` names no host and a run given no `--name` names no
    # container, so this page passed a rule whose whole question is whether the address reaches a
    # container. Each half is fixtured, and the two together are the shape that passed.
    (
        "an address that names no host",
        run_fixture(
            (2, "SELVAGE_SERVER=http://server:8080", "SELVAGE_SERVER=http://:8080")
        ),
        "names no host in it",
    ),
    (
        "an address in the bare form that names no host",
        run_fixture(
            (2, "SELVAGE_SERVER=http://server:8080", "SELVAGE_SERVER=:8080")
        ),
        "gives no other container the name ':8080'",
    ),
    (
        "an address that names no host beside a run that gives its container no name",
        run_fixture(
            (1, "--name server --network room", "--network room"),
            (2, "SELVAGE_SERVER=http://server:8080", "SELVAGE_SERVER=http://:8080"),
        ),
        "names no host in it",
    ),
    (
        "an address that names a container no run is named",
        run_fixture((1, "--name server --network room", "--network room")),
        "gives no other container the name 'server'",
    ),
    (
        "an address on a container that publishes no port",
        run_fixture((2, " -p 127.0.0.1:8080:8080", "")),
        "to a container that publishes no port",
    ),
    (
        "a command that runs no container",
        run_fixture(dropped=(1, 2)),
        "runs no container",
    ),
    (
        "a command whose two runs carry each other's image",
        RUN_FIXTURE_SWAPPED,
        "gives `-e SELVAGE_SERVER` to the run carrying",
    ),
    (
        "the page image on the run the address is not given to",
        run_fixture(
            (1, f"--network room {SERVER_REFERENCE}", f"--network room {PAGE_REFERENCE}"),
            blocks=RUN_FIXTURE_NAMED,
        ),
        "is the container the server's image belongs on",
    ),
    (
        "the addressed run carrying a reference the page image's is the start of",
        run_fixture(
            (2, PAGE_REFERENCE, f"{PAGE_REFERENCE}-extra"),
            blocks=RUN_FIXTURE_NAMED,
        ),
        "the address belongs on the page image",
    ),
    (
        "a run carrying a reference the server image's is the start of",
        run_fixture(
            (1, SERVER_REFERENCE, f"{SERVER_REFERENCE}-extra"),
            blocks=RUN_FIXTURE_NAMED,
        ),
        "is the container the server's image belongs on",
    ),
    (
        "a server run that publishes a port of its own",
        run_fixture(
            (
                1,
                f"--network room {SERVER_REFERENCE}",
                f"--network room -p 127.0.0.1:8080:8080 {SERVER_REFERENCE}",
            ),
            blocks=RUN_FIXTURE_NAMED,
        ),
        "publishes a port on the run carrying the server image",
    ),
    (
        "a run whose option carries the other image's reference",
        run_fixture(
            (
                1,
                f"--name server --network room {SERVER_REFERENCE}",
                f"--name server --network room --label note={PAGE_REFERENCE} "
                f"{SERVER_REFERENCE}",
            ),
            blocks=RUN_FIXTURE_NAMED,
        ),
        "",
    ),
    (
        "the same command with the address in the bare form the READMEs document",
        run_fixture(
            (2, "SELVAGE_SERVER=http://server:8080", "SELVAGE_SERVER=server:8080")
        ),
        "",
    ),
    (
        "the section's own shape, with the two references printed without their tags",
        RUN_FIXTURE_BARE,
        "",
    ),
    (
        "a third run the section publishes no image for",
        run_fixture(
            (
                2,
                f"-e SELVAGE_SERVER=http://server:8080 {PAGE_REFERENCE}",
                f"-e SELVAGE_SERVER=http://server:8080 {PAGE_REFERENCE}"
                " && docker run -d --rm --name other --network room example/other:1",
            ),
            blocks=RUN_FIXTURE_NAMED,
        ),
        "is given no `-e SELVAGE_SERVER`, and the section hands a reader two runs",
    ),
)

# The address the section tells a reader to open and the address its command publishes on are two
# copies of one fact, and nothing compared them: the section prints `http://127.0.0.1:8080/`, the
# command maps `-p 127.0.0.1:8080:8080`, and a command that publishes something else — another
# port, or the same port on another address — sends the reader to an address its own section says
# answers. `(what, the address the section prints, the blocks it prints beside it, the fragment of the
# rule that pair has to be reported as)`, the fragment empty for the pair that agrees.
RUN_OPENED_AT_FIXTURES: tuple[tuple[str, str, tuple[str, ...] | None, str], ...] = (
    (
        "a section whose command publishes another port than the one it prints",
        "http://127.0.0.1:9090/",
        RUN_FIXTURE_BLOCKS,
        "publishes 8080 and the section tells the reader to open http://127.0.0.1:9090/",
    ),
    (
        "a section whose address names no port",
        "http://127.0.0.1/",
        RUN_FIXTURE_BLOCKS,
        "names no port",
    ),
    (
        "a command that publishes the container's port on one docker picks",
        "http://127.0.0.1:8080/",
        run_fixture((2, "-p 127.0.0.1:8080:8080", "-p 8080")),
        "publishes no port on the host",
    ),
    # The host and the container port of a mapping are the two readings this check found
    # unfixtured: every fixture it had mapped `8080:8080`, where the field before the colon and the
    # one after it are the same number, so a reading of the container port answered for the host
    # port and a section over a mapping those two fields disagree in was never read.
    (
        "a command that publishes the host port on a container port of its own",
        "http://127.0.0.1:9090/",
        run_fixture((2, "-p 127.0.0.1:8080:8080", "-p 127.0.0.1:9090:8080")),
        "",
    ),
    (
        "a command that publishes the page on another address than the section prints",
        "http://127.0.0.1:8080/",
        run_fixture((2, "-p 127.0.0.1:8080:8080", "-p 192.168.1.5:8080:8080")),
        "publishes on 192.168.1.5 and the section tells the reader to open http://127.0.0.1:8080/",
    ),
    (
        "a command that publishes the page on the other loopback",
        "http://127.0.0.1:8080/",
        run_fixture((2, "-p 127.0.0.1:8080:8080", "-p [::1]:8080:8080")),
        "publishes on ::1 and the section tells the reader to open http://127.0.0.1:8080/",
    ),
    # Every interface is not the loopback the section prints, and this is what the host half of the
    # comparison does with it: `0.0.0.0` is a host a mapping names, so it is compared and refused,
    # where a mapping that names none is left to docker and passes.
    (
        "a command that publishes the page on every interface",
        "http://127.0.0.1:8080/",
        run_fixture((2, "-p 127.0.0.1:8080:8080", "-p 0.0.0.0:8080:8080")),
        "publishes on 0.0.0.0 and the section tells the reader to open http://127.0.0.1:8080/",
    ),
    (
        "a command that names the section's own loopback on a host port of its own",
        "http://localhost:9090/",
        run_fixture((2, "-p 127.0.0.1:8080:8080", "-p 127.0.0.1:9090:9090")),
        "",
    ),
    (
        "the section's own address against the address its own command publishes on",
        "http://127.0.0.1:8080/",
        RUN_FIXTURE_BLOCKS,
        "",
    ),
)

# The wire version this protocol has, and which wire each artefact the page hands a reader speaks.
# The page hands a reader artefacts whose wire is a fact about them, not a wording: under this
# version the room's bytes reach the server sealed, so a page that puts the sealing claim over a
# command yielding a relay that cannot seal is a silent downgrade. The map is a constant rather
# than a measurement because nothing on a registry answers what wire version a binary speaks: an
# index will say `linux/arm64` and nothing about the frames inside. A reference with no entry fails
# the check instead of defaulting, so a release that points one at a different wire has to declare
# it in the same wave — this map, `PUBLISHED_IMAGE_TAG` and the page's sentence about it move
# together, and `check_wire_binding` is what holds the last of the three to the first two.
#
# The entry is keyed by the full reference rather than by the tag, because two packages carry that
# tag now: the tag is a moving name, and what the entry refuses is a reference whose wire nobody
# has declared rather than a tag that has moved. Both packages speak the one wire version — the
# server seats it, and the page image carries the client that reaches it, so a page image built
# from a client speaking another wire would be refused by the server the command puts beside it.
WIRE = "selvage/2"
IMAGE_WIRE_BY_REFERENCE = {
    reference: WIRE for reference in IMAGE_REFERENCES
}
WIRE_VERSION = re.compile(r"\bselvage/\d+\b")

# The demo section points at a running instance, a claim with an artefact behind it in the same
# way the `docker run` is. Four sentences around it are checkable here: an instance of the server
# runs at that host, the address the section hands an editor hosts a room on it, that editor
# speaks a wire version the instance offers, and the browser row's guest page is served there. A
# host that has moved, a box that is down, or a box that answers only part of that is a false
# sentence, and no phrase list can enumerate those.
#
# `PUBLISHED_IMAGE_TAG` is asserted against the registry, as the tag the `docker run` hands a
# reader.
DEMO_HOST = "selvage-demo.dontblameme.dev"
DEMO_ORIGIN = "https://" + DEMO_HOST
# Every reference the page may carry to that host: the instance's own origin. It is the only
# address on that host the page may hand a reader. The session address is the origin as well, with
# no path. The
# clients append the endpoint path themselves (`sessionUrl` in the engines both clients vendor), so
# the two forms are not interchangeable: an address already carrying the path gets a second one
# appended and the socket is refused, which is why the full form is not an allowed reference.
DEMO_REFERENCES = (DEMO_ORIGIN, "wss://" + DEMO_HOST)
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
# decides for itself and not a statement of relay visibility at all. A loose pattern would let
# that paragraph stand in for the panel's statement, so the two are read as the panel's wording:
# `who is in it` is the panel's wording and `who is in one` is the donor's;
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
# wire layer's 25 vectors, 33,784 frame checks and 8,394 assertions, and the peer layer's 27
# vectors, 232 checks and 74 assertions are all constants in `specification/schema/validate.py`.
# The page shows none of them, because they move as the corpus grows, and names the file
# instead, which is where a reader reads the current ones. A number the page hands a reader with
# no file beside it is one the reader cannot check, so a count that comes back is held to the same
# citation.
# Where a sentence ends in the visible text. A bare `.` is not one: the file this check reads
# for is `schema/validate.py`, and cutting a window at the period before its `py` truncated the
# citation out of the very sentence that carries it.
SENTENCE_END = re.compile(r"\.(?=\s|$)")
CORPUS_COUNTS = (
    # Both spellings the forbidden-number rules accept: `25 conformance vectors` and `25 wire
    # vectors` are the same pin, and a citation rule that matched only one of them would leave
    # the other wording unguarded — the count would not be seen at all, so nothing would ask it
    # for a file.
    (re.compile(r"\b25 (?:conformance|wire) vectors\b"), "the 25 wire vectors"),
    (re.compile(r"\b33,?784 frame[- ]checks\b"), "33,784 frame checks"),
    (re.compile(r"\b8,?394 assertions\b"), "8,394 assertions"),
    (re.compile(r"\b27 peer vectors\b"), "27 peer vectors"),
    (re.compile(r"\b232 peer checks\b"), "232 peer checks"),
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
# Naming the two registries is required, and what is forbidden is a registry the project does not
# publish to — or "the extension gallery" without naming one, which is a channel the page cannot
# point at.
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
# page that links a listing has to link one of these two, so a listing that is not one of them
# fails on the destination rather than on the label.
EXTENSION_LISTINGS = (
    "https://marketplace.visualstudio.com/items?itemName=" + PUBLISHED_EXTENSION,
    "https://open-vsx.org/extension/" + PUBLISHED_EXTENSION.replace(".", "/"),
)
REGISTRY_LISTING = re.compile(
    r"marketplace\.visualstudio\.com/items\b|open-vsx\.org/extension/"
    r"|plugins\.jetbrains\.com/plugin/",
    re.IGNORECASE,
)

# The JetBrains plugin and its one listing. The plugin is a client of its own and the JetBrains
# Marketplace is not one of the extension's registries, so it is pinned apart from them: the route
# that hands the plugin over has to name the Marketplace and link this listing, any other link to a
# plugin listing fails on its destination, and the Marketplace has to say the listing is public.
# JetBrains reviews each version by hand before it is listed for everyone, and until then the
# version answers `"approve": false`; a route that sends a reader to the listing before a version is
# approved sends them to a plugin they cannot install yet, so the approval is asked for rather than
# assumed. The plugin's own `approve` is not that fact: it stays false on a plugin whose approved
# version the IDE already installs, so the versions are what is read.
JETBRAINS_PLUGIN_ID = 34763
JETBRAINS_LISTING_PATH = f"/plugin/{JETBRAINS_PLUGIN_ID}-selvage"
JETBRAINS_LISTING = "https://plugins.jetbrains.com" + JETBRAINS_LISTING_PATH
JETBRAINS_LISTING_API = f"https://plugins.jetbrains.com/api/plugins/{JETBRAINS_PLUGIN_ID}"
JETBRAINS_VERSIONS_API = JETBRAINS_LISTING_API + "/updates"
# The route's key: the install panel's id, which is the client's id in `lib/clients.ts`.
JETBRAINS_ROUTE = "jetbrains"
JETBRAINS_REGISTRY = (
    "the JetBrains Marketplace",
    re.compile(r"\bJetBrains\s+Marketplace\b", re.IGNORECASE),
)
# Every listing a link on the page may point at.
KNOWN_LISTINGS = (*EXTENSION_LISTINGS, JETBRAINS_LISTING)

# Registry-shaped words. Every one the page carries has to be part of one of the names above, the
# extension's two registries or the JetBrains Marketplace, so a page that also offers a client from
# somewhere else ("the extension gallery", the Eclipse marketplace, another editor's store) fails
# instead of passing on the names it carries as well. A bare "registry" is deliberately not here:
# `ghcr.io` is one, and the image section may name it.
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
# requiring it.
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
        # browser" makes); joining without the invite link a host copies; the denial that nothing
        # runs in a page; and the claim that the project's own landing page is a place to join a
        # room.
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
        # The denial the published artefacts refute: `reference_server/Dockerfile` builds the
        # anonymously pullable `ghcr.io/selvage-protocol/selvaged:latest`, `web_client/Dockerfile`
        # builds `ghcr.io/selvage-protocol/selvage-web:latest`, `reference_server/compose.yaml`
        # runs the server, and `reference_server/deploy/selvage-update.service` is the systemd
        # unit the demo box installs. A page saying none of that exists states the opposite of
        # the truth.
        r"\bno (?:image|container) to pull\b|\bnothing to install on the server\b"
        r"|\bno compose (?:file|configuration)\b|\bno systemd (?:service|unit)\b",
        "there is no image to pull and no service unit to install in any repository yet",
        "the images are published (`ghcr.io/selvage-protocol/selvaged:latest` and "
        "`ghcr.io/selvage-protocol/selvage-web:latest`) and pull with no account, "
        "`reference_server/compose.yaml` runs the server, and "
        "`reference_server/deploy/selvage-update.service` is the systemd unit the demo box "
        "installs: a page saying none of that exists states the opposite of the truth",
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
        # The JetBrains client is the second implementation: Kotlin, written from the
        # specification, passing the peer corpus and sharing rooms with the TypeScript engine
        # through a real server. What that shows is two implementations agreeing, so the page says
        # what the JetBrains client is and leaves the protocol's interoperability unclaimed.
        r"interoperab\w*",
        "the clients are interoperable",
        "two implementations exist, the TypeScript engine the VS Code, Neovim and browser "
        "clients share and the JetBrains client's Kotlin engine written from the specification, "
        "and two implementations agreeing is evidence about those two rather than a property of "
        "the protocol; say what the JetBrains client is instead",
        ("the clients are interop<!-- -->erable", "the protocol guarantees interoperability"),
        (
            "The JetBrains plugin is a separate implementation, written in Kotlin from the "
            "specification.",
            "The other clients share one TypeScript engine.",
        ),
    ),
    Phrase(
        # The extension is published under both registries, so the denial is what a rewrite would
        # reach for and what this forbids. The registries themselves are the other half of the
        # rule, in `check_published_extension`: this one only stops the page saying there are
        # none.
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
        "own validator pins (25 vectors, 33,784 frame checks, 8,394 assertions)",
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
        "keeps no work, nothing promises it is up, and it is not sized for a team, so the shape "
        "of a free tier of a service is a claim about a product that does not exist",
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
        # The project states nothing about how the instance may be used: the repository licences
        # are the whole of it, and they are not a non-commercial one
        # either — the workspace and clients are MIT OR Apache-2.0, `crates/selvaged` is
        # FSL-1.1-MIT, and the specification's prose, schema and vectors are CC-BY-4.0 — so a
        # non-commercial term asserted of the software, or of the instance, claims a restriction
        # nobody wrote.
        r"\bnon-?commercial licen[cs]e\b"
        r"|\b(?:licen[cs]e|software|project|selvage|selvaged|workspace|clients?|source"
        r"|instance|demo|server|box)\b"
        r"[^.]{0,12}\b(?:is|are|stays?|remains?|becomes?)\b[^.]{0,8}\bnon-?commercial\b",
        "the non-commercial licence covers the project",
        "the project's licences are not non-commercial: the workspace and the clients are "
        "MIT OR Apache-2.0, `crates/selvaged` is FSL-1.1-MIT, which reserves commercial hosting "
        "for its licensor, and the specification's prose, schema and vectors are CC-BY-4.0. The "
        "instance carries no term of its own either — the repository licences are the whole of "
        "what the project states about use — so naming the software or the instance "
        "non-commercial claims a restriction nobody wrote",
        (
            "Selvage is non-commercial software",
            "the project is non-commercial",
            "selvaged has a non-commercial licence",
            "The demo instance is non-commercial and for personal and evaluation use.",
        ),
        (
            "The demo instance carries no non-commercial term of its own.",
            "The project states no non-commercial restriction on the instance.",
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
        rf"(?<![\d,])\b(?!33,?784\b){VEHICLE}\s+frame[- ]checks?\b",
        "33783 frame checks",
        "the wire corpus's pinned number is 33,784 frame checks "
        "(`specification/schema/validate.py`); a different number is a claim the corpus "
        "disproves. The peer layer's 232 are checks and are pinned by that entry",
        clean=("33,784 frame checks", "33784 frame checks"),
    ),
    Phrase(
        # The wire corpus and the peer corpus are two layers of one corpus and each is counted
        # and pinned on its own (`EXPECTED_WIRE_VECTORS` and `EXPECTED_PEER_VECTORS`,
        # `EXPECTED_PEER_CHECKS`). One number pinned wherever the word sits would read the peer
        # layer's count as the wire layer's — `27 peer vectors` is the peer layer's pin, not a
        # wrong count — so the wire entries exclude the shape the peer entries pin, exactly:
        # `27 peer vectors`, never `27 peer-ish vectors`. The window is `\S+` rather than `\w+`
        # for that: a hyphenated word between the number and the noun is still a word in front
        # of it, and `27 peer-ish vectors` was a rewrite the `\w+` window passed.
        rf"\b(?!25\b)(?!27\s+peer\s+vectors?\b){VEHICLE}\s+(?:\S+\s+){{0,2}}vectors?\b",
        "24 conformance vectors",
        "the wire corpus's pinned number is 25 vectors (`specification/schema/validate.py`); a "
        "different number is a claim the corpus disproves, and the count is pinned wherever the "
        "word sits — the page writes both 'conformance vectors' and 'wire vectors'. The peer "
        "layer's own count is a separate pin and is written '27 peer vectors'; any other number "
        "before that noun is still a failure",
        clean=("25 conformance vectors", "the 25 wire vectors", "27 peer vectors"),
    ),
    Phrase(
        rf"(?<![\d,])\b(?!8,?394\b){VEHICLE}\s+assertions?\b",
        "8393 assertions",
        "the wire corpus's pinned number is 8,394 assertions "
        "(`specification/schema/validate.py`); a different number is a claim the corpus "
        "disproves. The peer layer's count is its own pin and is written '74 peer assertions'",
        clean=("8,394 assertions", "8394 assertions", "74 peer assertions"),
    ),
    Phrase(
        rf"\b(?!27\b){VEHICLE}\s+peer\s+vectors?\b",
        "26 peer vectors",
        "the peer corpus's pinned number is 27 vectors and 232 checks "
        "(`EXPECTED_PEER_VECTORS` and `EXPECTED_PEER_CHECKS` in "
        "`specification/schema/validate.py`, where the validator prints 'peer vectors 27 files, "
        "19 frame, 8 decision, 232 checks, 74 assertion steps'); a different number is a claim "
        "the corpus disproves. The layer has to be named: `27 vectors` is read as the wire "
        "layer's count and fails on that entry",
        ("26 peer ve<!-- -->ctors",),
        clean=("27 peer vectors",),
    ),
    Phrase(
        rf"\b(?!232\b){VEHICLE}\s+peer\s+checks?\b",
        "231 peer checks",
        "the peer corpus's pinned count is 232 checks (`EXPECTED_PEER_CHECKS` in "
        "`specification/schema/validate.py`); a different number is a claim the corpus "
        "disproves. The wire layer's 33,784 are frame checks and are pinned by that entry",
        clean=("232 peer checks",),
    ),
    Phrase(
        rf"\b(?!74\b){VEHICLE}\s+peer\s+assertions?\b",
        "75 peer assertions",
        "the peer corpus's pinned number is 74 assertion steps (`EXPECTED_PEER_ASSERTIONS` in "
        "`specification/schema/validate.py`); a different number is a claim the corpus "
        "disproves. The wire layer's 8,394 are pinned by that entry",
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


def anonymous_pull_token(repository: str) -> str:
    """The token a `docker pull` gets with no credentials: ghcr mints one to a bare GET."""
    with urllib.request.urlopen(
        f"https://{REGISTRY_HOST}/token?scope=repository:{repository}:pull"
        f"&service={REGISTRY_HOST}",
        timeout=REQUEST_TIMEOUT_SECONDS,
    ) as response:
        return json.loads(response.read())["token"]


def published_tag_legs(repository: str) -> dict[str, tuple[str, ...]]:
    """{platform: layer digests} for one package's tag, from the per-platform manifests.

    The tag's own document is an index that points at those; the layers live in the manifests
    it names, which is why the index alone cannot answer what this asks. Attestation entries
    carry `platform: unknown/unknown` and are skipped by the `os` filter.
    """
    token = anonymous_pull_token(repository)
    index = _registry_json(f"{repository}/manifests/{PUBLISHED_IMAGE_TAG}", token)
    legs: dict[str, tuple[str, ...]] = {}
    for entry in index.get("manifests", []):
        platform = entry.get("platform", {})
        if platform.get("os") != "linux":
            continue
        manifest = _registry_json(f"{repository}/manifests/{entry['digest']}", token)
        layers = tuple(layer["digest"] for layer in manifest.get("layers", []))
        if layers:
            legs[f"linux/{platform.get('architecture')}"] = layers
    return legs


def check_published_tag(reference: str) -> int:
    """One pinned reference against the registry its tag names.

    Returns 0 when the tag pulls anonymously and carries two builds, 1 when it does not, 2 when
    the registry cannot be asked.
    """
    # The reference without its registry host and its tag: what a pull token is scoped to.
    repository = reference.split("/", 1)[1].rsplit(":", 1)[0]
    try:
        legs = published_tag_legs(repository)
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
            "holding the other platform's build is the defect this asserts against",
            file=sys.stderr,
        )
        return 1
    print(
        f"check-claims: the published image {reference} pulls anonymously and carries two "
        f"builds — amd64 {' '.join(d.removeprefix('sha256:')[:12] for d in amd64)}, "
        f"arm64 {' '.join(d.removeprefix('sha256:')[:12] for d in arm64)}"
    )
    return 0


def check_published_image(pages: list[Scanned]) -> int:
    """The page's image references against the two the project publishes, and each against the
    registry its tag names.

    The section prints the repository without its tag — docker reads a bare repository as `:latest` —
    so a reference is read as its `:latest` form (`with_default_tag`) before it is compared, and
    the same page still may not name a version the release does not publish.

    Returns 0 when all of that holds, 1 when the page names something else or names only one of
    the two, 2 when the registry cannot be asked.
    """
    root = root_of_this_checkout()
    named: list[str] = []
    wrong: list[str] = []
    for page in pages:
        for match in IMAGE_REFERENCE.finditer(page.text):
            printed = match.group(0)
            reference = with_default_tag(printed)
            named.append(reference)
            if reference not in IMAGE_REFERENCES:
                where = os.path.relpath(page.path, root)
                wrong.append(f"{where}:{page.line_of[match.start()]}: {printed!r}")
    if wrong:
        for where in wrong:
            print(
                f"check-claims: the page hands a reader {where}, and the references it may "
                f"name are {', '.join(repr(one) for one in IMAGE_REFERENCES)}",
                file=sys.stderr,
            )
        return 1
    if not named:
        print(
            f"check-claims: none of {len(pages)} scanned file(s) carries a reference to an "
            f"image this project publishes, and the references the page may hand a reader are "
            f"{', '.join(repr(one) for one in IMAGE_REFERENCES)}: the page's happy path is "
            "where they are handed over, so a scan that never reaches them is not checking "
            "the tags",
            file=sys.stderr,
        )
        return 1
    absent = [reference for reference in IMAGE_REFERENCES if reference not in named]
    if absent:
        print(
            f"check-claims: the page names {', '.join(sorted(set(named)))} and not "
            f"{', '.join(absent)}; the command it hands a reader runs both containers, so one "
            "of the two packages standing in for the other is a command that pulls an image "
            "the page is not about",
            file=sys.stderr,
        )
        return 1

    for reference in IMAGE_REFERENCES:
        status = check_published_tag(reference)
        if status != 0:
            return status
    return 0


def command_block_markups(page: Scanned) -> list[str]:
    """The Run section's printed blocks, as markup, in the order the page puts them.

    Answers [] for a page that carries no such block, which is a failure where the block is
    required rather than a quiet pass: a scan that reaches no command is not checking one. Each
    command is read as the block it is printed in, because a reader selects a block, and the three
    steps are three selections.
    """
    markups: list[str] = []
    at = 0
    while True:
        match = COMMAND_BLOCK.search(page.raw, at)
        if match is None:
            return markups
        found = element_from(page.raw, match)
        if found is None:
            return markups
        _tag, markup = found
        markups.append(markup)
        at = match.start() + len(markup)


def command_blocks(page: Scanned) -> list[list[str]]:
    """Those blocks' printed lines, one list each: what the command is read out of."""
    return [
        [normalise(line.group("line"))[0] for line in RUN_BLOCK_LINE.finditer(markup)]
        for markup in command_block_markups(page)
    ]


def command_clauses(command: str) -> list[str]:
    """One command of the chain each.

    A clause ends where a failure would stop the rest of the chain, so a `||` guarding one stays
    inside it rather than starting another.
    """
    clauses: list[str] = []
    start = 0
    for separator in COMMAND_SEPARATOR.finditer(command):
        clauses.append(command[start : separator.start()])
        start = separator.end()
    clauses.append(command[start:])
    return clauses


def network_named_in(clause: str, verb: re.Match[str]) -> ParsedName | None:
    """The network a `docker network …` clause names, or None when it names none.

    Read from the clause's own words rather than from a spelling of its own: a flag is not a name,
    and neither is what a redirection writes, so `docker network create --driver bridge selvage`
    and `docker network create selvage 2>/dev/null` both name `selvage`.
    """
    tail = re.split(r"\|\||&&|;|[|&<>]", clause[verb.end() :])[0]
    named = [
        word
        for word in tail.split()
        if not word.startswith("-") and re.search(r"[A-Za-z]", word) is not None
    ]
    return ParsedName(named[-1]) if named else None


class UnseamedComparison(Exception):
    """A name read out of a command, compared outside the seam that holds the reading."""


# Set while `reads_the_name` is comparing, and only then: a reading is swappable there, so that is
# the one place a comparison of two names is allowed to answer.
reading_a_name = False


class ParsedName(str):
    """A container name, a network name or an image reference, read out of a command.

    Comparing two of these is a claim that two readings name the same thing, and every such claim
    has to be one the fixture harness can swap for the weaker reading a later edit would leave in
    its place: `selvage-net` is a different name from `selvage`, a `\b` search does not say so
    because a hyphen is one, and a comparison written around `reads_the_name` is one nothing swaps
    and nothing notices. That is
    what this class closes: the operators below answer inside the seam alone and name the line that
    wrote them otherwise, so a comparison written where no fixture can hold it fails the check
    rather than passing the page.

    Holding the text this way costs nothing a rule needs. The value still formats and prints as the
    string it was read from, so every message a rule emits is unchanged. Ordering one of these is a
    comparison like any other and is refused with the rest, so a rule that wants names in order
    sorts their text instead.

    A `str` this is, so what it can refuse is bounded by which side does the answering. The
    operators and methods below are the ones Python hands the subclass: `==`, `!=` and the four
    orderings answer for a `plain` receiver too, because a subclass's reflected method is tried
    first, and `in` is refused where this is the `str` it searches and `startswith`, `endswith`,
    `find`, `index` and `count` where this is the object they are called on. A plain receiver
    answers for the rest — `name in plain_text`, `plain.startswith(name)`, `plain.find(name)`, and
    the `str` side of any operator that answers with plain text, `"-" + name` among them — and so
    does any method that answers with plain text, `name.lower()` and `name.strip()` among them.
    `docs/claim-filter.md` writes that limit out with the edit that defeats each, and
    `seam_problems` fails this check when one of the refusals goes.

    What it does not close either is a comparison of the text a name was read from — a `.split()` of
    the clause, a fresh pattern matched against it — because that value is not one of these and
    carries no record of where it came from. `unseamed_field_problems` scans this file for the
    reads that would produce one, and the reach of both halves is written out in
    `docs/claim-filter.md`.
    """

    __hash__ = str.__hash__

    def _through_the_seam_alone(self) -> None:
        if not reading_a_name:
            # The third frame up is the line that wrote the comparison: this method, the operator
            # that called it, and the rule body.
            written = traceback.extract_stack()[-3]
            raise UnseamedComparison(
                f"{self!r} is a name read out of a command and is compared outside "
                f"`reads_the_name` at {written.filename}:{written.lineno}, where no fixture can "
                "hold the reading: name the place in `RUN_READINGS` and compare through the "
                "seam"
            )

    def __eq__(self, other: object) -> bool:
        self._through_the_seam_alone()
        return str.__eq__(self, other)

    def __ne__(self, other: object) -> bool:
        self._through_the_seam_alone()
        return str.__ne__(self, other)

    def __contains__(self, other: object) -> bool:
        self._through_the_seam_alone()
        return str.__contains__(self, other)

    def __lt__(self, other: object) -> bool:
        self._through_the_seam_alone()
        return str.__lt__(self, other)

    def __le__(self, other: object) -> bool:
        self._through_the_seam_alone()
        return str.__le__(self, other)

    def __gt__(self, other: object) -> bool:
        self._through_the_seam_alone()
        return str.__gt__(self, other)

    def __ge__(self, other: object) -> bool:
        self._through_the_seam_alone()
        return str.__ge__(self, other)

    def startswith(self, prefix: str | tuple[str, ...], *rest: int) -> bool:
        self._through_the_seam_alone()
        return str.startswith(self, prefix, *rest)

    def endswith(self, suffix: str | tuple[str, ...], *rest: int) -> bool:
        self._through_the_seam_alone()
        return str.endswith(self, suffix, *rest)

    def find(self, sub: str, *rest: int) -> int:
        self._through_the_seam_alone()
        return str.find(self, sub, *rest)

    def index(self, sub: str, *rest: int) -> int:
        self._through_the_seam_alone()
        return str.index(self, sub, *rest)

    def count(self, sub: str, *rest: int) -> int:
        self._through_the_seam_alone()
        return str.count(self, sub, *rest)


def container_name_in(clause: str) -> ParsedName | None:
    """The name a clause gives its container, or None when it gives it none."""
    found = CONTAINER_NAME.search(clause)
    return ParsedName(found.group("name")) if found is not None else None


def network_attached_in(clause: str) -> ParsedName | None:
    """The network a clause attaches its container to, or None when it attaches it to none."""
    found = NETWORK_FLAG.search(clause)
    return ParsedName(found.group("name")) if found is not None else None


def server_address_in(clause: str) -> str | None:
    """The address a clause points its container at its server with, as the section prints it, or None.

    The address is text a rule prints and reads a host out of, not a name two rules are about: the
    *host* is the name a rule compares against the containers the command gives names to, and
    `server_address_host` is what reads that out as one.
    """
    found = SERVER_ADDRESS.search(clause)
    return found.group("url") if found is not None else None


# The places the rules compare two names, each named because a name read as a search is what a
# fixture has to hold: `selvage-net` is a different name from `selvage`, a `\b` boundary does not
# say so because a hyphen is one, and read as a search `selvage-net` stands in for `selvage`. The
# shape reaches the network each run is attached to, the container the address names and the
# references the two runs carry: `selvage-net` read as `selvage` is a page container off the network
# its server is on, and `selvaged:latest-extra` read as `selvaged:latest` is a run this project
# publishes no image for. Every one of these places reads through `reads_the_name`,
# `run_section_reading_problems` swaps one place at a time for the search and requires a fixture to go
# red, and a comparison written outside it is refused where it is written — so a place no fixture
# distinguishes is reported rather than left in place, and a place nobody named is not silent.
READING_CONTAINER_NETWORK = "the network each run attaches its container to"
READING_ADDRESSED_CONTAINER = "the container the server's address names"
READING_PAGE_IMAGE_RUN = "the page image on the run the address is given to"
READING_SERVER_IMAGE_RUN = "the server image on the run beside it"


def the_same_name(one: str, other: str) -> bool:
    """Whether the whole of `one` is the whole of `other`, which is what a name claim reads.

    The two are the pair the place compares: two network names, a container name against a host an
    address names, or a reference a run carries against the one it has to be. An empty name — a run
    that gives no container a name, an address whose host is missing — is not the whole of any name
    but itself.
    """
    return one == other


def the_same_name_as_a_search(one: str, other: str) -> bool:
    """`the_same_name` weakened the way a search weakens a name: one inside the other reads as it.

    That is the reading a later edit reaches for — `selvage` inside `selvage-net`, `selvaged:latest`
    inside `selvaged:latest-extra` — and it is what these places are written to refuse.
    """
    return one in other or other in one


def names_something(name: ParsedName) -> bool:
    """Whether a name read out of the section names anything at all.

    The empty name is what a reading answers when there was nothing to read: a run that gives its
    container no name, an address whose host is missing. Two of those are not two names that are
    the same, and a rule that read them as one passed a section whose page container is pointed at
    `http://:8080` beside a server run it gives no name to — a pair that relays to nothing, read
    as satisfied by the very emptiness that is the defect. So the rule that compares a host against
    the containers the command names asks this of both, and an empty name is never evidence.
    """
    return str.__len__(name) > 0


# `(the reading the place does, the search it must not be)`.
RUN_READINGS: dict[str, tuple[Callable[[str, str], bool], Callable[[str, str], bool]]] = {
    READING_CONTAINER_NETWORK: (the_same_name, the_same_name_as_a_search),
    READING_ADDRESSED_CONTAINER: (the_same_name, the_same_name_as_a_search),
    READING_PAGE_IMAGE_RUN: (the_same_name, the_same_name_as_a_search),
    READING_SERVER_IMAGE_RUN: (the_same_name, the_same_name_as_a_search),
}

# Which places the fixtures reached, which of them read a name the search would read differently,
# and which of them the harness has swapped for the search. A place nothing reached is a place the
# rules no longer read; a place reached without a disagreement is one no fixture tells the search
# apart at; a place that disagreed without reddening a fixture is one where the difference never
# reaches a rule's answer.
readings_reached: set[str] = set()
readings_disagreed: set[str] = set()
swapped_readings: set[str] = set()


def reads_the_name(site: str, one: str, other: str) -> bool:
    """Whether the field `one` reads as the field `other`, the way the place `site` reads a pair.

    The two are the pair the place compares, in the order its reading documents them: a clause and
    the name it has to carry, or two names a rule is about to call the same. The place is passed by
    its caller rather than inferred from the fields, because it is what the fixture harness swaps:
    one place weakened at a time is what says a fixture holds *that* place, where a reading weakened
    everywhere would be held by whichever fixture noticed it first.

    A `ParsedName` answers nowhere else. That is what keeps a claim about two names inside the table
    of places a fixture can hold, and it is why the flag below is set here and unset everywhere
    else.
    """
    global reading_a_name
    readings_reached.add(site)
    reading, weakened = RUN_READINGS[site]
    was_reading = reading_a_name
    reading_a_name = True
    try:
        if site not in swapped_readings:
            return reading(one, other)
        if reading(one, other) != weakened(one, other):
            readings_disagreed.add(site)
        return weakened(one, other)
    finally:
        reading_a_name = was_reading


# The comparisons `ParsedName` has to refuse when they are written outside the seam, in the forms
# Python hands a subclass: the operands and the methods called on one of these. Every one of them
# answers for a plain `str` receiver — that is the limit the class's docstring writes out — so the
# list is the refusal half alone, one entry per operator a later edit could drop.
def unseamed_comparisons(
    one: ParsedName, two: ParsedName, plain: str
) -> tuple[tuple[str, Callable[..., object]], ...]:
    """Each comparison of a name read out of a command that the seam has to refuse, by shape."""
    return (
        ("`one == two`", lambda: one == two),
        ("`one != two`", lambda: one != two),
        ("`plain == one`", lambda: plain == one),
        ("`plain != one`", lambda: plain != one),
        ("`plain in one`", lambda: plain in one),
        ("`one.startswith(…)`", lambda: one.startswith("sel")),
        ("`one.endswith(…)`", lambda: one.endswith("ge")),
        ("`one < two`", lambda: one < two),
        ("`one <= two`", lambda: one <= two),
        ("`one > two`", lambda: one > two),
        ("`one >= two`", lambda: one >= two),
        ("`plain < one`", lambda: plain < one),
        ("`plain <= one`", lambda: plain <= one),
        ("`plain > one`", lambda: plain > one),
        ("`plain >= one`", lambda: plain >= one),
        ("`one.find(…)`", lambda: one.find("age")),
        ("`one.index(…)`", lambda: one.index("age")),
        ("`one.count(…)`", lambda: one.count("e")),
        ("`sorted([one, two])`", lambda: sorted([one, two])),
    )


def seam_problems() -> list[str]:
    """Every comparison the seam has to refuse, evaluated, against the one place it answers.

    The refusal is the whole guard on a name read out of a command, and it is one line per
    operator: delete `__lt__` and the class still reads exactly as it does now, the fixtures still
    pass, and a rule that orders two names is compared as plain text. So each shape is evaluated
    here, outside the seam where it has to name the line it was written on, and one comparison is
    evaluated through `reads_the_name` where it has to answer — a refusal that refuses everything
    would take the table's readings with it.

    What is not here is the other half of the class's limit, the forms a `str` receiver answers for
    on its own: `name in plain_text`, `plain.startswith(name)`, `plain.find(name)`, and the methods
    that answer with plain text, `name.lower()` among them. No evaluation can hold a shape that
    answers, and `docs/claim-filter.md` writes each of those out with the edit that defeats it.

    This runs after the fixture harness, because the comparison it makes inside the seam goes
    through `reads_the_name` and that records the place it read: the harness's answer about which
    places the rules still reach is finished by then, and this is not part of it.
    """
    one = ParsedName("selvage")
    two = ParsedName("selvage-net")
    plain = "selvage-net"
    problems: list[str] = []
    for what, comparison in unseamed_comparisons(one, two, plain):
        try:
            comparison()
        except UnseamedComparison:
            continue
        except Exception as thrown:
            problems.append(
                f"the seam refuses {what} with {type(thrown).__name__} rather than naming the "
                "line it was written on, so a comparison written outside `reads_the_name` is "
                "reported as something else"
            )
        else:
            problems.append(
                f"the seam answers {what}, a comparison of a name read out of a command written "
                "outside `reads_the_name`: the method that refuses it no longer does, so a "
                "fixture's reading can be replaced by this and nothing notices"
            )
    try:
        inside = reads_the_name(READING_CONTAINER_NETWORK, one, two)
    except UnseamedComparison:
        problems.append(
            "the seam refuses `reads_the_name`, the one place a comparison of two names is "
            "asked to answer, so every reading in the table is refused where it is made"
        )
    else:
        if inside is not False:
            problems.append(
                f"`reads_the_name` answers {inside!r} for two names that are not the same, so "
                "the place that reads a pair is not reading them"
            )
    return problems


def server_address_host(address: str) -> ParsedName:
    """The host an address names, in either form the page image accepts.

    `http://selvaged:8080` is a URL and is read as one. A bare `selvaged:8080` is not: as a URL
    its scheme is `selvaged`, which has no host at all, so the bare form — the one
    `web_client`'s README documents and `reference_server`'s README uses — is read as a host and
    an optional port instead. An address that names no host answers '' here, and '' names nothing:
    the rule that compares this against the containers the command names fails on it, because
    `names_something` says an empty name is not a host any container can be.

    The parameter is the address as text, and the host is the one thing read out of it that is a
    name: a rule compares that against the names the command gives its containers, and it is read
    as a `ParsedName` here so that comparison goes through the seam like any other.
    """
    if "://" in address:
        return ParsedName(urlsplit(address).hostname or "")
    host = address.split("/", 1)[0]
    if host.startswith("["):
        return ParsedName(host[1:].split("]", 1)[0])
    name, _, port = host.rpartition(":")
    return ParsedName(name if name and port.isdigit() else host)


def port_named_by(address: str) -> int | None:
    """The port the address the section prints names, or None when it names none."""
    match = RUN_OPENED_AT.search(address)
    if match is None or match.group("port") is None:
        return None
    return int(match.group("port"))


def mapping_fields(mapping: str) -> tuple[str, str, str]:
    """Docker's `-p` value as `(the host it names, its host port, its container port)`.

    The form is `[host-ip:][host-port:]container-port[/proto]`, and each of the first two may be
    absent. The host may be an IPv6 address, which is bracketed because it carries colons of its
    own, so it is read before the rest is split on them: `[::1]:8080:8080` is the host `::1` with
    the two ports after it, not five fields.
    """
    body = mapping.split("/", 1)[0]
    host = ""
    if body.startswith("["):
        host, _, body = body[1:].partition("]")
        body = body.removeprefix(":")
    fields = body.split(":")
    if len(fields) >= 3:
        return fields[0], fields[-2], fields[-1]
    if len(fields) == 2:
        return host, fields[0], fields[1]
    return host, "", fields[0]


def host_port_of_mapping(mapping: str) -> int | None:
    """The port a mapping publishes on the host, or None when it publishes none.

    Only the field before the last colon is a port on the host: `-p 8080` publishes the container's
    port on one docker picks, which is not a port the section's address can name.
    """
    host_port = mapping_fields(mapping)[1]
    return int(host_port) if host_port.isdigit() else None


def container_port_of_mapping(mapping: str) -> int | None:
    """The published port read as the mapping's last field: the edit this file has to refuse.

    Docker's last field is the container's port, and the guard above is left where it is: a mapping
    that names no host port is still read as naming none, and only the field the port comes out of
    moves. That is the shape a later hand reaches for — `fields[-1]` in place of `fields[-2]` — and
    the fixture that refuses it is a mapping
    whose two fields differ.
    """
    host_port, container_port = mapping_fields(mapping)[1:]
    if not host_port.isdigit() or not container_port.isdigit():
        return None
    return int(container_port)


# The mapping reading the fixture harness swaps, and the one it swaps in.
published_port_reading: Callable[[str], int | None] = host_port_of_mapping


def published_host_port(clause: str) -> int | None:
    """The host port a clause publishes, or None when it publishes none."""
    found = PUBLISHED_MAPPING.search(clause)
    if found is None:
        return None
    return published_port_reading(found.group("mapping"))


def published_host_address(clause: str) -> str:
    """The host address a clause publishes on, '' when its mapping names none.

    Docker leaves the host to itself when the mapping names none, and what is read here is the
    mapping and not docker's choice: an address nobody wrote is not one the section's own address can
    be held to, and the fixture that holds this reading is a mapping that names another one.
    """
    found = PUBLISHED_MAPPING.search(clause)
    if found is None:
        return ""
    return mapping_fields(found.group("mapping"))[0]


def run_image_operand(clause: str) -> ParsedName:
    """The reference a run names as its image, or '' when it names none.

    Docker's grammar puts the image after the options, so the reference read is the first token
    that is one of the project's references and nothing else, and a token that is an option or
    carries one (`--label note=ghcr.io/…`, `-v ghcr.io/…:/data`) is not it: read as `search`
    would, a reference in an option's value classifies the run as the image that value names, and
    a command with the two images in each other's place would pass.

    The section prints the repository without its tag, and docker reads a bare repository as
    `:latest`, so what is handed back is the reference with that tag spelled out: the comparison
    against the pinned reference is then the whole-name reading it has always been, and a run
    carrying any other tag of the same package is still refused.
    """
    for token in clause.split():
        if token.startswith("-") or "=" in token:
            continue
        if IMAGE_REFERENCE.fullmatch(token):
            return ParsedName(with_default_tag(token))
    return ParsedName("")


def classed_elements(raw: str, wanted: str) -> list[str]:
    """The markup of every element of `raw` whose class list carries `wanted`.

    The class is read as a whole name out of the class attribute's own tokens, so `command-line`
    does not answer for `command-label`. An element the scan cannot follow to its own closer is
    left out rather than guessed at.
    """
    found: list[str] = []
    for match in CLASSED_ELEMENT.finditer(raw):
        if wanted not in match.group("classes").split():
            continue
        element = element_from(raw, match)
        if element is not None:
            found.append(element[1])
    return found


def run_section_problems(blocks: list[list[str]]) -> list[str]:
    """What the section's commands have to be, one problem each.

    The section hands a reader three lines: the network the two containers share, the server that
    holds the room, and the page that reaches it. The first has to create that network before
    either run names it, every run
    has to join it, every run has to be detached, and the address the page container is given is
    read as two claims about the others: some run has to give that host a name on the network the
    two are attached to, and the run carrying the address has to be the one that publishes a port,
    or the page asks for a server nothing answers for. Neither side of that first claim may be the
    empty name — an address whose host is empty names no container, a run given no `--name` names
    none — because the two of those are equal and a section that relays to nothing would read as
    satisfied. The address is also read against the two references the page publishes: the run a
    reader opens carries the page image and the run beside it the server's, so the two swapped is a
    reader sent to the server's port for a page, and the server's run publishes nothing, because a
    port there collides with the page's own.

    Every rule here carries a fixture in `RUN_FIXTURES`, and each fixture pins the fragment
    its rule emits, so a rule removed is a rule this file fails on rather than one nothing reads.
    Every comparison of two names goes through `reads_the_name` with one of the places named at the
    top of this file, and it is a fixture rather than the code that says each place is held:
    `run_section_reading_problems` swaps each place in turn for the search it must not be and requires
    a fixture to go red, so a place whose fixtures all stay green is a reading nobody holds. A
    comparison written straight into this body instead is refused where it is written, because the
    names here are `ParsedName` and only the seam answers for one of those.

    What it does not read is anything about a second paste: the section promises nothing about one, so
    there is no shape here for it to hold.
    """
    problems: list[str] = []
    # Each block is one line a reader pastes, so the clauses of a block are read together and the
    # blocks are not joined to each other: two commands printed one above the other are not a chain.
    clauses = [
        clause for block in blocks for clause in command_clauses(" ".join(block))
    ]

    network: ParsedName | None = None
    created_at: int | None = None
    first_run: int | None = None
    for index, clause in enumerate(clauses):
        if first_run is None and DOCKER_RUN.search(clause) is not None:
            first_run = index
        created = NETWORK_CREATE.search(clause)
        if created is not None and network is None:
            network = network_named_in(clause, created)
            created_at = index
    if network is None:
        problems.append("does not create the network the two containers share")
    elif created_at is not None and first_run is not None and first_run < created_at:
        # The first command is the network's: a run that names a network nothing has created yet
        # fails where the reader pastes it, so the creation has to stand before every run.
        problems.append(
            f"runs a container before the command that creates {network}, so the run reaches "
            "a network nothing has made yet"
        )

    # The containers the runs start: the name each runs under, the network it is attached to, and
    # the clause itself, so the address one of them carries can be read against the others.
    started: list[tuple[ParsedName, ParsedName | None, str]] = []
    for clause in clauses:
        if DOCKER_RUN.search(clause) is None:
            continue
        named = container_name_in(clause)
        attached = network_attached_in(clause)
        started.append((named if named is not None else ParsedName(""), attached, clause))
        if DETACHED.search(clause) is None:
            problems.append(
                "runs a container without `-d`, so the run holds the reader's terminal instead "
                "of returning their prompt"
            )
        if network is not None and not (
            attached is not None
            and reads_the_name(READING_CONTAINER_NETWORK, attached, network)
        ):
            problems.append(
                f"runs a container that is not on {network}, the network it creates, so the "
                "page cannot reach its server by the name it is given"
            )
    if not started:
        problems.append("runs no container")

    addressed = 0
    for _name, _attached, clause in started:
        address = server_address_in(clause)
        if address is None:
            continue
        addressed += 1
        host = server_address_host(address)
        # A name that names nothing is not a name: `http://:8080` gives the page container no host
        # and a run given no `--name` gives it no container, and the two compared equal, so this
        # rule read a section whose page relays to nothing as satisfied. Both sides are asked here
        # rather than leaving it to the reading, because `reads_the_name` is the place a fixture
        # harness swaps for a weaker one, and a weaker reading is what `''` slips through.
        elsewhere = [
            one
            for one, _network, other in started
            if names_something(one)
            and names_something(host)
            and reads_the_name(READING_ADDRESSED_CONTAINER, one, host)
            and other != clause
        ]
        if not names_something(host):
            problems.append(
                f"points a container at {address} and names no host in it, so that address "
                "reaches nothing"
            )
        elif not elsewhere:
            problems.append(
                f"points a container at {address} and gives no other container "
                f"the name {host!r}, so that address reaches nothing"
            )
        elif PUBLISHED_PORT.search(clause) is None:
            problems.append(
                f"gives {address} to a container that publishes no port, so the "
                "page a reader opens is not the one that relays to the server"
            )
    if not addressed:
        problems.append(
            "gives no container `-e SELVAGE_SERVER`, so the page image it publishes has no "
            "server to relay to"
        )

    # Which of the two references the page hands a reader sits on which run, read only when the
    # command names them at all: a shape carrying neither is one with nothing to compare, which is
    # why the fixture shapes are written with names of their own. The run the address is given to is
    # the container a reader opens, so that run is the page image and the run beside it is the
    # server's: the two swapped is a reader sent to the server's port for a page, and the address on
    # the server's run is one sent to a container that serves no page. The server's run publishes
    # nothing, because the page container is the only one the section publishes: a second `-p` there
    # is a collision that leaves the page container never starting.
    named_runs: list[tuple[str, ParsedName]] = [
        (clause, run_image_operand(clause)) for _name, _attached, clause in started
    ]
    if any(reference for _clause, reference in named_runs):
        for clause, reference in named_runs:
            given = SERVER_ADDRESS.search(clause) is not None
            shown = reference or "a container this project publishes no image for"
            if given and not reads_the_name(READING_PAGE_IMAGE_RUN, reference, PAGE_REFERENCE):
                problems.append(
                    f"gives `-e SELVAGE_SERVER` to the run carrying {shown}, and the address "
                    f"belongs on the page image {PAGE_REFERENCE}: the container that publishes "
                    "the port a reader opens is the server's own"
                )
            on_the_server = reads_the_name(
                READING_SERVER_IMAGE_RUN, reference, SERVER_REFERENCE
            )
            if not given and reference and not on_the_server:
                problems.append(
                    f"runs {shown} on the container that is given no `-e SELVAGE_SERVER`, which "
                    f"is the container the server's image belongs on, {SERVER_REFERENCE}"
                )
            elif not given and not reference:
                problems.append(
                    "runs a container this project publishes no image for on the container that "
                    "is given no `-e SELVAGE_SERVER`, and the section hands a reader two runs: the "
                    f"page image {PAGE_REFERENCE} on the one the address is given to and the "
                    f"server's {SERVER_REFERENCE} beside it"
                )
            if on_the_server and PUBLISHED_PORT.search(clause) is not None:
                problems.append(
                    f"publishes a port on the run carrying the server image {SERVER_REFERENCE}, "
                    "and the server has none on the host: a server that takes 8080 leaves the "
                    "page container's own `-p` nothing to bind and the page never starts"
                )
    return problems


def run_section_region(page: Scanned) -> str:
    """The Run section's own text, the region the address it prints for a reader is read out of.

    The section prints the address and the command that publishes it inside one element, and the class
    is the section's own, so what is asked for is the element carrying both: a section the scan cannot
    follow to its closer, or one that carries an address and no command, answers '' rather than a
    fragment, which is a page this check refuses to pass.
    """
    for markup in classed_elements(page.raw, RUN_SECTION_CLASS):
        if any(RUN_BLOCK_LINE.finditer(markup)):
            return normalise(markup)[0]
    return ""


def run_section_opened_at_problems(opened_at: str, blocks: list[list[str]]) -> list[str]:
    """The address the section prints against the address its command publishes on, one problem each.

    The reader is told to open an address and the command maps one, and those are two copies of one
    fact: `http://127.0.0.1:8080/` in the section's own copy and `-p 127.0.0.1:8080:8080` in the
    command under it. A command that publishes another port, or only the container's port on one
    this machine picks, sends the reader to an address nothing answers on while the copy beside it
    says it does; an address that names no port is one no command can publish to; and a mapping
    that names a host other than the loopback the section prints — `-p 192.168.1.5:8080:8080`,
    `-p [::1]:8080:8080` — publishes the page where a browser sent to the section's own address never
    reaches it. A mapping that names no host at all is left to docker, which publishes it on every
    interface the machine has, and passes: what is read here is the address a mapping carries and
    not the one docker picks. The run the address is given to is the one read, because that is the
    container the reader opens, and it is read in whichever of the section's blocks it is printed in:
    the section hands a reader three commands, and the address belongs on the one that serves the page.
    """
    port = port_named_by(opened_at)
    if port is None:
        return [
            f"prints {opened_at} as the address a reader opens, and it names no port for the "
            "command beside it to publish"
        ]
    problems: list[str] = []
    for block in blocks:
        for clause in command_clauses(" ".join(block)):
            if SERVER_ADDRESS.search(clause) is None:
                continue
            published = published_host_port(clause)
            if published is None:
                problems.append(
                    f"gives the address {opened_at} to a run that publishes no port on the "
                    "host, so the address a reader opens answers nothing"
                )
            elif published != port:
                problems.append(
                    f"publishes {published} and the section tells the reader to open {opened_at}, "
                    "so the address it prints is on a port its own command does not serve"
                )
            bound = published_host_address(clause)
            if bound and bound not in LOOPBACK_NAMES:
                problems.append(
                    f"publishes on {bound} and the section tells the reader to open {opened_at}, "
                    "so the address it prints is not one its own command serves"
                )
    return problems


def check_run_section_address(pages: list[Scanned]) -> int:
    """The address the Run section tells a reader to open, against the address its command publishes.

    The section prints one address and its command publishes one, and those are two copies of one
    fact that nothing compared: a page saying `http://127.0.0.1:8080/` over a command publishing
    `-p 127.0.0.1:9090:8080` sends every reader it has to an address nothing answers on, and the
    check that reads the command's shape cannot see it, because the command is a correct command.
    The mapping's host is read the same way: `-p 192.168.1.5:8080:8080` publishes the page where
    the section's own loopback address reaches nothing, and a page that says its container is
    published on this machine's loopback while its command puts the page on a LAN address or on
    `::1` is one whose copy and command are two different facts.

    The address is read out of the section's own text, not off the command: what the run's
    `-e SELVAGE_SERVER` names is the address the page container relays to, which is a different
    address on a different network. It is read out of that one region for the same reason: an
    address another part of the page prints is a different fact, and a section whose own copy and
    command agree is a section that is right. Every place the section states it in that region is read,
    not the first one: the section prints three commands now, so there is no longer a single block a
    section's copy could be assumed to sit beside, and the run the address belongs to is looked for in
    whichever block carries it.

    Returns 0 when the address the section prints is the address its command publishes — its host
    port, and the host that mapping names where it names one — 1 when it is not, and 2 when no
    scanned page prints a loopback address inside the section that carries a command: an address the
    check cannot find is not an address it checked.
    """
    root = root_of_this_checkout()
    failures: list[tuple[str, list[str]]] = []
    reached = 0
    for page in pages:
        blocks = command_blocks(page)
        if not any(blocks):
            continue
        region = run_section_region(page)
        addresses = sorted({match.group(0) for match in RUN_OPENED_AT.finditer(region)})
        if not addresses:
            continue
        reached += 1
        problems = [
            problem
            for opened_at in addresses
            for problem in run_section_opened_at_problems(opened_at, blocks)
        ]
        if problems:
            failures.append((os.path.relpath(page.path, root), problems))
    if failures:
        for where, problems in failures:
            for problem in problems:
                print(
                    f"check-claims: the Run section at {where} {problem}; the section prints that "
                    "address for the command beside it, and a reader who opens it reaches what "
                    "the command published or nothing",
                    file=sys.stderr,
                )
        return 1
    if not reached:
        print(
            f"check-claims: none of {len(pages)} scanned file(s) carries the address the Run section "
            "tells a reader to open inside the section that prints the command beside it, and that "
            "section prints one, so a scan that reads no address is not checking one",
            file=sys.stderr,
        )
        return 2
    print(
        "check-claims: the address the Run section tells a reader to open is the address its command "
        "publishes, its host port and the loopback its mapping names where it names one, so the "
        "address the page sends a browser to is one the run beside it serves"
    )
    return 0


def check_run_section_command(pages: list[Scanned]) -> int:
    """The Run section's three commands, against what each of them has to be.

    The section hands a reader the network the two containers share, the server that holds the room and
    the page that reaches it, one command each. What is required is that the first creates their
    network, that every run joins it under the same name, that every run is detached, that the
    address the page is given names the container its server runs in on the network both are on and
    sits on the container a reader opens, that each of the two runs carries the reference the page
    publishes for it — the page image on the run the address is given to and the server's on the
    other — and that the run carrying the server image publishes no port.

    This host has no Docker, so this reads a shape and not a run, and it knows one way of writing
    each part of it: a command that is correct but spells one of them differently fails here, and
    a broken one that keeps these words together passes it. That is the limit of the reading.
    Returns 0 when a scanned page's section carries all of it, 1 when one part is missing, and 2
    when no scanned page carries the command blocks at all.
    """
    root = root_of_this_checkout()
    failures: list[tuple[str, list[str]]] = []
    reached = 0
    for page in pages:
        blocks = command_blocks(page)
        if not any(blocks):
            continue
        reached += 1
        problems = run_section_problems(blocks)
        if problems:
            failures.append((os.path.relpath(page.path, root), problems))
    if failures:
        for where, problems in failures:
            for problem in problems:
                print(
                    f"check-claims: the Run section's commands at {where} {problem}; the section hands "
                    "them to a reader to paste, and they have to run there",
                    file=sys.stderr,
                )
        return 1
    if not reached:
        print(
            f"check-claims: none of {len(pages)} scanned file(s) carries the Run section's "
            "command block, and that block is where the project hands a reader two containers "
            "to run, so a scan that reaches no command is not checking one",
            file=sys.stderr,
        )
        return 2
    print(
        "check-claims: the Run section creates the network the two containers share before the runs "
        "that name it, runs every "
        "container detached and on that network, points the page container at the server "
        "container, gives the address to the run carrying the page image, and publishes nothing "
        "on the run carrying the server's. This reads the shape of the commands and not a run, "
        "and it knows one way of writing each part of it: a correct command in other words fails "
        "here, and a broken one that keeps these words can pass"
    )
    return 0
def served_stylesheets(page: Scanned) -> tuple[list[str], str]:
    """The CSS the served page loads, and why it could not be read, one of the two empty.

    The page names its own stylesheet, and `next start` answers the `_next/static/` prefix out of
    the build this checkout made, so the bytes are read there rather than out of the source tree: a
    rule the build pipeline drops or rewrites is not in what a reader's browser gets, and what is
    pinned here is what the page loads. Nothing outside that prefix is read, because nothing
    outside it is served.
    """
    root = root_of_this_checkout()
    hrefs: list[str] = []
    for link in STYLESHEET_LINK.finditer(page.raw):
        rel = STYLESHEET_REL.search(link.group(0))
        if rel is None or "stylesheet" not in rel.group("rel").split():
            continue
        href = STYLESHEET_HREF.search(link.group(0))
        if href is not None:
            hrefs.append(href.group("href"))
    if not hrefs:
        return [], (
            "the served page names no stylesheet, so the rule that keeps the section's prompt and "
            "labels out of a copy was not reached; a page whose stylesheet cannot be read is not "
            "a page whose selection behaviour was checked"
        )
    sheets: list[str] = []
    for href in hrefs:
        if not href.startswith(BUILD_PREFIX):
            return [], (
                f"the served page loads a stylesheet from {href!r}, which is not this "
                f"checkout's own build under {BUILD_PREFIX}, so the rule that keeps the section's "
                "prompt and labels out of a copy is not the one this build produced"
            )
        # The page names the file with the build's own root-relative href, so what is opened is
        # the file the server serves and nothing else: the path is resolved, and a page whose
        # href walks out of the served part of the build (`.next/../style.css`, or a query string
        # trying to) is refused rather than read from the source tree a rule this check exists to
        # keep out of it was written in.
        build = os.path.realpath(os.path.join(root, ".next", "static"))
        path = os.path.realpath(
            os.path.join(build, href[len(BUILD_PREFIX) :].split("?", 1)[0])
        )
        if os.path.commonpath([build, path]) != build:
            return [], (
                f"the served page loads the stylesheet {href!r}, which resolves to {path}, "
                f"outside this checkout's build at {build}; a stylesheet the build did not "
                "produce is not the one the page loads"
            )
        try:
            with open(path, encoding="utf-8") as handle:
                sheets.append(handle.read())
        except OSError as error:
            return [], (
                f"the served page loads the stylesheet {href!r} and {path} does not carry it "
                f"({error}); the page was not served by this checkout's build"
            )
    return sheets, ""


def neutralised(sheets: list[str], class_name: str) -> bool:
    """Whether a rule in one of `sheets` takes elements classed `class_name` out of a selection.

    The rule is read as a rule: the declaration has to sit in a block whose selector names that
    class, so a stylesheet that excludes some other element from the selection does not stand in
    for the one the page prints.
    """
    if not class_name:
        return False
    selector = re.compile(rf"(?:^|[^\w-])\.{re.escape(class_name)}(?![\w-])")
    for sheet in sheets:
        for rule in CSS_RULE.finditer(sheet):
            if USER_SELECT_NONE.search(rule.group("body")) and selector.search(
                rule.group("selectors")
            ):
                return True
    return False


def prompt_classes(markup: str) -> list[list[str]]:
    """The class tokens of every element of `markup` whose whole visible text is the `$ ` prompt.

    Read out of the section's own markup rather than off a class name of this file's choosing, so a
    section that renames the prompt and its rule together still passes: what is required is that the
    rule the stylesheet carries names the element the page prints.
    """
    found: list[list[str]] = []
    for match in INNER_ELEMENT.finditer(markup):
        if normalise(match.group("text"))[0].strip() != "$":
            continue
        classes = CLASS_ATTRIBUTE.search(match.group("attrs"))
        found.append(classes.group("classes").split() if classes is not None else [])
    return found


def check_command_prompt_selection(pages: list[Scanned]) -> int:
    """The section's `$ ` prompt and its labels, against the stylesheet the served page loads.

    The section prints each command under a `$ ` prompt, and the prompt is not part of the command:
    a triple-click takes the whole line, and a `$ ` pasted into a shell is `command not found` on
    the first clause of it. The labels above the blocks are the same kind of text with the same
    consequence, and a selection that reaches across two blocks takes both. What keeps them out
    of a copy is a rule in the stylesheet the page loads — `user-select: none` — so this reads
    that rule out of the built stylesheet the server is serving and requires it to name the class
    the page prints. Removing the declaration brings the pasted prompt back with nothing else in
    the tree to say so, which is the hole this closes.

    A command line whose visible text begins with `$` but which carries no prompt element is the
    same defect written into the command's own text, and fails here.

    Returns 0 when every prompt and label the section prints is out of the selection, 1 when one is
    in it, and 2 when the check cannot reach what it has to read: a section that prints no prompt
    element at all, or a stylesheet this checkout's build does not carry.
    """
    root = root_of_this_checkout()
    failures: list[tuple[str, list[str]]] = []
    promptless: list[str] = []
    reached = 0
    for page in pages:
        markups = command_block_markups(page)
        if not markups:
            continue
        reached += 1
        where = os.path.relpath(page.path, root)
        problems: list[str] = []
        sheets, why = served_stylesheets(page)
        if not sheets:
            print(f"check-claims: {why}", file=sys.stderr)
            return 2
        chrome: list[tuple[str, list[str]]] = []
        for markup in markups:
            for line in RUN_BLOCK_LINE.finditer(markup):
                inner = line.group("line")
                prompts = prompt_classes(inner)
                if not prompts and normalise(inner)[0].startswith("$"):
                    problems.append(
                        "prints a `$ ` prompt as the command's own text, so a copy takes the "
                        "prompt with it and a shell refuses the first clause"
                    )
                for tokens in prompts:
                    chrome.append(("a `$ ` prompt", tokens))
        if not any(what == "a `$ ` prompt" for what, _tokens in chrome):
            promptless.append(where)
        for label in classed_elements(page.raw, RUN_BLOCK_LABEL_CLASS):
            chrome.append((f"the label {normalise(label)[0].strip()!r}", [RUN_BLOCK_LABEL_CLASS]))
        for what, tokens in chrome:
            if not tokens:
                problems.append(
                    f"prints {what} carrying no class, so no rule can keep it out of a copy"
                )
            elif not any(neutralised(sheets, token) for token in tokens):
                problems.append(
                    f"prints {what} and no rule in the stylesheet the page loads keeps it out "
                    "of a copy, so a reader's selection takes it"
                )
        if problems:
            failures.append((where, problems))
    if failures:
        for where, problems in failures:
            for problem in problems:
                print(
                    f"check-claims: the Run section at {where} {problem}; a `$ ` or a label "
                    "pasted into a shell is a command that does not exist",
                    file=sys.stderr,
                )
        return 1
    if promptless:
        print(
            f"check-claims: the Run section at {', '.join(promptless)} prints no prompt element, "
            "and the section's design prints a `$ ` in front of each block; a pin that reaches no "
            "prompt is not checking one",
            file=sys.stderr,
        )
        return 2
    if not reached:
        print(
            f"check-claims: none of {len(pages)} scanned file(s) carries the Run section's "
            "command block, so no prompt or label of it was read",
            file=sys.stderr,
        )
        return 2
    print(
        "check-claims: every `$ ` prompt and label the Run section prints is named by a rule in "
        "the stylesheet the served page loads that takes it out of a selection, so a reader's "
        "copy of the command does not carry the prompt or the labels"
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
    address is worth a sentence only if that path reaches the server. This is the plain request:
    the server refuses one that asks for no upgrade with its own JSON, and
    `session_path_reaches_the_server` is what decides it. The upgrade the clients actually open is
    a different request and is read by `demo_upgrade_route`, which asserts the handshake when the
    edge in front of the host answers it and records the refusal when the edge answers the probe's
    egress instead.
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


# The WebSocket handshake the clients perform on the address the page hands a reader, RFC 6455:
# the fixed GUID every server hashes a client's key with, and the deadline the read is bounded by.
# A socket that completes the handshake and sends no `hello` is answered with a `session.error`
# frame once the server's `hello_timeout` expires (`specification/schema/limits.json`, 10
# seconds), so the read has to outlast that limit rather than assume a frame arrives at once.
WS_GUID = "258EAFA5-E914-47DA-95CA-C5AB0DC85B11"
WS_OPCODE_TEXT = 0x1
WS_OPCODE_BINARY = 0x2
# How much of a refusal's body the probe reads: enough to say whether the server answered and to
# quote what did, in its own words. A refusal is read for its shape, never for its whole text.
REFUSAL_BODY_LIMIT = 512


@dataclass(frozen=True)
class UpgradeAnswer:
    """What the instance answered the WebSocket upgrade with, as the probe read it.

    `status` is `0` when no HTTP head arrived at all within `REQUEST_TIMEOUT_SECONDS`, which is
    neither a refusal nor a handshake. `media_type` and `body` are the refusal's own shape, read
    because which answer a `4xx` is — the server's own or something in front of it — decides
    whether the page's sentence is in question at all.
    """

    status: int
    accept_matches: bool
    frame: bytes
    media_type: str
    body: bytes

    def refused_by_the_edge(self) -> bool:
        """Whether something in front of the server refused the upgrade, rather than the server.

        Apart from a handshake, the server answers this path with JSON of its own: the plain
        request on the same address is read the same way, by `session_path_reaches_the_server`, and
        a server that answered an upgrade with a refusal of its own would be a defect the address
        the page hands over cannot survive. So a `4xx` that is neither that JSON nor a `404` came
        from something in front of the server — Cloudflare's bot list, for one, answers a
        hand-rolled upgrade from an egress it distrusts with `403`, `text/plain` and
        `error code: 1010` — and says what that network did, not what the page claims. A `404` is
        not that whatever its body is: it says the path itself is not there, which is a sentence
        about the address the page hands a reader. Nothing else is read here: `5xx`, `3xx` and
        `2xx` are not refusals at all and stay the caller's failure, and `0` is no answer having
        arrived.
        """
        if not 400 <= self.status <= 499 or self.status == 404:
            return False
        return self.media_type != "application/json"


def media_type_of(header: str) -> str:
    """A `Content-Type` header as the media type alone, lowercased: its parameters are not it.

    The plain request's media type comes from `urllib`'s own header object; this is the same
    reading for a response read off a socket, which has no such object.
    """
    return header.split(";", 1)[0].strip().lower()


def refusal_description(answer: UpgradeAnswer) -> str:
    """A refusal as the record states it: its status, its media type and its own first words.

    A log line naming all three says which conversation answered the probe, so nobody has to ask
    the host again to find out what happened.
    """
    first_line = answer.body.decode("utf-8", "replace").strip().partition("\n")[0].strip()
    words = f", {first_line!r}" if first_line else ""
    return f"{answer.status} ({answer.media_type or 'no media type'}{words})"


def _recv_exactly(connection: ssl.SSLSocket, count: int) -> bytes:
    """Up to `count` bytes, stopping when the connection's own timeout runs out."""
    data = b""
    while len(data) < count:
        try:
            chunk = connection.recv(count - len(data))
        except (TimeoutError, socket.timeout):
            break
        if not chunk:
            break
        data += chunk
    return data


def _read_websocket_frame(connection: ssl.SSLSocket) -> bytes:
    """The payload of the next data frame on the connection, or `b""` for anything else.

    A control frame (a ping, a close) is deliberately not the answer this reads: what the check
    is after is the server's own envelope, and a control frame is the connection rather than the
    protocol's first word. A frame that times out part-way is reported as none as well, so the
    caller says what it observed instead of reading a truncated payload as one.
    """
    header = _recv_exactly(connection, 2)
    if len(header) < 2:
        return b""
    opcode = header[0] & 0x0F
    masked = bool(header[1] & 0x80)
    length = header[1] & 0x7F
    if length == 126:
        extended = _recv_exactly(connection, 2)
        if len(extended) < 2:
            return b""
        length = int.from_bytes(extended, "big")
    elif length == 127:
        extended = _recv_exactly(connection, 8)
        if len(extended) < 8:
            return b""
        length = int.from_bytes(extended, "big")
    mask = _recv_exactly(connection, 4) if masked else b""
    if masked and len(mask) < 4:
        return b""
    payload = _recv_exactly(connection, length)
    if len(payload) < length:
        return b""
    if masked:
        payload = bytes(byte ^ mask[index % 4] for index, byte in enumerate(payload))
    if opcode not in (WS_OPCODE_TEXT, WS_OPCODE_BINARY):
        return b""
    return payload


def _read_refusal_body(connection: ssl.SSLSocket, head: bytes, buffered: bytes) -> bytes:
    """Up to `REFUSAL_BODY_LIMIT` bytes of the body of the response whose head is `head`.

    `buffered` is what arrived with the head. Only a `Content-Length` is believed, and a body that
    keeps arriving is cut at the limit: what a refusal is read for is the shape of what answered.
    A body that never arrives is reported as none rather than waited for.
    """
    body = buffered[:REFUSAL_BODY_LIMIT]
    length = 0
    for line in head.split(b"\r\n")[1:]:
        if line.lower().startswith(b"content-length:"):
            try:
                length = int(line.split(b":", 1)[1].strip())
            except ValueError:
                length = 0
    wanted = min(length, REFUSAL_BODY_LIMIT)
    while len(body) < wanted:
        chunk = _recv_exactly(connection, wanted - len(body))
        if not chunk:
            break
        body += chunk
    return body


def demo_upgrade_route() -> UpgradeAnswer:
    """What the instance answers a WebSocket upgrade on the session path with.

    The address the page hands a reader is one an editor opens a socket on, so the handshake is
    the sentence's own assertion: `session_path_reaches_the_server` decides the plain request, and
    a proxy that answers that one and refuses the upgrade would pass a check that never made this
    one. This performs the handshake the clients perform, and reads the answer as the status,
    whether its `Sec-WebSocket-Accept` is the client key's own digest, the payload of its first
    data frame — the server's envelope, which the caller reads against the one wire version — and,
    when the answer is no handshake, the refusal's own shape. An egress the edge refuses is a
    different fact from the server answering, and `UpgradeAnswer.refused_by_the_edge` is what
    tells the two apart.
    """
    context = ssl.create_default_context()
    with socket.create_connection(
        (DEMO_HOST, 443), timeout=REQUEST_TIMEOUT_SECONDS
    ) as raw:
        with context.wrap_socket(raw, server_hostname=DEMO_HOST) as connection:
            connection.settimeout(REQUEST_TIMEOUT_SECONDS)
            key = base64.b64encode(os.urandom(16)).decode("ascii")
            connection.sendall(
                (
                    f"GET {SESSION_PATH} HTTP/1.1\r\n"
                    f"Host: {DEMO_HOST}\r\n"
                    "Upgrade: websocket\r\n"
                    "Connection: Upgrade\r\n"
                    f"Sec-WebSocket-Key: {key}\r\n"
                    "Sec-WebSocket-Version: 13\r\n"
                    f"User-Agent: {USER_AGENT}\r\n"
                    "\r\n"
                ).encode("ascii")
            )
            raw = b""
            while b"\r\n\r\n" not in raw and len(raw) <= 64 * 1024:
                try:
                    chunk = connection.recv(4096)
                except (TimeoutError, socket.timeout):
                    break
                if not chunk:
                    break
                raw += chunk
            head, _, buffered = raw.partition(b"\r\n\r\n")
            lines = head.split(b"\r\n")
            if not lines or not lines[0].startswith(b"HTTP/"):
                return UpgradeAnswer(0, False, b"", "", b"")
            status = int(lines[0].split(b" ", 2)[1])
            accept = ""
            media_type = ""
            for line in lines[1:]:
                lowered = line.lower()
                if lowered.startswith(b"sec-websocket-accept:"):
                    accept = line.split(b":", 1)[1].strip().decode("ascii", "replace")
                elif lowered.startswith(b"content-type:"):
                    media_type = media_type_of(line.split(b":", 1)[1].decode("ascii", "replace"))
            expected = base64.b64encode(
                hashlib.sha1((key + WS_GUID).encode("ascii")).digest()
            ).decode("ascii")
            if status != 101:
                return UpgradeAnswer(
                    status,
                    accept == expected,
                    b"",
                    media_type,
                    _read_refusal_body(connection, head, buffered),
                )
            return UpgradeAnswer(
                status, accept == expected, _read_websocket_frame(connection), media_type, b""
            )


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
    instance cannot be asked. A refusal an edge answers the upgrade probe with is the probe's own
    egress rather than the page, so it is recorded and a run it happened on still returns 0 here.
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
        upgrade = demo_upgrade_route()
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
            f"is {SERVER_IMAGE.rsplit('/', 1)[-1]}, so this is a different thing answering "
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

    # The upgrade is the sentence's own assertion, and the one thing between the probe and it that
    # is not the page is the network the probe runs from: a refusal the edge answers is recorded,
    # and every outcome the page's claim depends on stays a failure. `upgrade_recorded` is what
    # makes the closing line say which of the two runs this was.
    upgrade_recorded = False
    if upgrade.status != 101:
        if upgrade.refused_by_the_edge():
            upgrade_recorded = True
            print(
                f"check-claims: {DEMO_HOST}{SESSION_PATH} answered the WebSocket upgrade with "
                f"{refusal_description(upgrade)} rather than the server's own JSON: that is the "
                "edge in front of the server refusing this probe's egress, and not the server and "
                "not the page the sentences are about, so the refusal is recorded here and the "
                "handshake is not asserted on this run"
            )
        elif upgrade.status == 0:
            print(
                f"check-claims: {DEMO_ORIGIN}{SESSION_PATH} sent no HTTP answer to a WebSocket "
                f"upgrade within {REQUEST_TIMEOUT_SECONDS}s, and the page hands a reader "
                f"{DEMO_REFERENCES[-1]!r} as the address to give an editor: the clients open a "
                "socket on that address, and a socket that is answered nothing at all is not one "
                "an editor can use",
                file=sys.stderr,
            )
            return 1
        else:
            print(
                f"check-claims: {DEMO_ORIGIN}{SESSION_PATH} answered a WebSocket upgrade with "
                f"{upgrade.status}, and the page hands a reader {DEMO_REFERENCES[-1]!r} as the "
                "address to give an editor: the clients open a socket on that address, so the "
                "upgrade has to be accepted, and a plain path that answers while the upgrade does "
                "not is a name an editor cannot use",
                file=sys.stderr,
            )
            return 1

    if upgrade.status == 101:
        if not upgrade.accept_matches:
            print(
                f"check-claims: {DEMO_ORIGIN}{SESSION_PATH} answered a WebSocket upgrade with a "
                "`Sec-WebSocket-Accept` that is not the client key's own digest: the 101 did not "
                "complete a WebSocket handshake, so it is not the upgrade an editor opens",
                file=sys.stderr,
            )
            return 1

        try:
            handshake = json.loads(upgrade.frame)
        except (json.JSONDecodeError, UnicodeDecodeError):
            handshake = None
        if not isinstance(handshake, dict) or handshake.get("v") != WIRE:
            observed = "nothing" if not upgrade.frame else repr(upgrade.frame[:120])
            print(
                f"check-claims: {DEMO_ORIGIN}{SESSION_PATH} accepted the WebSocket upgrade and "
                f"sent {observed} as its first frame, and the page's own sentences put the one "
                f"wire version, {WIRE}, on that address: a socket that opened and produced no "
                "frame of the server's is a relay the page's claim does not reach",
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

    if upgrade_recorded:
        print(
            f"check-claims: the demo instance {DEMO_ORIGIN} answers, reports {reported!r} offering "
            f"{', '.join(offered)}, answers {SESSION_PATH} with the server's own JSON "
            f"({session_status}), and serves a page whose shell carries the host card; the "
            f"WebSocket upgrade on {SESSION_PATH} was refused by the edge in front of the server, "
            "which is recorded above and is not asserted on this run"
        )
        return 0

    print(
        f"check-claims: the demo instance {DEMO_ORIGIN} answers, reports {reported!r} offering "
        f"{', '.join(offered)}, answers {SESSION_PATH} with the server's own JSON "
        f"({session_status}), accepts a WebSocket upgrade there with a {WIRE} frame, and serves "
        "a page whose shell carries the host card"
    )
    return 0


def disclosure_region(page: Scanned) -> str:
    """The page from its own `docker run` on: the text the relay's disclosure is read from.

    The paragraph sits under the packed command because a reader can take the claim and the
    command together, which is also what tells the paragraph apart from the hero. What is read is
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
    every collaborative tool decides for itself, so those two have to be read as the panel's own
    wording. The region is the page from the
    `docker run` that pulls the page's image onwards: the panel's place under that command is
    part of the claim, the chips and the heading over them state the facts a line at a time, and a
    hero line above the command is not where a reader is owed them. Returns 0 when a
    scanned page carries all four below its own command and 1 when none does; it asks no network.
    """
    if not any(IMAGE_REFERENCE.search(page.text) for page in pages):
        print(
            f"check-claims: none of {len(pages)} scanned file(s) carries a reference to "
            f"{' or '.join(PUBLISHED_IMAGES)}, and what the relay still sees is read from "
            "the page's own `docker run` onwards: without that command the panel has "
            "nowhere its place puts it",
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
    - that every registry-shaped word on the page is part of one of those two names or of the
      JetBrains Marketplace's, where the JetBrains plugin is handed over, so a page offering a
      client from somewhere else — "the extension gallery", the Eclipse marketplace, another
      editor's store — fails rather than passing on the names it also carries;
    - that any link the page does carry to a listing is one of the two or the JetBrains plugin's,
      so a listing that is not one of them fails on the destination rather than on the label.

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
            for _, pattern in (*PUBLISHED_REGISTRIES, JETBRAINS_REGISTRY)
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
                f"check-claims: the page names a registry at {where}, and the extension is "
                f"published to {' and '.join(name for name, _ in PUBLISHED_REGISTRIES)} and the "
                f"JetBrains plugin to {JETBRAINS_REGISTRY[0]}. A registry the project does not "
                "publish to is a distribution channel it does not have, and \"the extension "
                "gallery\" names a channel without naming which",
                file=sys.stderr,
            )
        return 1

    missing = [
        f"{os.path.relpath(scanned.path, root)}:{line}: {destination!r}"
        for scanned in pages
        for destination, line in scanned.destinations
        if REGISTRY_LISTING.search(destination) and destination not in KNOWN_LISTINGS
    ]
    if missing:
        for where in missing:
            print(
                f"check-claims: the page links a listing at {where}, and the extension is "
                f"published as `{PUBLISHED_EXTENSION}`, whose listing on each registry is "
                f"{' and '.join(EXTENSION_LISTINGS)}, and the JetBrains plugin's listing is "
                f"{JETBRAINS_LISTING}. A link to a listing is a claim about which one, and the "
                "retired ID's listing is one that no longer exists: a reader sent to that address "
                "finds nothing,",
                file=sys.stderr,
            )
        return 1

    print(
        f"check-claims: the page hands a reader `{PUBLISHED_EXTENSION}` on "
        f"{' and '.join(name for name, _ in PUBLISHED_REGISTRIES)}, names no registry the "
        "project does not publish to, links no listing but the extension's and the JetBrains "
        "plugin's, and says an install is the client and not a server"
    )
    return 0


# What the Marketplace's answers for the plugin have to say, read by `jetbrains_listing_problems`.
# Each fixture is a plugin answer and a version list of the API's shapes with the defect its name
# gives written into them, and the fragment the reading has to report for it; an empty fragment is a
# pair the reading has to pass. They run before the scan, so a reading that stops telling a listing
# in review from a public one fails the check rather than passing every page.
JETBRAINS_PLUGIN = {"id": JETBRAINS_PLUGIN_ID, "link": JETBRAINS_LISTING_PATH, "approve": False}
JETBRAINS_VERSION = {
    "pluginId": JETBRAINS_PLUGIN_ID,
    "version": "0.1.0",
    "channel": "",
    "approve": True,
    "listed": True,
    "hidden": False,
}
JETBRAINS_LISTING_FIXTURES: tuple[tuple[str, object, object, str], ...] = (
    ("a public listing", JETBRAINS_PLUGIN, [JETBRAINS_VERSION], ""),
    (
        "a public listing with a newer version in review",
        JETBRAINS_PLUGIN,
        [{**JETBRAINS_VERSION, "version": "0.2.0", "approve": False}, JETBRAINS_VERSION],
        "",
    ),
    (
        "a listing whose only version is in review",
        JETBRAINS_PLUGIN,
        [{**JETBRAINS_VERSION, "approve": False}],
        "no version is approved",
    ),
    ("a listing with no version", JETBRAINS_PLUGIN, [], "no version is approved"),
    (
        "an approval written as a string",
        JETBRAINS_PLUGIN,
        [{**JETBRAINS_VERSION, "approve": "true"}],
        "no version is approved",
    ),
    (
        "an approved version that is unlisted",
        JETBRAINS_PLUGIN,
        [{**JETBRAINS_VERSION, "listed": False}],
        "no version is approved",
    ),
    (
        "an approved version that is hidden",
        JETBRAINS_PLUGIN,
        [{**JETBRAINS_VERSION, "hidden": True}],
        "no version is approved",
    ),
    (
        "an approved version on a channel other than stable",
        JETBRAINS_PLUGIN,
        [{**JETBRAINS_VERSION, "channel": "eap"}],
        "no version is approved",
    ),
    (
        "another plugin's version",
        JETBRAINS_PLUGIN,
        [{**JETBRAINS_VERSION, "pluginId": JETBRAINS_PLUGIN_ID + 1}],
        "no version is approved",
    ),
    (
        "another plugin's listing",
        {**JETBRAINS_PLUGIN, "id": JETBRAINS_PLUGIN_ID + 1, "link": "/plugin/34764-other"},
        [JETBRAINS_VERSION],
        f"plugin {JETBRAINS_PLUGIN_ID + 1}",
    ),
    (
        "the listing moved to another address",
        {**JETBRAINS_PLUGIN, "link": "/plugin/34763-renamed"},
        [JETBRAINS_VERSION],
        "/plugin/34763-renamed",
    ),
    ("an answer that is not an object", [JETBRAINS_PLUGIN_ID], [JETBRAINS_VERSION], "not a JSON object"),
    ("a version list that is not a list", JETBRAINS_PLUGIN, JETBRAINS_VERSION, "not a JSON list"),
)


def jetbrains_listing_problems(answer: object, versions: object) -> list[str]:
    """What the Marketplace's answers for the plugin say against the page, or [] when they hold.

    The plugin answer has to be about the plugin the page links, at the address the page links,
    and one of its versions has to be one a reader installs: on the stable channel, listed, not
    hidden, and approved by JetBrains. `approve` and `listed` are read as the JSON `true` and
    nothing looser, so a string or a number in their place is not taken for an approval.
    """
    if not isinstance(answer, dict):
        return [f"the answer is not a JSON object ({type(answer).__name__})"]
    problems: list[str] = []
    plugin = answer.get("id")
    if plugin != JETBRAINS_PLUGIN_ID or isinstance(plugin, bool):
        problems.append(f"it describes plugin {plugin!r}, and the page links {JETBRAINS_PLUGIN_ID}")
    link = answer.get("link")
    if link != JETBRAINS_LISTING_PATH:
        problems.append(
            f"it puts the listing at {link!r}, and the page links {JETBRAINS_LISTING_PATH!r}"
        )
    if not isinstance(versions, list):
        problems.append(f"its version list is not a JSON list ({type(versions).__name__})")
        return problems
    public = [
        one
        for one in versions
        if isinstance(one, dict)
        and one.get("pluginId") == JETBRAINS_PLUGIN_ID
        and one.get("channel") == ""
        and one.get("approve") is True
        and one.get("listed") is True
        and one.get("hidden") is not True
    ]
    if not public:
        problems.append(
            f"no version is approved, listed and on the stable channel among the {len(versions)} "
            "it lists: JetBrains has not approved the plugin yet, so it is not public"
        )
    return problems


def jetbrains_listing(api: str = JETBRAINS_LISTING_API) -> object:
    """The Marketplace's answer at `api`, as JSON. Raises when it cannot be asked."""
    request = urllib.request.Request(api)
    request.add_header("Accept", "application/json")
    request.add_header("User-Agent", USER_AGENT)
    with urllib.request.urlopen(request, timeout=REQUEST_TIMEOUT_SECONDS) as response:
        return json.loads(response.read())


def check_jetbrains_listing(pages: list[Scanned]) -> int:
    """The JetBrains route against the listing it links, and the listing against the Marketplace.

    The page hands the plugin over in the terminal's JetBrains route, so that route has to name the
    JetBrains Marketplace and link the plugin's listing, read from the route's own panel. Then the
    Marketplace is asked about the plugin and its versions: the listing has to be the one the route
    links and JetBrains has to have approved a version of it, because a listing with no approved
    version is not one a reader can install from, and the route says the plugin is published there.

    Returns 0 when it holds, 1 when the page or the Marketplace disproves the route, and 2 when the
    Marketplace cannot be asked.
    """
    root = root_of_this_checkout()
    page = next(
        (one for one in pages if install_panel_markup(one.raw, JETBRAINS_ROUTE) is not None), None
    )
    if page is None:
        print(
            f"check-claims: none of {len(pages)} scanned file(s) carries the JetBrains install "
            "route, and the grid says the JetBrains plugin is available: a client the page offers "
            "has to say where a reader installs it",
            file=sys.stderr,
        )
        return 1
    where = os.path.relpath(page.path, root)
    route = install_panel_markup(page.raw, JETBRAINS_ROUTE) or ""
    absent = []
    if not JETBRAINS_REGISTRY[1].search(normalise(route)[0]):
        absent.append(JETBRAINS_REGISTRY[0])
    if JETBRAINS_LISTING not in [found for found, _ in destinations(route)]:
        absent.append(f"a link to {JETBRAINS_LISTING}")
    if absent:
        print(
            f"check-claims: the JetBrains route in {where} is missing {' and '.join(absent)}. "
            "The route is where a reader is handed the plugin, so it names the registry and "
            "links the listing it installs from",
            file=sys.stderr,
        )
        return 1

    try:
        answer = jetbrains_listing()
        versions = jetbrains_listing(JETBRAINS_VERSIONS_API)
    except urllib.error.HTTPError as error:
        print(
            f"check-claims: {error.url} answered {error.code} {error.reason}; the "
            f"route links {JETBRAINS_LISTING}, and a listing the Marketplace does not describe "
            "is one nothing can confirm",
            file=sys.stderr,
        )
        return 1 if error.code == 404 else 2
    except (urllib.error.URLError, OSError, ValueError) as error:
        print(
            f"check-claims: cannot ask {JETBRAINS_LISTING_API} about the plugin and its "
            f"versions ({error}); the "
            "JetBrains route cannot be checked against the listing it links, so this is a "
            "failure rather than a pass",
            file=sys.stderr,
        )
        return 2

    problems = jetbrains_listing_problems(answer, versions)
    if problems:
        print(
            f"check-claims: the JetBrains route in {where} links {JETBRAINS_LISTING} and says the "
            f"plugin is published on {JETBRAINS_REGISTRY[0]}, and {JETBRAINS_LISTING_API} "
            f"and its versions answer that {'; '.join(problems)}. The route waits for that approval",
            file=sys.stderr,
        )
        return 1

    print(
        f"check-claims: the JetBrains route links {JETBRAINS_LISTING} on "
        f"{JETBRAINS_REGISTRY[0]}, and the Marketplace lists a version JetBrains approved"
    )
    return 0


# The card the page offers and does not have: a hosted tier the project would run for the reader.
# Its parts are one claim — the card, the status on it, the sentence saying who would run it, and
# the row that is a plan rather than a control — and each is a required fact of its own, so a
# rewrite that keeps the fact passes and a card that drops it fails.
#
# The status is stated once, in either of two spellings: the pill says the tier is not available
# yet and the row calls it planned. The pattern reads both rather than requiring both; a card that
# states it
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
    (
        "jetbrains_client",
        "JetBrains IDE plugin",
        "available",
        re.compile(r"\bjetbrains_client[^.]{0,32}available\b", re.IGNORECASE),
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
    markup = install_panel_markup(raw, panel)
    return normalise(markup)[0] if markup is not None else None


def install_panel_markup(raw: str, panel: str) -> str | None:
    """One install route's own markup, its panel read to the panel's own closer, or None."""
    opening = re.compile(
        rf'<(?P<tag>[a-z][\w-]*)\b[^>]*\bid="install-panel-{re.escape(panel)}"[^>]*>',
        re.IGNORECASE,
    )
    match = opening.search(raw)
    element = element_from(raw, match) if match is not None else None
    return element[1] if element is not None else None


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
    else the grid carries: the specification is the source of truth, every client the page hands
    over keeps a row that says it is available, and the extension's row is the one a reader is
    also handed an install for.
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
    facts = [(f"the {name} row", pattern) for name, _desc, _status, pattern in GRID_PINNED_ROWS]
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
    # hold the facts that have to stay true of the rows the page carries by name.
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

    print(
        f"check-claims: the grid draws {len(rows)} rows, {len(linked_repos)} of them linked, "
        f"and its {len(client_rows)} clients, its {len(chips)} chips and its {len(routes)} "
        "install routes name the same ones. Each row joins its own name, description and word "
        "to its own link, every row left unlinked says it is a plan, every repository the page "
        f"links is one the grid links, and the extension is handed over in a VS Code install "
        f"route that names `{PUBLISHED_EXTENSION}` on both registries it is published to"
    )
    return 0


def wire_binding_problems(
    page: Scanned, offered: tuple[str, ...], image_wires: dict[str, str]
) -> list[str]:
    """What this page says about the wire that the artefacts behind it do not support.

    Nothing here has to be said: the page names no wire version and binds no artefact to one. Each
    rule reads what a page does say and holds it to the thing it names, so a sentence that comes
    back is checked the moment it is written rather than passing unread.
    """
    problems: list[str] = []
    image = WIRE_OF_IMAGE.search(page.text)
    if image is not None:
        # The command pulls two images, so a sentence about the wire of "the image" is held to
        # every reference the page hands over rather than to one of them.
        for reference, wire in sorted(image_wires.items()):
            if image.group(1) != wire:
                problems.append(
                    f"it says the images under the `docker run` speak {image.group(1)!r}, and "
                    f"{reference} speaks {wire}"
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
            f"it calls the wire unreleased ({unreleased.group(0)!r}), and the references the "
            f"page hands a reader ({', '.join(IMAGE_REFERENCES)}) speak it "
            "(`IMAGE_WIRE_BY_REFERENCE`)"
        )
    return problems


def check_wire_binding(pages: list[Scanned]) -> int:
    """Which wire version the page says each artefact it hands a reader speaks.

    The page hands a reader one `docker run` and one instance address, there is one wire version,
    and it is the sealed one. What is read here is what the page says about the wire, and behind
    that the artefacts against each other. The wire each reference speaks is read from
    `IMAGE_WIRE_BY_REFERENCE`,
    because no registry answers what wire a binary or a bundle speaks and a reference the map does
    not name has to declare its wire in the same wave; the instance's half is measured, from
    `/meta`, where no wording can forge it. A reference the instance does not offer, or a version
    the page names that this protocol does not have, is a reader pasting the command under the
    sealing paragraph and getting a server that carries the room through it in the clear — the
    failure a confidentiality feature cannot have, and the one the pairing of the command and the
    paragraph is for.

    Returns 0, 1 when a page says something the artefacts disprove, 2 when the instance cannot
    be asked or this file cannot say what a reference speaks.
    """
    root = root_of_this_checkout()
    undeclared = [
        reference
        for reference in IMAGE_REFERENCES
        if reference not in IMAGE_WIRE_BY_REFERENCE
    ]
    if undeclared:
        print(
            f"check-claims: the page hands a reader {', '.join(undeclared)} and nothing here "
            "says which wire version that reference speaks (see `IMAGE_WIRE_BY_REFERENCE`); a "
            "reference whose wire is unknown cannot be held to what the page hands over "
            "beside it",
            file=sys.stderr,
        )
        return 2
    image_wires = {
        reference: IMAGE_WIRE_BY_REFERENCE[reference]
        for reference in IMAGE_REFERENCES
    }
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
    unreachable = sorted({wire for wire in image_wires.values() if wire not in offered})
    if unreachable:
        print(
            f"check-claims: the page hands a reader {', '.join(IMAGE_REFERENCES)}, which speak "
            f"{', '.join(unreachable)}, and {DEMO_ORIGIN}/meta offers {', '.join(offered)}: the "
            "command and the address on the page are not the same protocol, so a reader who "
            "follows both meets a version one of the two does not have",
            file=sys.stderr,
        )
        return 1

    failed: list[tuple[str, list[str]]] = []
    for page in pages:
        problems = wire_binding_problems(page, offered, image_wires)
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
        + f"; the references the page hands a reader ({', '.join(IMAGE_REFERENCES)}) speak "
        f"{', '.join(sorted(set(image_wires.values())))} and {DEMO_ORIGIN}/meta offers "
        f"{', '.join(offered)}, so the artefacts the page hands a reader speak the same "
        "version, and nothing here names another one or calls the wire unreleased"
    )
    return 0


def fixture_failure(what: str, problems: list[str], expected: str) -> str:
    """Why a fixture is not reading the rule it names, or '' when it is.

    A fixture with an expected fragment names a defect its rule has to report, and one with an
    empty fragment is a correct command that rule has to leave alone. Either failure is reported
    here rather than passing: a rule that stops matching the shape it was written for passes
    everything, and one that starts failing a correct command fails a page that is right.
    """
    if expected and not any(expected in problem for problem in problems):
        return (
            f"the Run section fixture {what!r} is the defect {expected!r} names and is not reported "
            "as one; a rule that stops matching the shape it was written for passes everything"
        )
    if not expected and problems:
        return (
            f"the Run section fixture {what!r} is a correct command and is reported as "
            f"{'; '.join(problems)}, so the rule that reads it fails a page that is right"
        )
    return ""


def reddened_run_fixtures() -> list[str]:
    """The Run section fixtures the rules as they now stand report, by name."""
    reddened: list[str] = []
    for what, shape, expected in RUN_FIXTURES:
        if shape is None:
            continue
        problems = run_section_problems([[line] for line in shape])
        if fixture_failure(what, problems, expected):
            reddened.append(what)
    return reddened


def reddened_run_address_fixtures() -> list[str]:
    """The Run section address fixtures the rules as they now stand report, by name."""
    reddened: list[str] = []
    for what, opened_at, shape, expected in RUN_OPENED_AT_FIXTURES:
        if shape is None:
            continue
        problems = run_section_opened_at_problems(opened_at, [[line] for line in shape])
        if fixture_failure(what, problems, expected):
            reddened.append(what)
    return reddened


def run_section_reading_problems() -> list[str]:
    """Every reading the section's rules do, against the fixture that has to hold it.

    A fixture holds a rule when it pins the fragment the rule emits; it holds a *reading* when
    swapping that reading for the weaker one a later edit would leave in its place turns a fixture
    red, and those are two different things. Each place is one a weaker reading would replace: the
    published host
    port is one — every mapping a fixture carries is `8080:8080`, where the field before the last
    colon and the one after it are one number, so reading the container port would answer for the
    host port unless a fixture writes two different numbers; and the network a run attaches its
    container to is another, because a fixture that names a network plainly does not tell a
    `\b{name}\b` search apart from the whole name unless some fixture writes `--network room-net`
    beside `docker network create room`.

    So each place is swapped on its own — one place at a time, so the fixture that reddens is the
    one holding *that* place and not a fixture some other place reddened — and a reading which
    leaves every fixture green is reported here rather than left in place. The three ways that
    happens are told apart: a place the rules no longer read, a place no fixture clause tells the
    two readings apart at, and a place whose difference never reaches a rule's answer.
    """
    problems: list[str] = []
    for site in RUN_READINGS:
        swapped_readings.add(site)
        try:
            reddened = reddened_run_fixtures()
        finally:
            swapped_readings.discard(site)
        if reddened:
            continue
        if site not in readings_reached:
            problems.append(
                f"the name reading {site!r} is a place the rules no longer read, so the table "
                "names a comparison nothing makes"
            )
        elif site not in readings_disagreed:
            problems.append(
                f"the name reading {site!r} can be replaced with a `\\b{{name}}\\b` search with "
                "every Run section fixture still green, and no fixture reaches a clause there where "
                "the two readings differ: a reading no fixture tells apart is a reading nothing "
                "holds"
            )
        else:
            problems.append(
                f"the name reading {site!r} can be replaced with a `\\b{{name}}\\b` search with "
                "every Run section fixture still green although a fixture reads a name there the two "
                "readings differ on: the difference never reaches a rule's answer"
            )

    global published_port_reading
    published_port_reading = container_port_of_mapping
    try:
        reddened = reddened_run_address_fixtures()
    finally:
        published_port_reading = host_port_of_mapping
    if not reddened:
        problems.append(
            "the published host port can be read as the mapping's container port with every Run "
            "section address fixture still green: no fixture publishes the host port and the "
            "container port as two different numbers"
        )
    return problems


# The patterns a container name, a network name or an image reference is read out of, and the name
# a field read out of one has to be read as. The address's `url` group is deliberately not here: it
# is a URL a rule prints and reads a host out of, and the host is what `server_address_host` mints.
FIELD_PATTERNS = frozenset({"CONTAINER_NAME", "NETWORK_FLAG", "IMAGE_REFERENCE"})
MINTED_FIELD = "ParsedName"

# The entries the scan walks out from, and the values it walks out from beside them. What these
# reach is what the scan reads, so a function the rules call is a function the scan covers — and so
# is one the rules reach through a table or a variable rather than by calling it.
RULE_ENTRY_POINTS = ("run_section_problems", "run_section_opened_at_problems")


def called_names(node: ast.AST) -> set[str]:
    """The names called anywhere in `node`."""
    return {
        call.func.id
        for call in ast.walk(node)
        if isinstance(call, ast.Call) and isinstance(call.func, ast.Name)
    }


def named_function_values(tree: ast.Module, functions: dict[str, ast.FunctionDef]) -> set[str]:
    """Every function of this file a module-level value of it *is*, rather than a call it is in.

    `called_names` follows a bare call, and the rules do not reach every function that way: the four
    places a name is compared sit in `RUN_READINGS` and are called through the table, and the
    mapping reading the fixture harness swaps sits in a variable, so a function reachable only as
    a value has to be walked as one. What is read is a value that is
    one of these functions, or a collection of
    them: the table and the variable, and not a function handed to another call.
    `first_page_stating(pages, RELAY_DISCLOSURE, disclosure_region)` names one too, and that one
    reads the page's image reference rather than a name out of the section.
    """
    named: set[str] = set()
    for node in tree.body:
        if not isinstance(node, (ast.Assign, ast.AnnAssign)):
            continue
        value = node.value
        if value is None:
            continue
        collected = (
            list(ast.walk(value))
            if isinstance(value, (ast.Dict, ast.Tuple, ast.List, ast.Set))
            else [value]
        )
        named |= {
            inner.id
            for inner in collected
            if isinstance(inner, ast.Name) and inner.id in functions
        }
    return named


def reached_functions(roots: Iterable[str], functions: dict[str, ast.FunctionDef]) -> set[str]:
    """Every function of this file `roots` reach, by name, transitively."""
    reached = {root for root in roots if root in functions}
    pending = list(reached)
    while pending:
        for name in called_names(functions[pending.pop()]):
            if name in functions and name not in reached:
                reached.add(name)
                pending.append(name)
    return reached


def reads_a_field_pattern(node: ast.AST | None) -> bool:
    """Whether `node` reads a match out of one of the field patterns, however it is written.

    The whole value is walked rather than its outer call alone. A match bound through a conditional
    expression, an `or`, a `list(…)`, an `enumerate(…)` or a `re.search(PATTERN, …)` is the same
    read a direct `PATTERN.search(…)` is, and following only the direct spelling left the other
    bindings unread: a name taken out of one of them and compared with a stretch search or a
    `.startswith` on the text passed the scan written to refuse exactly that.
    """
    if node is None:
        return False
    return any(
        isinstance(inner, ast.Name) and inner.id in FIELD_PATTERNS for inner in ast.walk(node)
    )


def bound_names(target: ast.AST) -> set[str]:
    """Every name an assignment, a loop, a comprehension or a walrus binds."""
    if isinstance(target, ast.Name):
        return {target.id}
    if isinstance(target, (ast.Tuple, ast.List)):
        return {name for element in target.elts for name in bound_names(element)}
    return set()


def field_match_names(function: ast.FunctionDef) -> set[str]:
    """The names `function` binds to a match of one of the field patterns.

    Every place a name can be bound is read: an assignment, an annotated one, a loop, a
    comprehension and a walrus. A tuple target is read for all of its names, so a shape this does
    not tell apart is one it reads as a field rather than one it misses. What is bound is any value
    that names one of the patterns anywhere inside it, for the reason `reads_a_field_pattern`
    gives.
    """
    matches: set[str] = set()
    for node in ast.walk(function):
        target: ast.AST | None = None
        source: ast.AST | None = None
        if isinstance(node, ast.Assign):
            targets = node.targets
            source = node.value
            if reads_a_field_pattern(source):
                matches |= {name for one in targets for name in bound_names(one)}
            continue
        if isinstance(node, ast.AnnAssign):
            target, source = node.target, node.value
        elif isinstance(node, (ast.For, ast.comprehension)):
            target, source = node.target, node.iter
        elif isinstance(node, ast.NamedExpr):
            target, source = node.target, node.value
        if target is not None and reads_a_field_pattern(source):
            matches |= bound_names(target)
    return matches


def carried_by_names(function: ast.FunctionDef) -> dict[int, set[str]]:
    """The plain names each expression of `function` is assigned to, by identity."""
    bindings: dict[int, set[str]] = {}
    for node in ast.walk(function):
        targets: list[ast.AST] = []
        value: ast.AST | None = None
        if isinstance(node, ast.Assign):
            targets, value = list(node.targets), node.value
        elif isinstance(node, ast.AnnAssign):
            targets, value = [node.target], node.value
        elif isinstance(node, ast.NamedExpr):
            targets, value = [node.target], node.value
        else:
            continue
        if value is None:
            continue
        for target in targets:
            for name in bound_names(target):
                bindings.setdefault(id(value), set()).add(name)
    return bindings


def field_group_reads(function: ast.FunctionDef) -> list[tuple[ast.Call, set[str]]]:
    """Every `.group(…)` read off a match of a field pattern, and the names carrying that read.

    A read bound to a plain name and handed to `ParsedName(…)` a line later is the same read as one
    minted where it is read, so the names it is bound to travel with it: without that,
    `name = found.group("name"); return ParsedName(name)` was refused as a function that "hands back
    the text it matched", which it does not.
    """
    matches = field_match_names(function)
    carried = carried_by_names(function)
    reads: list[tuple[ast.Call, set[str]]] = []
    for node in ast.walk(function):
        if not (
            isinstance(node, ast.Call)
            and isinstance(node.func, ast.Attribute)
            and node.func.attr == "group"
        ):
            continue
        receiver = node.func.value
        if not (
            reads_a_field_pattern(receiver)
            or (isinstance(receiver, ast.Name) and receiver.id in matches)
        ):
            continue
        reads.append((node, carried.get(id(node), set())))
    return reads


def minted_arguments(function: ast.FunctionDef) -> set[int]:
    """The expressions `function` reads a `ParsedName` out of, by identity."""
    return {
        id(argument)
        for call in ast.walk(function)
        if isinstance(call, ast.Call)
        and isinstance(call.func, ast.Name)
        and call.func.id == MINTED_FIELD
        for argument in call.args
    }


def minted_field_names(function: ast.FunctionDef) -> set[str]:
    """The plain names `function` hands to `ParsedName(…)`, which carries a read minted a line on."""
    return {
        argument.id
        for call in ast.walk(function)
        if isinstance(call, ast.Call)
        and isinstance(call.func, ast.Name)
        and call.func.id == MINTED_FIELD
        for argument in call.args
        if isinstance(argument, ast.Name)
    }


# The three calls that want a yes or a no out of a match rather than the match itself.
PRESENCE_CALLS = frozenset({"bool", "any", "all"})


def parent_nodes(function: ast.FunctionDef) -> dict[int, ast.AST]:
    """Every node of `function` under its parent, by identity."""
    parents: dict[int, ast.AST] = {}
    for node in ast.walk(function):
        for child in ast.iter_child_nodes(node):
            parents[id(child)] = node
    return parents


def only_asks_whether_it_matches(call: ast.Call, parents: dict[int, ast.AST]) -> bool:
    """Whether the match `call` answers is only asked about, or kept.

    `CONTAINER_NAME.search(clause) is not None` asks whether the pattern matches and throws the
    match away: no name is read there, so a helper that answers that way is not a read this scan
    has anything to say about, and refusing it as one that reads "a name or a reference … without
    reading it as a `ParsedName`" describes code that does not exist. What tells the two apart is
    the context the call stands in. A comparison against `None`, a `not`, a truth test, and a
    `bool(…)`, `any(…)` or `all(…)` around it all answer with a yes or a no whatever else happens
    to that answer, so the match itself cannot escape them. A match handed on as one of those is
    not the one the question is about: `PATTERN.search(c) if flag else None` and
    `PATTERN.search(c) or None` answer with the match, so they are walked out to whatever holds
    them, and only a truth test above them makes the match a thing nobody kept. Everything else —
    a return, a binding, a `.group(…)` off it, an iteration over it, a call built from it — keeps
    it.
    """
    node: ast.AST = call
    while True:
        parent = parents.get(id(node))
        if isinstance(parent, ast.Compare):
            beside = [
                side
                for side in [parent.left, *parent.comparators]
                if side is not node
            ]
            return bool(beside) and all(
                isinstance(side, ast.Constant) and side.value is None for side in beside
            )
        if isinstance(parent, ast.UnaryOp) and isinstance(parent.op, ast.Not):
            return True
        if isinstance(parent, (ast.If, ast.While, ast.Assert)):
            return True
        if isinstance(parent, ast.IfExp) and parent.test is not node:
            # A branch answers with itself; a test is only asked whether it is true.
            node = parent
            continue
        if isinstance(parent, (ast.IfExp, ast.BoolOp)):
            # The test of a conditional, and an operand of `and`/`or` whose own value nothing keeps.
            node = parent
            continue
        if (
            isinstance(parent, ast.Call)
            and isinstance(parent.func, ast.Name)
            and parent.func.id in PRESENCE_CALLS
        ):
            return True
        return isinstance(parent, ast.Expr)


def kept_field_matches(function: ast.FunctionDef) -> list[ast.Call]:
    """Every call in `function` that reads one of the field patterns and keeps what it answers."""
    parents = parent_nodes(function)
    return [
        node
        for node in ast.walk(function)
        if isinstance(node, ast.Call)
        and reads_a_field_pattern(node)
        and not only_asks_whether_it_matches(node, parents)
    ]


def unseamed_field_problems() -> list[str]:
    """Every read of a name or a reference the section's rules reach that does not mint a `ParsedName`.

    `ParsedName` refuses a comparison written outside the seam, and a value that never became one is
    a comparison it cannot see. This is the half that checks the read itself, and it is what makes
    the closure stick rather than hold until the next edit. It walks this file's own syntax tree,
    out from the functions the section's
    rules are built from and out from the function values those rules reach through a table or a
    variable, and fails on two shapes:

    - a `.group(…)` read taken off a match of one of the three patterns, which is neither the
      expression a `ParsedName` is made from where it is read nor the plain name such an expression
      is bound to; and
    - a function that keeps a match of one of those patterns and makes no `ParsedName` at all.

    A return annotation naming the type does not satisfy either; only minting the value does. A read
    that only asks whether the pattern matches — `CONTAINER_NAME.search(clause) is not None` — reads
    no name and is not one of these shapes.

    What it does not see: a function the rules do not reach (`check_published_image` compares the
    references the whole page carries, and that is not one of the section's rules), a name read with a
    pattern of the rule's own rather than one of those three, a function that mints a `ParsedName`
    and keeps a match of one of those patterns without a `.group(…)` read off it, and a comparison
    of the text a `ParsedName` was read from — that value is a `str` and carries no record of where
    it came from.
    """
    with open(__file__, encoding="utf-8") as handle:
        tree = ast.parse(handle.read(), filename=__file__)
    functions = {
        node.name: node for node in tree.body if isinstance(node, ast.FunctionDef)
    }
    problems: list[str] = []
    roots = set(RULE_ENTRY_POINTS) | named_function_values(tree, functions)
    for root in sorted(roots):
        if root not in functions:
            problems.append(
                f"the scan's root {root!r} is not a function of this file, so what the section's "
                "rules are built from is not what this reads"
            )
    reached = reached_functions(roots, functions)
    # A pin must reach what it claims to cover, and this half of the scan claims the functions the
    # rules reach: a reading the table names but the walk does not is one a weakened edit inside it
    # is invisible in, which is what the table-shaped readings were.
    for place, readings in RUN_READINGS.items():
        for reading in readings:
            if reading.__name__ not in reached:
                problems.append(
                    f"the name reading {place!r} is read through {reading.__name__}, which the "
                    "scan does not reach, so a comparison written inside it is one nothing reads"
                )
    if published_port_reading.__name__ not in reached:
        problems.append(
            f"the published port reading is {published_port_reading.__name__}, which the scan "
            "does not reach, so a comparison written inside it is one nothing reads"
        )
    readers = 0
    for name in sorted(reached):
        function = functions[name]
        mentioned = {
            node.id for node in ast.walk(function) if isinstance(node, ast.Name)
        } & FIELD_PATTERNS
        if not mentioned:
            continue
        readers += 1
        reads = field_group_reads(function)
        minted = minted_arguments(function)
        minted_names = minted_field_names(function)
        for read, carrying in reads:
            if id(read) in minted or carrying & minted_names:
                continue
            problems.append(
                f"the function {name} reads a container or network name out of a command "
                f"through {', '.join(sorted(mentioned))} and hands back the text it matched: "
                "a comparison of it is one no fixture can hold, so read it as a `ParsedName` "
                "where the field is read"
            )
        if not reads and not minted and kept_field_matches(function):
            problems.append(
                f"the function {name} keeps a match of {', '.join(sorted(mentioned))} and reads "
                "no `ParsedName` out of it, so whatever it takes from that match — a `groupdict`, "
                "a `findall`, a subscript — is compared as plain text, which no fixture can hold"
            )
    if not readers:
        problems.append(
            "the scan reached no function of the section's rules that reads a name or a reference "
            "out of a command, so it is checking nothing"
        )
    return problems


def scan(targets: list[str]) -> int:
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

    for what, shape, expected in RUN_FIXTURES:
        if shape is None:
            print(
                f"check-claims: the Run section fixture {what!r} does not apply to the shape it "
                f"names, so it is not reading what it says it is",
                file=sys.stderr,
            )
            return 2
        failure = fixture_failure(what, run_section_problems([[line] for line in shape]), expected)
        if failure:
            print(f"check-claims: {failure}", file=sys.stderr)
            return 2

    for what, opened_at, shape, expected in RUN_OPENED_AT_FIXTURES:
        if shape is None:
            print(
                f"check-claims: the Run section address fixture {what!r} does not apply to the "
                "blocks it names, so it is not reading what it says it is",
                file=sys.stderr,
            )
            return 2
        failure = fixture_failure(
            what, run_section_opened_at_problems(opened_at, [[line] for line in shape]), expected
        )
        if failure:
            print(f"check-claims: {failure}", file=sys.stderr)
            return 2

    for what, answer, versions, expected in JETBRAINS_LISTING_FIXTURES:
        problems = jetbrains_listing_problems(answer, versions)
        if expected and not any(expected in problem for problem in problems):
            print(
                f"check-claims: the JetBrains listing fixture {what!r} is the defect {expected!r} "
                "names and is not reported as one; a reading that stops seeing it passes a "
                "listing that is not public",
                file=sys.stderr,
            )
            return 2
        if not expected and problems:
            print(
                f"check-claims: the JetBrains listing fixture {what!r} is a public listing and is "
                f"reported as {'; '.join(problems)}, so the reading fails a route that is right",
                file=sys.stderr,
            )
            return 2

    # The fixtures above say the rules read the right commands; this says they read them the right
    # way, which is the half that was missing: a reading can be swapped for a weaker one with every
    # fixture still green, and then the fixtures hold a rule and not the reading inside it.
    reading_problems = run_section_reading_problems() + unseamed_field_problems() + seam_problems()
    if reading_problems:
        for problem in reading_problems:
            print(f"check-claims: {problem}", file=sys.stderr)
        return 2

    root = root_of_this_checkout()
    os.chdir(root)
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
        check_run_section_command,
        check_run_section_address,
        check_command_prompt_selection,
        check_demo_instance,
        check_wire_binding,
        check_jetbrains_listing,
    ):
        status = check(scanned)
        if status != 0:
            return status

    print(
        f"check-claims: {len(compiled)} known wordings alive over {len(paths)} file(s), none "
        "found. This is a filter, not a proof: a false claim in other words passes it"
    )
    return 0


def main() -> int:
    """The check's entry point, and the one place a name compared outside the seam is turned into
    the exit this check promises for a check that cannot run rather than for a page that is wrong.
    """
    try:
        return scan(sys.argv[1:] or ["."])
    except UnseamedComparison as unseamed:
        print(f"check-claims: {unseamed}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
