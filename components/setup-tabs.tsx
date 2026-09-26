"use client";

import type { KeyboardEvent } from "react";
import { useEffect, useRef, useState } from "react";
import {
  ArrowUpRight,
  Code,
  Copy,
  Globe,
  HardDrive,
  Info,
  Terminal,
} from "lucide-react";
import type { LucideIcon } from "lucide-react";
import { useCopy } from "@/lib/use-copy";
import { COMMAND, DEMO } from "@/lib/selvage";

/* The terminal a reader copies from: one route per client, with the command that
   route is, the note a reader needs before running it, and the repository it comes
   from. The panels are the ARIA tabs pattern — one strip, one panel per tab, the
   inactive ones `hidden` — and every panel is in the document, so the page still
   carries all four routes for a reader without scripting. */

const NEOVIM_COMMAND = ":SelvageHost ws://127.0.0.1:8080";
const NEOVIM_PLUGIN_LINE = "{ 'selvage-protocol/nvim_client', build = 'npm ci' }";

type Line = { prompt?: string; text: string; comment?: boolean };

type Tab = {
  id: string;
  label: string;
  Icon: LucideIcon;
  lines: Line[];
  copy: string;
  /** What the control puts on the clipboard, named in the announcement: the tab it
      came from is not something the reader listening can see. */
  announce: string;
  note: string;
  source: string;
};

const TABS: Tab[] = [
  {
    id: "server",
    label: "Server",
    Icon: HardDrive,
    lines: [
      { prompt: "$", text: COMMAND },
      { text: "# answers ws://127.0.0.1:8080/session", comment: true },
      { text: "# serves the page on the same port", comment: true },
    ],
    copy: COMMAND,
    announce: "Server command",
    note: "Rooms live in memory, so a restart ends them.",
    source: "https://github.com/selvage-protocol/reference_server",
  },
  {
    id: "vscode",
    label: "VS Code",
    Icon: Code,
    lines: [
      { prompt: "$", text: "code --install-extension selvage-protocol.selvage" },
      { text: "# then run  Selvage: Host a session", comment: true },
    ],
    copy: "code --install-extension selvage-protocol.selvage",
    announce: "VS Code command",
    note: "Published on the VS Code Marketplace and on Open VSX.",
    source: "https://github.com/selvage-protocol/vscode_client",
  },
  {
    id: "nvim",
    label: "Neovim",
    Icon: Terminal,
    lines: [
      { text: "-- lazy.nvim: add this line to your spec", comment: true },
      { text: NEOVIM_PLUGIN_LINE },
      /* `:SelvageHost` is the whole command, colon included: this row's prompt gutter stays
         empty so the line reads as one colon, and the command lines up with the rows that
         draw a prompt of their own. */
      { text: NEOVIM_COMMAND },
    ],
    copy: NEOVIM_PLUGIN_LINE,
    announce: "Neovim plugin line",
    note: "Works with any plugin manager; the spec above is the lazy.nvim form.",
    source: "https://github.com/selvage-protocol/nvim_client",
  },
  {
    id: "web",
    label: "Browser",
    Icon: Globe,
    lines: [
      { text: `# point an editor at wss://${DEMO}`, comment: true },
      { prompt: "›", text: DEMO },
      { text: "# the invite a host sends opens in the page", comment: true },
    ],
    copy: DEMO,
    announce: "Browser address",
    note: "Guests need nothing installed.",
    source: "https://github.com/selvage-protocol/web_client",
  },
];

