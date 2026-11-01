# The page, and its copy

The landing page presents the product and its supported routes, not a task ledger. Copy must agree
with the public specification, client READMEs, release workflows and executable claim checks. The
page itself is not an editor or a hosted room service.

## Section contract

| Section | Required content and behavior |
|---|---|
| Hero | The promise, demo and editor CTAs, four facts (*Sealed*, *Specified*, *Path-scoped*, *No account*) and a room illustration. Put the CTAs before the facts so the next action is visible on short screens. The header CTA also leads to the demo. The specification is a text link in *Why a spec*, not a third button |
| Try → Run | Three equal-height cards in increasing order of commitment: *Try* the demo, *Run* the two published containers, *Rent* as a plan. The demo card qualifies browser hosting as desktop Chrome or Edge. The run card links to the full commands below and says rooms are in memory. The hosted tier says *Not available yet* or *Planned* in its own card and offers no actionable signup or purchase control |
| Start a room | A concrete first-room recipe using the demo, followed by editor alternatives. Retain the `How it works` anchor. Include the safety, browser and invite qualifications below |
| Run it yourself | Three separately selectable commands: create the shared network, start the server, start the web container. State the local-only scope, the address to open and the teardown. Details below |
| Get it working | One server and five client routes in an accessible tabbed terminal: VS Code, Neovim, JetBrains, Browser and AI agent. Each route carries its install command or address, necessary note and public repository. Beside it, disclose the relay's limits and the peer's signed host claim |
| See it working | Four explanatory drawings: invite holders join, peer carets in one file, granted paths and multiple clients on one protocol. These are illustrations, not acceptance-test screenshots or testimonials |
| Why a spec | Distinguish session semantics from LSP, DAP and `y-protocols`. Link the specification and its validator rather than printing moving corpus counts. Describe the Kotlin JetBrains implementation separately from the shared TypeScript engine. The repository grid names the public artifacts and their actual destinations |
| Footer | The licenses, the page's own privacy notice and contact address. No unsupported provenance or product claims |

Section headings have no counters. Numbers belong to ordered steps and choices, not the privacy
notice or licenses. Avoid disabled-looking links, empty feature cards and a general-purpose status
ledger. Repository rows describe what exists; a future artifact must be marked unavailable and
must not link to an artifact that does not exist.

## The second route: `Get it working`

`app/get-it-working/page.tsx` is the page the landing page's *Run* card and the header
link to. Its contract, and where it differs from the landing page's:

| Section | Required content |
|---|---|
| Head | One sentence of scope: a room needs one server, and everything else joins by the invite link the host is given |
| From a checkout | The one command (`reference_server/scripts/demo/demo.sh`) and what it starts, including that the shared folder is a copy and `--keep` keeps it |
| Published images | `docker compose up` in `reference_server`, the three `RUN_STEPS` commands, the teardown sentence, and that rooms are held in memory |
| Recording | The 78-second MP4 at `public/selvage-demo.mp4`, with a caption saying every frame is a real client and the captions are the only drawn-on part |
| Clients | One row per client that has an install route, from `CLIENTS` in `lib/clients.ts`, plus the MCP entry. The section states that an install is a client and not a server, and that a session needs a `selvaged` the reader runs |
| Before you invite anyone | What the sealed relay still sees, in the same words the landing page's panel uses, and that a room is not a file store |
| Footer | The licences, including `selvaged`'s FSL terms and the citation to `specification/schema/validate.py` |

The wording rules in [what the page must never say](must-not-say.md) apply to this route as
they do to the landing page. `scripts/check-claims.py` scans the page it is pointed at, and
its artefact checks — the Run card's prompt markup, the Rent card, the served-document CSP
model — are the landing page's own regions; CI runs it over `/` alone. The recording is the
one media element either route carries, which is why `vercel.json`'s policy names
`media-src 'self'`.

## First-room recipe

The browser recipe is for **desktop Chrome or Edge**:

1. Open the demo and choose a small disposable text folder. Warn that anyone with the invite can
   edit files on the host's disk.
2. Enter **Your name**, choose **Share a folder…**, allow read/write access and open a text file.
3. Choose **Copy invite link** and send the complete link, including everything after `#`, to
   someone trusted. The guest opens it, enters their name, chooses **Join** and opens the same
   file. Type in both windows.
