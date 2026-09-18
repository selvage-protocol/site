import { ArrowUpRight, Check } from "lucide-react";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { SiteHeader } from "@/components/site-header";
import {
  CaretLines,
  ClientChips,
  RoomWindow,
  TreeFigure,
} from "@/components/room-visuals";

const heroFacts = [
  <>
    <strong>The specification is the artifact.</strong> Prose, JSON Schema and
    conformance vectors: the session layer that language tooling has as LSP and
    debugging has as DAP, and that collaborative editing has never had.
  </>,
  <>
    <strong>Your working copy is the truth.</strong> Guests see the paths you
    grant and edit the room&apos;s text; nothing writes to your folder, and the
    room ends when you leave.
  </>,
  <>
    <strong>No account on either end.</strong> Rooms live in memory on the
    server you chose, the invite is the whole permission, and nothing is
    written to disk.
  </>,
];

const roomCards = [
  {
    lead: "The invite is the permission",
    body: (
      <>
        Anyone holding the link is in the room: no account, no approval step,
        and no waiting for the host to let you in. Treat an invite the way you
        would treat a password.
      </>
    ),
    figure: <InviteCard />,
  },
  {
    lead: "Two carets, one text",
    body: (
      <>
        Everyone&apos;s edits land in the one CRDT, and carets and selections
        travel as anchors inside it — so a peer&apos;s caret stays where it was
        while the text around it moves.
      </>
    ),
    figure: <CaretLines />,
  },
  {
    lead: "Your tree, not your disk",
    body: (
      <>
        The host publishes the paths inside the folder it granted — paths, never
        content — and reads a file from its own disk when somebody opens it. The
        room carries no file mutations, so nothing adds, renames or removes a
        path in your working copy.
      </>
    ),
    figure: (
      <div className="fig">
        <TreeFigure label="guest · mirror" />
      </div>
    ),
  },
  {
    lead: "Three clients, one engine",
    body: (
      <>
        The VS Code client, the Neovim client and the browser page all drive a
        copy of the same engine and bridge, so the room&apos;s rules are one
        implementation rather than three. The browser page is the third client:
        guests only, and served over the project&apos;s own private network.
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
        from the command palette. The client lists the paths inside the folder
        you granted and puts that listing on the wire.
      </>
    ),
  },
  {
    lead: "Send the invite",
    body: (
      <>
        Copy the invite link and send it however you already talk to each other.
        The token in it is the permission, and only the paths you granted are
        behind it.
      </>
    ),
  },
  {
    lead: "Type in the same file",
    body: (
      <>
        Each guest opens a file when they want it, and it is read from the
        host&apos;s disk at that moment. A file nobody has opened sends no text,
        so looking at one file never moves the whole project over the wire.
      </>
    ),
  },
  {
    lead: "Close the window",
    body: (
      <>
        The room dies with its host after a short grace period, so a dropped
        connection does not end it. Rooms live in memory only: nothing survives
        a restart of the server.
      </>
    ),
  },
];

const built = [
  <>
    <strong>The specification, in draft</strong> — prose, a canonical byte form,
    JSON Schema and conformance vectors.
  </>,
  <>
    <strong>
      <code>selvaged</code>, the server
    </strong>{" "}
    — one Rust binary, rooms in memory, nothing written to disk.
  </>,
  <>
    <strong>The VS Code and Neovim clients</strong> — host, join, presence, a
    mirrored tree, follow.
  </>,
  <>
    <strong>The browser client</strong> — guests only, in a page, served over
    the project&apos;s own private network.
  </>,
];

const notYet = [
  <>
    <strong>No public demo.</strong> The demo instance and the browser page run
    on a private network of ours, so there is no open link to hand out.
  </>,
  <>
    <strong>No release.</strong> The wire version is <code>selvage/1</code> and
    the compatibility rule in force for it is the same major; nothing has been
    published to an extension store.
  </>,
  <>
    <strong>No persistence.</strong> Rooms die with the host, and nothing
    survives a restart of the server.
  </>,
  <>
    <strong>No encryption layer in version 1.</strong> Frames travel through the
    server as unencrypted bytes, and this slice has no transport security
    either, so treat the server&apos;s operator and the network path as able to
    see the room&apos;s text.
  </>,
  <>
    <strong>One engine.</strong> The three clients drive a copy of the same
    engine, so a client written from the prose alone has not been shown to agree
    with it byte for byte.
  </>,
  <>
    <strong>The specification is a draft.</strong> <code>NOTES.md</code> lists
    what the prose deliberately leaves open: the invite carries the token in its
    URL, the host role is claimed rather than proven, and a document path is any
    non-blank string.
  </>,
];

