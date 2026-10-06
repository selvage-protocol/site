# The claim filter

The page's job is to be checkable, so the rule is mechanical where it can be:
[`scripts/check-claims.py`](../scripts/check-claims.py) fails the build on each of the known
wordings in [What the page must never say](must-not-say.md), carries the reason beside each, and
normalises the served HTML before matching: comments, tags, scripts and styles removed, entities
decoded, whitespace collapsed. So a phrase cannot pass by wrapping across a line or by encoding a
character. The scan runs against what the server renders, not the source: the gate builds, starts
the production server, fetches `/` over HTTP and checks that HTML. It reads the prose the page
carries in its `meta` attributes — `description`, `og:*`, `twitter:*` — as text beside the visible
text, because a link unfurl prints that prose verbatim and the tags themselves are stripped from the
body: five planted overclaims in `og:description` used to pass the scan unseen, on the surface a
person deciding whether to paste a link meets first. It also asserts facts in the positive — the
images the section's commands name, which of the two runs carries which, the demo instance, the one
wire version those artefacts speak, two disclosures (what the relay still sees, and the terms
`selvaged` is under), the file the corpus counts are pinned in, the identity the extension is
published under with the two registries it is on, that the hosted tier the page offers is not
available yet, the word beside each repository in the grid, and the JetBrains plugin's listing with
the Marketplace's word that it is public — described just below. **It is a
filter, not a proof.** It cannot see meaning: a false claim in different words, a synonym outside
the list, a superlative, an unbacked sentence or a wrong number the list does not pin all pass it. A
green gate means the known wordings are absent, nothing more. The reasons are summarised here so
that the constraint survives without the file that produced it.

`scripts/check-claims.py` asserts facts in the positive, because a phrase list cannot reach them.
The first is the image tags the happy path hands a reader: the check pins
`ghcr.io/selvage-protocol/selvaged` and `ghcr.io/selvage-protocol/selvage-web` to one version,
requires every reference the rendered page carries to be one of the two and both of them to be there
— a command that names one where the other belongs pulls an image the page is not about, and a
reference printed as a bare repository is read as the `:latest` tag docker reads it as, which is the
tag the section prints — and then asks the registry for each tag — anonymously, with no credential
in the request, because no account is the point of the command. It compares the **per-platform
manifests' layer digests**, not the index: a platform entry only states that a slot is *labelled*
arm64, and `selvaged:0.1.1` proved the difference by publishing both legs around the amd64 binary,
every layer digest identical across the two. `0.1.0` carries the same defect and `0.1.2` is the fix;
neither broken tag will be retagged or removed. That proof runs per package, so the page half of the
command is held to it too. The card's commands are then read as the three steps they are, one per
line, and the promise the single chained command used to carry is gone with it: `docker network create`
chained with `&&` stopped the second paste at an error, and the detached server kept its name for
the next one with nothing on the section to remove it, so everything that read that promise went too
and the check has no shape for a second paste at all. This host has no Docker, so what is asserted
is the shape rather than a run: the first command creates the network the two containers share, and
it stands before every run that names it, because a run reaches a network nothing has made yet;
every run is detached, because one that is not holds the reader's terminal instead of returning
their prompt; every run joins that network, read as a whole name, so a `--network selvage-net` is
not read as the `selvage` the first command creates; the address the page container is given names
the container the server runs in, on the network both are attached to — and a host that is the empty
name is refused rather than read as the empty name a run given no `--name` answers, which is the
pair that passed this rule — and sits on the container that publishes the port a reader opens — read
in either form the page image accepts, `http://selvaged:8080` or the bare `selvaged:8080`, which is
the form `web_client`'s README documents; each of the two runs carries the reference the page
publishes for it, the run a reader opens the page image and the run beside it the server's, so a
command with the two swapped is refused rather than passed, and the section prints those references
as bare repositories, which the check reads as the `:latest` tag docker gives a bare repository; the
server's run publishes no port, because the page's own `-p` would collide with it and the page would
never start; the address the command publishes is the address the section prints for a reader — its
**host port**, and the host its mapping names when it names one — read out of the section's own text
rather than the page, because `http://127.0.0.1:8080/` in the copy and `-p 127.0.0.1:8080:8080` in
the command are one fact printed twice: a command publishing another port, or publishing that port
on `192.168.1.5` or on `::1`, sends every reader to an address its own card says answers. The
address is read wherever the section states it in its own element, and the run it belongs to is
looked for in whichever of the three commands carries `SELVAGE_SERVER`. A mapping that names no host
(`-p 8080:8080`) passes, because what is read is the address a mapping carries and not the one
docker picks when it carries none — while a mapping that writes the wildcard down (`-p 0.0.0.0:8080:8080`)
is **refused**, because `0.0.0.0` is a host a mapping names and it is neither loopback the section's
own address may print, so the form that leaves the host out passes and the form that spells every
interface out fails; and the mapping's **container** port is not compared either, so `-p 8080:80`
passes on its port. The host is compared against the two loopback names the section's own address
may print, `127.0.0.1` and `localhost`, and it is not validated as an address: docker's own
reference calls that field an IP address, writes one in every example and never writes the name
`localhost` as a value of it, and this check has no docker to ask, so `-p localhost:8080:8080`
passes here as one of the two loopback names and whether docker accepts it was not settled. It reads
one way of writing each part, so a command that is correct in other words fails it and a broken one
that keeps those words can pass — the limit every assertion here has, and the reverse of the one
this paragraph used to state. Every one of those rules carries a fixture in the check itself: a
command of its own with the defect written into it, run before the scan, pinning the fragment the
rule emits, so a rule deleted is a rule the check fails on rather than one nothing reads. Holding a
rule is not holding the *reading* inside it, and that is the other half: the four comparisons and
the published host port are each named in the check, and before it scans anything it swaps each one
in turn for the weaker reading a later edit would leave in its place — a `\b{name}\b` search for a
name or one name inside the other either way round for a pair of them, the mapping's container port
for the host port — and fails unless a fixture goes red. The port reading is the shape that failure
used to have: with every mapping a fixture carried written `8080:8080`, where the two fields are one
number, reading the container port answered for the host port and no fixture said otherwise, so the
fixture that holds it is a mapping whose two numbers differ. Each of the four comparisons is held
the same way: the network every run attaches to, by a fixture writing `--network room-net` beside
`docker network create room`; the container the address names, by one naming `server-net` under an
address naming `server`; and the two references, by one whose run carries `selvaged:latest-extra`.
The host a mapping names is held the ordinary way rather than by a swap, by the three fixtures a
command that names `192.168.1.5`, `::1` or `0.0.0.0` has to be reported as; and the empty name is
held the same way, by the fixtures an address that names no host and an address that names no host
beside a run given no `--name` have to be reported as, which is what the rule that compares an
address's host against the containers the command names reads first.

