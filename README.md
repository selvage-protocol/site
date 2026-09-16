# selvageprotocol.com — the public landing page

The landing page for **Selvage** (the project) and the **Selvage Session Protocol** (the protocol
it publishes). A Next.js App Router project with one route (`/`): the page component carries the
prose, the global stylesheet carries the styling, and nothing else ships to the browser beyond
the framework's own runtime.

The canonical material lives in the other repositories —
[`selvage-protocol/specification`](https://github.com/selvage-protocol/specification) for the
protocol, prose and vectors, [`selvage-protocol/reference_server`](https://github.com/selvage-protocol/reference_server)
for the server and client library, and [`selvage-protocol/vscode_client`](https://github.com/selvage-protocol/vscode_client)
and [`selvage-protocol/nvim_client`](https://github.com/selvage-protocol/nvim_client) for the two
editor clients. This repository holds the page, the two checks that gate it, and nothing else.

| Path | What it is |
|---|---|
| `app/page.tsx` | the page: the prose |
| `app/layout.tsx` | the root layout: `lang`, title, description and Open Graph metadata, favicon, global stylesheet |
| `style.css` | the one stylesheet, dark-only Catppuccin Mocha with a mauve accent: the Tailwind v4 entry (`@import "tailwindcss"` plus a `@theme` block pinning the palette) followed by the page's own rules under CSS variables, and a system font stack, so no font is fetched from a third party |
| `app/icon.svg` | the vector favicon: the owner's `svp` monogram redrawn as paths (see "The site mark"). Stays because it is resolution-independent at 3 KB; nothing in the page body uses it |
| `app/icon.png` / `app/apple-icon.png` | raster favicon fallbacks (32 and 180 px) resized from the owner's opaque export, for contexts without the font (see "The site mark") |
| `app/opengraph-image.png` | the social card image (Next file convention, served as `/opengraph-image.png`): the owner's opaque export at full size, so cards crop owner's pixels |
| `public/mark-opaque.png` / `public/mark-transparent.png` | the mark as served in the page body: the owner's opaque and transparent 800×800 exports, vendored byte-identical (see "The site mark") |
| `postcss.config.mjs` | the one PostCSS plugin (`@tailwindcss/postcss`), so `style.css` compiles on build |
| `components/ui/button.tsx` | the button primitive (shadcn-style `cva` variants: filled default, tinted secondary, ghost; renders an anchor when given `href`): the nav CTA and the two hero CTAs, nothing else |
| `components/ui/badge.tsx` | the pill primitive: the hero status line |
| `components/ui/card.tsx` | the card primitive: the abstract panel's glass card |
| `lib/utils.ts` | the one shared helper (`cn`: `clsx` + `tailwind-merge`) |
| `package.json` / `package-lock.json` | the only dependencies: `next`, `react`, `react-dom`, `tailwindcss` (+ its PostCSS plugin), `clsx`, `tailwind-merge`, `class-variance-authority` and `lucide-react` for icons, `typescript` and `@types/*`. No Radix, no component library, nothing else without a written reason |
| `.nvmrc` | the pinned Node version for local work and CI (`nvm use` reads it); `package.json` `engines` carries the major (`24.x`), because Vercel only deploys major versions |
| `scripts/check-claims.py` | the claim check: the phrases the page must not carry, each with its reason |
| `scripts/ci-local.sh` | the gate, running the same commands as the workflow |
| `lychee.toml` | what the link check does not check, and why |
| `vercel.json` | platform configuration: the Next.js framework preset, and three response headers |
| `.github/workflows/ci.yml` | the gate, on `push` to `main` and on `pull_request` |

## The site mark

The page body serves the owner's raster mark, not the redrawn SVG: two 800×800
PNG exports vendored byte-identical under `public/` (checksums match the owner's
files) and never hotlinked. Which export goes where is a contrast call:

| Surface | File | Why |
|---|---|---|
| Nav header on dark Mocha | `public/mark-transparent.png` | the bar is translucent Mocha over the page; the opaque export's baked `#1e1e2e` base would draw a visible box against it, while the transparent glyphs sit straight on the bar |
| Hero panel on the light mauve gradient | `public/mark-opaque.png` | the panel field runs near-white at its lightest stop; the transparent mauve glyphs would wash out on it, while the opaque export's dark Mocha chip keeps its contrast |
| Favicon and social card | `app/icon.png` / `app/apple-icon.png` / `app/opengraph-image.png` | tab bars and link unfurls crop unpredictably, so these stay opaque: the two favicon fallbacks resized from the opaque export, the social card the full-size opaque export |

`app/icon.svg` stays as the vector favicon: the owner's `svp` monogram (a Comfortaa
Bold monogram in Catppuccin mauve/teal/red on a Mocha base) with the Inkscape editor
metadata stripped, the Mocha base (`#1e1e2e`) baked in to match the opaque export,
and the live Comfortaa `<text>` converted to paths, because no visitor has the font
installed. At 3 KB it is the resolution-independent favicon; the page body does
not use it.

The favicon fallbacks are the owner's own pixels, not a render of the SVG: each is
the opaque 800×800 export resized down with ImageMagick, verified pixel-identical
to a fresh resize (RMSE 0 at both 32 and 180 px).

The prose in `app/page.tsx` descends from the static page's prose: the commands, the numbers,
the licence footer, the privacy notice with its two visible blanks, and the waitlist form are
unchanged. One sentence differs on purpose: the static page's "loads no JavaScript" is
false once Next.js serves the route, so the page says it prerenders to static HTML and names
the framework runtime scripts instead. Above the carried-over sections sits a benefit-first
hero in a dark-SaaS layout (nav, pill badge, two-line headline, checkmark list, two CTAs,
abstract mauve panel): every added sentence is a paraphrase of an already-audited true sentence
— the hook and workflow sentence from the design record, the memory-only server, the invite
as the whole permission, the spec corpus in its pinned numbers — or framed as direction (the
hosted tier, planned and built last). The must-not-say table still binds every line, and the
checker grew seven patterns for the traps the new vocabulary invites (a "live" status, a
proven-pairing claim, a speed adjective, an ease claim, an only-machine claim, a
third-party-sees claim, and SaaS-creep words like sign-in, download or pricing).

## Running it

```console
$ npm ci --no-audit --no-fund
$ npm run dev
# then open http://localhost:3000/
```

Production, the way the gate checks it:

```console
$ npm run build && npm start
# then open http://localhost:3000/
```

Node comes from `.nvmrc` (`nvm use`, or any manager that reads it); CI installs exactly that
version. `package.json` `engines` carries only the major (`24.x`): Vercel deploys major
versions alone, and an exact pin fails the deployment before anything builds. Telemetry is off
in the gate (`NEXT_TELEMETRY_DISABLED=1`).

## Deploying it

Vercel, connected to this repository over the GitHub integration, building the Next.js project:
`vercel.json` carries `"framework": "nextjs"` so the dashboard does not have to, plus the three
response headers. There is nothing to configure beyond connecting the repository.

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

## The waitlist endpoint and the notice

Two things must be true before the page collects an address, and neither is optional.

**The endpoint.** In `app/page.tsx`, the waitlist form carries it:

```tsx
<form className="waitlist" method="post" action="https://waitlist.example.invalid/subscribe">
```

`waitlist.example.invalid` is a [reserved name](https://www.rfc-editor.org/info/rfc2606/) that
cannot resolve, so until it is replaced a submission fails loudly instead of quietly going
nowhere. Replace it with the URL the service gives you.

**The notice.** The page carries a privacy notice below the form, with two blanks marked in the
page: the controller's name and contact, and the processor (the mailing service that sends the
message). Only the owner can fill them in. **Do not point the form at a live endpoint, and do not
publish the page, until both blanks are filled in:** a notice that names a controller nobody can
contact is not a notice, and a form that posts while its notice is a draft collects personal data
without the lawful basis the page states. The mailing service is a processor of the address, so
its own terms, or a data-processing agreement, belong with this step too.

Three things to check when you replace the endpoint:

- **The field name.** The form posts one field, `name="email"`. Services that want a different
  name, or their own hidden field, tell you which in their own documentation; change the
  `name` attribute to match, and add no provider-specific markup for one that is not chosen yet.
- **Confirmation mail.** If the service offers double opt-in, turn it on. It is the reader's
  proof that they asked for the message, and it keeps an address out of the list until they
  answer.
- **The copy.** The page says the address is used to tell you when the hosted tier opens "and for
  nothing else". Keep that true: no reselling, no unrelated list, and a deletion at the reader's
  request.

Two decisions taken here, stated so that they are not re-litigated silently:

- **No honeypot field.** A hidden field only works because whatever receives the submission
  discards the ones that fill it, and each service spells that field its own way. Naming one
  service's convention before the service is chosen would bake the provider in — exactly what
  the one-endpoint rule exists to avoid — so spam filtering is configured at the service, where
  it belongs. The reasoning is in a comment above the form, where the field would have gone.
- **No `form-action` in the Content-Security-Policy.** The CSP in `vercel.json` would have to
  name the endpoint to keep the form working, which is a second place to edit and a way to ship
  a form the policy blocks. The page renders no user input into itself, so the directive would
  defend against an injection that has no path in. Add it at the same time as the endpoint if
  you want the belt and braces.

## What the page must never say

The page's job is to be checkable, so the rule is mechanical where it can be:
`scripts/check-claims.py` fails the build on each of the known wordings below, carries the reason
beside each, and normalises the served HTML before matching — comments, tags, scripts and styles
removed, entities decoded, whitespace collapsed — so a phrase cannot pass by wrapping across a
line or by encoding a character. The scan runs against what the server renders, not the source:
the gate builds, starts the production server, fetches `/` over HTTP and checks that HTML.
**It is a filter, not a proof.** It cannot see meaning: a false claim in different words, a
synonym outside the list, a superlative, an unbacked sentence or a wrong number the list does not
pin all pass it. A green gate means the known wordings are absent, nothing more. The reasons are
summarised here so that the constraint survives without the file that produced it.

| Must not appear | Why not |
|---|---|
| "open source" of the server or the project | The server binary is `FSL-1.1-MIT`: source-available, not OSI-approved, free for non-competing use and under MIT two years after each release. The specification and the clients are the open ones, and the page names their licences instead of reaching for the phrase |
| "SSP" | The abbreviation is taken by stack-smashing protection and by supply-side platforms. The protocol is the Selvage Session Protocol, written out |
| `salvage/1` | The wire version is `selvage/1`. "Selvage" is heard as "salvage", which is why the full protocol title appears at least once in the page's first paragraph |
| end-to-end encryption, E2EE | Version 1 has no encryption layer: frames travel through the server as unencrypted bytes, and the slice has no transport security either. The relay is payload-opaque but not confidential |
| "the server cannot read it" / "the text never reaches the server" | The relay routes opaque bytes and keeps no document text, but it can read a frame as it passes and there is no transport security. It is not a confidential relay |
| a browser client | There is no client that runs in a web page. Both clients are editor plugins |
| file create, rename or delete | The room carries no file mutations and nothing writes to the host's working copy. The host's own editor still changes that folder, and a Neovim guest's mirror materialises the granted paths |
| Docker, or a one-command self-host | No image, compose file or service unit exists in any repository. The documented path is `cargo run -p selvaged -- --listen …` |
| a stable 1.0 | The wire version is `selvage/1`; the compatibility rule in force is the same major. Nothing has been released and no shape is frozen. No corpus line puts the design at 0.x |
| a second implementation, or interoperability | There is none. The Neovim client drives a byte-identical copy of the same engine, so nothing yet shows a client built from the prose alone agreeing byte for byte with the Rust one |
| marketplace or extension-gallery availability | The extension is unpublished, and publishing it is a non-goal until it works with a friend |
| "guests are read-only" or "view-only" | The design inverts it: read-only scopes the host's filesystem, never the shared buffer, and every holder of the invite edits the session CRDT. Saying otherwise would be a lie about the product's central idea |
| "your code never leaves your machine" | Document payloads travel through the server to the peers that ask for them, and there is no encryption layer. What is bounded is the grant: the paths the host enumerates, and the reads it serves from inside the granted root |
| invented proof: screenshots, testimonials, user counts, a production deployment, a demo link | None of them exist. There is no recording, no user count and no production deployment in this project, and the only server that has ever run was a local debug build. The one image the page carries is the project's own site mark (see above), not proof of anything |
| a claim of priority ("the first protocol to specify …") | The design record surveys prior art — Eclipse Open Collaboration Tools and others. The project's claim is that the session layer is unspecified, not that this is first |
| a corpus number other than the pinned one | The counts (23 vectors, 806 frame checks, 192 assertions) are constants in `specification/schema/validate.py`; any other number is a claim the corpus disproves |
| a third party seeing the room | The relay is payload-opaque but plaintext with no transport security in this slice, so the operator and the network path can see the room's text. Only the page's own weak reading (no third party's cloud holding the room) is backed |
| a proven cross-editor pairing | Both existing proofs drive two instances of one editor; the cross-editor session has never run. "Built so either editor can join the same room" states the design goal, not a demonstrated pairing |
| a speed adjective (instant, real-time, lag-free) | No performance data exists anywhere in the corpus |
| an ease claim (takes seconds, one-click, just works) | No image, compose file or service unit exists; the documented path is `cargo run`, and no ease claim is backed |
| an only-machine claim (untouched by the network) | Document payloads travel through the server to the peers that ask for them; the grant bounds which paths are served, not which machines code touches |
| a "live" / "now available" status | Nothing is released, hosted or published. The honest status line is the wire version plus the specification draft |
| SaaS-creep words (sign in/up, get started, download, pricing) | No accounts exist, so nothing can be signed into; no package exists to download and no price exists to show. The page offers the specification to read and a waitlist to join |

Three things the check cannot make mechanical, and which a reader of a change has to hold:

- **A number on the page has a home.** The corpus counts (23 vectors, 806 frame checks, 192
  assertions) are the constants `specification/schema/validate.py` pins; when the corpus moves,
  the page moves with it. The commands are the ones the repositories' own READMEs document.
- **No adjective does the work of a fact.** If a sentence could be true of any project, it does
  not belong on this page.
- **A false claim in other words.** The check matches a list of known wordings, so a synonym, a
  paraphrase or an assertion the list does not know about passes it. Green means those wordings
  are absent; it does not mean every sentence was checked against the corpus.

## The domain and canonical metadata

`selvageprotocol.com` is the project's intended domain and it is **not registered**. The page
therefore carries **no** `<link rel="canonical">` and no Open Graph URL: a canonical URL pointing
at a host that does not exist tells a search engine that the real page is a duplicate of nothing,
and an `og:url` on a dead host breaks the preview card it exists for. The title, description and
`og:title`/`og:description` mirror the page's own heading and lede; both URL-bearing tags go in
when the domain does:

1. register the domain;
2. add `rel="canonical"` plus `og:url`, pointing at it;
3. attach the domain to the Vercel project, apex and `www`;
4. remove nothing from `lychee.toml` — a URL that resolves needs no exclusion. If some URL ever
   does need one, it goes there with its reason beside it, as the placeholder endpoint's does.

Until then the page is reachable at its `*.vercel.app` URL, which is honest.

## The gate

```console
$ scripts/ci-local.sh              # typecheck, build, claims, links, lint
$ scripts/ci-local.sh typecheck    # tsc --noEmit
$ scripts/ci-local.sh build        # next build
$ scripts/ci-local.sh claims       # rebuild, serve production, fetch / and scan the rendered HTML
$ scripts/ci-local.sh links        # serve production, lychee over the rendered page and README.md
$ scripts/ci-local.sh lint         # actionlint over the workflows (nix; the workflow pins a release)
```

The claims step fetches `/` from the production server into `.tmp/rendered.html` (`PORT`
overrides the default `3100`) and scans that file by name — reaching no file is an error rather
than a pass, and every pattern must match its own sample before the scan, so a dead pattern fails
the gate instead of passing everything.

`.github/workflows/ci.yml` runs the same commands on `ubuntu-24.04` on every push to `main`
and every pull request: Node from `.nvmrc`, `npm ci`, then `typecheck`, `build`, `claims`,
`links` and `lint`. It installs lychee and actionlint from pinned releases — the runner has no
nix, so `scripts/ci-local.sh` takes both from `PATH` when they are there and from nixpkgs
otherwise, and all three places run the same checkers.

## Licence

`MIT OR Apache-2.0`, the pair the clients carry — see `LICENSE-MIT` and `LICENSE-APACHE`. The
page's framing follows the project's own design record, which is private and carries no licence;
the workflow sentence is adapted from the Neovim client's README, which is `MIT OR Apache-2.0`.
The page footer says the same thing.
