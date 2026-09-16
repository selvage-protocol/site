import { ArrowUpRight, Check } from "lucide-react";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { SiteHeader } from "@/components/site-header";

const checklist = [
  "One Rust binary holds the room \u2014 in memory only, nothing on disk.",
  "The invite is the share \u2014 the token is the permission, with no approval step.",
  "Prose, nine schemas and 23 vectors \u2014 replayed byte for byte against a real server.",
];

export default function Home() {
  return (
    <div className="min-h-screen bg-base font-sans text-text antialiased">
      <SiteHeader />

      <main id="top">
        <section className="mx-auto w-full max-w-6xl px-5 pb-16 pt-14 md:pb-24 md:pt-20">
          <div className="grid items-center gap-12 lg:grid-cols-2 lg:gap-10">
            <div>
              <Badge>
                <span
                  aria-hidden="true"
                  className="inline-block h-1.5 w-1.5 rounded-full bg-mauve"
                />
                Selvage Session Protocol &middot; wire selvage/1 &middot;
                specification draft
              </Badge>
              <h1 className="mt-6 text-4xl font-bold leading-[1.08] tracking-tight text-text md:text-[3.4rem]">
                Your server, your code.
                <br />
                Share a link, come edit with me.
              </h1>
              <p className="mt-6 max-w-xl text-lg leading-relaxed text-subtext">
                Selvage Session Protocol is a written specification for the
                session layer of collaborative editing &mdash; rooms,
                participants, open documents, presence. You run the server,
                you send the link &mdash; no account, no third party&apos;s cloud holding the room.
              </p>
              <ul className="mt-8 space-y-3.5">
                {checklist.map((item) => (
                  <li key={item} className="flex items-start gap-3">
                    <span className="mt-0.5 inline-flex h-5 w-5 shrink-0 items-center justify-center rounded-full bg-mauve/15">
                      <Check
                        className="h-3.5 w-3.5 text-mauve"
                        strokeWidth={3}
                      />
                    </span>
                    <span className="text-[15px] leading-relaxed text-text">
                      {item}
                    </span>
                  </li>
                ))}
              </ul>
              <div className="mt-9 flex flex-wrap items-center gap-3">
                <Button
                  href="https://github.com/selvage-protocol/specification"
                  size="lg"
                >
                  Read the spec
                  <ArrowUpRight />
                </Button>
                <Button href="#run-it" variant="secondary" size="lg">
                  Run it today
                </Button>
              </div>
            </div>

            {/* Abstract panel, not a product capture: a mauve glow field with the
                site mark and one card carrying the project's own sentences. */}
            <div aria-hidden="true" className="hero-visual min-h-[420px] p-6 md:min-h-[480px] md:p-8">
              <div className="hero-visual-grain" />
              <div className="relative flex h-full min-h-[372px] flex-col md:min-h-[416px]">
                <img
                  className="h-14 w-auto self-start rounded-lg"
                  src="/mark-opaque.png"
                  alt=""
                  width={800}
                  height={800}
                />
                <Card className="hero-glass mt-auto w-full max-w-md self-end border-mauve/30 bg-mantle/80">
                  <div className="flex items-center gap-1.5 border-b border-surface0/70 px-5 pb-3 pt-4">
                    <span className="h-2.5 w-2.5 rounded-full bg-surface0" />
                    <span className="h-2.5 w-2.5 rounded-full bg-surface0" />
                    <span className="h-2.5 w-2.5 rounded-full bg-surface0" />
                    <span className="ml-2 font-mono text-xs text-subtext">
                      selvage:/&lt;path&gt;
                    </span>
                  </div>
                  <div className="space-y-2.5 px-5 py-4">
                    <p className="font-mono text-[13px] leading-relaxed text-text">
                      share a link, come edit my code with me.
                    </p>
                    <p className="font-mono text-[13px] leading-relaxed text-subtext">
                      paths, never content.
                    </p>
                    <p className="font-mono text-[13px] leading-relaxed text-subtext">
                      the room ends when the host leaves.
                    </p>
                  </div>
                </Card>
              </div>
            </div>
          </div>
        </section>

        <div className="prose-body mx-auto w-full max-w-3xl px-5 pb-4">
          <section id="who-its-for" className="scroll-mt-24">
            <h2>Who this is for</h2>
            <p>
              <strong>Two developers pairing.</strong> One of you hosts a folder in VS Code; the other pastes an
              invite link and the folder&apos;s shape appears. Open the same file and both of you
              type into the same text &mdash; built so either editor can join the same room.
            </p>
            <p>
              <strong>A team that wants its own server.</strong> Rooms live in one Rust binary you run yourself
              &mdash; in memory only, nothing written to disk &mdash; so the machine the room passes
              through is one you chose. No account on either end, and no third party&apos;s cloud
              holding the room.
            </p>
            <p>
              <strong>Tooling people who want the session layer written down.</strong> The specification is prose, a
              canonical byte form, nine JSON Schema 2020-12 documents, 23 wire vectors, and a runner
              that replays them byte for byte against a real server &mdash; written to be implemented
              on its own, without reading the Rust.
            </p>
          </section>

          <section id="session" className="scroll-mt-24">
            <h2>Your server, your code</h2>
            <p>
              Selvage is the project: the specification, a reference server you run yourself, and
              clients for VS Code and Neovim. The server is one Rust binary that holds rooms in memory
              &mdash; no account, no database, no cloud. The workflow it serves is one sentence:{" "}
              <strong>share a link, come edit my code with me.</strong> The host&apos;s working copy
              is the truth, the invite is the share, and the room ends when the host leaves.
            </p>
          </section>

          <section>
            <h2>How a session feels, minute to minute</h2>
            <ol>
            <li>
              The host grants a folder. The client lists the paths inside it and puts the listing on
              the wire &mdash; paths, never content &mdash; and the guest mirrors that shape. A
              file&apos;s text arrives when someone opens it, and the host reads that one file from
              its own disk when a peer asks for it, inside the granted root.
            </li>
            <li>
              Everyone holding the invite edits the same document. The token is the permission: there
              is no account and no per-join approval, and anyone with the link is in the room, so
              treat an invite as you would a password.
            </li>
            <li>
              The host&apos;s filesystem is the scoped part
              &mdash; no guest writes to the host&apos;s working copy &mdash; while the room&apos;s
              text belongs to everyone in it: every participant&apos;s edits land in the one CRDT,
              which is what &quot;come edit my code with me&quot; means. Other people&apos;s carets
              and selections travel as anchors in that same CRDT, so they stay where they were as the
              text around them moves.
            </li>
            <li>
              A file nobody has opened sends no text yet &mdash; only the listing did &mdash; so
              looking at one file never moves the whole project over the wire.
            </li>
            <li>
              The room ends when the host leaves. Rooms live in memory only, the server writes nothing
              to disk, and a room dies with its host after a short grace period, so a dropped
              connection does not end it.
            </li>
            </ol>
          </section>

          <section id="run-it" className="scroll-mt-24">
            <h2>Run it today</h2>
            <p>
              There is no hosted demo, no release and no package to install from an extension store,
              so every route below starts with a clone.
            </p>

            <h3>Read the specification</h3>
            <p>
              <a href="https://github.com/selvage-protocol/specification">
                selvage-protocol/specification
              </a>{" "}
              holds the prose (<code>PROTOCOL.md</code>), the canonical byte form of a frame (
              <code>CANONICAL.md</code>), nine JSON Schema 2020-12 documents, 23 wire vectors, a
              language-neutral replay of those vectors in Python, and <code>NOTES.md</code>, which
              says what the prose deliberately leaves open &mdash; written to be implemented on its
              own, without reading the Rust.
            </p>
            <pre><code>{"git clone https://github.com/selvage-protocol/specification\ncd specification\npip install jsonschema referencing\npython3 schema/validate.py"}</code></pre>
            <p>
              The validator checks every frame of every vector against the schemas and against the
              canonical form, and pins the size of the corpus:{" "}
              <strong>23 vectors, 806 frame checks and 192 assertions</strong>. The numbers are
              constants in <code>schema/validate.py</code>, so deleting an assertion is a red run
              rather than smaller totals in a line of output.
            </p>

            <h3>Replay the vectors against a server</h3>
            <p>
              The same transcripts replayed against a real <code>selvaged</code> over a WebSocket,
              with no Rust in the comparison: <code>runner/run_vectors.py</code> reads the vectors,
              starts a server of its own on an ephemeral port, and compares what comes back byte for
              byte. It needs a built <code>selvaged</code>, named by{" "}
              <code>SELVAGE_SELVAGED</code>.
            </p>
            <pre><code>{"git clone https://github.com/selvage-protocol/reference_server\ngit clone https://github.com/selvage-protocol/specification\ncd reference_server\ncargo build -p selvaged\nexport SELVAGE_SELVAGED=$PWD/target/debug/selvaged\ncd ../specification\npip install websockets jsonschema referencing\npython3 runner/run_vectors.py"}</code></pre>
            <p>
              <code>selvaged</code> serves <code>ws://&hellip;/session</code> and{" "}
              <code>http://&hellip;/meta</code>, and keeps nothing on disk. Running it is the
              documented way to stand up a server: there is no image to pull and no service unit to
              install in any repository yet.
            </p>

            <h3>Two editors in one room</h3>
            <p>
              Start a server to host on, then build the VS Code client from its checkout and install
              the packaged extension by hand:
            </p>
            <pre><code>{"git clone https://github.com/selvage-protocol/reference_server\ncd reference_server\ncargo run -p selvaged -- --listen 127.0.0.1:8080"}</code></pre>
            <pre><code>{"git clone https://github.com/selvage-protocol/vscode_client\ncd vscode_client\nnpm ci --no-audit --no-fund\nnpm run package\ncode --install-extension selvage-client-<version>.vsix"}</code></pre>
            <p>
              Open a folder in one window, run <em>Selvage: Host a session</em> from the command
              palette, and give it the server address (<code>ws://127.0.0.1:8080</code>) plus a
              display name. Open a file inside that folder: it joins the room as soon as it is open.
              Run <em>Selvage: Copy the invite link</em>, and in a second window &mdash; of the same
              editor or a different machine &mdash; run{" "}
              <em>Selvage: Join a session from an invite link</em> and paste it. The host&apos;s file
              opens in the guest as <code>selvage:/&lt;path&gt;</code> and both windows type into the
              same text. Closing the host&apos;s window ends the room.
            </p>
            <p>
              The Neovim client is the same room, from the other editor. It keeps its engine and
              bridge in a companion Node process, and mirrors the granted folder into a real
              directory, so ripgrep, ctags and a language server see ordinary paths:
            </p>
            <pre><code>{"git clone https://github.com/selvage-protocol/nvim_client\ncd nvim_client\nnpm ci --no-audit --no-fund"}</code></pre>
            <p>
              Point a plugin manager at the checkout (
              <code>{"{ dir = '/path/to/nvim_client' }"}</code> in lazy.nvim), then use{" "}
              <code>:SelvageHost ws://127.0.0.1:8080</code>, <code>:SelvageCopyInvite</code> and{" "}
              <code>:SelvageJoin</code>.
            </p>
          </section>

          <section id="not-yet" className="scroll-mt-24">
            <h2>What this is not yet</h2>
            <ul>
              <li>
                <strong>No hosted demo.</strong> There is no server of ours on the internet, so there
                is no demo link &mdash; the way in is a checkout and <code>cargo run</code>.
              </li>
              <li>
                <strong>No released version.</strong> The wire version is <code>selvage/1</code>, and
                the compatibility rule in force for it is the same major: every{" "}
                <code>selvage/1.x</code> is accepted. The specification is a draft and nothing has
                been released.
              </li>
              <li>
                <strong>Two editors, one engine.</strong> The VS Code and Neovim clients drive the
                same CRDT engine, so nothing here yet shows that a client built from the prose alone
                would agree byte for byte with this one. That is what the vectors are for, and that
                test has not been run against a separate codebase.
              </li>
              <li>
                <strong>No persistence.</strong> Rooms are held in memory and die with the host;
                nothing survives a restart of the server.
              </li>
              <li>
                <strong>No encryption layer in version 1.</strong> Frames travel through the server as
                unencrypted bytes, and this slice has no transport security either. The server keeps
                no document text &mdash; it knows only which peers are connected and which paths they
                have open &mdash; but it can read a frame as it routes it, so treat the
                server&apos;s operator and the network path as able to see the room&apos;s text.
              </li>
              <li>
                <strong>No changes to the shape of the host&apos;s folder.</strong> The room carries
                no file mutations &mdash; nothing on the wire adds, renames or removes a path &mdash;
                and nothing writes to the host&apos;s working copy. The host&apos;s own editor still
                changes that folder, and a Neovim guest&apos;s mirror materialises the granted paths
                into a directory of its own.
              </li>
              <li>
                <strong>Nothing runs in a web page.</strong> Both clients are editor plugins; there is
                no client to open in a tab and no link that starts an editor by itself.
              </li>
              <li>
                <strong>The specification is a draft.</strong> <code>NOTES.md</code> lists the
                questions the prose leaves open, and the caveats it records are real: the invite
                carries the token in its URL, the host role is claimed rather than proven, and a
                document path is an opaque string the protocol requires only to be non-blank. Holding
                a read inside the granted folder is a rule the clients carry, not one the wire
                enforces. Reading <code>NOTES.md</code> is the point of publishing it.
              </li>
            </ul>
          </section>

          <section id="privacy" className="scroll-mt-24">
            <h2>Privacy notice</h2>
            <p>
              <strong>Controller.</strong> The{" "}
              <a href="https://github.com/selvage-protocol">selvage-protocol</a> GitHub
              organisation is the controller.
              This page collects no personal data: it sets no cookie, makes no
              third-party request, and sends nothing anywhere.
            </p>
          </section>
        </div>
      </main>

      <footer className="prose-body mx-auto w-full max-w-3xl px-5 pb-16 text-[0.9375rem] text-subtext">
        <div className="mt-12 border-t border-surface0 pt-5">
          <h2>Licences</h2>
          <p>
            The specification &mdash; prose, canonical form, JSON Schema and vectors &mdash; is
            CC-BY-4.0, and its tooling is MIT OR Apache-2.0. The reference server workspace and both
            clients are MIT OR Apache-2.0, with one exception that matters: the server binary{" "}
            <code>selvaged</code> is <strong>FSL-1.1-MIT</strong>. That is source-available, not
            OSI-approved: free for any non-competing purpose, converting to MIT two years after each
            release, with a non-compete clause that reserves exactly the thing a hosted Selvage would
            be.
          </p>
          <p>
            This page prerenders to static HTML with one stylesheet and a favicon. The served
            document includes the framework&apos;s runtime scripts; it sets no cookie, makes no
            third-party request, and sends nothing anywhere. The page is MIT OR Apache-2.0. Its framing follows the project&apos;s
            own design record, which is private and carries no licence; the workflow sentence is
            adapted from the Neovim client&apos;s README, which is MIT OR Apache-2.0.
          </p>
          <ul className="repos">
            <li>
              <a href="https://github.com/selvage-protocol/specification">specification</a> &mdash;
              the protocol, in prose, schema and vectors
            </li>
            <li>
              <a href="https://github.com/selvage-protocol/reference_server">reference_server</a>{" "}
              &mdash; the server, the client library, the harness
            </li>
            <li>
              <a href="https://github.com/selvage-protocol/vscode_client">vscode_client</a> &mdash;
              the VS Code client
            </li>
            <li>
              <a href="https://github.com/selvage-protocol/nvim_client">nvim_client</a> &mdash; the
              Neovim client
            </li>
          </ul>
        </div>
      </footer>
    </div>
  );
}
