#!/usr/bin/env python3
"""Fails the tree when the policy in vercel.json would refuse something the page serves.

This is the defect it exists for: `default-src 'none'` with no `script-src` makes the page's
own seven chunks and its inline bootstrap fall back to `'none'`, so the browser loads the HTML
and nothing else — the page never hydrates, and anything client-side (the header's hide-on-
scroll) silently does nothing while the README reads as if it works. A policy that blocks the
page it ships with is not a strict policy, it is a broken one, and nothing in the gate noticed.

So: the CSP is read from `vercel.json` (the file Vercel applies, not a copy of it), the page is
read from the served HTML, and every subresource the page carries is decided against the
directive that would govern it, following the fallback chains a browser follows
(`script-src-elem` → `script-src` → `default-src`, and so on). Scripts, stylesheets, inline
style and handler attributes, images, `<base>` and the element kinds `default-src 'none'`
blocks structurally (`iframe`, `object`, `embed`, media) are all in scope. The inventory it
prints on success is what makes the pass legible: how many external and inline scripts, which
directive permitted them, and why.

It is a model of the CSP resource-loading rules, not a browser. Two consequences are deliberate:
a source expression it does not model (`'strict-dynamic'`, `'unsafe-hashes'`, a report-only
mechanism) is an error rather than an assumption, so the check can never pass a policy it does
not understand; and the Chromium run that proves the real thing — zero `securitypolicyviolation`
events on a page served with these exact headers — is not in this file, because the runner has
no browser. What is here is the part that can run on every push. Neither this nor that run can
see the deployed headers: if Vercel stops applying the `headers` block, nothing local notices.

Exit 0 prints what the policy permits. Exit 1 names each subresource it would block, with the
directive and the reason. Exit 2 means the check itself cannot run — an unmodelled source
expression, an ambiguous or unreadable policy, or a self-test fixture that no longer behaves —
which is a failure, not a pass.

`VERCEL_JSON` overrides the policy file under test, so the check can be probed against the
policy it was written for: `VERCEL_JSON=.tmp/vercel-without-script-src.json scripts/check-csp.py`
has to fail, and a check that only ever sees a passing policy proves nothing.

    scripts/check-csp.py [rendered.html]      # defaults to .tmp/rendered.html
"""

from __future__ import annotations

import base64
import hashlib
import json
import os
import re
import sys
from dataclasses import dataclass, field
from html.parser import HTMLParser
from urllib.parse import urljoin, urlparse

# The origin an absolute URL is resolved against. Only matters for `'self'`: every URL the page
# serves today is root-relative, and a root-relative URL is same-origin whatever this is.
DEFAULT_ORIGIN = "https://selvage.dontblameme.dev"

HASHES = {"sha256": hashlib.sha256, "sha384": hashlib.sha384, "sha512": hashlib.sha512}

# The directive that governs each kind of subresource, in fallback order: the first one present
# in the policy wins. `base-uri` and `form-action` really have no fallback to `default-src`.
CHAINS = {
    "script": ("script-src-elem", "script-src", "default-src"),
    "script-attr": ("script-src-attr", "script-src", "default-src"),
    "style": ("style-src-elem", "style-src", "default-src"),
    "style-attr": ("style-src-attr", "style-src", "default-src"),
    "image": ("img-src", "default-src"),
    "frame": ("frame-src", "child-src", "default-src"),
    "object": ("object-src", "default-src"),
    "media": ("media-src", "default-src"),
    "base": ("base-uri",),
    "form": ("form-action",),
}

# Element → kind. `<link rel="stylesheet">` and the icon links are handled by rel, below.
ELEMENT_KIND = {
    "iframe": "frame",
    "frame": "frame",
    "object": "object",
    "embed": "object",
    "audio": "media",
    "video": "media",
    "track": "media",
    "source": "media",
}

