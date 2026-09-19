import { ArrowUpRight, Check } from "lucide-react";
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
    Guests see the paths you grant and edit the room&apos;s text. Nothing writes to
    your folder, and the room ends when you leave.
  </>,
  <>
    There is no account on either side. Rooms live in memory on the server you host,
    and nothing is written to disk.
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
        implementation. The browser page is guests-only, and served over the
        project&apos;s own private network.
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
        from the command palette. The client lists the paths inside that folder and
        sends the listing.
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
        The room dies with its host after a short grace period, so a dropped
        connection does not end it. Rooms live in memory: nothing survives a restart
        of the server.
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
              <p className="mt-4 font-mono text-[12px] text-subtext">
                The specification is a draft, and the wire version is{" "}
                <code>selvage/1</code>.
              </p>
            </div>

            <RoomWindow />
          </div>
        </section>

        <div className="prose-body mx-auto w-full max-w-6xl px-5 pb-14">
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
              The specification is Selvage&apos;s flagship artifact: that layer,
              written out as prose, a canonical byte form for a frame, JSON Schema
              documents, and 31 conformance vectors (34858 frame checks and 8642
              assertions) replayed byte for byte against a real server. The numbers
              are constants in <code>schema/validate.py</code>, so deleting an
              assertion fails the run instead of shrinking a total in a line of
              output.
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
          </section>

          <section id="run-it" className="scroll-mt-28 md:scroll-mt-24">
            <h2>Run it</h2>
            <p>
              You run the server, and the invite link is how somebody joins you.
              There is nothing hosted to open, so every route in starts with a
              checkout. The server is one binary:
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
              <code>ws://127.0.0.1:8080</code>. Each client is built from its own
              checkout: the VS Code client with <code>npm ci</code> and{" "}
              <code>npm run package</code>, its <code>.vsix</code> installed by
              hand, and the Neovim client by pointing a plugin manager at the clone
              (
              <code>{"{ dir = '/path/to/nvim_client' }"}</code> in lazy.nvim).
            </p>
            <details className="quickstart">
              <summary>
                The long version: the spec route, the vector replay, and two
                editors in one room
              </summary>
              <div className="quickstart-body">
                <h3>Read the specification</h3>
                <p>
                  <a href="https://github.com/selvage-protocol/specification">
                    selvage-protocol/specification
                  </a>{" "}
                  holds the prose, the canonical byte form, the JSON Schema
                  documents, the 31 wire vectors, a Python replay of those vectors,
                  and <code>NOTES.md</code>, which says what the prose deliberately
                  leaves open.
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
                  schemas and against the canonical form, and pins the size of the
                  corpus, so a dropped assertion fails the run instead of shrinking
                  a total.
                </p>

                <h3>Replay the vectors against a server</h3>
                <p>
                  <code>runner/run_vectors.py</code> replays the same transcripts
                  against a real <code>selvaged</code> over a WebSocket, with no
                  Rust in the comparison: it reads the vectors, starts a server of
                  its own on an ephemeral port, and compares what comes back byte
                  for byte.
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
                  there is no image to pull and no service unit to install in any
                  repository yet.
                </p>

                <h3>Two editors in one room</h3>
                <p>
                  Start a server to host on, then build the client you want to host
                  from:
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
                  inside that folder: it joins the room as soon as it is open. Run{" "}
                  <em>Selvage: Copy the invite link</em>, open a second window in
                  the same editor or in the other one, and run{" "}
                  <em>Selvage: Join a session from an invite link</em> with the
                  link pasted in. The host&apos;s file opens in the guest as{" "}
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

        </div>
      </main>

      <footer className="page-foot mx-auto w-full max-w-6xl px-5 pb-20">
        <div className="foot-grid">
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
              (the protocol, in prose, schema and vectors)
            </li>
            <li>
              <a href="https://github.com/selvage-protocol/reference_server">
                reference_server
              </a>{" "}
              (the server, the client library, the harness)
            </li>
            <li>
              <a href="https://github.com/selvage-protocol/vscode_client">
                vscode_client
              </a>{" "}
              (the VS Code client)
            </li>
            <li>
              <a href="https://github.com/selvage-protocol/nvim_client">
                nvim_client
              </a>{" "}
              (the Neovim client)
            </li>
          </ul>
        </div>
      </footer>
    </div>
  );
}
