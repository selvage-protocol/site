import type { ReactNode } from "react";
import type { LucideIcon } from "lucide-react";
import {
  ArrowDown,
  ArrowUpRight,
  BookOpenText,
  Check,
  Eye,
  Globe,
  HardDrive,
  Lock,
  Play,
  Plus,
  SquareTerminal,
} from "lucide-react";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { DemoEndpoint } from "@/components/demo-endpoint";
import { RoomWindow } from "@/components/room-window";
import { SetupTerminal } from "@/components/setup-tabs";
import { SiteHeader } from "@/components/site-header";
import {
  CaretLines,
  ClientChips,
  InviteChip,
  TreeFigure,
} from "@/components/room-visuals";
import { COMMAND, DEMO } from "@/lib/selvage";
import { CLIENTS, repositoryUrl } from "@/lib/clients";

const DEMO_ORIGIN = `https://${DEMO}`;

/** One word each. Three of the four are argued on the page — the sealed relay in the
    panel under the terminal, the specification in its own section, the granted paths
    in the third figure — and `No account` is a fact stated nowhere else, which is
    why the row stays a row. */
const heroFacts = ["Sealed", "Specified", "Path-scoped", "No account"];

type RoomCard = {
  lead: string;
  body: string;
  figure: ReactNode;
};

const roomCards: RoomCard[] = [
  {
    lead: "Anyone with the link is in",
    body: "There is no approval step and no account to create. Treat an invite the way you would treat a password.",
    figure: (
      <div className="fig fig-center">
        <InviteChip />
      </div>
    ),
  },
  {
    lead: "Everyone's caret, in one file",
    body: "You see where each person is typing, and their caret and selection travel with their edits.",
    figure: <CaretLines />,
  },
  {
    lead: "Guests only see the folder you shared",
    body: "The room never adds, renames or removes a file in your working copy.",
    figure: (
      <div className="fig">
        <TreeFigure />
      </div>
    ),
  },
  {
    lead: "Clients share one protocol",
    body: "The session layer is written down rather than glued into each editor, so any client that speaks it can share the room.",
    figure: (
      <div className="fig">
        <ClientChips />
      </div>
    ),
  },
];

const steps = [
  {
    n: "01",
    title: "Host a folder",
    body: "Start the server, open a folder in your editor and host a room.",
  },
  {
    n: "02",
    title: "Send the invite",
    body: "Send the link however you like. Anyone who has it can join and see the folder you shared.",
  },
  {
    n: "03",
    title: "Type in the same file",
    body: "Type in the same file and your edits arrive in everyone's copy.",
  },
  {
    n: "04",
    title: "Close the window",
    body: "Closing the host's window ends the room after a short countdown. A dropped connection can rejoin before it runs out.",
  },
];

type Comparison = { label: string; value: string; here?: boolean };

/** The layers each collaborative tool builds for itself, and the one this project
    writes down instead. */
const comparison: Comparison[] = [
  { label: "Language tooling", value: "LSP" },
  { label: "Debugging", value: "DAP" },
  { label: "Document sync", value: "y-protocols" },
  { label: "Session layer", value: "selvage", here: true },
];

/** A row of the repository grid. Two rows are the project's own repositories and carry no
    client; the rest are one per client, drawn from the one list the chips and the terminal
    read too. */
type GridRow = {
  name: string;
  desc: string;
  Icon: LucideIcon;
  /** The word beside the row, and the status it states. A plan wears the plan's word and is
      not linked: there is no repository at the other end of its row. */
  tag: "source of truth" | "available" | "planned";
  /** The client this row draws, where it draws one. The chips and the install routes carry the
      same key, which is what holds the three surfaces to one list. */
  client?: string;
};

/** The tone each word is drawn in: the palette's colour for the status the word states. */
const GRID_TONE: Record<GridRow["tag"], string> = {
  "source of truth": "bg-mauve/12 text-mauve",
  available: "bg-green/10 text-green",
  planned: "bg-overlay2/12 text-overlay2",
};

