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
three editor clients.

## Running it

```console
$ npm ci --no-audit --no-fund
$ npm run dev
# then open http://localhost:3000/
```

Production, the way the deployment builds it:

```console
$ npm run build && npm start
# then open http://localhost:3000/
```

`npm run dev` is the framework's development server, and a dev server restarted underneath a reader
can look like a page that keeps refreshing itself; the `next build` output carries no way to reload
a page, and the deployed policy refuses every origin but its own.

Node comes from `.nvmrc` (`nvm use`, or any manager that reads it). `package.json` `engines` carries
only the major (`24.x`): Vercel deploys major versions alone, and an exact pin fails the deployment
before anything builds.

## Editing it

The page's copy, the wordings it must not carry, the facts it is held to and the figures' rules are
`docs/`. Those wordings are enforced rather than remembered: `scripts/ci-local.sh` runs the same
checks as `.github/workflows/ci.yml`.

- [The page, and its copy](docs/page-copy.md): the parts of the page, and the wording behind each.
- [What the page must never say](docs/must-not-say.md): the forbidden wordings, with reasons.
- [The claim filter](docs/claim-filter.md): what the check enforces, and the limits of a phrase list.
- [The product figures](docs/product-figures.md): the window, the four drawings, and their rules.
- [Deploying it](docs/deployment.md): Vercel, the response headers, and why it is not a release.

## Licence

`MIT OR Apache-2.0`, the pair the clients carry; see `LICENSE-MIT` and `LICENSE-APACHE`. The
page's framing follows the project's own design record, which is private and carries no licence;
the workflow sentence is adapted from the Neovim client's README, which is `MIT OR Apache-2.0`.
Where the wording came from is recorded here and not in the footer: the page states the licence a
visitor is bound by, and provenance is a note for whoever maintains the page.
