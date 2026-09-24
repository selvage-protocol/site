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
   sample's body colour.

   A peer is drawn the way the browser client draws one (`renderCursors` in
   web_client/src/browser/editor.ts): a 2 px bar in their colour at the caret's own
   range, which is a column *between two characters* of the line; a translucent fill
   over the characters they have selected; and their name in the left gutter, on the
   line the caret is on, where that client puts its glyph-margin badge. The name is
   never written into the Rust text — read as a word there it would pass for syntax —
   so it stays in the gutter lane, beside the line number. Every line fits the narrowest
   panel the page is drawn at.

   The file the room has open is named twice, in the guest's tree and in the room bar,
   and both names carry the same colour. It wears one mark: the dot beside it in the
   tree, drawn in the panel's own text colour. No second dot and no peer's colour, so
   the mark reads as the file rather than as somebody's caret. */

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

/** One line of a sample: the gutter lane — the peer's name badge when their caret is on
    this line, then the line's number — and the code token by token. The lane is on every
    line, so the code keeps one left edge and the badges line up with the lines they
    name. */
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
      <span className="code-gutter">{at ? <PeerBadge name={at} /> : null}</span>
      <span className="code-num">{n}</span>
      {children}
    </span>
  );
}

/** A peer's caret: the 2 px bar the browser client's editor draws on the caret's range
    (`className: … 'border-left: 2px solid …'`), written into the line between the two
    characters it stands between. */
function Caret({ name }: { name: PeerName }) {
  return <span className={`caret peer-${PEERS[name]}`} />;
}

/** The characters a peer has selected: their colour at the client's quarter alpha
    (`translucent(colour, 0.25)` in web_client/src/bridge/cursors.ts) behind the text,
    which is the other half of how an editor shows a peer. */
function Selected({ name, children }: { name: PeerName; children: ReactNode }) {
  return <span className={`selected selected-${PEERS[name]}`}>{children}</span>;
}

/** A peer's name in the gutter, on the line their caret is on: the badge the browser
    client paints in the glyph margin (`badgeCss` in web_client/src/browser/presence.ts)
    — the peer's colour behind a dark label. It is the peer's name and not their
    initials: the name has nowhere else to be drawn, since the Rust text is not the
    place for it. */
function PeerBadge({ name }: { name: PeerName }) {
  return <span className={`peer-badge peer-${PEERS[name]}`}>{name}</span>;
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

/** The paths the host granted, as a guest sees them, with the one the room has open
    carrying the figure's only mark. */
export function TreeFigure({ label = "guest" }: { label?: string }) {
  return (
    <div className="room-tree" aria-hidden="true">
      <p className="room-tree-label">{label}</p>
      <ul>
        <li className="room-tree-dir">src/</li>
        <li>main.rs</li>
        <li className="room-tree-here">
          room.rs
          <span className="open-dot" />
        </li>
        <li>session.rs</li>
      </ul>
    </div>
  );
}

/** Two people in one file: their carets travel as anchors inside the text, so each one
    is drawn where it sits rather than listed beside the sample — a bar at a column of a
    line, the name in the gutter on that line's row, and a fill behind what they hold. */
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
          <Tok kind="type">
            {"st"}
            <Caret name="mira" />
            {"r"}
          </Tok>
          {","}
        </CodeLine>
        <CodeLine n={5} at="jonas">
          {"    at: "}
          <Selected name="jonas">
            <Tok kind="type">SelectionOffsets</Tok>
          </Selected>
          <Caret name="jonas" />
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
          {"    engine.set_selection(path, at)"}
        </CodeLine>
        <CodeLine n={8}>{"        .await"}</CodeLine>
        <CodeLine n={9}>{"}"}</CodeLine>
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
      <p className="client-rail">one engine &middot; selvage/2</p>
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
              <CodeLine n={5} at="jonas">
                {"    "}
                <Tok kind="keyword">let</Tok>
                {" file = "}
                <Selected name="jonas">
                  <Tok kind="string">{'"room.rs"'}</Tok>
                </Selected>
                <Caret name="jonas" />
                {";"}
              </CodeLine>
              <CodeLine n={6} at="mira">
                {"    engine.open(file"}
                <Caret name="mira" />
                {").await?;"}
              </CodeLine>
              <CodeLine n={7}>
                {"    engine.insert(file, "}
                <Tok kind="number">0</Tok>
                {", "}
                <Tok kind="string">{'"hi"'}</Tok>
                {")"}
              </CodeLine>
              <CodeLine n={8}>{"        .await"}</CodeLine>
              <CodeLine n={9}>{"}"}</CodeLine>
            </code>
          </pre>
          <div className="room-invite">
            <InviteChip />
          </div>
        </Card>
      </div>
      <figcaption>
        An illustration of a guest&apos;s window: the paths the host granted, the dot
        beside the file the room has open, the two carets in it, and the invite link that
        put them there.
      </figcaption>
    </figure>
  );
}
