# The public landing page

The landing page for **Selvage** (the project) and the **Selvage Session Protocol** (the protocol it
publishes), served at **https://selvage.dontblameme.dev**. It is one Next.js App Router project: the
route `/` carries the page, and `app/not-found.tsx` is the route beside it. The canonical material
lives in the other repositories:
[`selvage-protocol/specification`](https://github.com/selvage-protocol/specification) for the
protocol, prose and vectors, [`selvage-protocol/reference_server`](https://github.com/selvage-protocol/reference_server)
for the server and client library, and [`selvage-protocol/vscode_client`](https://github.com/selvage-protocol/vscode_client),
[`selvage-protocol/nvim_client`](https://github.com/selvage-protocol/nvim_client) and
[`selvage-protocol/jetbrains_client`](https://github.com/selvage-protocol/jetbrains_client) for the
three editor clients. This repository holds the page, the six check scripts that gate it, the one
browser proof the runner cannot run, and nothing else.

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

`npm run dev` is the framework's development server, and its page can reload itself: Next's dev
client calls `window.location.reload()` when it decides the server it was talking to has been
replaced (a new session id, a changed compilation hash) or after twelve failed attempts to hold
its hot-reload channel. A dev server restarted underneath a reader therefore looks like a page
that keeps refreshing on its own. That is the dev server being a dev server, and it is nothing a
visitor to the deployed site can see: the `next build` output carries no way to reload a page —
no meta refresh, no service worker, no polling script — and the policy below refuses every origin
but its own.

Node comes from `.nvmrc` (`nvm use`, or any manager that reads it); CI installs exactly that
version. `package.json` `engines` carries only the major (`24.x`): Vercel deploys major
versions alone, and an exact pin fails the deployment before anything builds. Telemetry is off
in the gate (`NEXT_TELEMETRY_DISABLED=1`).

## Checks

The gate is `scripts/ci-local.sh`, and it runs the same commands as `.github/workflows/ci.yml`:

```console
$ scripts/ci-local.sh              # typecheck, build, button, contrast, mark, claims, csp, weight, links, lint
$ scripts/ci-local.sh typecheck    # tsc --noEmit
$ scripts/ci-local.sh build        # next build
$ scripts/ci-local.sh button       # render the button/anchor variants and assert their props reach the DOM
$ scripts/ci-local.sh contrast     # the theme token pairs at or above WCAG AA, and the nav mark's own pixels at its visibility floor
$ scripts/ci-local.sh mark         # re-derive the nav mark from the master and compare it with the committed file
$ scripts/ci-local.sh claims       # rebuild, serve production, fetch / and scan the rendered HTML
$ scripts/ci-local.sh csp          # the policy in vercel.json over the served page and its not-found route, refusing nothing either carries
$ scripts/ci-local.sh weight       # every image the page body fetches, against its byte budget
$ scripts/ci-local.sh links        # serve production, lychee over the rendered page, the README and the docs tree
$ scripts/ci-local.sh lint         # actionlint over the workflows (nix; the workflow pins a release)
```

## More

- [The page](docs/the-page.md): how it is built, what it fetches, and the not-found route.
- [Repository layout](docs/repository-layout.md): every file in the tree and what it is.
- [The site mark](docs/site-mark.md): its derivatives, the favicons, and the removed vector icon.
- [The page, and its copy](docs/page-copy.md): the seven parts and the wording behind each.
- [The product figures](docs/product-figures.md): the window, the four drawings, and their rules.
- [Deploying it](docs/deployment.md): Vercel, the response headers, and why it is not a release.
- [The Content-Security-Policy](docs/content-security-policy.md): the policy and its two proofs.
- [Privacy](docs/privacy.md): the controller, the removed waitlist, and two decisions.
- [The claim filter](docs/claim-filter.md): the facts it asserts in the positive, and its limits.
- [What the page must never say](docs/must-not-say.md): the forbidden wordings, with reasons.
- [The live origin](docs/live-origin.md): the origin, the canonical tags, and the metadata.
- [The gate](docs/gate.md): what each step reads and what it fails on.
- [Accessibility](docs/accessibility.md): the measured ratios and what a person checks.

## Licence

`MIT OR Apache-2.0`, the pair the clients carry; see `LICENSE-MIT` and `LICENSE-APACHE`. The
page's framing follows the project's own design record, which is private and carries no licence;
the workflow sentence is adapted from the Neovim client's README, which is `MIT OR Apache-2.0`.
Where the wording came from is recorded here and not in the footer: the page states the licence a
visitor is bound by, and provenance is a note for whoever maintains the page.
