"use client";

import type { ReactNode } from "react";
import { useEffect, useState } from "react";

/* The one animated part of the room window: the line a second peer is typing.
   It lives on its own so the timer re-renders these few spans rather than the
   whole figure. */

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

export function TypedLine({ animatePlayground = true }: { animatePlayground?: boolean }) {
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

  return typedPieces(count);
}
