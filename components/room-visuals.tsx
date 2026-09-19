import type { ReactNode } from "react";
import { Copy } from "lucide-react";
import { Card } from "@/components/ui/card";

/* Renderings of the product surface: the guest's window, the invite chip, the mirrored
   tree, the clients. They are drawn in markup and the page's own stylesheet — no
   image, no dependency, nothing fetched — and each one is `aria-hidden` inside a
   labelled `figure`, so a screen reader hears the caption instead of the drawing.

   The code in them is an illustration rather than a transcript, and it is the API the
   client crate has: the calls, the types and the paths are the ones in
   `crates/client`, with the `use selvage_client::…` line elided. A peer's name is
   never written into the source; the carets are drawn in a row under the sample,
   where a caret marker belongs. Every line fits the narrowest panel the page is
   drawn at. */

function CodeLine({ n, children }: { n: number; children: ReactNode }) {
  return (
    <span className="code-line">
      <span className="code-num">{n}</span>
      {children}
    </span>
  );
}

/** One peer's caret in a document: a bar in the peer's colour with their name beside it. */
function Peer({ name, tone }: { name: string; tone: "mauve" | "teal" }) {
  return <span className={`peer peer-${tone}`}>{name}</span>;
}

/** The two carets in the open file, drawn beside the sample rather than inside it. */
function Carets() {
  return (
    <span className="code-carets">
      <Peer name="mira" tone="mauve" />
      <Peer name="jonas" tone="teal" />
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

/** Two people in one file: one client publishes its caret, and both are drawn under it. */
export function CaretLines() {
  return (
    <pre className="code fig-code" aria-hidden="true">
      <code>
        <CodeLine n={1}>{"/// Publish where this peer's caret sits."}</CodeLine>
        <CodeLine n={2}>{"async fn caret("}</CodeLine>
        <CodeLine n={3}>{"    engine: &SyncEngine,"}</CodeLine>
        <CodeLine n={4}>{"    path: &str,"}</CodeLine>
        <CodeLine n={5}>{"    at: SelectionOffsets,"}</CodeLine>
        <CodeLine n={6}>{") -> Result<(), Error> {"}</CodeLine>
        <CodeLine n={7}>{"    engine.set_selection(path, at).await"}</CodeLine>
        <CodeLine n={8}>{"}"}</CodeLine>
        <Carets />
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
              <CodeLine n={1}>{"/// Say hi in the room's file."}</CodeLine>
              <CodeLine n={2}>{"async fn greet("}</CodeLine>
              <CodeLine n={3}>{"    engine: &SyncEngine,"}</CodeLine>
              <CodeLine n={4}>{") -> Result<(), Error> {"}</CodeLine>
              <CodeLine n={5}>{"    let file = \"room.rs\";"}</CodeLine>
              <CodeLine n={6}>{"    engine.open(file).await?;"}</CodeLine>
              <CodeLine n={7}>{"    engine.insert(file, 0, \"hi\").await"}</CodeLine>
              <CodeLine n={8}>{"}"}</CodeLine>
            </code>
          </pre>
          <Carets />
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
