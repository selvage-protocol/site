"use client";

import { Copy } from "lucide-react";
import { useCopy } from "@/lib/use-copy";

/** The instance an editor points at, with the one control the card needs: the host a
    reader pastes into a client, on the clipboard. */
const HOST = "selvage-demo.dontblameme.dev";

export function DemoEndpoint() {
  const { copied, copy } = useCopy<"endpoint">();
  return (
    <button
      type="button"
      className="copy-host"
      onClick={() => copy("endpoint", HOST)}
    >
      {HOST}
      <span className="copy-host-label">
        <Copy className="icon-14" aria-hidden="true" />
        {copied === "endpoint" ? "Copied" : "Copy"}
      </span>
    </button>
  );
}
