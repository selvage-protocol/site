"use client";

import { useEffect, useState } from "react";
import { ArrowUpRight } from "lucide-react";
import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils";

const navLinks = [
  { href: "#who-its-for", label: "Who it's for" },
  { href: "#session", label: "Session" },
  { href: "#run-it", label: "Run it" },
  { href: "#not-yet", label: "Not yet" },
];

export function SiteHeader() {
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
    <header
      className={cn(
        "site-header sticky top-0 z-10 border-b border-surface0/70 bg-base/85 backdrop-blur transition-transform duration-300 focus-within:translate-y-0",
        concealed && "-translate-y-full",
      )}
    >
      <nav
        aria-label="Page"
        className="mx-auto flex h-16 w-full max-w-6xl items-center gap-6 px-5"
      >
        <a href="#top" className="flex items-center gap-2.5">
          <img
            className="h-8 w-auto"
            src="/mark-transparent.png"
            alt=""
            width={800}
            height={800}
          />
          <span className="text-[17px] font-semibold tracking-tight text-text">
            Selvage
          </span>
        </a>
        <div className="hidden items-center gap-6 md:flex">
          {navLinks.map((link) => (
            <a
              key={link.href}
              href={link.href}
              className="text-sm text-subtext transition-colors hover:text-text py-1"
            >
              {link.label}
            </a>
          ))}
        </div>
        <div className="ml-auto flex items-center gap-2.5">
          <a
            href="https://github.com/selvage-protocol"
            className="hidden items-center gap-1 text-sm text-subtext transition-colors hover:text-text sm:inline-flex py-1"
          >
            GitHub
            <ArrowUpRight className="h-3.5 w-3.5" />
          </a>
          <Button
            href="https://github.com/selvage-protocol/specification"
            size="sm"
          >
            Read the spec
          </Button>
        </div>
      </nav>
      <nav
        aria-label="Sections"
        className="flex gap-4 overflow-x-auto whitespace-nowrap border-t border-surface0/70 px-5 py-2 text-[13px] md:hidden"
      >
        {navLinks.map((link) => (
          <a
            key={link.href}
            href={link.href}
            className="py-1 text-subtext transition-colors hover:text-text"
          >
            {link.label}
          </a>
        ))}
      </nav>
    </header>
  );
}
