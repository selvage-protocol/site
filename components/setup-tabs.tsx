"use client";

import type { KeyboardEvent } from "react";
import { useEffect, useRef, useState } from "react";
import { ArrowUpRight, Copy, Info } from "lucide-react";
import { CLIENTS, repositoryUrl, type InstallLine } from "@/lib/clients";
import { useCopy } from "@/lib/use-copy";

/* The terminal a reader copies from: one route per client that has one, with the command that
   route is, the note a reader needs before running it, and the repository it comes from. The
   panels are the ARIA tabs pattern — one strip, one panel per tab, the inactive ones `hidden` —
   and every panel is in the document, so the page still carries every route for a reader
   without scripting.

   The routes are the client list's own install data, and the tab labels are its chip labels:
   a client is added to the list and its route appears here, rather than being written out a
   second time. */

type Tab = {
  id: string;
  label: string;
  Icon: (typeof CLIENTS)[number]["Icon"];
  source: string;
  lines: InstallLine[];
  copy: string;
  announce: string;
  note: string;
};

/* Only the clients a reader can install have a route: a plan has none, and so has no tab. */
const TABS: Tab[] = CLIENTS.flatMap((client) =>
  client.install
    ? [
        {
          id: client.id,
          label: client.chip,
          Icon: client.Icon,
          source: repositoryUrl(client.repository),
          ...client.install,
        },
      ]
    : [],
);

export function SetupTerminal() {
  const [active, setActive] = useState(TABS[0].id);
  /* Which edge of the strip has a tab past it. Three tabs fit every panel this page is read at
down to 360 px; at 320 the last one is clipped, and the clipped label on its own reads as a
mistake. */
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

  /* The tab a reader picks has to be the one in view: the strip can be wider than its panel, so
     the tab at either end sits clipped at the edge until it is scrolled to. */
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