# Link relations whose href is a stylesheet, an image, or neither.
LINK_REL = {
    "stylesheet": ("style", "href"),
    "icon": ("image", "href"),
    "shortcut": ("image", "href"),
    "apple-touch-icon": ("image", "href"),
    "mask-icon": ("image", "href"),
    "preload": ("preload", "href"),
}

@dataclass
class Item:
    kind: str
    element: str
    url: str | None = None
    text: str | None = None
    nonce: str | None = None


@dataclass
class Verdict:
    allowed: bool
    directive: str | None
    reason: str
    unsupported: str | None = None


@dataclass
class Report:
    # kind -> the short reason it was permitted -> how many
    inventory: dict[str, dict[str, int]] = field(default_factory=dict)
    blocked: list[str] = field(default_factory=list)
    unsupported: list[str] = field(default_factory=list)

    def note(self, kind: str, reason: str) -> None:
        seen = self.inventory.setdefault(kind, {})
        seen[reason] = seen.get(reason, 0) + 1

    def summary(self) -> str:
        parts = []
        for kind in sorted(self.inventory):
            breakdown = sorted(self.inventory[kind].items(), key=lambda kv: (-kv[1], kv[0]))
            total = sum(report_count for _, report_count in breakdown)
            detail = ", ".join(f"{count} {reason}" for reason, count in breakdown)
            parts.append(f"{total} {kind} ({detail})")
        return "; ".join(parts)


def parse_policy(value: str) -> dict[str, tuple[str, ...]]:
    """A CSP header value as directive -> sources, lowercased on the directive name."""
    policy: dict[str, tuple[str, ...]] = {}
    for part in value.split(";"):
        tokens = part.split()
        if not tokens:
            continue
        policy[tokens[0].lower()] = tuple(tokens[1:])
    return policy


class PolicyError(Exception):
    """The policy cannot be judged: ambiguous, absent, or not deny-by-default."""


def policy_from_vercel(vercel_json: str, page: str = "/") -> str:
    """The Content-Security-Policy vercel.json would apply to `page`."""
    try:
        config = json.loads(vercel_json)
    except json.JSONDecodeError as exc:  # a policy nobody can read is not a pass
        raise PolicyError(f"vercel.json is not JSON: {exc}") from exc
    found: list[tuple[str, str]] = []
    for block in config.get("headers", []):
        source = block.get("source", "")
        for header in block.get("headers", []):
            if header.get("key", "").lower() == "content-security-policy":
                found.append((source, header.get("value", "")))
    if not found:
        raise PolicyError(
            "vercel.json sets no Content-Security-Policy header; a page with no policy is not "
            "the policy this check verifies"
        )
    if len(found) > 1:
        raise PolicyError(
            "vercel.json sets more than one Content-Security-Policy header, so which one "
            f"applies to {page} is not decidable here: {[s for s, _ in found]}"
        )
    return found[0][1]


