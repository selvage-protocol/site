"use client";

import { useEffect, useState, type ReactNode } from "react";

/** The one piece of the header that runs in the browser: the hide-on-scroll state. Everything
    it wraps renders on the server, so the client bundle carries this effect and nothing of the
    buttons' class merging or the icon set. */
export function ConcealingHeader({
  className,
  children,
}: {
  className: string;
  children: ReactNode;
}) {
  const [concealed, setConcealed] = useState(false);

  useEffect(() => {
    let lastY = window.scrollY;
    let pending = false;
    let frame = 0;
    const onScroll = () => {
      // Decide synchronously: the frame callback only applies the latest
      // verdict, so a coalesced frame can never compare a stale position, and
      // no updater closure reads a variable this handler keeps mutating.
      // Past the bar's own height and moving down: slide it away. Anywhere
      // near the top, or moving up, it stays. The bar is sticky, so hiding
      // is a visual slide only — nothing below it moves.
      const y = window.scrollY;
      pending = y > 64 && y > lastY;
      lastY = y;
      if (frame) return;
      frame = window.requestAnimationFrame(() => {
        frame = 0;
        setConcealed(pending);
      });
    };
    window.addEventListener("scroll", onScroll, { passive: true });
    return () => {
      window.removeEventListener("scroll", onScroll);
      if (frame) window.cancelAnimationFrame(frame);
    };
  }, []);

  return (
    <header className={concealed ? `${className} -translate-y-full` : className}>
      {children}
    </header>
  );
}
