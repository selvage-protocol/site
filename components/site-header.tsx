"use client";

import { useEffect, useState } from "react";
import { ArrowUpRight } from "lucide-react";
import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils";

const navLinks = [
  { href: "#try", label: "Try" },
  { href: "#run", label: "Run" },
  { href: "#how-it-works", label: "How it works" },
  { href: "#why-a-spec", label: "Specification" },
];

/** The GitHub mark, drawn here because the icon set the page uses carries no brand
    marks: the octocat is what the link to the organisation is known by, and it is
    drawn rather than fetched, so it is one more shape from this origin. */
function GithubMark({ className }: { className?: string }) {
  return (
    <svg className={className} viewBox="0 0 24 24" aria-hidden="true" focusable="false">
      <path
        fill="currentColor"
        d="M12 .3a12 12 0 0 0-3.8 23.4c.6.1.8-.3.8-.6v-2c-3.3.7-4-1.6-4-1.6-.6-1.4-1.4-1.8-1.4-1.8-1-.7.1-.7.1-.7 1.2.1 1.8 1.2 1.8 1.2 1 1.8 2.8 1.3 3.5 1a2.6 2.6 0 0 1 .8-1.6c-2.7-.3-5.5-1.3-5.5-5.9 0-1.3.5-2.4 1.2-3.2-.1-.3-.5-1.5.1-3.2 0 0 1-.3 3.3 1.2a11.5 11.5 0 0 1 6 0c2.3-1.5 3.3-1.2 3.3-1.2.6 1.7.2 2.9.1 3.2.8.8 1.2 1.9 1.2 3.2 0 4.6-2.8 5.6-5.5 5.9.4.4.8 1.1.8 2.2v3.3c0 .3.2.7.8.6A12 12 0 0 0 12 .3"
      />
    </svg>
  );
}

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
        "site-header motion-reduce:transition-none transition-transform duration-300 focus-within:translate-y-0",
        concealed && "-translate-y-full",
      )}
    >
      <nav
        aria-label="Page"
        className="mx-auto flex h-[60px] max-w-[1160px] items-center gap-7 px-4 min-[720px]:px-6"
      >
        <a href="#top" className="flex items-center gap-2.5 text-text">
          <img
            className="block h-[30px] w-auto"
            src="/mark-header.png"
            alt=""
            width={128}
            height={128}
          />
          {/* `text-base` is the palette's own base colour, not a size: a named theme
              colour wins the ambiguity, and this label would be the page's background
              drawn on the page. */}
          <span className="text-[16px] font-semibold tracking-[-0.01em]">
            Selvage
          </span>
        </a>
        <div className="hidden items-center gap-[22px] text-[14px] min-[720px]:flex">
          {navLinks.map((link) => (
            <a
              key={link.href}
              href={link.href}
              className="text-subtext transition-colors hover:text-text"
            >
              {link.label}
            </a>
          ))}
        </div>
        <div className="ml-auto flex items-center gap-3.5">
          {/* The label is hidden below 720px, so the icon would be the anchor's only
              name there; the attribute names it at every width. */}
          <a
            href="https://github.com/selvage-protocol"
            aria-label="GitHub"
            className="inline-flex items-center gap-1.5 text-[14px] text-subtext transition-colors hover:text-text"
          >
            <GithubMark className="icon-18" />
            <span className="hidden min-[720px]:inline">GitHub</span>
          </a>
          <Button
            href="https://selvage-demo.dontblameme.dev"
            size="sm"
            className="text-crust [&_svg]:size-3.5"
          >
            Try the demo
            <ArrowUpRight aria-hidden="true" />
          </Button>
        </div>
      </nav>
      {/* A phone keeps every in-page route: the bar itself has no room for them
          beside the mark and the two actions. */}
      <nav
        aria-label="Sections"
        className="header-row gap-4 overflow-x-auto whitespace-nowrap px-4 text-[13px]"
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
