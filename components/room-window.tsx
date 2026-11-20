import type { ReactNode } from "react";
import { FolderOpen, Link as LinkIcon } from "lucide-react";
import { TypedLine } from "@/components/typed-line";

/* The hero figure: a guest's window onto the host's folder, with the line the two
   of them are in being typed. The typing is the point rather than decoration — it
   is what the page is: one file, edited by two people at once. */

function Line({
  n,
  badge,
  children,
}: {
  n: number;
  badge?: ReactNode;
  children: ReactNode;
}) {
  return (
    <div className="room-line">
      <span className="room-badges">{badge}</span>
      <span className="room-num">{n}</span>
      {/* The line is a flex row, and a whitespace-only text node between two flex
          items is not a flex item at all: the code sits in one span, so the spaces
          inside it survive. */}
      <span>{children}</span>
    </div>
  );
}

/** The room window. The line being typed is the only animated part, so the timer
    re-renders a few spans rather than the whole figure. */
export function RoomWindow({ animatePlayground = true }: { animatePlayground?: boolean }) {
  return (
    <figure className="hero-visual" aria-hidden="true">
      <div className="hero-glow" aria-hidden="true" />
      <div className="hero-glass">
        <div className="room-grid">
          <div className="room-side" aria-hidden="true">
            <div className="room-dir">
              <FolderOpen className="room-dir-icon" />
              src/
            </div>
            <div className="room-file">main.rs</div>
            <div className="room-open">room.rs</div>
            <div className="room-file">session.rs</div>
          </div>
          <div className="room-code" aria-hidden="true">
            <Line n={1}>
              <span className="tok-comment">{"/// Open the room's file."}</span>
            </Line>
            <Line n={2}>
              <span className="tok-keyword">async</span>{" "}
              <span className="tok-keyword">fn</span>
              {" open_room("}
            </Line>
            <Line n={3}>
              {"    engine: &"}
              <span className="tok-type">SyncEngine</span>
              {","}
            </Line>
            <Line n={4}>
              {") -> "}
              <span className="tok-type">Result</span>
              {"<(), "}
              <span className="tok-type">Error</span>
              {"> {"}
            </Line>
            <Line
              n={5}
              badge={<span className="peer-badge peer-teal">jonas</span>}
            >
              {"    "}
              <span className="tok-keyword">let</span>
              {" file = "}
              <span className="selected selected-teal tok-string">
                {'"room.rs"'}
              </span>
              <span className="caret caret-room peer-teal blink" />
              {";"}
            </Line>
            <Line
              n={6}
              badge={<span className="peer-badge peer-mauve">mira</span>}
            >
              <TypedLine animatePlayground={animatePlayground} />
              <span className="caret caret-room peer-mauve blink" />
            </Line>
            <Line n={7}>{"}"}</Line>
          </div>
        </div>
        <div className="room-foot">
          {/* A sample, not a control: the link is one to no room, so the figure draws it
              with the word `sample` and nothing to press. */}
          <div className="invite-sample" aria-hidden="true">
            <LinkIcon className="invite-glyph" />
            <span className="invite-url">
              ?room=k7m2&amp;token=4f9c#k=&hellip;&amp;h=&hellip;
            </span>
            <span className="invite-label">sample</span>
          </div>
        </div>
      </div>
    </figure>
  );
}
