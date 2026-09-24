import { Check } from "lucide-react";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { SiteHeader } from "@/components/site-header";
import {
  CaretLines,
  ClientChips,
  RoomWindow,
  TreeFigure,
} from "@/components/room-visuals";

const heroFacts = [
  <>
    The session layer is written down as a specification: prose, JSON Schema and
    conformance vectors.
  </>,
  <>
    The server relays the room as ciphertext: it sees that a room exists, who is
    in it, their names and the sizes and timing of what moves, and never the file
    text, the cursors or the file names.
  </>,
  <>
    Guests see the paths you grant and edit the room&apos;s text. Only your own
    client writes to your folder.
  </>,
  <>
    There is no account on either side. Rooms live in memory on the server you host,
    and the server writes nothing to disk.
  </>,
];

const roomCards = [
  {
    lead: "Anyone with the link is in",
    body: (
      <>
        Hold the link and you are in. There is no approval step, and nobody waits for
        the host to let them in. Treat an invite the way you would treat a password.
      </>
    ),
    figure: <InviteCard />,
  },
  {
    lead: "Two carets, one text",
    body: (
      <>
        Everyone&apos;s edits land in the one CRDT, and carets and selections travel
        as anchors inside it. A peer&apos;s caret stays where it was while the text
        around it moves.
      </>
    ),
    figure: <CaretLines />,
  },
  {
    lead: "A guest sees the paths you granted",
    body: (
      <>
        The host publishes the paths inside the folder it granted, and reads a file
        from its own disk when somebody opens it. The room never adds, renames or
        removes a path in your working copy.
      </>
    ),
    figure: (
      <div className="fig">
        <TreeFigure label="guest · mirror" />
      </div>
    ),
  },
  {
    lead: "Multiple clients, one engine",
    body: (
      <>
        The VS Code client, the Neovim client and the browser page each drive a copy
        of the same engine and bridge, so a room&apos;s rules live in one
        implementation. The page joins a room from a link, and on the
        server&apos;s own page, Chrome or Edge can start one from a folder you
        pick.
      </>
    ),
    figure: (
      <div className="fig">
        <ClientChips />
      </div>
    ),
  },
];

const steps = [
  {
    lead: "Host a folder",
    body: (
      <>
        Start the server, open a folder in VS Code or Neovim, and host a session
        from the command palette. On the server&apos;s own page, Chrome or Edge can
        host from a folder the page asks for. The host lists the paths inside that
        folder and sends the listing.
      </>
    ),
  },
  {
    lead: "Send the invite",
    body: (
      <>
        Copy the invite link and send it however you already talk to each other. The
        token in it is the permission, and only the paths you granted are behind it.
        The host&apos;s client holds that confinement; nothing on the wire enforces
        it.
      </>
    ),
  },
  {
    lead: "Type in the same file",
    body: (
      <>
        A guest opens a file when they want it, and the host reads it from disk at
        that moment. A file nobody has opened sends no text, so opening one file
        never moves the whole project over the wire.
      </>
    ),
  },
  {
    lead: "Close the window",
    body: (
      <>
        Closing or reloading the host&apos;s window ends the room: whoever is in it
        keeps editing while a short countdown runs, and then each client&apos;s
        session ends and the room closes. A room lives while it has connections and
        for a short grace period after its last one ends, which is why a dropped
        connection does not end it, and why the server reaps a room only once its
        last connection goes. Rooms live in memory: nothing survives a restart of
        the server.
      </>
    ),
  },
];

/** The invite, at card weight: the same chip the hero figure carries, with the copy glyph's
    job done by the label alone. */
function InviteCard() {
  return (
    <div className="fig fig-invite">
      <span className="invite">
        <span className="invite-label">invite link</span>
        <span className="invite-url">
          ?room=k7m2&amp;token=4f9c
          <wbr />
          #k=&hellip;&amp;h=&hellip;
        </span>
      </span>
    </div>
  );
}