const gridRows: GridRow[] = [
  {
    name: "specification",
    desc: "Prose, schema, vectors",
    Icon: BookOpenText,
    tag: "source of truth",
  },
  { name: "reference_server", desc: "selvaged", Icon: HardDrive, tag: "available" },
  ...CLIENTS.map((client) => ({
    name: client.repository,
    desc: client.description,
    Icon: client.Icon,
    tag: client.status,
    client: client.id,
  })),
];

function Eyebrow({ children }: { children: ReactNode }) {
  return <p className="eyebrow">{children}</p>;
}

export default function Home() {
  return (
    <div className="min-h-screen bg-base font-sans text-text antialiased">
      <SiteHeader />
      <div className="prose-body">
        <main id="top">
          <section className="hero">
            <div className="hero-grid">
              <div className="hero-copy">
                {/* One sentence per block, and a real space between them: the claims
                    filter joins block markup with a single space, and without it the
                    sentence boundary reads as `run.on` to it. */}
                <h1 className="hero-title">
                  Edit the same file together,{" "}
                  <span className="hero-accent text-mauve">on a server you run.</span>
                </h1>
                <p className="hero-lede">
                  Your editor, their editor or a browser tab, all in the same file.
                  No third party&apos;s cloud holds the room.
                </p>
                <div className="hero-actions">
                  <Button
                    href={DEMO_ORIGIN}
                    size="hero"
                    className="cta cta-glow flex-auto rounded-[10px] font-medium text-crust motion-safe:hover:-translate-y-px [&_svg]:size-[17px]"
                  >
                    <Play aria-hidden="true" />
                    Try the demo in your browser
                  </Button>
                  <Button
                    href="#run"
                    variant="outline"
                    size="hero"
                    className="cta flex-auto rounded-[10px] font-medium [&_svg]:size-[17px]"
                  >
                    <SquareTerminal aria-hidden="true" />
                    Run it in your editor
                  </Button>
                </div>
                <ul className="hero-facts">
                  {heroFacts.map((fact) => (
                    <li key={fact}>
                      <Check
                        className="hero-fact-icon"
                        strokeWidth={2.5}
                        aria-hidden="true"
                      />
                      {fact}
                    </li>
                  ))}
                </ul>
              </div>
              <RoomWindow />
            </div>
          </section>

          <section id="try" className="band">
            <div className="shell">
              <div className="head-block">
                <Eyebrow>Try &rarr; Run</Eyebrow>
                <h2 className="display">
                  Try it in the browser, then run your own.
                </h2>
                <p className="lede">
                  Every room runs on a server. The demo is one; the Run card starts the
                  same server on a machine you control.
                </p>
              </div>
              <div className="try-grid">
                <div className="try-card try-card-live">
                  <div className="try-head">
                    <p className="try-name">
                      <span className="try-num">01</span>
                      <span className="try-title">Try</span>
                    </p>
                    <Badge variant="pill" className="bg-green/12 text-green">
                      Live
                    </Badge>
                  </div>
                  <p className="try-body">
                    Open the demo in your browser, or point your editor at it.
                    Guests join from the invite link.
                  </p>
                  <div className="try-actions">
                    <a className="demo-link" href={DEMO_ORIGIN}>
                      <Globe className="icon-17" aria-hidden="true" />
                      Open the demo
                      <ArrowUpRight className="icon-14 ml-auto" aria-hidden="true" />
                    </a>
                    <DemoEndpoint />
                  </div>
                </div>

                <div className="try-card">
                  <div className="try-head">
                    <p className="try-name">
                      <span className="try-num">02</span>
                      <span className="try-title">Run</span>
                    </p>
                    <Badge variant="pill" className="bg-green/12 text-green">
                      selvaged
                    </Badge>
                  </div>
                  <p className="try-body">
                    One Docker command. Rooms live in memory, so a restart ends them.
                  </p>
                  <div className="command">
                    <p className="command-line">
                      <span className="command-prompt">$ </span>
                      {COMMAND}
                    </p>
                  </div>
                  <a className="try-link" href="#run">
                    Set up the server and your editor
                    <ArrowDown className="icon-14" aria-hidden="true" />
                  </a>
                </div>

                <div className="try-card try-card-planned">
                  <div className="try-head">
                    <p className="try-name">
                      <span className="try-num">03</span>
                      <span className="try-title">Rent a server</span>
                    </p>
                    <Badge variant="pill" className="bg-yellow/10 text-yellow">
                      Not available yet
                    </Badge>
                  </div>
                  <p className="try-body">We run the server, you open rooms.</p>
                  <p className="planned-row">
                    <HardDrive className="icon-17" aria-hidden="true" />
                    Hosted servers
                  </p>
                </div>
              </div>
            </div>
          </section>

          <section id="run" className="shell">
            <div className="head-block">
              <Eyebrow>Get it working</Eyebrow>
              <h2 className="display">One server, any client.</h2>
              <p className="lede">
                The extension, the plugin and the browser page are clients, not a
                server: each one connects to a {" "}
                <code>selvaged</code> you run.
              </p>
            </div>
            <div className="run-grid">
              <SetupTerminal />
              <div className="panels">
                <Card className="p-5">
                  <p className="panel-head">
                    <Lock className="panel-icon-green" aria-hidden="true" />
                    The server carries bytes it cannot read
                  </p>
                  <p className="panel-body">
                    Documents, cursors, the file listing and the roles the host signs
                    travel sealed, under keys the invite link carries in the part a
                    browser never sends to a server.
                  </p>
                  <ul className="chips chips-green">
                    <li>documents</li>
                    <li>cursors</li>
                    <li>the file listing</li>
                    <li>the roles the host signs</li>
                  </ul>
                </Card>
                <Card className="p-5">
                  <p className="panel-head">
                    <Eye className="panel-icon-peach" aria-hidden="true" />
                    What the server can still see
                  </p>
                  <ul className="chips chips-peach">
                    <li>that a room exists</li>
                    <li>who is in it and their names</li>
                    <li>sizes and timing of what moves</li>
                  </ul>
                  <p className="panel-body">
                    It can drop, delay or end a room. The host is a peer&apos;s signed
                    claim: the server cannot seat a host, prove one, or take the role.
                  </p>
                </Card>
              </div>
            </div>
          </section>

          <section id="see-it" className="shell">
            <div className="head-block">
              <Eyebrow>See it working</Eyebrow>
              <h2 className="display">Your folder, open in their editor.</h2>
            </div>
            <ul className="cards">
              {roomCards.map((card) => (
                <li key={card.lead}>
                  {card.figure}
                  <div className="card-text">
                    <p className="card-lead">{card.lead}</p>
                    <p className="card-body">{card.body}</p>
                  </div>
                </li>
              ))}
            </ul>
          </section>

          <section id="how-it-works" className="shell">
            <div className="head-block">
              <Eyebrow>How it works</Eyebrow>
              <h2 className="display">Share a link and edit the same file together.</h2>
            </div>
            <ol className="steps">
              {steps.map((step) => (
                <li key={step.n}>
                  <p className="step-num">{step.n}</p>
                  <p className="step-title">{step.title}</p>
                  <p className="step-body">{step.body}</p>
                </li>
              ))}
            </ol>
          </section>

          <section id="why-a-spec" className="shell shell-end">
            <div className="spec-grid">
              <div className="spec-copy">
                <Eyebrow>Why a spec</Eyebrow>
                <h2 className="display">The session layer is written down.</h2>
                <p className="spec-line">
                  Which rooms exist, who is in one, which documents are open, where the
                  carets are: every collaborative tool decides those for itself, so a
                  tool from one cannot join a room from another.
                </p>
                <p className="spec-line">
                  Selvage writes that layer down: prose, a canonical byte form for a
                  frame, JSON Schema, and a corpus of conformance vectors, replayed byte
                  for byte against a real server. The specification&apos;s own validator,
                  <code>specification/schema/validate.py</code>, prints the corpus&apos;s
                  counts, so a reader can check the current figures. It is written to be
                  implemented on its own, without reading the server&apos;s code.
                </p>
                <a
                  className="spec-link"
                  href="https://github.com/selvage-protocol/specification"
                >
                  <BookOpenText className="icon-18" aria-hidden="true" />
                  Read the specification
                </a>
                <p className="spec-note">The specification is a draft.</p>
              </div>
              <div className="compare">
                {comparison.map((row) => (
                  <div
                    key={row.label}
                    className={row.here ? "compare-row compare-here" : "compare-row"}
                  >
                    <span>{row.label}</span>
                    <span className="compare-value">{row.value}</span>
                  </div>
                ))}
              </div>
            </div>
            <ul className="repos">
              {gridRows.map((row) => {
                const body = (
                  <>
                    <row.Icon className="repo-icon" aria-hidden="true" />
                    <span className="repo-text">
                      <span className="repo-name">{row.name}</span>
                      <span className="repo-desc">{row.desc}</span>
                    </span>
                    <Badge
                      variant="pill"
                      className={`repo-pill text-[11px] ${GRID_TONE[row.tag]}`}
                    >
                      {row.tag}
                    </Badge>
                  </>
                );
                return (
                  <li key={row.name}>
                    {row.tag === "planned" ? (
                      <div className="repo" data-client={row.client}>
                        {body}
                      </div>
                    ) : (
                      <a
                        className="repo"
                        data-client={row.client}
                        href={repositoryUrl(row.name)}
                      >
                        {body}
                        {/* Linked rows only: the row that is a plan has nowhere to go, so it
                            carries no mark either. */}
                        <ArrowUpRight className="repo-go icon-14" aria-hidden="true" />
                      </a>
                    )}
                  </li>
                );
              })}
            </ul>
            {/* The grid's own last row, and a full-width one: the list it stands under is
                open, and a strip that spans the grid says so without becoming a cell that a
                row count can strand. */}
            <div className="repos-more">
              <Plus className="repos-more-icon" aria-hidden="true" />
              <span className="repos-more-lead">More clients</span>
              <span className="repos-more-note">Planned</span>
            </div>
          </section>
        </main>

        <footer className="band">
          <div className="shell foot-grid">
            <div className="foot-col">
              <h3 className="foot-h">Licences</h3>
              <dl className="licences">
                <div className="licence-row">
                  <dt>Specification</dt>
                  <dd>CC-BY-4.0</dd>
                </div>
                <div className="licence-row">
                  <dt>Spec tooling and clients</dt>
                  <dd>MIT OR Apache-2.0</dd>
                </div>
              </dl>
              <p className="foot-note">
                <code>selvaged</code> is FSL-1.1-MIT: source-available, not
                OSI-approved, free for any non-competing purpose, and it converts to
                MIT two years after each release.
              </p>
            </div>
            <div className="foot-col">
              <h3 className="foot-h">This page</h3>
              <p className="foot-note">
                No cookies, no tracking, no personal data: it prerenders to static
                HTML and makes no third-party request. Run by the{" "}
                <a href="https://github.com/selvage-protocol">selvage-protocol</a>{" "}
                GitHub organisation, and the page itself is MIT OR Apache-2.0.
              </p>
            </div>
            <div className="foot-col">
              <h3 className="foot-h">Contact</h3>
              <p className="foot-note">
                Questions or security reports:{" "}
                <a href="mailto:selvage@dontblameme.dev">
                  selvage@dontblameme.dev
                </a>
                . We only keep your address to reply.
              </p>
            </div>
          </div>
        </footer>
      </div>
    </div>
  );
}
