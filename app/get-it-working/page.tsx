import type { Metadata } from "next";
import type { ReactNode } from "react";
import { ArrowUpRight, Bot, Box, Eye, Play, TerminalSquare } from "lucide-react";
import { SiteHeader } from "@/components/site-header";
import { DEMO_ORIGIN, OPEN_AT, RUN_STEPS, STOP_STEPS } from "@/lib/selvage";
import { CLIENTS, repositoryUrl } from "@/lib/clients";

export const metadata: Metadata = {
  title: "Get it working: run Selvage and open your clients",
  description:
    "One command starts the server, the page and two editors in a room; a compose file runs the published images; and each client joins with the invite link.",
  alternates: { canonical: "/get-it-working" },
  openGraph: {
    title: "Get it working: run Selvage and open your clients",
    description:
      "One command starts the server, the page and two editors in a room; a compose file runs the published images; and each client joins with the invite link.",
    url: "/get-it-working",
    type: "website",
  },
};

function Eyebrow({ children }: { children: ReactNode }) {
  return <p className="eyebrow">{children}</p>;
}

/** The one command, as the checkout spells it: the script is `reference_server`'s. */
const DEMO_COMMAND = "reference_server/scripts/demo/demo.sh";

const MCP_ENTRY = `{
  "mcpServers": {
    "selvage": {
      "command": "node",
      "args": ["<path>/mcp/dist/main.js"],
      "env": {
        "SELVAGE_SERVER_URL": "ws://127.0.0.1:8080",
        "SELVAGE_DISPLAY_NAME": "agent"
      }
    }
  }
}`;

const editorRoutes = CLIENTS.filter((client) => client.install !== undefined);

