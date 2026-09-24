import { ArrowUpRight } from "lucide-react";
import { ConcealingHeader } from "@/components/concealing-header";
import { Button } from "@/components/ui/button";

const navLinks = [
  { href: "#get-it-working", label: "Get it working" },
  { href: "#how-it-works", label: "How it works" },
  { href: "#why-a-spec", label: "Why a spec" },
];

export function SiteHeader() {
  return (
    <ConcealingHeader className="site-header sticky top-0 z-10 border-b border-surface0/70 bg-base/85 backdrop-blur transition-transform duration-300 focus-within:translate-y-0">
      <nav
        aria-label="Page"
        className="mx-auto flex h-16 w-full max-w-6xl items-center gap-6 px-5"
      >
        <a href="#top" className="flex items-center gap-2.5">
          <img
            className="h-8 w-auto"
            src="/mark-header.png"
            alt=""
            width={128}
            height={128}
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
          <Button href="#get-it-working" size="sm">
            Run it
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
    </ConcealingHeader>
  );
}