class PageParser(HTMLParser):
    """The subresources a page carries, as Items. Element text comes back raw for script
    and style, which is what a hash is computed over."""

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.items: list[Item] = []
        self._capture: Item | None = None
        self._buffer: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        self._element(tag, {k.lower(): (v or "") for k, v in attrs})

    def handle_startendtag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        self._element(tag, {k.lower(): (v or "") for k, v in attrs})

    def _element(self, tag: str, attrs: dict[str, str]) -> None:
        if tag == "script":
            if attrs.get("src"):
                self.items.append(Item("script", "<script src>", url=attrs["src"], nonce=attrs.get("nonce") or None))
            elif "nonce" in attrs or "type" in attrs or "src" not in attrs:
                self._capture = Item("script", "<script>", nonce=attrs.get("nonce") or None)
            return
        if tag == "style":
            self._capture = Item("style", "<style>")
            return
        if tag == "link":
            kind, attr = LINK_REL.get((attrs.get("rel") or "").lower(), ("ignore", ""))
            if kind == "preload" and (attrs.get("as") or "").lower() != "image":
                kind = "ignore"
            if kind in ("style", "image") and attrs.get(attr):
                self.items.append(Item(kind, f'<link rel="{attrs.get("rel")}">', url=attrs[attr]))
            return
        if tag == "img":
            url = attrs.get("src")
            if url:
                self.items.append(Item("image", "<img>", url=url))
            for candidate in (attrs.get("srcset") or "").split(","):
                candidate = candidate.strip().split(" ")[0]
                if candidate:
                    self.items.append(Item("image", "<img srcset>", url=candidate))
            return
        if tag == "base":
            self.items.append(Item("base", "<base>", url=attrs.get("href") or "/"))
            return
        if tag in ELEMENT_KIND:
            self.items.append(Item(ELEMENT_KIND[tag], f"<{tag}>", url=attrs.get("src") or attrs.get("data") or ""))
            return
        if tag == "form":
            self.items.append(Item("form", "<form>", url=attrs.get("action") or ""))
        for name in attrs:
            if name.startswith("on"):
                self.items.append(Item("script-attr", f"{tag}[{name}]"))
        if "style" in attrs:
            self.items.append(Item("style-attr", f"{tag}[style]"))

    def handle_data(self, data: str) -> None:
        if self._capture is not None:
            self._buffer.append(data)

    def handle_endtag(self, tag: str) -> None:
        if self._capture is None:
            return
        if (tag == "script" and self._capture.kind == "script") or (
            tag == "style" and self._capture.kind == "style"
        ):
            self._capture.text = "".join(self._buffer)
            self.items.append(self._capture)
            self._capture = None
            self._buffer = []


def items_of(html: str) -> list[Item]:
    parser = PageParser()
    parser.feed(html)
    parser.close()
    if parser._capture is not None:  # an unclosed <script> or <style>
        parser._capture.text = "".join(parser._buffer)
        parser.items.append(parser._capture)
    return parser.items


def source_allowed(source: str, url: str, origin: str) -> bool | None:
    """Whether one source expression permits one resolved URL. None means not modelled."""
    if source == "'none'":
        return False
    if source == "'self'":
        return same_origin(url, origin)
    if source == "*":
        return urlparse(url).scheme in ("http", "https", "ws", "wss")
    if source.endswith(":") and not source.startswith("'"):
        return urlparse(url).scheme == source[:-1]
    if source.startswith(("'nonce-", "'sha")) or source in ("'unsafe-inline'", "'unsafe-eval'"):
        # A nonce or hash permits the element it is written on, not a fetched URL: without
        # 'strict-dynamic' it does not authorise an external script.
        return False
    if source.startswith("'") and source.endswith("'"):
        return None
    if re.match(r"^(?:([a-zA-Z][a-zA-Z0-9+.\-]*):)?//", source) or "/" in source or "." in source:
        return host_allowed(source, url, origin)
    return None


def host_allowed(source: str, url: str, origin: str) -> bool:
    target = urlparse(url)
    if not source.startswith(("http://", "https://", "//")):
        source = "//" + source
    pattern = urlparse(urljoin(origin, source))
    if (pattern.hostname or "").startswith("*."):
        host = pattern.hostname[2:]
        if target.hostname != host and not (target.hostname or "").endswith("." + host):
            return False
    elif target.hostname != pattern.hostname:
        return False
    if pattern.port != target.port:
        return False
    if pattern.path and not target.path.startswith(pattern.path):
        return False
    return True


def same_origin(url: str, origin: str) -> bool:
    a, b = urlparse(url), urlparse(origin)
    return (a.scheme, a.hostname, a.port) == (b.scheme, b.hostname, b.port)


