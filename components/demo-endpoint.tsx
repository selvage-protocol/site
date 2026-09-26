"use client";

import { Copy } from "lucide-react";
import { useCopy } from "@/lib/use-copy";
import { DEMO } from "@/lib/selvage";

/** The instance an editor points at, with the one control the card needs: the host a
    reader pastes into a client, on the clipboard. */
export function DemoEndpoint() {
  const { copied, copy } = useCopy<"endpoint">();
  return (
    <>
      <button
        type="button"
        className="copy-host"
        onClick={() => copy("endpoint", DEMO)}
      >
        {DEMO}
        <span className="copy-host-label">
          <Copy className="icon-14" aria-hidden="true" />
          {copied === "endpoint" ? "Copied" : "Copy"}
        </span>
      </button>
      <span role="status" className="sr-only">
        {copied === "endpoint" ? "Demo address copied" : ""}
      </span>
    </>
  );
}
