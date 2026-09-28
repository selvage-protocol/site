# The gate

The commands are in the [README's checks section](../README.md#checks). This is what each step reads
and what it fails on.

The claims step fetches `/` from the production server into `.tmp/rendered.html` (`PORT` overrides
the default `3100`) and scans that file by name; reaching no file is an error rather than a pass,
and every pattern must match its own sample before the scan, so a dead pattern fails the gate
instead of passing everything; named honest wordings must stay unmatched, so a broadening that
reintroduces a false positive fails it too, and those fixtures include the sealed-material readings
the specification itself uses and the peer's signed host claim. The scan reads the prose in the
page's `meta` attributes beside the visible text, because a link unfurl prints it. It also requires
two disclosures in the scanned file: the relay-visibility facts and the licence terms `selvaged` is
under, each as its own pattern, and the non-competing grant is read as a grant: a `not` in front of
it or inside it denies it and fails. Neither statement can be deleted while the fixtures stay green.
The corpus's citation is required the same way: the page states no count, because the counts move as
the corpus grows, so the sentence that names the conformance vectors, or the one after it, has to
name `specification/schema/validate.py`, the file that prints the current ones, and the scan fails
when no page does. A count that comes back is held to the same rule around the number, because a
number with nowhere to check it is one a reader takes on trust. The scan reads every count in every
file it was given — a rule that returned on the first cited page, or the first cited number, would
let a later one carry a number nobody can check. Both spellings the number rules accept are read:
`24 conformance vectors` and `24 wire vectors` are one pin, and a citation rule that matched one of
them would leave the other unguarded. The extension's publication is required the same way — the
identity, both registries, and what an install is and is not — and it is the one rule here that also
forbids: every registry-shaped word on the page has to belong to one of the two registries the
release publishes to, and a link to a listing has to be one of the two the release produces, so a
page offering the extension from "the extension gallery" or from somebody else's marketplace fails
rather than passing on the two names it also carries. It asks no network, and why is in [the claim
filter](claim-filter.md). The hosted tier the page offers and does not run yet is required the same
way — the card, a status stated once in either its pill or its row, the sentence saying who would
run it, and a row that is a plan rather than a control, read from the card's own markup — and so is
the repository grid, where every row joins its own word to its own link, the extension's row is read
against the VS Code install route that names the identity the release publishes under and both
registries, the row that is a plan is held to carrying no link, every repository the page links is
one the grid links, so `jetbrains_client` cannot come back as a link to a repository that is not
there, and the grid's client rows, the chips figure and the terminal's install routes have to name
the same clients, so a client written onto one surface and not the others fails the gate. It then
reads the page's image references, holds each to the tag `scripts/check-claims.py` carries on its
package — a bare repository being that tag — and asks `ghcr.io` for both of them; reads the Run
section's three commands — the first creates the network, every run is detached and on it, the page
container is pointed at the server container on the network both are on and is the one that
publishes a port, with the page image on that run and the server's on the other, which publishes
none, and the address the section prints for a reader is the host port that run publishes, with the
host its mapping names where it names one — and reads the `$ ` prompt and the labels the section
prints against the stylesheet the served page loads, requiring a rule that names their class and
takes it out of a selection, read from the build the server is serving rather than from `style.css`,
which this host having no Docker makes a shape and not a run, read in one way of writing each part,
so a correct command in other words fails it; reads the page's demo reference, holds it to the one
host the check allows, and asks that instance what it reports, whether the editor address's
`/session` path is answered by the server rather than by the proxy in front of it, and whether its
`/` serves the page with a host card in its shell; and holds the tag's declared wire and that
address against each other, since a reader takes both of them from the page — so the sealing claim
cannot be read without the command under it being read too. Where the page names a version for
either of the two, that sentence is held to the same pair.

The policy step reads the same rendered file, its not-found route, and the policy out of
`vercel.json`, and fails when the policy would refuse a script, stylesheet, image or font either
page carries, the defect described under [the Content-Security-Policy](content-security-policy.md).
Its fixtures run first: a policy without `script-src`, a policy without `font-src` and a policy that
drops `default-src 'none'` all have to fail it, so the check cannot have gone blind.

The weight step reads the same rendered file again and the bytes of every image it fetches out of
`public/`, and holds each to a budget: a surface this page paints at 30 px may not be handed the
owner's 800×800 master. It also asserts the `width`/`height` an `<img>` declares are the file's own
pixels, because a `src` swap that leaves them behind distorts the mark and no failed request says
so. It is a ceiling per image rather than a total for the page, so a framework upgrade that changes
nothing a reader sees cannot redden it.

`.github/workflows/ci.yml` runs the same commands on `ubuntu-24.04` on every pull request (and on
demand, through `workflow_dispatch`): Node from `.nvmrc`, `npm ci`, then `typecheck`, `build`,
`button`, `contrast`, `mark`, `claims`, `csp`, `weight`, `links` and `lint`. It installs lychee and
actionlint from pinned releases: the runner has no nix, so
[`scripts/ci-local.sh`](../scripts/ci-local.sh) takes both from `PATH` when they are there and from
nixpkgs otherwise, and all three places run the same checkers.