def decide(policy: dict[str, tuple[str, ...]], item: Item, origin: str) -> Verdict:
    chain = CHAINS[item.kind]
    directive = next((name for name in chain if name in policy), None)
    if directive is None:
        return Verdict(True, None, "no directive applies")
    sources = policy[directive]
    inline = item.url is None
    if inline:
        return decide_inline(directive, sources, item)
    if item.kind in ("script-attr", "style-attr"):
        return decide_attribute(directive, sources, item)
    url = urljoin(origin, item.url or "")
    for source in sources:
        verdict = source_allowed(source, url, origin)
        if verdict is None:
            return Verdict(False, directive, "", unsupported=source)
        if verdict:
            return Verdict(True, directive, f"{source} in {directive}")
    return Verdict(False, directive, f"nothing in {directive} matches {url}")


def decide_inline(directive: str, sources: tuple[str, ...], item: Item) -> Verdict:
    nonces = [s[7:-1] for s in sources if s.startswith("'nonce-")]
    hashes = [s for s in sources if re.match(r"'sha(256|384|512)-", s)]
    if nonces or hashes:
        # CSP3: a nonce or hash in the list switches 'unsafe-inline' off for that directive.
        if item.nonce and item.nonce in nonces:
            return Verdict(True, directive, f"a listed nonce in {directive}")
        if hashes and item.text is not None:
            for wanted in hashes:
                algorithm, _, digest = wanted[1:-1].partition("-")
                computed = base64.b64encode(HASHES[algorithm](item.text.encode()).digest()).decode()
                if computed == digest:
                    return Verdict(True, directive, f"a listed {algorithm} hash in {directive}")
            return Verdict(
                False,
                directive,
                f"{directive} lists {len(hashes)} hash(es) and none is this element's content, "
                "and a nonce or hash in the list switches 'unsafe-inline' off",
            )
        return Verdict(False, directive, f"{directive} lists a nonce or hash this element does not match")
    if "'unsafe-inline'" in sources:
        return Verdict(True, directive, f"'unsafe-inline' in {directive}")
    for source in sources:
        if source not in ("'none'", "'unsafe-eval'"):
            if source_allowed(source, "", "") is None:
                return Verdict(False, directive, "", unsupported=source)
    return Verdict(False, directive, f"nothing in {directive} permits inline content")


def decide_attribute(directive: str, sources: tuple[str, ...], item: Item) -> Verdict:
    if "'unsafe-inline'" in sources:
        return Verdict(True, directive, f"'unsafe-inline' in {directive}")
    hashes = [s for s in sources if re.match(r"'sha(256|384|512)-", s)]
    if hashes:
        # Hashes on an attribute need 'unsafe-hashes', which this model does not judge.
        return Verdict(False, directive, "", unsupported=hashes[0])
    return Verdict(False, directive, f"nothing in {directive} permits an inline {'script' if item.kind == 'script-attr' else 'style'} attribute")


def default_src_floor(policy: dict[str, tuple[str, ...]]) -> str | None:
    """The policy is only worth checking if it still denies by default."""
    if "default-src" not in policy:
        return "the policy has no default-src, so it does not deny by default"
    if policy["default-src"] != ("'none'",):
        return f"default-src is {policy['default-src']}, not 'none'"
    return None


def analyse(csp: str, html: str, origin: str = DEFAULT_ORIGIN) -> Report:
    policy = parse_policy(csp)
    report = Report()
    for item in items_of(html):
        verdict = decide(policy, item, origin)
        if verdict.unsupported is not None:
            report.note(item.kind, "unmodelled")
            report.unsupported.append(
                f"{item.element} {item.url or 'inline'}: {verdict.directive} lists "
                f"{verdict.unsupported!r}, which this check does not model"
            )
            continue
        if not verdict.allowed:
            report.note(item.kind, "blocked")
            report.blocked.append(
                f"{item.element} {item.url or 'inline'}: {verdict.reason or 'blocked'}"
            )
            continue
        report.note(item.kind, verdict.reason)
    return report


