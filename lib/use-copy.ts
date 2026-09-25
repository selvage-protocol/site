"use client";

import { useCallback, useEffect, useRef, useState } from "react";

/** How long a control says `Copied` before it says what it does again. */
const COPIED_MS = 1600;

/**
 * Put `text` on the clipboard.
 *
 * The async clipboard needs a secure context, so it is missing on a plain
 * `http://` development origin; a hidden textarea and the old `execCommand` is
 * what is left there. Rejections are swallowed: a reader who pressed copy gets
 * the label either way, and there is nothing else the page can do about a
 * clipboard the browser refuses.
 */
async function writeClipboard(text: string): Promise<void> {
  try {
    if (navigator.clipboard && window.isSecureContext) {
      await navigator.clipboard.writeText(text);
      return;
    }
  } catch {
    // Fall through to the textarea.
  }
  const field = document.createElement("textarea");
  field.value = text;
  field.setAttribute("readonly", "");
  field.style.position = "fixed";
  field.style.top = "0";
  field.style.left = "0";
  field.style.opacity = "0";
  document.body.appendChild(field);
  field.select();
  try {
    document.execCommand("copy");
  } catch {
    // Nothing left to try.
  }
  field.remove();
}

/**
 * The state one or more copy controls share: which key was copied last, and the
 * button that copies a value under a key. A control reads its own key, so the
 * tab a reader copied from says `Copied` and the others do not.
 */
export function useCopy<Key extends string>() {
  const [copied, setCopied] = useState<Key | null>(null);
  const timer = useRef<number | undefined>(undefined);

  useEffect(() => () => window.clearTimeout(timer.current), []);

  const copy = useCallback((key: Key, text: string) => {
    void writeClipboard(text);
    setCopied(key);
    window.clearTimeout(timer.current);
    timer.current = window.setTimeout(() => setCopied(null), COPIED_MS);
  }, []);

  return { copied, copy };
}
