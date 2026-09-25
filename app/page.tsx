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

// One word each. The hero carried the four as full sentences, and three of them are argued
// anyway below — the sealed relay in the paragraph under the `docker run`, the specification in
// its own section, the granted paths in the third card — while `No account` is a fact the page
// states nowhere else, which is why the row stays a row.
const heroFacts = ["Sealed", "Specified", "Path-scoped", "No account"];

const roomCards = [
  {
    lead: "Anyone with the link is in",
    body: (
      <>
        Hold the link and you are in, with no approval step. Treat an invite the way
        you would treat a password.
      </>
    ),
    figure: <InviteCard />,
  },
  {
    lead: "Two carets, one text",
    body: (
      <>
        Everyone&apos;s edits land in the one CRDT, and carets and selections travel
        as anchors inside it, so a peer&apos;s caret stays where it was while the
        text around it moves.
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
        of the same engine, so a room&apos;s rules live in one implementation.
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
        from there. The host lists the paths inside that folder and sends the
        listing.
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
        Closing the host&apos;s window ends the room: whoever is in it keeps editing
        while a short countdown runs, and then each client&apos;s session ends. A
        dropped connection does not end a room: it lives while it has connections
        and for a short grace period after its last one. Rooms live in memory, so
        nothing survives a restart of the server.
      </>
    ),
  },
];

/** The invite, at card weight: the same chip the hero figure carries, minus the copy glyph
    (there is nothing to copy here) and the label (the lead under it names the link). */