export default function GetItWorking() {
  return (
    <div className="min-h-screen bg-base font-sans text-text antialiased">
      <SiteHeader />
      <div className="prose-body">
        <main id="top">
          <section className="shell">
            <div className="head-block">
              <Eyebrow>Get it working</Eyebrow>
              <h1 className="display">A room on this machine, and your clients in it.</h1>
              <p className="lede">
                A room needs one server. Everything else — an editor, a browser tab, an
                agent — joins by the invite link that server hands its host.
              </p>
            </div>

            <div className="walkthrough">
              <div className="walkthrough-card">
                <p className="panel-head">
                  <TerminalSquare className="panel-icon-peach" aria-hidden="true" />
                  From a checkout, one command
                </p>
                <pre className="command-block">
                  <code>{DEMO_COMMAND}</code>
                </pre>
                <p className="panel-body">
                  It builds what is missing, starts <code>selvaged</code> serving the
                  browser page from the same origin, opens two Neovim windows — one
                  hosting, one joined — opens the page, and prints the invite and the MCP
                  entry an agent joins by. The shared folder is a copy, so the checkout is
                  left alone; <code>--keep</code> keeps that copy and the logs for a look.
                </p>
                <p className="panel-body">
                  <code>--agent</code> adds an MCP agent seat to the same room,{" "}
                  <code>--port</code> moves the server off 8080.
                </p>
              </div>

              <div className="walkthrough-card">
                <p className="panel-head">
                  <Box className="panel-icon-peach" aria-hidden="true" />
                  Or the two published images
                </p>
                <p className="panel-body">
                  The server and the page are published containers. Compose runs the pair,
                  and the browser editor is then one origin: <code>{OPEN_AT}</code>.
                </p>
                <pre className="command-block">
                  <code>cd reference_server &amp;&amp; docker compose up</code>
                </pre>
                <p className="panel-body">
                  The same pair as three commands, with the images named:
                </p>
                <ol className="run-steps">
                  {RUN_STEPS.map((step) => (
                    <li key={step.label}>
                      <span className="run-step-label">{step.label}</span>
                      <pre className="command-block">
                        <code>{step.command}</code>
                      </pre>
                    </li>
                  ))}
                </ol>
                <p className="panel-body run-note">
                  Rooms are held in memory: one ends when its host leaves, and nothing is
                  written down. Stopping the pair is <code>docker compose down</code>, or
                  the two commands the landing page prints:{" "}
                  {STOP_STEPS.map((step) => step.command).join(" and ")}.
                </p>
              </div>
            </div>
          </section>

          <section id="recording" className="band">
            <div className="shell">
              <div className="head-block">
                <Eyebrow>See it</Eyebrow>
                <h2 className="display">
                  Two editors, a browser tab and an agent, one file.
                </h2>
                <p className="lede">
                  Recorded from one run of the command above: Ada hosts from Neovim, Grace
                  joins from the invite link, both type in the same file at once, the page
                  joins as a third seat, and an MCP agent reads and edits that file through
                  its own server.
                </p>
              </div>
              <figure className="recording">
                <video
                  className="recording-video"
                  controls
                  preload="metadata"
                  width={1920}
                  height={1080}
                  aria-label="Two Neovim windows, a browser tab and an agent editing one file in one room"
                >
                  <source src="/selvage-demo.mp4" type="video/mp4" />
                  The recording is a silent MP4 of the demo run.
                </video>
                <figcaption>
                  Every frame is a client against a real <code>selvaged</code>: the edits
                  are typed, the agent&apos;s are <code>tools/call</code> messages, and the
                  only drawn-on parts are the captions.
                </figcaption>
              </figure>
            </div>
          </section>

          <section className="shell shell-end">
            <div className="head-block">
              <Eyebrow>Clients</Eyebrow>
              <h2 className="display">Install the editor you have, then join.</h2>
              <p className="lede">
                Every one of these is a client and not a server: each joins a{" "}
                <code>selvaged</code> you run. A host shares a folder or a buffer, and every
                other seat joins with the invite link — the link is the whole permission.
              </p>
            </div>
            <ul className="routes">
              {editorRoutes.map((client) => (
                <li key={client.id} data-client={client.id}>
                  <p className="route-head">
                    <client.Icon className="icon-18" aria-hidden="true" />
                    <span className="route-name">{client.chip}</span>
                    <a className="route-repo" href={repositoryUrl(client.repository)}>
                      {client.repository}
                      <ArrowUpRight className="icon-14" aria-hidden="true" />
                    </a>
                  </p>
                  <pre className="command-block">
                    <code>{client.install?.copy}</code>
                  </pre>
                  <p className="panel-body run-note">{client.install?.note}</p>
                </li>
              ))}
              <li data-client="mcp">
                <p className="route-head">
                  <Bot className="icon-18" aria-hidden="true" />
                  <span className="route-name">AI agent, over MCP</span>
                  <a className="route-repo" href={repositoryUrl("mcp")}>
                    mcp
                    <ArrowUpRight className="icon-14" aria-hidden="true" />
                  </a>
                </p>
                <pre className="command-block">
                  <code>{MCP_ENTRY}</code>
                </pre>
                <p className="panel-body run-note">
                  An agent&apos;s own host starts this server over stdio. It reads, edits
                  and writes the files the room shares, and <code>wait_for_change</code>{" "}
                  tells it when a person edits.
                </p>
              </li>
            </ul>
          </section>

          <section className="band">
            <div className="shell">
              <div className="head-block">
                <Eyebrow>Before you invite anyone</Eyebrow>
                <h2 className="display">What the server still sees.</h2>
              </div>
              <div className="walkthrough">
                <div className="walkthrough-card">
                  <p className="panel-head">
                    <Eye className="panel-icon-peach" aria-hidden="true" />
                    The relay, and its limits
                  </p>
                  <p className="panel-body">
                    The relay still sees that a room exists, who is in it and their names,
                    and the sizes and timing of what moves.
                  </p>
                  <p className="panel-body">
                    Document text, cursors, file names and roles are sealed. The server can
                    still drop, delay or end a room, and the host is a peer&apos;s signed
                    claim: it cannot seat a host, prove one, or take the role.
                  </p>
                </div>
                <div className="walkthrough-card">
                  <p className="panel-head">
                    <Play className="panel-icon-peach" aria-hidden="true" />
                    A room is not a file store
                  </p>
                  <p className="panel-body">
                    Nothing on the wire adds, renames or deletes a path, and the server
                    keeps nothing: a room lives in memory and ends when its host leaves.
                    Anyone holding the invite can edit the shared buffer, so hand it on the
                    way you would hand on a password.
                  </p>
                  <p className="panel-body">
                    <a className="spec-link" href={DEMO_ORIGIN}>
                      Open the demo instance instead
                      <ArrowUpRight className="icon-14" aria-hidden="true" />
                    </a>
                  </p>
                </div>
              </div>
            </div>
          </section>
        </main>

        <footer className="band">
          <div className="shell foot-grid">
            <div className="foot-col">
              <h3 className="foot-h">Licences</h3>
              <p className="foot-note">
                Specification CC-BY-4.0; tooling and clients MIT OR Apache-2.0. The
                specification&apos;s conformance vectors are replayed by{" "}
                <code>specification/schema/validate.py</code>.{" "}
                <code>selvaged</code> is FSL-1.1-MIT: source-available, not OSI-approved,
                free for any non-competing purpose, and it converts to MIT two years after
                each release.
              </p>
            </div>
            <div className="foot-col">
              <h3 className="foot-h">This page</h3>
              <p className="foot-note">
                No cookies, no tracking, no third-party request. <a href="/">The landing
                page</a> has the rest.
              </p>
            </div>
            <div className="foot-col">
              <h3 className="foot-h">Contact</h3>
              <p className="foot-note">
                <a href="mailto:selvage@dontblameme.dev">selvage@dontblameme.dev</a>
              </p>
            </div>
          </div>
        </footer>
      </div>
    </div>
  );
}
