import type { ReactNode } from "react";
import { Link as LinkIcon } from "lucide-react";

/* Renderings of the product surface: the invite a host copies, the carets in one
   file, the guest's view of the folder, the clients that can share a room. They
   are drawn in markup and the page's own stylesheet — no image, no dependency,
   nothing fetched — and each is `aria-hidden`, so a screen reader hears the card's
   own sentence instead of the drawing.

   The Rust in them is an illustration rather than a transcript, and it is coloured
   with the browser client's own `selvage-mocha` token rules: a span per token
   rather than a highlighter, because punctuation has no rule in that theme and so
   keeps the sample's body colour.

   A peer is drawn the way the browser client draws one (`renderCursors` in
   web_client/src/browser/editor.ts): a 2 px bar in their colour at the caret's own
   range, which is a column *between two characters* of the line; a translucent fill
   over the characters they hold; and their name in the glyph margin, on the line
   their caret is on, where that client paints its badge. The name is never written
   into the Rust text — read as a word there it would pass for syntax. */

/** The colours of `selvage-mocha`, the theme the browser client defines
    (`defineTheme` in web_client/src/browser/main.ts), so the figure and the real
    editor describe Rust the same way. The classes live in style.css, where
    scripts/check-contrast.py measures them. */
type Token = "comment" | "keyword" | "fn" | "string" | "number" | "type";

function Tok({ kind, children }: { kind: Token; children: ReactNode }) {
  return <span className={`tok-${kind}`}>{children}</span>;
}

/** The peers in the room, and the accent each is drawn in: the page's mauve for the
    first, its teal for the second, its peach for the third. */
const PEERS = { mira: "mauve", jonas: "teal", sam: "peach" } as const;
type PeerName = keyof typeof PEERS;

/** A peer's caret: the 2 px bar the browser client's editor draws on the caret's
    range (`className: … 'border-left: 2px solid …'`), written into the line between
    the two characters it stands between. */
function Caret({ name }: { name: PeerName }) {
  return <span className={`caret peer-${PEERS[name]}`} />;
}

/** The characters a peer has selected: their colour at the client's quarter alpha
    (`translucent(colour, 0.25)` in web_client/src/bridge/cursors.ts) behind the
    text, which is the other half of how an editor shows a peer. */
function Selected({ name, children }: { name: PeerName; children: ReactNode }) {
  return <span className={`selected selected-${PEERS[name]}`}>{children}</span>;
}

/** A peer's name in the glyph margin, on the line their caret is on: the badge the
    browser client paints there (`badgeCss` in web_client/src/browser/presence.ts)
    — the peer's colour behind a dark label. */
function PeerBadge({ name }: { name: PeerName }) {
  return <span className={`peer-badge peer-${PEERS[name]}`}>{name}</span>;
}

/** The invite a host copies: the glyph the client's own control carries, and the
    link itself on one line. */
export function InviteChip() {
  return (
    <span className="invite" aria-hidden="true">
      <LinkIcon className="invite-glyph" />
      <span className="invite-url">?room=k7m2&amp;token=4f9c#k=&hellip;</span>
    </span>
  );
}

/** Three people in one file: their carets travel as anchors inside the text, so
    each one is drawn where it sits rather than listed beside the sample — a bar at a
    column of a line, a fill behind what one of them holds, and a name in the glyph
    margin on that line's row. */
export function CaretLines() {
  return (
    <pre className="code fig-code" aria-hidden="true">
      <code>
        <span className="code-line">
          <Tok kind="keyword">async fn</Tok>
          {" caret("}
        </span>
        <span className="code-line">
          {"    path: &"}
          <Tok kind="type">st</Tok>
          <Caret name="mira" />
          <Tok kind="type">r</Tok>
          {","}
          <span className="badge-gap">
            <PeerBadge name="mira" />
          </span>
        </span>
        <span className="code-line">
          {"    at: "}
          <Selected name="jonas">
            <Tok kind="type">SelectionOffsets</Tok>
          </Selected>
          <Caret name="jonas" />
          <span className="badge-gap">
            <PeerBadge name="jonas" />
          </span>
        </span>
        <span className="code-line">
          {") -> "}
          <Tok kind="type">Result</Tok>
          <Caret name="sam" />
          <span className="badge-gap">
            <PeerBadge name="sam" />
          </span>
        </span>
      </code>
    </pre>
  );
}

/** The paths the host granted, as a guest sees them, with the one the room has open
    carrying the figure's only mark: a dot in the panel's own text colour, so it
    reads as the file rather than as somebody's caret. */
export function TreeFigure() {
  return (
    <div className="tree" aria-hidden="true">
      <span>src/</span>
      <span className="tree-file">main.rs</span>
      <span className="tree-here">
        room.rs
        <span className="open-dot" />
      </span>
    </div>
  );
}

/** The clients one room is open to, and the one that is still only planned. */
export function ClientChips() {
  return (
    <div className="clients" aria-hidden="true">
      <span className="client">VS Code</span>
      <span className="client">Neovim</span>
      <span className="client">Browser</span>
      <span className="client client-more">and more&hellip;</span>
    </div>
  );
}