export default function Home() {
  return (
    <div className="min-h-screen bg-base font-sans text-text antialiased">
      <SiteHeader />

      <main id="top">
        <section className="mx-auto w-full max-w-6xl px-5 pb-16 pt-10 md:pb-24 md:pt-16">
          <div className="grid items-center gap-10 xl:grid-cols-[minmax(0,35rem)_minmax(0,1fr)] xl:gap-12">
            <div>
              <Badge>Live-coding collaboration protocol</Badge>
              {/* One sentence per block, and a real space between them: the claims
                  filter joins block markup with a single space, and without it the
                  sentence boundary reads as `run.on` to it. */}
              <h1 className="mt-7 text-balance text-[2rem] font-semibold leading-[1.12] tracking-[-0.025em] text-text sm:text-[2.375rem] xl:text-[2.5rem]">
                <span className="block">Edit the same file together,</span>{" "}
                <span className="block">on a server you run.</span>
              </h1>
              <p className="mt-6 max-w-[35rem] text-[1.0625rem] leading-[1.7] text-subtext md:text-[1.125rem]">
                Selvage is a live-coding collaboration protocol: one Rust binary
                you host holds the room, and an invite link is the whole
                permission. VS Code, Neovim and a browser page join the same
                file, with no account and no third party&apos;s cloud holding
                the room.
              </p>
              <ul className="mt-8 max-w-[35rem] space-y-3">
                {heroFacts.map((fact, index) => (
                  <li key={index} className="flex items-start gap-3">
                    <span className="mt-0.5 inline-flex h-5 w-5 shrink-0 items-center justify-center rounded-full bg-mauve/15">
                      <Check
                        className="h-3.5 w-3.5 text-mauve"
                        strokeWidth={3}
                        aria-hidden="true"
                      />
                    </span>
                    <span className="text-[15px] leading-relaxed text-text">
                      {fact}
                    </span>
                  </li>
                ))}
              </ul>
              <div className="mt-9 flex flex-wrap items-center gap-3">
                <Button href="https://selvage-demo.dontblameme.dev" size="lg">
                  Try the demo in your browser
                </Button>
                <Button href="#get-it-working" variant="secondary" size="lg">
                  Run it in your editor
                </Button>
                <Button
                  href="https://github.com/selvage-protocol/specification"
                  variant="ghost"
                  size="lg"
                >
                  Read the specification
                </Button>
              </div>
              <p className="mt-4 font-mono text-[12px] text-subtext">
                The specification is a draft, and the wire version is{" "}
                <code>selvage/2</code>.
              </p>
            </div>

            <RoomWindow />
          </div>
        </section>

        <div className="prose-body mx-auto w-full max-w-6xl px-5 pb-14">
          <section
            id="get-it-working"
            className="scroll-mt-28 md:scroll-mt-24"
          >
            <h2>Get it working</h2>
            <p>
              One server holds the room, and the editor you already use is where
              you type. Run the published container, then open one row per
              editor below.
            </p>

            <h3>Start a server</h3>
            <pre>
              <code>
                {
                  "docker run --rm -p 127.0.0.1:8080:8080 ghcr.io/selvage-protocol/selvaged:0.4.1"
                }
              </code>
            </pre>
            <p>
              The server answers{" "}
              <code>ws://127.0.0.1:8080/session</code> and reports on{" "}
              <code>http://127.0.0.1:8080/meta</code>, one port for the room and
              the page that joins it. Rooms live in memory, so a restart ends
              them. The <code>127.0.0.1</code> binding keeps the room on your
              own machine; serving guests on other machines means rebinding
              (for example <code>-p 8080:8080</code>) and an invite URL that
              names a reachable address.{" "}
              <a href="https://github.com/selvage-protocol/reference_server">
                selvage-protocol/reference_server
              </a>{" "}
              holds the compose file and the source build.
            </p>
            <p>
              The container image above and the demo speak <code>selvage/2</code>, the
              one wire version this protocol has, and it is the sealed one: the
              room&apos;s bytes reach that server as ciphertext.
            </p>
            <p>
              The server relays ciphertext: documents,
              cursors, the file listing, which files are open and who may edit are
              sealed under keys that travel in the part of the link a browser never
              sends to a server, and the decisions a session used to ask the server
              to make are signed by the peers instead. The box — and whoever holds it
              — carries bytes it cannot read, and the host is a peer&apos;s signed
              claim rather than a server fact: it cannot seat a host, prove one or
              take the role. The peer layer has its own corpus for that: 26 peer
              vectors, 221 peer checks and 74 peer assertions, replayed in one
              process with no socket and no client. The relay still sees that a room
              exists, who is in it, their names, and the sizes and timing of what
              moves, and it can still drop, delay, reorder or refuse frames and end
              any room.
            </p>
            <p>
              Whoever holds the invite holds the keys to it: a leaked link is a leaked
              room, fragment included, so treat an invite the way you would treat a
              password.
            </p>

            <h3>Pick your editor</h3>
            <p>
              One row per editor, folded shut. The commands inside are the ones
              the editor&apos;s own README documents.
            </p>
            <details className="quickstart">
              <summary>
                VS Code: install the extension, then host a session
              </summary>
              <div className="quickstart-body">
                <p>
                  Needs VS Code 1.85 or newer. The extension is published as{" "}
                  <code>selvage-protocol.selvage</code> on the VS Code Marketplace
                  and on Open VSX:
                </p>
                <pre>
                  <code>
                    {"code --install-extension selvage-protocol.selvage"}
                  </code>
                </pre>
                <p>
                  An install is the client and not a server: a session pairs with
                  a <code>selvaged</code> you run. Or build the <code>.vsix</code>{" "}
                  from a checkout, which needs Node 22.18 or newer:
                </p>
                <pre>
                  <code>
                    {
                      "git clone https://github.com/selvage-protocol/vscode_client\ncd vscode_client\nnpm ci --no-audit --no-fund\nnpm run package\ncode --install-extension selvage-<version>.vsix"
                    }
                  </code>
                </pre>
                <p>
                  Open the folder you want to share and run{" "}
                  <em>Selvage: Host a session</em> against{" "}
                  <code>ws://127.0.0.1:8080</code>; the invite link is copied as
                  the room opens. A guest runs{" "}
                  <em>Selvage: Join a session from an invite link</em> and pastes
                  it, which reloads that window onto the room&apos;s own folder.{" "}
                  <a href="https://github.com/selvage-protocol/vscode_client">
                    selvage-protocol/vscode_client
                  </a>
                </p>
              </div>
            </details>
            <details className="quickstart">
              <summary>
                Neovim: the plugin manager installs it, then host with one command
              </summary>
              <div className="quickstart-body">
                <p>
                  Needs Neovim 0.10 or newer, and Node 22.18 or newer on{" "}
                  <code>PATH</code> for the companion process the plugin runs.
                  The plugin manager runs <code>npm ci</code> when it installs the
                  plugin:
                </p>
                <pre>
                  <code>{`{ 'selvage-protocol/nvim_client', build = 'npm ci' }`}</code>
                </pre>
                <p>
                  That is the whole lazy.nvim spec, and vim-plug takes{" "}
                  <code>
                    {"Plug 'selvage-protocol/nvim_client', { 'do': 'npm ci' }"}
                  </code>
                  . Then <code>:SelvageHost ws://127.0.0.1:8080</code> shares the
                  current buffer and copies the invite,{" "}
                  <code>:SelvageCopyInvite</code> copies it again later, and{" "}
                  <code>{":SelvageJoin <invite>"}</code> joins the room the link
                  names.{" "}
                  <a href="https://github.com/selvage-protocol/nvim_client">
                    selvage-protocol/nvim_client
                  </a>
                </p>
              </div>
            </details>
            <details className="quickstart">
              <summary>
                Browser page: join a room, or start one in Chrome or Edge
              </summary>
              <div className="quickstart-body">
                <p>
                  The server above serves the page on the same port, and{" "}
                  <a href="https://selvage-demo.dontblameme.dev">the demo</a>{" "}
                  serves it too. A guest opens the invite link the host copied
                  and edits in the page, which takes the room and token in its
                  query string and the room&apos;s keys in its fragment:
                </p>
                <pre>
                  <code>
                    {
                      "http://127.0.0.1:8080/?room=<room>&token=<token>#k=<room key>&h=<host public key>"
                    }
                  </code>
                </pre>
                <p>
                  With no invite link, Chrome or Edge can start a session from the
                  page instead: the page asks for a folder, lists the paths inside
                  it, and writes the room&apos;s settled text back into the file it
                  came from. It has to be the page its own server serves, which is
                  how <a href="https://selvage-demo.dontblameme.dev">the demo</a> is
                  served.
                </p>
                <p>
                  A guest who opens the page the room&apos;s own server serves trusts
                  that server for the client code as well as for the relay: the
                  program that reads the link&apos;s fragment was served by the party
                  the sealing is meant to keep out. The VS Code and Neovim clients
                  are installed artefacts and are not in that position.
                </p>
                <p>
                  The page lives in{" "}
                  <a href="https://github.com/selvage-protocol/web_client">
                    web_client
                  </a>
                  : <code>npm ci</code>, <code>npm run build</code> and{" "}
                  <code>npm run serve</code> build and serve it on its own.
                </p>
              </div>
            </details>

            <h3>Try the demo</h3>
            <p>
              A small instance of the server runs at{" "}
              <a href="https://selvage-demo.dontblameme.dev">
                selvage-demo.dontblameme.dev
              </a>
              . Point one of the editors above at{" "}
              <code>wss://selvage-demo.dontblameme.dev</code> and it hosts a room
              there: <code>selvage.serverUrl</code> in VS Code,{" "}
              <code>vim.g.selvage_server_url</code> in Neovim. A host started
              with neither setting asks for the address. The invite link it
              copies opens the room in the browser page, so a guest needs
              nothing installed. Chrome or Edge can start a room there from the
              page itself, with no editor running at all.
            </p>
            <p>
              Rooms live in memory on one small box, and a restart ends every one
              of them. Run the server above for work you need to keep, on your
              own machine or on one you rent. The instance is for personal and
              evaluation use, and non-commercial:{" "}
              <a href="https://selvage-demo.dontblameme.dev/terms">its terms</a> cover
              this one box, and the licences below decide what the software itself
              may be used for, <code>selvaged</code>&apos;s FSL-1.1-MIT reserving
              commercial hosting for the project.
            </p>
          </section>

          <section id="see-it" className="scroll-mt-28 md:scroll-mt-24">
            <h2>See it working</h2>
            <p>
              A room is the host&apos;s folder, seen from somebody else&apos;s
              editor.
            </p>
            <ul className="cards">
              {roomCards.map((card) => (
                <li key={card.lead}>
                  {card.figure}
                  <p className="card-lead">{card.lead}</p>
                  <p className="card-body">{card.body}</p>
                </li>
              ))}
            </ul>
          </section>

          <section id="how-it-works" className="scroll-mt-28 md:scroll-mt-24">
            <h2>How it works</h2>
            <p>
              The workflow is one sentence:{" "}
              <strong>share a link, come edit my code with me.</strong> In order, it
              comes to four moves.
            </p>
            <ol className="steps">
              {steps.map((step) => (
                <li key={step.lead}>
                  <strong>{step.lead}.</strong> {step.body}
                </li>
              ))}
            </ol>
          </section>

          <section id="why-a-spec" className="scroll-mt-28 md:scroll-mt-24">
            <h2>The session layer has no specification</h2>
            <p>
              Language tooling has the Language Server Protocol and debugging has
              the Debug Adapter Protocol. Document sync has{" "}
              <code>y-protocols</code> and the CRDT libraries beneath it. Which
              rooms exist, who is in one, what their role is, which documents are
              open, where their carets are, what happens when somebody leaves:
              every collaborative tool decides those for itself, so none of the
              tools can talk to each other.
            </p>
            <p>
              Selvage writes that layer down: prose, a canonical byte form for a
              frame, JSON Schema documents, and 24 conformance vectors (33760 frame
              checks and 8387 assertions) replayed byte for byte against a real
              server. The numbers are constants in <code>schema/validate.py</code>,
              so deleting an assertion fails the run instead of shrinking a total in
              a line of output.
            </p>
            <p>
              The vectors are also the honest test: nothing yet shows that code
              written from the prose alone agrees with this implementation byte for
              byte, and a corpus you can replay is what would settle it.
            </p>
            <p>
              <a href="https://github.com/selvage-protocol/specification">
                Read the specification
              </a>
              . It is written to be implemented on its own, without reading the
              Rust.
            </p>
            <details className="quickstart">
              <summary>
                Verify the corpus, and see what the clients do with the room
              </summary>
              <div className="quickstart-body">
                <h3>Check the corpus</h3>
                <p>
                  The schemas and the vectors are checked on their own, with no
                  server and no Rust: every schema-eligible frame parses and
                  validates against the schema for the concern it names, and
                  every expected frame is written in the canonical byte form.
                </p>
                <pre>
                  <code>
                    {
                      "git clone https://github.com/selvage-protocol/specification\ncd specification\npip install jsonschema referencing\npython3 schema/validate.py"
                    }
                  </code>
                </pre>

                <h3>Replay the vectors against a server</h3>
                <p>
                  The same transcripts are replayed against a real{" "}
                  <code>selvaged</code> over a WebSocket, with no Rust in the
                  comparison: the runner reads the vectors, starts a server of
                  its own on an ephemeral port, and compares what comes back byte
                  for byte. It exits non-zero on any mismatch.
                </p>
                <pre>
                  <code>
                    {
                      "git clone https://github.com/selvage-protocol/reference_server\ngit clone https://github.com/selvage-protocol/specification\ncd reference_server\nnix develop . -c cargo build -p selvaged\nexport SELVAGE_SELVAGED=$PWD/target/debug/selvaged\ncd ../specification\npip install websockets jsonschema referencing\npython3 runner/run_vectors.py"
                    }
                  </code>
                </pre>

                <h3>What the clients do with the room</h3>
                <p>
                  A host shares the documents it has open under the folder it
                  granted, and a guest reads a file from that folder when it opens
                  one, so nothing is copied until somebody asks for it. The
                  Neovim client mirrors the granted folder into a real directory
                  of its own, so ripgrep, ctags and a language server see ordinary
                  paths, and it keeps its engine in a companion process.
                </p>
                <p>
                  VS Code adds <code>Selvage: Copy the invite link</code>,{" "}
                  <code>Selvage: Open a document from the room</code> and{" "}
                  <code>Selvage: Leave the session</code>; Neovim answers with{" "}
                  <code>:SelvageCopyInvite</code>, <code>:SelvageJoin</code> and{" "}
                  <code>:SelvageLeave</code>. Each repository&apos;s own README is
                  the full command list.
                </p>
              </div>
            </details>
          </section>


        </div>
      </main>

      <footer className="prose-body page-foot mx-auto w-full max-w-6xl px-5 pb-20">
        <div>
          <h2>Licences</h2>
            <p>
              The specification (prose, canonical form, JSON Schema and vectors) is
              CC-BY-4.0, and its tooling is MIT OR Apache-2.0. The reference server
              and the clients are MIT OR Apache-2.0, with one exception: the server
              binary <code>selvaged</code> is <strong>FSL-1.1-MIT</strong>, which
              is source-available and not OSI-approved. It is free for any
              non-competing purpose, converts to MIT two years after each release,
              and carries a non-compete clause that reserves exactly the thing a
              hosted Selvage would be.
            </p>
            <p>
              This page prerenders to static HTML: one stylesheet, the mark in its
              header, the favicon set and the framework&apos;s runtime scripts, every
              one of them from this origin. It sets no cookie, makes no third-party
              request and collects no personal data of its own; the{" "}
              <a href="https://github.com/selvage-protocol">selvage-protocol</a>{" "}
              GitHub organisation is its controller.
            </p>
            <p>
              Mail you send to{" "}
              <a href="mailto:selvage@dontblameme.dev">
                selvage@dontblameme.dev
              </a>{" "}
              about the project or a security problem in it is the one thing here
              that carries your own address back: the controller receives it and keeps
              it only to answer. The page is MIT OR Apache-2.0, and its workflow
              sentence is adapted from the Neovim client&apos;s README, which is MIT
              OR Apache-2.0.
            </p>
          </div>
      </footer>
    </div>
  );
}