function InviteCard() {
  return (
    <div className="fig fig-invite">
      <span className="invite">
        <span className="invite-label">invite link</span>
        <span className="invite-url">?room=k7m2&amp;token=4f9c&hellip;</span>
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
                file &mdash; no account, and no third party&apos;s cloud holding
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
                <Button
                  href="https://github.com/selvage-protocol/specification"
                  size="lg"
                >
                  Read the specification
                  <ArrowUpRight />
                </Button>
                <Button href="#run-it" variant="secondary" size="lg">
                  Run it
                </Button>
              </div>
            </div>

            <RoomWindow />
          </div>
        </section>

        <div className="prose-body mx-auto w-full max-w-6xl px-5 pb-14">
          <section id="see-it" className="scroll-mt-28 md:scroll-mt-24">
            <h2>See it working</h2>
            <p>
              A room is the host&apos;s folder, seen from somebody else&apos;s
              editor. Four things are true of every one.
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
              <strong>share a link, come edit my code with me.</strong> In
              order, it is four moves.
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
            <h2>Collaboration never had its LSP</h2>
            <p>
              Language tooling has the Language Server Protocol and debugging
              has the Debug Adapter Protocol. Document sync has{" "}
              <code>y-protocols</code> and the CRDT libraries beneath it. The
              session layer &mdash; which rooms exist, who is in one, what their
              role is, which documents are open, where their carets are, what
              happens when somebody leaves &mdash; has never been written down,
              so every collaborative tool invents it again and none of the
              inventions can talk to each other.
            </p>
            <p>
              The specification is Selvage&apos;s flagship artifact: that layer,
              written out as prose, a canonical byte form for a frame, JSON Schema
              documents, and 28 conformance vectors &mdash; 34766 frame checks and
              8617 assertions &mdash; replayed byte for byte against a real server.
              The numbers are constants in <code>schema/validate.py</code>, so
              deleting an assertion is a red run rather than smaller totals in a
              line of output.
            </p>
            <p>
              The vectors are also the honest test of the whole idea: nothing
              yet shows that code written from the prose alone agrees with this
              implementation byte for byte, and a corpus you can replay is what
              would settle it.
            </p>
            <p>
              <a href="https://github.com/selvage-protocol/specification">
                Read the specification
              </a>{" "}
              &mdash; it is written to be implemented on its own, without
              reading the Rust.
            </p>
          </section>

          <section id="run-it" className="scroll-mt-28 md:scroll-mt-24">
            <h2>Run it</h2>
            <p>
              No package to install from a store and no image to pull, so every
              route in starts with a checkout. The server is one binary:
            </p>
            <pre>
              <code>
                {
                  "git clone https://github.com/selvage-protocol/reference_server\ncd reference_server\ncargo run -p selvaged -- --listen 127.0.0.1:8080"
                }
              </code>
            </pre>
            <p>
              Then open a folder in one editor and host a session against{" "}
              <code>ws://127.0.0.1:8080</code>. Both clients are built from
              their own checkouts: the VS Code client with{" "}
              <code>npm ci</code> and <code>npm run package</code>, its{" "}
              <code>.vsix</code> installed by hand, and the Neovim client by
              pointing a plugin manager at the clone (
              <code>{"{ dir = '/path/to/nvim_client' }"}</code> in lazy.nvim).
            </p>
            <details className="quickstart">
              <summary>
                The long version: the spec route, the vector replay, and both
                editors in one room
              </summary>
              <div className="quickstart-body">
                <h3>Read the specification</h3>
                <p>
                  <a href="https://github.com/selvage-protocol/specification">
                    selvage-protocol/specification
                  </a>{" "}
                  holds the prose, the canonical byte form, the JSON Schema
                  documents, the 28 wire vectors, a language-neutral replay of
                  those vectors in Python, and <code>NOTES.md</code>, which says
                  what the prose deliberately leaves open.
                </p>
                <pre>
                  <code>
                    {
                      "git clone https://github.com/selvage-protocol/specification\ncd specification\npip install jsonschema referencing\npython3 schema/validate.py"
                    }
                  </code>
                </pre>
                <p>
                  The validator checks every frame of every vector against the
                  schemas and against the canonical form, and pins the size of
                  the corpus, so a dropped assertion fails the run instead of
                  quietly shrinking a total.
                </p>

                <h3>Replay the vectors against a server</h3>
                <p>
                  The same transcripts replayed against a real{" "}
                  <code>selvaged</code> over a WebSocket, with no Rust in the
                  comparison: <code>runner/run_vectors.py</code> reads the
                  vectors, starts a server of its own on an ephemeral port, and
                  compares what comes back byte for byte.
                </p>
                <pre>
                  <code>
                    {
                      "git clone https://github.com/selvage-protocol/reference_server\ngit clone https://github.com/selvage-protocol/specification\ncd reference_server\ncargo build -p selvaged\nexport SELVAGE_SELVAGED=$PWD/target/debug/selvaged\ncd ../specification\npip install websockets jsonschema referencing\npython3 runner/run_vectors.py"
                    }
                  </code>
                </pre>
                <p>
                  <code>selvaged</code> serves <code>ws://&hellip;/session</code>{" "}
                  and <code>http://&hellip;/meta</code>, and keeps nothing on
                  disk. Running it is the documented way to stand up a server:
                  there is no image to pull and no service unit to install in
                  any repository yet.
                </p>

                <h3>Two editors in one room</h3>
                <p>
                  Start a server to host on, then build the client you want to
                  host from:
                </p>
                <pre>
                  <code>
                    {
                      "git clone https://github.com/selvage-protocol/vscode_client\ncd vscode_client\nnpm ci --no-audit --no-fund\nnpm run package\ncode --install-extension selvage-client-<version>.vsix"
                    }
                  </code>
                </pre>
                <p>
                  Open a folder in one window, run{" "}
                  <em>Selvage: Host a session</em> from the command palette, and
                  give it the server address plus a display name. Open a file
                  inside that folder: it joins the room as soon as it is open.
                  Run <em>Selvage: Copy the invite link</em>, and in a second
                  window &mdash; of the same editor or the other one &mdash; run{" "}
                  <em>Selvage: Join a session from an invite link</em> and paste
                  it. The host&apos;s file opens in the guest as{" "}
                  <code>selvage:/&lt;path&gt;</code> and both windows type into
                  the same text.
                </p>
                <p>
                  The Neovim client mirrors the granted folder into a real
                  directory of its own, so ripgrep, ctags and a language server
                  see ordinary paths, and it keeps its engine in a companion
                  process:
                </p>
                <pre>
                  <code>
                    {
                      "git clone https://github.com/selvage-protocol/nvim_client\ncd nvim_client\nnpm ci --no-audit --no-fund"
                    }
                  </code>
                </pre>
                <p>
                  Point a plugin manager at the checkout, then use{" "}
                  <code>:SelvageHost ws://127.0.0.1:8080</code>,{" "}
                  <code>:SelvageCopyInvite</code> and <code>:SelvageJoin</code>.
                </p>
              </div>
            </details>
          </section>

          <section id="status" className="scroll-mt-28 md:scroll-mt-24">
            <h2>What is built, and what is not</h2>
            <div className="ledger">
              <div>
                <h3 className="ledger-head">Built today</h3>
                <ul className="ledger-list">
                  {built.map((item, index) => (
                    <li key={index}>{item}</li>
                  ))}
                </ul>
              </div>
              <div>
                <h3 className="ledger-head">Not yet</h3>
                <ul className="ledger-list">
                  {notYet.map((item, index) => (
                    <li key={index}>{item}</li>
                  ))}
                </ul>
              </div>
            </div>
          </section>
        </div>
      </main>

      <footer className="page-foot mx-auto w-full max-w-6xl px-5 pb-20">
        <div className="foot-grid">
          <div>
            <h2>Licences</h2>
            <p>
              The specification &mdash; prose, canonical form, JSON Schema and
              vectors &mdash; is CC-BY-4.0, and its tooling is MIT OR
              Apache-2.0. The reference server and the clients are MIT OR
              Apache-2.0, with one exception that matters: the server binary{" "}
              <code>selvaged</code> is <strong>FSL-1.1-MIT</strong>. That is
              source-available, not OSI-approved: free for any non-competing
              purpose, converting to MIT two years after each release, with a
              non-compete clause that reserves exactly the thing a hosted
              Selvage would be.
            </p>
            <p>
              This page prerenders to static HTML with one stylesheet and a
              favicon, and the served document includes the framework&apos;s
              runtime scripts. It sets no cookie, makes no third-party request
              and collects no personal data; the{" "}
              <a href="https://github.com/selvage-protocol">selvage-protocol</a>{" "}
              GitHub organisation is its controller. The page is MIT OR
              Apache-2.0. Its framing follows the project&apos;s own design
              record, which is private and carries no licence; the workflow
              sentence is adapted from the Neovim client&apos;s README, which is
              MIT OR Apache-2.0.
            </p>
          </div>
          <ul className="repos">
            <li>
              <a href="https://github.com/selvage-protocol/specification">
                specification
              </a>{" "}
              &mdash; the protocol, in prose, schema and vectors
            </li>
            <li>
              <a href="https://github.com/selvage-protocol/reference_server">
                reference_server
              </a>{" "}
              &mdash; the server, the client library, the harness
            </li>
            <li>
              <a href="https://github.com/selvage-protocol/vscode_client">
                vscode_client
              </a>{" "}
              &mdash; the VS Code client
            </li>
            <li>
              <a href="https://github.com/selvage-protocol/nvim_client">
                nvim_client
              </a>{" "}
              &mdash; the Neovim client
            </li>
          </ul>
        </div>
      </footer>
    </div>
  );
}