SUITE_HTML = (
    '<script src="/_next/static/chunks/a.js" async=""></script>'
    '<script>self.__next_f.push([1,"x"])</script>'
)
SHIPPED = (
    "default-src 'none'; script-src 'self' 'unsafe-inline'; script-src-attr 'none'; "
    "img-src 'self' data:; style-src 'self'; form-action 'none'; base-uri 'none'; "
    "frame-ancestors 'none'"
)
REGRESSED = "default-src 'none'; img-src 'self' data:; style-src 'self'; base-uri 'none'; frame-ancestors 'none'"


def self_test() -> str | None:
    """Every verdict this checker can reach, on a fixture that has to reach it.

    A checker whose fixtures stopped behaving reports a clean page: this is the same discipline
    the claim filter keeps, and the reason the regressed policy is here — the defect this file
    was written for stays reachable, so the check cannot quietly become blind to it.
    """
    body = 'self.__next_f.push([1,"x"])'
    digest = base64.b64encode(hashlib.sha256(body.encode()).digest()).decode()
    inline_only = f"<script>{body}</script>"
    cases: list[tuple[str, str, str, str]] = [
        # (name, policy, html, expected: "clean" | "blocked" | "unsupported")
        ("the shipped policy over the shipped shape", SHIPPED, SUITE_HTML, "clean"),
        ("the policy with no script-src (the defect)", REGRESSED, SUITE_HTML, "blocked"),
        ("script-src 'self' does not carry the inline bootstrap", "default-src 'none'; script-src 'self'", SUITE_HTML, "blocked"),
        ("script-src 'self' carries the chunk", "default-src 'none'; script-src 'self'", '<script src="/_next/a.js"></script>', "clean"),
        ("a third-party chunk", "default-src 'none'; script-src 'self' 'unsafe-inline'", '<script src="https://cdn.example/a.js"></script>', "blocked"),
        ("an absolute same-origin chunk under 'self'", "default-src 'none'; script-src 'self'", f'<script src="{DEFAULT_ORIGIN}/_next/a.js"></script>', "clean"),
        ("an inline style body under style-src 'self'", "default-src 'none'; style-src 'self'", "<style>body{}</style>", "blocked"),
        ("a style attribute under style-src 'self'", "default-src 'none'; style-src 'self'", '<p style="color:red">x</p>', "blocked"),
        ("a style attribute under 'unsafe-inline'", "default-src 'none'; style-src 'self' 'unsafe-inline'", '<p style="color:red">x</p>', "clean"),
        ("an inline handler under script-src 'self'", "default-src 'none'; script-src 'self'", '<a onclick="x()">x</a>', "blocked"),
        (
            "an inline handler under 'unsafe-inline' in script-src",
            "default-src 'none'; script-src 'self' 'unsafe-inline'",
            '<a onclick="x()">x</a>',
            "clean",
        ),
        (
            "script-src-attr 'none' over that same handler",
            SHIPPED,
            '<a onclick="x()">x</a>',
            "blocked",
        ),
        (
            "script-src-attr 'none' still leaves the inline bootstrap to script-src",
            SHIPPED,
            SUITE_HTML,
            "clean",
        ),
        ("the inline bootstrap by its own hash", f"default-src 'none'; script-src 'sha256-{digest}'", inline_only, "clean"),
        ("'unsafe-inline' is switched off by a hash in the list", f"default-src 'none'; script-src 'unsafe-inline' 'sha256-{digest}'", inline_only, "clean"),
        ("a hash that is not this element's content", "default-src 'none'; script-src 'sha256-AAAA'", inline_only, "blocked"),
        ("a nonce policy over a prerendered page (no nonce to match)", "default-src 'none'; script-src 'nonce-abc123'", inline_only, "blocked"),
        ("a nonce policy over an element that carries the nonce", "default-src 'none'; script-src 'nonce-abc123'", '<script nonce="abc123">x</script>', "clean"),
        ("an iframe under default-src 'none'", "default-src 'none'", '<iframe src="/x"></iframe>', "blocked"),
        ("a base element under base-uri 'none'", "default-src 'none'; base-uri 'none'", '<base href="/">', "blocked"),
        ("a base element with no base-uri directive", "default-src 'none'", '<base href="/">', "clean"),
        ("a form action with no form-action directive", "default-src 'none'", '<form action="/x"></form>', "clean"),
        ("a form action under form-action 'none'", SHIPPED, '<form action="/x"></form>', "blocked"),
        ("a form with no action under form-action 'none'", SHIPPED, "<form></form>", "blocked"),
        ("an image off-origin", "default-src 'none'; img-src 'self' data:", '<img src="https://evil.example/a.png">', "blocked"),
        ("an image on-origin", "default-src 'none'; img-src 'self' data:", '<img src="/a.png">', "clean"),
        ("a data: image under img-src data:", "default-src 'none'; img-src 'self' data:", '<img src="data:image/png;base64,AA">', "clean"),
        ("a source expression this check does not model", "default-src 'none'; script-src 'strict-dynamic'", SUITE_HTML, "unsupported"),
        ("a document that carries nothing judgeable", SHIPPED, "<p>prose</p>", "clean"),
    ]
    for name, policy, html, expected in cases:
        report = analyse(policy, html)
        got = "unsupported" if report.unsupported else ("blocked" if report.blocked else "clean")
        if got != expected:
            detail = (report.unsupported or report.blocked or ["nothing"])[0]
            return f"self-test {name!r}: expected {expected}, got {got} ({detail})"
    floors = [
        (SHIPPED, None),
        (REGRESSED, None),
        ("script-src 'self'", "no default-src"),
        ("default-src 'self'; script-src 'self'", "default-src is"),
    ]
    for policy, expected in floors:
        got = default_src_floor(parse_policy(policy))
        if (got is None) != (expected is None):
            return f"self-test default-src floor on {policy!r}: expected {expected}, got {got}"
    return None


