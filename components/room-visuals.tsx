import type { ReactNode } from "react";
import { Copy } from "lucide-react";
import { Card } from "@/components/ui/card";

/* Renderings of the product surface: the guest's window, the invite chip, the mirrored
   tree, the clients. They are drawn in markup and the page's own stylesheet — no
   image, no dependency, nothing fetched — and each one is `aria-hidden` inside a
   labelled `figure`, so a screen reader hears the caption instead of the drawing.

   The code in them is an illustration rather than a transcript, and it is the API the
   client crate has: the calls, the types and the paths are the ones in
   `crates/client`, with the `use selvage_client::…` line elided. It is coloured by
   hand with the browser client's own `selvage-mocha` token rules, a span per token
   rather than a highlighter: punctuation has no rule in that theme, so it keeps the
   sample's body colour. A peer's name is never written into the source — a name inside
   a line of Rust reads as syntax — and their caret is drawn at the end of the line it
   sits on: the bar and the name chip an editor draws beside a remote cursor, in the
   line's own flow. Every line fits the narrowest panel the page is drawn at. */

/** The colours of `selvage-mocha`, the theme the browser client defines
    (`defineTheme` in web_client/src/browser/main.ts), so the figure and the real
    editor describe Rust the same way. The classes live in style.css, where
    scripts/check-contrast.py measures them. */
type Token = "comment" | "keyword" | "string" | "number" | "type";

function Tok({ kind, children }: { kind: Token; children: ReactNode }) {
  return <span className={`tok-${kind}`}>{children}</span>;
}

/** The two peers in the room, and the accent each is drawn in: the page's mauve for the
    first and its teal for the second, as the editor draws two remote cursors. */
const PEERS = { mira: "mauve", jonas: "teal" } as const;
type PeerName = keyof typeof PEERS;

/** One line of a sample: its number in the gutter, the code token by token, and — when a
    peer's caret sits at the end of it — that peer's marker. */
function CodeLine({
  n,
  at,
  children,
}: {
  n: number;
  at?: PeerName;
  children: ReactNode;
}) {
  return (
    <span className="code-line">
      <span className="code-num">{n}</span>
      {children}
      {at ? <Peer name={at} /> : null}
    </span>
  );
}

/** A peer's caret at the end of a line: the bar in their colour, with their name in a
    chip beside it. The chip is the default button's pair — a dark label on mauve or
    teal — so both tones are measured rather than chosen by eye. */
function Peer({ name }: { name: PeerName }) {
  return (
    <span className={`peer peer-${PEERS[name]}`}>
      <span className="peer-name">{name}</span>
    </span>
  );
}

export function InviteChip() {
  return (
    <span className="invite" aria-hidden="true">
      <Copy className="invite-glyph" aria-hidden="true" />
      <span className="invite-label">invite link</span>
      <span className="invite-url">?room=k7m2&amp;token=4f9c&hellip;</span>
    </span>
  );
}

/** The paths the host granted, as a guest sees them. */
export function TreeFigure({ label = "guest" }: { label?: string }) {
  return (
    <div className="room-tree" aria-hidden="true">
      <p className="room-tree-label">{label}</p>
      <ul>
        <li className="room-tree-dir">src/</li>
        <li>main.rs</li>
        <li className="room-tree-here">
          room.rs
          <span className="peer-dot" />
        </li>
        <li>session.rs</li>
      </ul>
    </div>
  );
}

/** Two people in one file: their carets travel as anchors inside the text, so each one
    is drawn where it sits rather than listed beside the sample. */
export function CaretLines() {
  return (
    <pre className="code fig-code" aria-hidden="true">
      <code>
        <CodeLine n={1}>
          <Tok kind="comment">{"/// Publish this peer's caret."}</Tok>
        </CodeLine>
        <CodeLine n={2}>
          <Tok kind="keyword">async</Tok>
          {" "}
          <Tok kind="keyword">fn</Tok>
          {" caret("}
        </CodeLine>
        <CodeLine n={3}>
          {"    engine: &"}
          <Tok kind="type">SyncEngine</Tok>
          {","}
        </CodeLine>
        <CodeLine n={4} at="mira">
          {"    path: &"}
          <Tok kind="type">str</Tok>
          {","}
        </CodeLine>
        <CodeLine n={5} at="jonas">
          {"    at: "}
          <Tok kind="type">SelectionOffsets</Tok>
          {","}
        </CodeLine>
        <CodeLine n={6}>
          {") -> "}
          <Tok kind="type">Result</Tok>
          {"<(), "}
          <Tok kind="type">Error</Tok>
          {"> {"}
        </CodeLine>
        <CodeLine n={7}>
          {"    engine.set_selection(path, at)."}
          <Tok kind="keyword">await</Tok>
        </CodeLine>
        <CodeLine n={8}>{"}"}</CodeLine>
      </code>
    </pre>
  );
}

/** The clients and the one wire version they all speak. */
export function ClientChips() {
  return (
    <div className="clients" aria-hidden="true">
      <p className="client-row">
        <span className="client">VS Code</span>{" "}
        <span className="client">Neovim</span>{" "}
        <span className="client">a browser page</span>
      </p>
      <p className="client-rail">one engine &middot; selvage/1</p>
    </div>
  );
}

/** The hero figure: the whole surface at once — tree, one file, two carets, the invite. */
export function RoomWindow() {
  return (
    <figure className="hero-visual">
      <div className="hero-visual-rules" aria-hidden="true" />
      <div className="room" aria-hidden="true">
        <TreeFigure />
        <Card className="hero-glass">
          <div className="room-bar">
            <span className="room-dot" />
            <span className="room-file">room.rs</span>
            <span className="room-count">2 in the room</span>
          </div>
          <pre className="code">
            <code>
              <CodeLine n={1}>
                <Tok kind="comment">{"/// Say hi in the room's file."}</Tok>
              </CodeLine>
              <CodeLine n={2}>
                <Tok kind="keyword">async</Tok>
                {" "}
                <Tok kind="keyword">fn</Tok>
                {" greet("}
              </CodeLine>
              <CodeLine n={3}>
                {"    engine: &"}
                <Tok kind="type">SyncEngine</Tok>
                {","}
              </CodeLine>
              <CodeLine n={4}>
                {") -> "}
                <Tok kind="type">Result</Tok>
                {"<(), "}
                <Tok kind="type">Error</Tok>
                {"> {"}
              </CodeLine>
              <CodeLine n={5} at="mira">
                {"    "}
                <Tok kind="keyword">let</Tok>
                {" file = "}
                <Tok kind="string">{'"room.rs"'}</Tok>
                {";"}
              </CodeLine>
              <CodeLine n={6} at="jonas">
                {"    engine.open(file)."}
                <Tok kind="keyword">await</Tok>
                {"?;"}
              </CodeLine>
              <CodeLine n={7}>
                {"    engine.insert(file, "}
                <Tok kind="number">0</Tok>
                {", "}
                <Tok kind="string">{'"hi"'}</Tok>
                {")."}
                <Tok kind="keyword">await</Tok>
              </CodeLine>
              <CodeLine n={8}>{"}"}</CodeLine>
            </code>
          </pre>
          <div className="room-invite">
            <InviteChip />
          </div>
        </Card>
      </div>
      <figcaption>
        An illustration of a guest&apos;s window: the paths the host granted, one file open,
        two carets in it, and the invite link that put them there.
      </figcaption>
    </figure>
  );
}
