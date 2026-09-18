import type { ReactNode } from "react";
import { Copy } from "lucide-react";
import { Card } from "@/components/ui/card";

/* Renderings of the product surface: the guest's window, the invite chip, the mirrored
   tree, the three clients. They are drawn in markup and the page's own stylesheet — no
   image, no dependency, nothing fetched — and each one is `aria-hidden` inside a
   labelled `figure`, so a screen reader hears the caption instead of the drawing.

   The code sample is an illustration, not a transcript: the page's caption says so. */

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

/** Two people in one file: two carets on one line. */
export function CaretLines() {
  return (
    <pre className="code fig-code" aria-hidden="true">
      <code>
        <CodeLine n={3}>
          {"    doc.write("}
          <Peer name="mira" tone="mauve" />
          {"\"hi\");"}
          <Peer name="jonas" tone="teal" />
        </CodeLine>
      </code>
    </pre>
  );
}

/** The three clients and the one wire version they all speak. */
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
              <CodeLine n={1}>{"fn invite(&mut self, peer: Peer) {"}</CodeLine>
              <CodeLine n={2}>
                {"    let doc = open("}
                <span className="code-style">&quot;room.rs&quot;</span>
                {");"}
              </CodeLine>
              <CodeLine n={3}>
                {"    doc.write("}
                <Peer name="mira" tone="mauve" />
                {"\"hi\");"}
                <Peer name="jonas" tone="teal" />
              </CodeLine>
              <CodeLine n={4}>{"}"}</CodeLine>
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