4. Keep the host tab open and do not reload it. To finish, choose **Leave and end the room**, then
   **Leave anyway**.

Firefox and Safari can join from an invite but cannot host from the page because they lack the
directory picker. The Browser route carries this distinction and directs them to an editor host.
The VS Code route names `wss://selvage-demo.dontblameme.dev`, the display name, the clipboard invite
and the extension's published Marketplace listing. Do not turn these directions into a claim that
a human acceptance recording exists or is required.

## Local container recipe

The startup blocks are the page's published image recipe, derived from the same constants used by
the checks:

- Create the shared network, then start the server and the page containers, detached and named.
- Print bare image repository names; Docker supplies `:latest`. The server exposes no host port.
- Publish the page on `127.0.0.1:8080` and link that address. Only another window on the **same
  machine** can use its loopback invite. For another machine, point to the demo or the remote
  deployment guide, which covers TLS and hardening.
- Keep each label beside its command and the `$ ` prompt outside the selectable command text.
  Copying one block or dragging across blocks must not pick up prompts or labels.
- Print teardown after startup: `docker stop selvage-web selvaged`, then
  `docker network rm selvage`. Stopping ends rooms; startup's `--rm` removes stopped containers.
  Derive these names from the startup constants rather than maintaining a second list.

These commands are the happy path. They do not delete existing container names or inspect an
existing network before starting. The only local URL excluded from link checking is this loopback
address; `mailto:` is the other exclusion.

## Install routes and disclosures

The tabs follow the ARIA tabs pattern: arrow keys move between them, a selected tab scrolls into
view when the strip is narrow, and every panel remains in the document without scripting. Routes
come from the same client data as the repository grid, so adding a client does not require another
hand-maintained list.

- **VS Code:** `selvage-protocol.selvage`, both the VS Code Marketplace and Open VSX, the actual
  Marketplace listing and the server the extension connects to.
- **Neovim:** the public plugin-manager line and `:SelvageHost`.
- **JetBrains:** the plugin's Marketplace listing, platform version requirement and repository;
  there is no universal IDE launcher command.
- **Browser:** the demo route and the hosting-versus-joining distinction above.
- **AI agent:** the instruction to start the MCP server through `npx` from the repository, not an
  invented registry package.

Settings and full command lists belong in client READMEs. The adjacent disclosure panels must say
what sealing hides and what remains visible: no text, cursor, file name or role payload, but room
existence, membership, display names, sizes and timing remain visible. The relay can drop, delay,
reorder or refuse frames and end rooms. The host role is a peer's signed claim, not a server-granted
identity. A hero chip cannot substitute for these panels beside the install instructions.

## Claim and privacy boundaries

[What the page must never say](must-not-say.md) binds every section. The
[claim filter](claim-filter.md) documents the executable gate and its limits.

- The demo is a small in-memory instance, not a persistent or team-sized hosted service. The
  landing page's origin is not a place to join rooms. Do not describe the software or demo as
  non-commercial: state the actual licenses.
- Hosting is qualified by browser support and server origin; joining needs the host's complete
  invite. Do not restore stale denials that no browser client or published container exists.
- State what clients implement and what public tests cover. Do not infer universal interoperability,
  native editor UX acceptance, performance or ease of setup from protocol fixtures or illustrations.
- The specification is a draft and releases are 0.x. The wire version is held by the checks rather
  than repeated in copy that does not need it.
- Corpus numbers, if reintroduced, must match `specification/schema/validate.py` by layer. The wire
  and peer corpora are distinct; one layer's number cannot stand in for the other. Prefer linking
  the validator so copy does not become stale as vectors are added.
- The page prerenders static HTML but loads JavaScript. Its privacy notice names the resources
  fetched from this origin: stylesheet, two fonts, header mark, favicon set and framework runtime
  scripts. It names the controller and says it collects nothing; there is no waitlist form or
  mailing-service placeholder.

The page's public evidence is the linked source and CI results. Neither a green phrase filter nor
a local CSP check establishes that every possible claim is true or every production header is
present; deployment observations are kept separate in [Deploying it](deployment.md).