What that guarantees is exact, and so is what it does not. Of the table: a reading that *is* one of
those named places cannot be weakened to a search without the check failing on its own fixtures, and
a place a fixture never tells the two readings apart at, or one the rules stop reading, fails with
it. A table holds what someone remembered, though, so a comparison written *around* it is closed by
construction instead of by another entry: every container name, network name and image reference the
card's rules touch is read as a `ParsedName`, and one of those answers only inside `reads_the_name`
— for the forms Python hands a subclass: `==`, `!=`, `in`, `startswith`, `endswith`, `find`, `index`
and `count` where the name is the object they are called on or the `str` they search, and the four
orderings, which answer for a plain receiver too because a subclass's reflected method is tried
first. `attached.group("name") != network`, the comparison that read `--network selvage-net` as
`selvage`, therefore fails where it is written rather than passing the page, and the check exits
**2** naming the line it was written on. Those refusals are one method each, so they are evaluated
rather than trusted: `seam_problems` runs every one of them outside the seam, where it has to raise,
and one through `reads_the_name`, where it has to answer, and fails the check when a method that
refuses no longer does. The other half is a scan of the check's own syntax tree
(`unseamed_field_problems`): it walks the functions the section's rules can reach — by a bare call,
and out from the function values `RUN_CARD_READINGS` and `published_port_reading` hold, which are
called through a table or a variable and are never written as a call, so the four readings and their
weakened twins are walked too — and reads the three patterns those rules match a command with —
`CONTAINER_NAME`, `NETWORK_FLAG` and `IMAGE_REFERENCE`, which are where a container name, a network
name and an image reference come from — and fails when a `.group(…)` read taken off a match of one
of them, however that match was bound (an assignment, a loop, a comprehension, a walrus, a tuple
target, or any value that names one of the patterns anywhere inside it, which is what catches a
match bound through a conditional expression, an `or`, a `list(…)`, an `enumerate(…)` or a
`re.search(PATTERN, …)`), is neither the expression a `ParsedName` is made from where it is read nor
the plain name that expression is bound to, or when a function it reaches keeps a match of one of
those patterns and mints no `ParsedName` at all. What it does not catch, and this check cannot: the
forms a `str` receiver answers for on its own, which no method of a `ParsedName` can reach. `name in clause`,
`clause.split().count(name)` and `"-" + name` put the name on the right of a `str` and answer with
its text; `clause.startswith(name)` and `clause.find(name)` put the text there; and
`name.lower().strip() == other` leaves the `ParsedName` behind at the first method call, with the
text it was read from compared in its place. Each of those answers outside `reads_the_name`, each is
what a later hand reaches for, and each is closed by reading the value as a `ParsedName` at the
comparison rather than by the class — which is also why they are limits rather than entries in the
table. Then a comparison of the *text* a name was read from — a `.split()` of the clause, a pattern
matched against the name, `str()` of one — because that value is a `str` with no record of where it
came from; a read of a match that is not `.group(…)` (`match[0]`, `match.expand()`) inside a
function that mints a `ParsedName` somewhere else, which is the one surviving way past the second
shape above, or a match bound by `with … as`; a name read with a pattern of the rule's own rather
than one of the three; and any function the section's rules do not reach, `check_published_image`
among them, which compares the references the whole page carries against the two the project
publishes and is held by the served page rather than by a fixture. A fixture a rule passes is not a
proof the rule is complete, either. What carries none is what is not a command — the pin below that
holds the `$ ` prompt and the labels to the stylesheet, and the refusal to pass when no scanned page
carries a block: those read a served page and the build it was served from, so their fixture would
be a page and a build rather than a line. The pin that closes the section's last hole is not a
phrase or a command at all: the `$ ` prompt in front of each block and the label above it are read
out of the served page's own markup, and a rule in **the stylesheet the served page loads** has to
name the class they carry and take it out of a selection. The stylesheet is read from the build the
server is serving rather than from `style.css`, under `/_next/static/` where the build puts what a
browser is served, so a declaration the build drops fails here, and deleting `user-select: none`
fails the gate instead of bringing a pasted `$ ` back with nothing to say so. The second is the demo
instance: the page points at one host, every reference to that host has to be one of the two the
page may carry, a link has to point at the instance itself, and
`https://selvage-demo.dontblameme.dev/meta` has to report a `selvaged` server. The references are
read from the visible text *and* from the links' destinations, because a label and the place it goes
are two claims: an anchor labelled with the demo host whose `href` points elsewhere passes a
text-only scan. The allowed references are the origin and the `wss://` origin with **no path**,
because both clients append `/session` to whatever address they are given (`sessionUrl` in the
engine they vendor), so the page naming `wss://…/session` would hand a reader an address that gets a
second `/session` appended and is refused. The check asserts that path separately, by asking
`https://selvage-demo.dontblameme.dev/session` for a plain `GET` and requiring a **4xx carrying the
server's own JSON**: the path has to reach the server the page names, a redirect or a `5xx` must not
stand in for it, and the proxy's own `404` page is `text/html`. Which `4xx` the server picks is its
business, and pinning `404` would redden this gate for a change in `selvaged` that makes no sentence
on the page false. The **WebSocket upgrade itself is not asserted**, because the host's proxy
answers a hand-rolled upgrade from a runner's egress with `403` and a request the proxy refuses
asserts nothing; the upgrade was verified by hand, from a client the proxy accepts, and that is
recorded in the findings rather than claimed here. It also asks `/` for a `200` and a `text/html`,
because the browser row tells a guest the demo serves the page and the proxy's own `404` is
`text/html` too, so the media type alone would let a dead page satisfy it. It then reads the bytes
`/` answered with and requires the host card's own element in them, because the browser row also
says a session can be started from the demo's page: the card is markup the client's shell carries,
so it is in the served bytes whether or not the bundle's script has run, and a demo rolled back to a
guests-only release is that sentence going false with nothing else to say so. What the demo half no
longer does is compare the instance's release to the page: the page named one, a reader had no use
for it, and it is gone from the section. The image half still ties the page's `docker run` to the
registry: the tags it names have to be `PUBLISHED_IMAGE_TAG` on both packages, and the registry has
to serve each of them. What the instance offers on the wire is read here and held to the tags'
declared wire by the check below, which is where the artefacts the page hands over are compared.
**That assertion couples the site's gate to a running box**: a demo that is down or moved, a
`/session` the proxy no longer routes to the server, and a box whose `/` is not the page all fail
the build, because a page claiming a demo that is not there is the defect it exists to catch. It
sends its own user agent, since the host's proxy answers `403` to an interpreter's default
signature. The image half needs egress to `ghcr.io` and exits 2 rather than passing when it cannot
reach it; the demo half does the same for an instance that does not answer at all, and exits 1 when
the instance answers something that disproves a sentence.

