"use client";

import type { ReactNode } from "react";
import { useEffect, useState } from "react";
import { FolderOpen, Link as LinkIcon } from "lucide-react";

/* The hero figure: a guest's window onto the host's folder, with the line the two
   of them are in being typed. The typing is the point rather than decoration — it
   is what the page is: one file, edited by two people at once. */

const TICK_MS = 85;
/** How long the finished line rests before it is typed again. */
const HOLD_TICKS = 36;

type Piece = { text: string; className?: string };

/** The line being typed, in the pieces the theme colours differently. */
const TYPED: Piece[] = [
  { text: "    engine." },
  { text: "open", className: "tok-fn" },
  { text: "(file)." },
  { text: "await", className: "tok-keyword" },
];

const TYPED_LENGTH = TYPED.reduce((total, piece) => total + piece.text.length, 0);

/** The first `count` characters of the line, in their own spans, so a piece that is
    half typed is drawn in its own colour all the same. */
function typedPieces(count: number): ReactNode[] {
  const drawn: ReactNode[] = [];
  let left = count;
  for (const [at, piece] of TYPED.entries()) {
    if (left <= 0) break;
    drawn.push(
      <span key={at} className={piece.className}>
        {piece.text.slice(0, left)}
      </span>,
    );
    left -= piece.text.length;
  }
  return drawn;
}

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

/** The room window. `animatePlayground` types the line and holds it; with it off
    the line is already written. Either way the caret is drawn, and a reader who
    asked for less motion gets a still one. */
export function RoomWindow({ animatePlayground = true }: { animatePlayground?: boolean }) {
  const [count, setCount] = useState(0);

  useEffect(() => {
    if (
      !animatePlayground ||
      window.matchMedia("(prefers-reduced-motion: reduce)").matches
    ) {
      setCount(TYPED_LENGTH);
      return;
    }
    let position = 0;
    let held = 0;
    const timer = window.setInterval(() => {
      if (position < TYPED_LENGTH) {
        position += 1;
        setCount(position);
        return;
      }
      if (held < HOLD_TICKS) {
        held += 1;
        return;
      }
      position = 0;
      held = 0;
      setCount(0);
    }, TICK_MS);
    return () => window.clearInterval(timer);
  }, [animatePlayground]);

  return (
    <figure className="hero-visual">
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
              {typedPieces(count)}
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