function InviteCard() {
  return (
    <div className="fig fig-invite">
      <span className="invite">
        <span className="invite-url">
          ?room=k7m2&amp;token=4f9c#k=&hellip;&amp;h=&hellip;
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
                VS Code, Neovim and the browser join the same file, with no
                third party&apos;s cloud holding the room.
              </p>
              {/* Two actions, and both of them are actions: the demo needs nothing
                  installed and the editor is the other way in. The specification is a
                  link in the body below, where a reader who wants the manual goes. */}
              <div className="mt-9 flex flex-wrap items-center gap-3">
                <Button href="https://selvage-demo.dontblameme.dev" size="lg">
                  Try the demo in your browser
                </Button>
                <Button href="#get-it-working" variant="secondary" size="lg">
                  Run it in your editor
                </Button>
              </div>
              <ul className="mt-8 flex max-w-[35rem] flex-wrap items-center gap-x-5 gap-y-3">
                {heroFacts.map((fact) => (
                  <li key={fact} className="flex items-center gap-2.5">
                    <span className="inline-flex h-5 w-5 shrink-0 items-center justify-center rounded-full bg-mauve/15">
                      <Check
                        className="h-3.5 w-3.5 text-mauve"
                        strokeWidth={3}
                        aria-hidden="true"
                      />
                    </span>
                    <span className="text-[15px] font-medium text-text">
                      {fact}
                    </span>
                  </li>
                ))}
              </ul>
              <p className="mt-6 font-mono text-[12px] text-subtext">
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
              One server holds the room, and the invite link your editor copies is
              how somebody joins you. The published image is one command:
            </p>
            <pre>
              <code>
                {
                  "docker run --rm -p 127.0.0.1:8080:8080 ghcr.io/selvage-protocol/selvaged:0.4.3"
                }
              </code>
            </pre>
            <p>
              The server answers <code>ws://127.0.0.1:8080/session</code> and serves
              the page on the same port. Rooms live in memory, so a restart ends
              them.
            </p>
            <p>
              The image and the demo speak <code>selvage/2</code>, the one wire
              version this protocol has, and it is the sealed one.
            </p>
            <p>
              The server carries bytes it cannot read: documents, cursors, the file
              listing and the roles the host signs travel sealed under keys in the
              part of the invite link a browser never sends to a server. It still
              sees that a room exists, who is in it, their names, and the sizes and
              timing of what moves, and it can drop, delay or end a room. The host is
              a peer&apos;s signed claim: the server cannot seat a host, prove one,
              or take the role.
            </p>

            <h3>Run it in an editor</h3>
            <p>
              VS Code installs it with{" "}
              <code>code --install-extension selvage-protocol.selvage</code>: the
              extension is published on the VS Code Marketplace and on Open VSX (
              <a href="https://github.com/selvage-protocol/vscode_client">source</a>
              ). An install is the client and not a server: a session pairs with the{" "}
              <code>selvaged</code> you run. Then <em>Selvage: Host a session</em>.
            </p>
            <p>
              Neovim: add{" "}
              <code>{`{ 'selvage-protocol/nvim_client', build = 'npm ci' }`}</code> to
              your plugin manager (
              <a href="https://github.com/selvage-protocol/nvim_client">source</a>
              ), then <code>:SelvageHost ws://127.0.0.1:8080</code> shares the current
              buffer and copies the invite.
            </p>

            <h3>Try the demo</h3>
            <p>
              A small instance of the server runs at{" "}
              <a href="https://selvage-demo.dontblameme.dev">
                selvage-demo.dontblameme.dev
              </a>
              . Point an editor at{" "}
              <code>wss://selvage-demo.dontblameme.dev</code> and it hosts a room
              there; the invite link it copies opens in the page, so a guest needs
              nothing installed. On Chrome or Edge the page can start its own room
              from a folder you pick.
            </p>
            <p>
              A guest who opens the page the room&apos;s own server serves trusts
              that server for the client code as well as for the relay; the installed
              clients are not in that position.
            </p>
            <p>
              The instance&apos;s rooms live in memory, so a restart ends every one of
              them, and it is non-commercial and for personal and evaluation use: its{" "}
              <a href="https://selvage-demo.dontblameme.dev/terms">terms</a> cover that
              one box, and the licences below cover the software.
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
            <h2>The session layer is written down</h2>
            <p>
              Language tooling has the Language Server Protocol and debugging has
              the Debug Adapter Protocol. Document sync has{" "}
              <code>y-protocols</code>. Which rooms exist, who is in one, which
              documents are open, where the carets are: every collaborative tool
              decides those for itself, so none of the tools can talk to each other.
            </p>
            <p>
              Selvage writes that layer down: prose, a canonical byte form for a
              frame, JSON Schema, and 24 conformance vectors (33760 frame checks and
              8387 assertions) replayed byte for byte against a real server. The
              numbers are constants in <code>schema/validate.py</code>.
            </p>
            <p>
              <a href="https://github.com/selvage-protocol/specification">
                Read the specification
              </a>
              . It is written to be implemented on its own, without reading the
              server&apos;s code.
            </p>
          </section>
        </div>
      </main>

      <footer className="prose-body page-foot mx-auto w-full max-w-6xl px-5 pb-20">
        <div>
          <h2>Licences</h2>
          <p>
            The specification (prose, canonical form, JSON Schema and vectors) is
            CC-BY-4.0, and its tooling is MIT OR Apache-2.0. The reference server and
            the clients are MIT OR Apache-2.0, with one exception: the server binary{" "}
            <code>selvaged</code> is <strong>FSL-1.1-MIT</strong>, which is
            source-available and not OSI-approved. It is free for any non-competing
            purpose, converts to MIT two years after each release, and carries a
            non-compete clause that reserves commercial hosting for its licensor.
          </p>
          <p>
            This page prerenders to static HTML: one stylesheet, the mark in its
            header, the favicon set and the framework&apos;s runtime scripts, every one
            of them from this origin. It sets no cookie, makes no third-party request
            and collects no personal data of its own; the{" "}
            <a href="https://github.com/selvage-protocol">selvage-protocol</a> GitHub
            organisation is its controller.
          </p>
          <p>
            Write to{" "}
            <a href="mailto:selvage@dontblameme.dev">
              selvage@dontblameme.dev
            </a>{" "}
            about the project or a security problem in it. A message is the only thing
            here that carries your own address back; the controller receives it and
            keeps it only to answer. This page is MIT OR Apache-2.0.
          </p>
        </div>
      </footer>
    </div>
  );
}