The next positive assertion binds the page's sealing claim to the one wire version, and it exists
because the paragraph that makes that claim sits directly under a `docker run`: a reader can take
the claim and the command together and get a server that carries the room through it in the clear.
The page no longer names a version, and the check no longer requires it to. What it holds instead is
the artefacts against each other, which are still on the page: the wire the tags speak, read from
`IMAGE_WIRE_BY_REFERENCE`, because no registry says what wire version a binary or a bundle speaks,
has to be one the address beside it reaches, measured from `/meta`, where no wording can forge it. A
reader who takes the command and the address from the page therefore meets one protocol, whatever
the page says about the wire. A reference with no entry in that map fails the check, so a tag a
release points at a different wire has that wire declared in the same wave. Where the page does say
which wire an artefact speaks, that sentence is held to the same declaration or the same `/meta`, so
a version sentence cannot come back unchecked. The one-wire rule is what catches the other
direction: a second version named on the page is a claim about a version this protocol does not
have, and a page that says the wire is unreleased — or that hands a reader the plaintext wire's
command — tells a guest their room is in the clear when it is not, which is the same defect with the
sign the other way round.

The relay-visibility statement is required rather than permitted, and it exists because the `clean`
fixtures can only prove the phrase pattern does not reject a sentence, not that the page carries
one. The check requires the rendered page's visible text to state each of the four facts the relay's
half of the panel is there to state — the room's existence, its membership, the display names, and
the sizes and timing of what moves — as a small pattern of its own rather than the sentence, so a
rewritten panel that keeps the facts passes and one that drops a fact fails. Three of the four are
the panel's chips, a line each; the fourth is the heading over them, *What the server can still
see*, read together with the chip under it that completes it, *that a room exists*. Two of the four
are read that closely, because the page states the same two nouns a second time in *The session
layer is written down*: matched loosely, that earlier paragraph supplied them for a page whose
statement had been deleted, and a rewrite that dropped those two while keeping the other two passed
with them gone. Deleting a chip fails the check on its fact, and deleting the heading fails it on
the room's existence, which is the one the two halves state together. The facts are read from the
page's own `docker run` onwards, and not over the whole page: the hero's second fact used to state
the same four facts in the same wording, and it is above the command, so a page-wide scan let the
hero satisfy a check written to require the panel — deleting the statement passed with the hero
standing in for it, which is the mutation that added the bound. The hero states them in a word each
now (*Sealed* for the relay's half), and the bound stays: a hero line that states a fact in full
still cannot stand in for the panel's place, which is under the command a reader can take it
together with. It asks no network.

The browser guest's own residual is the one disclosure the page carried and no longer does: a guest
who opens the page the room's own server serves trusts that server for the client code as well as
for the relay, and the installed clients are not in that position. Nothing here requires it, and no
phrase forbids it, because the page's remaining sentences about the server are about the relay — the
bytes it carries, the shape it can see — and the shape a browser guest is in is not one the page
describes any more. What the phrase list above still holds is the overclaim in that direction: that
nobody else can read the room, that the server learns nothing, or that the relay is blind.

The extension's publication is asserted the same way, and it is the one entry here that was a
prohibition turned round. The page used to be forbidden the words "marketplace", "open vsx" and
"gallery", on the ground that publishing the extension was a non-goal (`DESIGN.md` §11: "marketplace
publication until it works with a friend"); the owner retired that non-goal, and the extension is
published as `selvage-protocol.selvage` on the VS Code Marketplace and on Open VSX, which are the
two publish steps in `vscode_client/.github/workflows/release.yml`. So what is required is now the
truth and what is forbidden is the false direction: the identity and both registry names have to be
in the row, every registry-shaped word the page carries has to be part of one of those two names or
of the JetBrains Marketplace's, where the JetBrains plugin is handed over — any other registry, or
"the extension gallery" without saying which, fails — and any link the page carries to a listing has
to be one of the two or the JetBrains plugin's, because the retired
`selvage-protocol.selvage-client` listing is still live and still linkable by mistake. The row also has to say what an install is: the
clients are not a server, and each connects to a `selvaged` the reader runs. That last fact is
required rather than left to the phrase list because the registry names alone would read as a
running room, and "on a server you run" is not the sentence to read — the hero carries it. It asks
no network, and that is deliberate: the page's own link check reaches every URL it carries, and the
Marketplace's listing URL answers `404` until the release that publishes the extension has run, so
requiring a listing link here would redden this step for a release that has not been dispatched.
What the check proves is that the page agrees with the release workflow about the identity and the
two registries — not that either registry answers.

The hosted tier is required the same way, and it is the one card on the page that offers something
the project cannot hand over yet. The card, the sentence saying who would run it and the row that is
a plan rather than a control are read one pattern each, and the status is read in either of its two
spellings — the pill's *not available yet* or the row's *planned* — from the card's own markup, so a
rewrite that keeps the fact passes, a card that states it neither way fails, and the same words
elsewhere on the page (the grid's plan wears them) cannot stand in for it. The row's half is the
element it is written on: the card is read for a link or a button, so a row a reader can press fails
even though the words still read as a plan. The phrase list's `now available` entry can only catch
the other direction: a page that reads as an offer with nothing saying it cannot be taken is the
page this is for. It asks no network.

The repository grid is required the same way, and it is the page's own account of what exists. Its
rows are read from the page rather than listed in the check, because the clients are the page's own
list: a hand-maintained list of names here would be the drift the rule exists to catch, and a client
added to the page would be one the check never looked at. What is pinned by name is the handful of
facts that have to stay true of named rows: the specification is the source of truth, the
extension's row is the one a reader is also handed an install for, and `reference_server`,
`nvim_client`, `web_client` and `jetbrains_client` each keep a row that names them. A row's name,
description, word and destination are one claim, read together from the row's own list item rather
than from the page's text, so a row that links a different repository fails even though the page
still carries every name and every word. A row the page links has to wear one of the words a live
row may wear, and a row it does not link has to be a plan and say so, so a live repository cannot
give up its link by being called a plan without the word moving with it and the absence showing in
the diff. Every repository the page links has to be one the grid links, so no row and no source link
beside the terminal points at a repository the project does not have. The extension's row is the one
whose repository a reader is also handed an install for, and the install is where the claim about a
registry rather than a repository lives: the VS Code route in the terminal has to carry
`selvage-protocol.selvage` and both registries it is published to, read from that route's own panel,
so the row that says the client is available and the install a reader follows cannot be read apart —
a route that lost the identity or a registry fails even though the page names them somewhere else.

The three surfaces that draw a client — the grid's rows, the chips figure in *Clients share one
protocol* and the terminal's install routes — each carry the client's own key, and the check reads
them against each other: a client a chip names has to be a row in the grid, an install route's key
has to be a client the grid draws, and the chips have to be the leading clients in the grid's own
order, so what the figure's cap leaves out is the tail of the list rather than a scatter. A client
added to the page's own list moves all three at once; a surface written out by hand instead is the
half-added client this catches. It asks no network either.

The JetBrains plugin's listing is asserted against the Marketplace itself, and it is the one claim
here that waits on somebody else. The JetBrains route in the terminal has to name the JetBrains
Marketplace and link `https://plugins.jetbrains.com/plugin/34763-selvage`, read from the route's own
panel, and then the check asks `https://plugins.jetbrains.com/api/plugins/34763` about the plugin
and `…/34763/updates` about its versions: the plugin has to be plugin 34763 at that listing's path,
and one of its versions has to be on the stable channel, not hidden, and carry `"approve": true` and
`"listed": true`, read as the JSON `true` and nothing looser. JetBrains reviews each version by hand
before it lists it for everyone, and until then the version answers `"approve": false`, so a route
that says the plugin is published there with no approved version sends a reader to a plugin they
cannot install yet, and the step fails with exit 1. The plugin's own `"approve"` is not read: it
stayed `false` on a plugin whose approved version the IDE already offered to install.
The extension's half asks no registry, for the release-ordering reason above; this half does,
because the plugin's first listing is uploaded by hand and approved by JetBrains rather than
produced by a release this project dispatches, so what the page waits on is the approval. The
reading carries fixtures of its own, run before the scan: an approved version has to pass, and so
does one beside a newer version still in review; a listing whose only version is in review, one with
no version, one whose `approve` is the string `"true"`, an unlisted, hidden or non-stable version,
another plugin's version, another plugin's listing, one at another path, an answer that is not an
object and a version list that is not a list each have to be reported, so a reading that stops telling
a listing in review from a public one fails the check with exit 2 rather than passing every page. It
needs egress to `plugins.jetbrains.com` and exits 2 when it cannot ask; a `404` for the plugin is
exit 1, because a listing the Marketplace does not have disproves the route. It runs after every
other assertion, so a step that is red only on the approval is a page whose other claims all held.