export function SetupTerminal() {
  const [active, setActive] = useState(TABS[0].id);
  /* Which edge of the strip has a tab past it. Four tabs are wider than a phone's panel, and
     this is what says so: the clipped label on its own reads as a mistake. */
  const [edges, setEdges] = useState({ left: false, right: false });
  const strip = useRef<HTMLDivElement>(null);
  const { copied, copy } = useCopy<string>();

  useEffect(() => {
    const el = strip.current;
    if (!el) return;
    let live = true;
    const measure = () => {
      if (!live) return;
      const left = el.scrollLeft > 1;
      const right = el.scrollLeft + el.clientWidth < el.scrollWidth - 1;
      setEdges((was) =>
        was.left === left && was.right === right ? was : { left, right },
      );
    };
    measure();
    el.addEventListener("scroll", measure, { passive: true });
    /* A rotation or a wider panel moves the strip's own box, and the labels' face arrives
       after the first paint, so the row is measured again when it is in. */
    const watched = new ResizeObserver(measure);
    watched.observe(el);
    document.fonts?.ready.then(measure, () => {});
    return () => {
      live = false;
      el.removeEventListener("scroll", measure);
      watched.disconnect();
    };
  }, []);

  /* The tab a reader picks has to be the one in view: the strip is wider than its panel on a
     phone, so the tab at either end sits clipped at the edge until it is scrolled to. */
  function select(id: string) {
    setActive(id);
    const tab = document.getElementById(`install-tab-${id}`);
    tab?.scrollIntoView({ inline: "nearest", block: "nearest" });
    return tab;
  }

  /* The strip is one tab stop: arrows move between tabs, Home and End go to the
     ends, and the tab that becomes selected is the one the focus follows. */
  function onKeyDown(event: KeyboardEvent<HTMLDivElement>) {
    const last = TABS.length - 1;
    const at = TABS.findIndex((tab) => tab.id === active);
    let next = -1;
    if (event.key === "ArrowRight") next = at === last ? 0 : at + 1;
    else if (event.key === "ArrowLeft") next = at === 0 ? last : at - 1;
    else if (event.key === "Home") next = 0;
    else if (event.key === "End") next = last;
    if (next < 0) return;
    event.preventDefault();
    select(TABS[next].id)?.focus();
  }

  return (
    <div className="terminal">
      <div className="tab-strip">
        {edges.left && <span className="tab-fade tab-fade-left" aria-hidden="true" />}
        <div
          className="tabs"
          role="tablist"
          aria-label="Install routes"
          ref={strip}
          onKeyDown={onKeyDown}
        >
          {TABS.map((tab) => (
            <button
              key={tab.id}
              type="button"
              role="tab"
              id={`install-tab-${tab.id}`}
              aria-selected={tab.id === active}
              aria-controls={`install-panel-${tab.id}`}
              tabIndex={tab.id === active ? 0 : -1}
              className="tab"
              onClick={() => select(tab.id)}
            >
              <tab.Icon className="tab-icon" aria-hidden="true" />
              {tab.label}
            </button>
          ))}
        </div>
        {edges.right && <span className="tab-fade tab-fade-right" aria-hidden="true" />}
      </div>
      {TABS.map((tab) => (
        <div
          key={tab.id}
          id={`install-panel-${tab.id}`}
          role="tabpanel"
          aria-labelledby={`install-tab-${tab.id}`}
          hidden={tab.id !== active}
        >
          <div className="term-output">
            <button
              type="button"
              className="term-copy"
              onClick={() => copy(tab.id, tab.copy)}
            >
              <Copy className="icon-14" aria-hidden="true" />
              {copied === tab.id ? "Copied" : "Copy"}
            </button>
            <span role="status" className="sr-only">
              {copied === tab.id ? `${tab.announce} copied` : ""}
            </span>
            {tab.lines.map((line, at) => (
              <div key={at} className="term-line">
                <span className="term-prompt">{line.prompt ?? ""}</span>
                <span className={line.comment ? "term-text term-comment" : "term-text"}>
                  {line.text}
                </span>
              </div>
            ))}
          </div>
          <div className="term-note">
            <Info className="term-info" aria-hidden="true" />
            <span className="term-note-text">{tab.note}</span>
            <a className="source-link" href={tab.source}>
              Source
              <ArrowUpRight className="icon-14" aria-hidden="true" />
            </a>
          </div>
        </div>
      ))}
    </div>
  );
}