def main(argv: list[str]) -> int:
    dead = self_test()
    if dead is not None:
        print(f"check-csp: {dead}; a check that cannot decide passes everything", file=sys.stderr)
        return 2

    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    policy_path = os.environ.get("VERCEL_JSON", os.path.join(root, "vercel.json"))
    try:
        with open(policy_path, encoding="utf-8") as handle:
            vercel_json = handle.read()
        csp = policy_from_vercel(vercel_json)
    except (OSError, PolicyError) as exc:
        print(f"check-csp: {exc}", file=sys.stderr)
        return 2

    floor = default_src_floor(parse_policy(csp))
    if floor is not None:
        print(f"check-csp: {floor} ({policy_path})", file=sys.stderr)
        return 1

    page = argv[1] if len(argv) > 1 else os.path.join(root, ".tmp", "rendered.html")
    try:
        with open(page, encoding="utf-8") as handle:
            html = handle.read()
    except OSError as exc:
        print(
            f"check-csp: cannot read {page}: {exc}. A check that reaches no page reports a page "
            "that loads, so build and serve it first (scripts/ci-local.sh csp)",
            file=sys.stderr,
        )
        return 2
    if "<script" not in html:
        print(
            f"check-csp: {page} carries no script element; a page with no scripts is not the "
            "page this check verifies",
            file=sys.stderr,
        )
        return 2

    report = analyse(csp, html)
    if report.unsupported:
        for line in report.unsupported:
            print(f"check-csp: {line}", file=sys.stderr)
        return 2
    if report.blocked:
        for line in report.blocked:
            print(f"check-csp: blocked: {line}")
        print(
            f"check-csp: {len(report.blocked)} subresource(s) the page serves are refused by its "
            f"own policy in {os.path.relpath(policy_path, root)}: {csp}"
        )
        return 1
    print(
        f"check-csp: the policy in {os.path.relpath(policy_path, root)} permits everything "
        f"{os.path.relpath(page, root)} carries — {report.summary()}. This is a model of the "
        "policy, not a browser: it cannot see whether the host applies the header"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
