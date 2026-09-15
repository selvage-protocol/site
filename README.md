# selvageprotocol.com — the public landing page

The landing page for **Selvage** (the project) and the **Selvage Session Protocol** (the protocol
it publishes). Static HTML and one stylesheet, served as they are: no build step, no Node, no
framework, no lockfile, no generator.

The canonical material lives in the other repositories —
[`selvage-protocol/specification`](https://github.com/selvage-protocol/specification) for the
protocol, prose and vectors, [`selvage-protocol/reference_server`](https://github.com/selvage-protocol/reference_server)
for the server and client library, and [`selvage-protocol/vscode_client`](https://github.com/selvage-protocol/vscode_client)
and [`selvage-protocol/nvim_client`](https://github.com/selvage-protocol/nvim_client) for the two
editor clients. This repository holds the page, the two checks that gate it, and nothing else.

| Path | What it is |
|---|---|
| `index.html` | the page |
| `style.css` | the one stylesheet: a system font stack, so no font is fetched from a third party |
| `favicon.svg` | the favicon, and the whole of it: the letter `S` in a system monospace font. It is not a wordmark — this project has no logo, and the page does not pretend otherwise |
| `scripts/check-claims.py` | the claim check: the phrases the page must not carry, each with its reason |
| `scripts/ci-local.sh` | the gate, running the same commands as the workflow |
| `lychee.toml` | what the link check does not check, and why |
| `vercel.json` | platform configuration only: the build step skipped, and three response headers |
| `.github/workflows/ci.yml` | the gate, on `push` to `main` and on `pull_request` |

## Previewing it

Any static file server will do; there is nothing to build first.

```console
$ python3 -m http.server 8000
# then open http://localhost:8000/
```

Opening `index.html` from the filesystem works too, except that the stylesheet resolves
differently under `file://` in some browsers; the server is the honest preview.

## Deploying it

Vercel, connected to this repository over the GitHub integration, with **no build step**. A
project created from the dashboard needs three settings, and `vercel.json` carries all three so
that the dashboard does not have to: `"framework": null` selects the "Other" preset,
`"buildCommand": ""` and `"installCommand": ""` leave the install and build steps empty. There is
nothing to install and nothing to compile, so the deployment is the checkout itself; the output
directory is the repository root.

Production deploys on `main` and every branch and pull request gets a preview URL. That is all
Vercel is used for. It does not run the checks — the workflow does, and those are the ones worth
making required status checks under branch protection.

Two things about the host plan are the owner's call, not this page's:

- Vercel's terms restrict the **Hobby** plan to personal, non-commercial use, and their Fair Use
  Guidelines count "advertising the sale of a product or service" as commercial. A page that
  advertises a future paid tier is on the commercial side of that line by their own definition,
  so Hobby may not be the right plan even before anything is sold. [Fair Use
  Guidelines](https://vercel.com/docs/limits/fair-use-guidelines), [Terms](https://vercel.com/legal/terms).
- The Hobby terms also allow Hobby content to be used for model training. A paid plan turns that
  off by default.

Cloudflare Pages is the $0 alternative with no commercial-use restriction, if either becomes
binding. Nothing here depends on which one is chosen: the page is files.

## The waitlist endpoint

**One edit.** In `index.html`, the waitlist form carries the endpoint:

```html
<form class="waitlist" method="post" action="https://waitlist.example.invalid/subscribe">
```

`waitlist.example.invalid` is a [reserved name](https://www.rfc-editor.org/info/rfc2606/) that
cannot resolve, so until it is replaced a submission fails loudly instead of quietly going
nowhere. **Replace it with the URL the service gives you before the page is announced anywhere.**

Three things to check when you do:

- **The field name.** The form posts one field, `name="email"`. Services that want a different
  name, or their own hidden field, tell you which in their own documentation; change the
  `name` attribute to match, and add no provider-specific markup for one that is not chosen yet.
- **Confirmation mail.** If the service offers double opt-in, turn it on. It is the reader's
  proof that they asked for the message, and it keeps an address out of the list until they
  answer.
- **The copy.** The page says the address is used to tell you when the hosted tier opens "and for
  nothing else". Keep that true: no reselling, no unrelated list, and a deletion at the reader's
  request.

The page also needs a privacy notice before it collects anything from a real visitor — what is
collected, who processes it, for how long, and how to ask for deletion. That is a document, not a
line of copy, and it is the owner's to write.

Two decisions taken here, stated so that they are not re-litigated silently:

- **No honeypot field.** A hidden field only works because whatever receives the submission
  discards the ones that fill it, and each service spells that field its own way. Naming one
  service's convention before the service is chosen would bake the provider in — exactly what
  the one-endpoint rule exists to avoid — so spam filtering is configured at the service, where
  it belongs. The reasoning is in a comment above the form, where the field would have gone.
- **No `form-action` in the Content-Security-Policy.** The CSP in `vercel.json` would have to
  name the endpoint to keep the form working, which is a second place to edit and a way to ship
  a form the policy blocks. The page is static HTML with no script and no user input rendered
  into it, so the directive would defend against an injection that has no path in. Add it at the
  same time as the endpoint if you want the belt and braces.

## What the page must never say

The page's job is to be checkable, so the rule is mechanical where it can be: `scripts/check-claims.py`
fails the build on each of these phrases, and carries the reason beside it. The reasons are
summarised here so that the constraint survives without the file that produced it.

| Must not appear | Why not |
|---|---|
| "open source" of the server or the project | The server binary is `FSL-1.1-MIT`: source-available, not OSI-approved, free for non-competing use and under MIT two years after each release. The specification and the clients are the open ones, and the page names their licences instead of reaching for the phrase |
| "SSP" | The abbreviation is taken by stack-smashing protection and by supply-side platforms. The protocol is the Selvage Session Protocol, written out |
| `salvage/1` | The wire version is `selvage/1`. "Selvage" is heard as "salvage", which is why the full protocol title appears at least once in the page's first paragraph |
| end-to-end encryption | Version 1 has no encryption layer. The server routes document payloads as bytes and holds them in memory |
| a browser client | There is no client that runs in a web page. Both clients are editor plugins |
| file create, rename or delete | The room carries no file mutations, and nothing writes to the host's working folder |
| Docker, or a one-command self-host | No image, compose file or service unit exists in any repository. The documented path is `cargo run -p selvaged -- --listen …` |
| a stable 1.0 | The wire version is `selvage/1` while the design is at 0.x: the same major, and at 0.x the same minor. Nothing has been released |
| a second implementation, or interoperability | There is none. The Neovim client drives a byte-identical copy of the same engine, so nothing yet shows a client built from the prose alone agreeing byte for byte with the Rust one |
| Marketplace availability | The extension is unpublished, and publishing it is a non-goal until it works with a friend |
| "guests are read-only" | The design inverts it: read-only scopes the host's filesystem, never the shared buffer, and every holder of the invite edits the session CRDT. Saying otherwise would be a lie about the product's central idea |
| "your code never leaves your machine" | Document payloads travel through the server to the peers that ask for them, and there is no encryption layer. What is bounded is the grant: the paths the host enumerates, and the reads it serves from inside the granted root |
| invented proof: logos, screenshots, testimonials, user counts, a demo link | None of them exist. There is no logo, no image, no recording and no user count in this project, and the only server that has ever run was a local debug build |

Two rules the check cannot make mechanical, and which a reader of a change has to hold:

- **A number on the page has a home.** The corpus counts (23 vectors, 806 frame checks, 192
  assertions) are the constants `specification/schema/validate.py` pins; when the corpus moves,
  the page moves with it. The commands are the ones the repositories' own READMEs document.
- **No adjective does the work of a fact.** If a sentence could be true of any project, it does
  not belong on this page.

## The domain and canonical metadata

`selvageprotocol.com` is the project's intended domain and it is **not registered**. The page
therefore carries **no** `<link rel="canonical">` and no Open Graph URL, and the link check has
nothing to exclude for it: a canonical URL pointing at a host that does not exist tells a search
engine that the real page is a duplicate of nothing, and an `og:url` on a dead host breaks the
preview card it exists for. Both go in when the domain does:

1. register the domain;
2. add `rel="canonical"`, plus `og:url`, `og:title` and `og:description`, pointing at it;
3. attach the domain to the Vercel project, apex and `www`;
4. remove nothing from `lychee.toml` — a URL that resolves needs no exclusion. If some URL ever
   does need one, it goes there with its reason beside it, as the placeholder endpoint's does.

Until then the page is reachable at its `*.vercel.app` URL, which is honest.

## The gate

```console
$ scripts/ci-local.sh            # lint, claims and links
$ scripts/ci-local.sh claims     # the phrase check over every *.html in the checkout
$ scripts/ci-local.sh links      # lychee over index.html and README.md
$ scripts/ci-local.sh lint       # actionlint over the workflows (local only; needs nix)
```

`.github/workflows/ci.yml` runs `claims` and `links` on `ubuntu-24.04` on every push to `main`
and every pull request. It installs lychee from a pinned release — the runner has no nix, so
`scripts/ci-local.sh` takes lychee from `PATH` when it is there and from nixpkgs otherwise, and
both places run the same checker. `lint` is local-only, as it is in the sibling repositories.

The claim check has two failure modes built in, because they are the same failure: a *pattern*
that matches nothing passes everything, and a *scan* that reaches no file reports a clean page.
Each entry carries a sample its own pattern must match, and reaching no `.html` file is an error
rather than a pass.

## Licence

`MIT OR Apache-2.0`, the pair the clients carry — see `LICENSE-MIT` and `LICENSE-APACHE`. The
prose on the page adapts the framing and the workflow sentence from the specification
repository's README, which is `CC-BY-4.0`, and says so in the page footer.
