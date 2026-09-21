#!/usr/bin/env node
// The browser proof for the page's Content-Security-Policy, and for the one behaviour that
// silently depends on it.
//
// scripts/check-csp.py decides the policy against the page's markup in the gate, but a model
// cannot see whether a browser enforces it the way the model assumes — and the defect this file
// exists for was exactly that: `default-src 'none'` with no `script-src` refused all seven
// chunks and all fifteen inline scripts, `window.__next_f` stayed undefined, the page never
// hydrated, and SiteHeader's hide-on-scroll did nothing while the README described it working.
// Nothing in the gate noticed, because nothing ran a browser.
//
// So this runs one. It serves the built page through a proxy that applies the `headers` block
// out of `vercel.json` (`next start` does not apply it — only the host does), drives headless
// Chromium over CDP, and asserts:
//
//   1. the document response carries the policy from vercel.json, verbatim;
//   2. zero `securitypolicyviolation` events, collected as they happen rather than inferred;
//   3. `window.__next_f` is an object, so the inline bootstrap ran, and the page's scripts
//      therefore executed;
//   4. the header conceals itself when the page is scrolled down and comes back when it is
//      scrolled up — the React effect, which only runs once the page hydrates. The concealed
//      class is asserted absent from the served bytes first, so what is observed is the
//      effect, not the prerender;
//   5. the document response carries no `X-Powered-By` (next.config.ts's `poweredByHeader`);
//   6. a request for a path no route claims, which is the other page this policy covers, carries
//      zero violations too. The framework's own 404 document carries a `<style>` element and four
//      `style` attributes and `style-src 'self'` refuses all five, so this route is where the
//      policy was refusing the site: `app/not-found.tsx` is styled from `style.css` instead.
//
// It needs a Chromium and so is not in the workflow; `scripts/ci-local.sh` is what CI runs.
// Every wait is a bounded poll for the state being waited for, so a page that never hydrates
// fails here instead of passing slowly.
//
//   npm run build
//   CHROMIUM=/path/to/chromium node scripts/check-csp-browser.mjs
//
// `VERCEL_JSON` points it at another policy file, the same override scripts/check-csp.py takes,
// so it can be run against the policy that caused the defect: that run has to fail.
//
// Exit 0 prints what was observed. Exit 1 names the assertion that failed. Exit 2 means the
// check could not run at all — no Chromium, no build, or a port already in use — which is a
// failure, not a pass.

import { spawn } from "node:child_process";
import { readFileSync, existsSync, mkdirSync, rmSync } from "node:fs";
import { createServer, request as httpRequest } from "node:http";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const root = dirname(dirname(fileURLToPath(import.meta.url)));
const PORT = Number(process.env.CSP_PORT || 3210); // proxy: the page under its real headers
const UPSTREAM = Number(process.env.CSP_UPSTREAM || 3211); // the built page, via next start
const WINDOW = "1000,900";
const sleep = (ms) => new Promise((r) => setTimeout(r, ms));

function giveUp(message) {
  console.error(`check-csp-browser: ${message}`);
  process.exit(2);
}

function fail(message) {
  console.error(`check-csp-browser: FAILED: ${message}`);
  process.exit(1);
}

const children = [];
function spawnChild(command, args, options = {}) {
  const child = spawn(command, args, { stdio: ["ignore", "ignore", "pipe"], ...options });
  child.stderr.on("data", () => {}); // drained; the messages this check reports are its own
  children.push(child);
  return child;
}
function stopChildren() {
  for (const child of children) {
    try {
      child.kill("SIGKILL");
    } catch {
      /* already gone */
    }
  }
}
process.on("SIGINT", () => {
  stopChildren();
  process.exit(130);
});

const policyFile = process.env.VERCEL_JSON ?? join(root, "vercel.json");
const policyLabel = policyFile.startsWith(`${root}/`) ? policyFile.slice(root.length + 1) : policyFile;
const vercel = JSON.parse(readFileSync(policyFile, "utf8"));
const headers = (vercel.headers ?? [])
  .flatMap((block) => block.headers ?? [])
  .map(({ key, value }) => [key, value]);
const declared = headers.find(([key]) => key.toLowerCase() === "content-security-policy")?.[1];
if (!declared) {
  giveUp(`${policyLabel} declares no Content-Security-Policy; there is nothing to prove here`);
}

const chromium = process.env.CHROMIUM;
if (!chromium || !existsSync(chromium)) {
  giveUp(
    `CHROMIUM must name a Chromium binary (got ${chromium ?? "nothing"}). This host has one ` +
      "under a nix store path; CI has none, which is why this check is not in the workflow",
  );
}
if (!existsSync(join(root, ".next", "BUILD_ID"))) {
  giveUp("no build to serve: run `npm run build` first");
}

async function answers(port) {
  try {
    const res = await fetch(`http://127.0.0.1:${port}/`);
    await res.text();
    return res.status === 200;
  } catch {
    return false;
  }
}

// The same refusal `scripts/ci-local.sh` makes: a 200 from a server this check did not start
// would let it assert against unrelated content.
for (const port of [PORT, UPSTREAM]) {
  if (await answers(port)) {
    giveUp(`127.0.0.1:${port} already answers; refusing a port this check did not bind`);
  }
}

// The page, the way the host serves it.
spawnChild(join(root, "node_modules", ".bin", "next"), ["start", "-p", String(UPSTREAM)], {
  env: { ...process.env, NEXT_TELEMETRY_DISABLED: "1" },
});
let up = false;
for (let i = 0; i < 120 && !up; i += 1) {
  up = await answers(UPSTREAM);
  if (!up) await sleep(500);
}
if (!up) {
  stopChildren();
  giveUp(`next start never answered on ${UPSTREAM}`);
}

// The host's own behaviour: the headers block, applied to every response.
const proxy = createServer((incoming, outgoing) => {
  const upstream = httpRequest(
    { host: "127.0.0.1", port: UPSTREAM, path: incoming.url, method: incoming.method, headers: incoming.headers },
    (response) => {
      const sent = new Set(Object.keys(response.headers));
      const relayed = { ...response.headers };
      for (const [key, value] of headers) if (!sent.has(key.toLowerCase())) relayed[key] = value;
      outgoing.writeHead(response.statusCode ?? 502, relayed);
      response.pipe(outgoing);
    },
  );
  upstream.on("error", () => outgoing.destroy());
  incoming.pipe(upstream);
});
await new Promise((resolve) => proxy.listen(PORT, "127.0.0.1", resolve));

const cleanup = () => {
  proxy.close();
  stopChildren();
};
process.on("exit", cleanup);

// ---- Chromium over CDP ------------------------------------------------------------------

const profile = join(root, ".tmp", "chrome-csp-check");
rmSync(profile, { recursive: true, force: true });
mkdirSync(profile, { recursive: true });
const debugPort = 9333;
spawnChild(chromium, [
  "--headless=new",
  `--remote-debugging-port=${debugPort}`,
  `--user-data-dir=${profile}`,
  "--no-sandbox",
  "--disable-gpu",
  "--disable-dev-shm-usage",
  "--no-first-run",
  "--no-default-browser-check",
  `--window-size=${WINDOW}`,
  "about:blank",
]);

let version = null;
for (let i = 0; i < 100 && !version; i += 1) {
  try {
    const res = await fetch(`http://127.0.0.1:${debugPort}/json/version`);
    if (res.ok) version = await res.json();
  } catch {
    /* not up yet */
  }
  if (!version) await sleep(100);
}
if (!version) giveUp("CHROMIUM never opened a debugging port");

const cdp = { id: 0, pending: new Map(), listeners: [], socket: null };
function send(method, params = {}, sessionId) {
  cdp.id += 1;
  const id = cdp.id;
  return new Promise((resolve, reject) => {
    cdp.pending.set(id, { resolve, reject });
    cdp.socket.send(JSON.stringify({ id, method, params, ...(sessionId ? { sessionId } : {}) }));
  });
}

const refusals = [];
let document_ = null;
let loaded = false;

cdp.socket = new WebSocket(version.webSocketDebuggerUrl);
await new Promise((resolve, reject) => {
  cdp.socket.addEventListener("open", resolve, { once: true });
  cdp.socket.addEventListener("error", reject, { once: true });
});
cdp.socket.addEventListener("message", (event) => {
  const message = JSON.parse(event.data);
  if (message.id && cdp.pending.has(message.id)) {
    const { resolve, reject } = cdp.pending.get(message.id);
    cdp.pending.delete(message.id);
    if (message.error) reject(new Error(JSON.stringify(message.error)));
    else resolve(message.result);
    return;
  }
  if (message.method === "Page.loadEventFired") loaded = true;
  if (message.method === "Network.responseReceived" && message.params.type === "Document") {
    document_ = message.params.response;
  }
  const text = message.params?.entry?.text ?? message.params?.args?.map((a) => a.value ?? "").join(" ");
  if (text && /Refused|Content Security|violat/i.test(text)) refusals.push(text);
});

const { targetId } = await send("Target.createTarget", { url: "about:blank" });
const { sessionId } = await send("Target.attachToTarget", { targetId, flatten: true });
for (const domain of ["Page", "Runtime", "Log", "Network"]) {
  await send(`${domain}.enable`, {}, sessionId);
}
// Registered before the document's own scripts: a violation is recorded when it happens, not
// reconstructed afterwards from a console string.
await send(
  "Page.addScriptToEvaluateOnNewDocument",
  {
    source: `window.__violations = [];
      document.addEventListener('securitypolicyviolation', (event) => window.__violations.push({
        directive: event.effectiveDirective, blockedURI: event.blockedURI, disposition: event.disposition,
      }));`,
  },
  sessionId,
);

const evaluate = async (expression) => {
  const result = await send("Runtime.evaluate", { expression, returnByValue: true, awaitPromise: true }, sessionId);
  if (result.exceptionDetails) fail(`evaluating in the page threw: ${JSON.stringify(result.exceptionDetails)}`);
  return result.result.value;
};

await send("Page.navigate", { url: `http://127.0.0.1:${PORT}/` }, sessionId);
for (let i = 0; i < 120 && !loaded; i += 1) await sleep(100);
if (!loaded) fail("the page never fired a load event");

// Bounded poll for the state under test, so a page that never hydrates fails instead of passing.
async function waitFor(expression, seconds = 5) {
  const deadline = Date.now() + seconds * 1000;
  for (;;) {
    if (await evaluate(expression)) return true;
    if (Date.now() > deadline) return false;
    await sleep(100);
  }
}

const where = `http://127.0.0.1:${PORT}/`;
const info = await evaluate(`JSON.stringify({
  scripts: document.scripts.length,
  external: [...document.scripts].filter((s) => s.src).length,
  inline: [...document.scripts].filter((s) => !s.src).length,
  nextF: typeof window.__next_f,
})`);
const page = JSON.parse(info);

// 1. the policy on the response is the one in vercel.json
const served = Object.entries(document_?.headers ?? {}).find(
  ([key]) => key.toLowerCase() === "content-security-policy",
)?.[1];
if (served !== declared) fail(`the document response carries ${served ?? "no CSP"}, not ${policyLabel}'s ${declared}`);

// 2. zero violations, as the browser recorded them
const seen = JSON.parse(await evaluate("JSON.stringify(window.__violations ?? null)"));
if (!Array.isArray(seen)) fail("the violation listener never ran, so this check saw nothing");
if (seen.length > 0 || refusals.length > 0) {
  // The console lines repeat the structured events one for one, so they are printed only when
  // the listener recorded nothing — a refusal raised before it was installed, or on a page that
  // never ran it. Printing both would double every line of the transcript.
  const lines = seen.length > 0 ? seen.map((v) => `${v.directive} ${v.blockedURI}`) : refusals;
  for (const violation of lines) console.error(`  refused: ${violation}`);
  fail(
    `the page's own policy refuses it: ${seen.length} securitypolicyviolation event(s), ` +
      `${refusals.length} console refusal(s), on ${where}`,
  );
}

// 3. the inline bootstrap ran, so the page's scripts executed
if (page.nextF !== "object") fail(`window.__next_f is ${page.nextF}, not an object: the bootstrap never ran`);

// 4. the header's hide-on-scroll, which is the React effect. The served bytes are checked
// first, so what is observed afterwards is the effect and not the prerender.
const servedHtml = await (await fetch(where)).text();
if (servedHtml.includes("-translate-y-full")) {
  fail("the served HTML already carries -translate-y-full, so the concealment is not the effect");
}
await evaluate("window.scrollTo({ top: 900, behavior: 'instant' })");
const concealed = await waitFor(
  "document.querySelector('header.site-header').className.includes('-translate-y-full')",
);
// The class is applied before the 300 ms transition has moved anything, so the displacement is
// polled to its settled value rather than read once and reported mid-flight.
const moved = await waitFor(
  "getComputedStyle(document.querySelector('header.site-header')).translate === '0px -100%'",
);
const concealedTranslate = await evaluate(
  "getComputedStyle(document.querySelector('header.site-header')).translate",
);
await evaluate("window.scrollTo({ top: 300, behavior: 'instant' })");
const returned = await waitFor(
  "!document.querySelector('header.site-header').className.includes('-translate-y-full')",
);
if (!concealed) fail("the header never concealed itself when scrolled down: the page is not hydrating");
if (!moved) fail(`the header's translate settled at ${concealedTranslate}, not 0px -100%`);
if (!returned) fail("the header stayed concealed when scrolled back up");

// 5. no framework banner on the document response
const banner = Object.keys(document_?.headers ?? {}).some((key) => key.toLowerCase() === "x-powered-by");
if (banner) fail("the document response carries X-Powered-By: next.config.ts should have stopped it");

// 6. the site's own not-found route, served with the same policy. Asserted separately from the
// page above because it is a different document with different markup: the framework's default
// 404 is styled with a `<style>` element and four `style` attributes, every one of which
// `style-src 'self'` refuses, and nothing looked at this route before.
const refusalsBeforeNotFound = refusals.length;
loaded = false;
await send("Page.navigate", { url: `http://127.0.0.1:${PORT}/no-such-path` }, sessionId);
for (let i = 0; i < 120 && !loaded; i += 1) await sleep(100);
if (!loaded) fail("a request for an unrouted path never fired a load event");
const notFoundStatus = document_?.status;
if (notFoundStatus !== 404) {
  fail(`a request for an unrouted path answered ${notFoundStatus}, so it did not render the not-found route`);
}
const notFoundViolations = JSON.parse(await evaluate("JSON.stringify(window.__violations ?? null)"));
if (!Array.isArray(notFoundViolations)) {
  fail("the violation listener never ran on the not-found route, so this check saw nothing there");
}
if (notFoundViolations.length > 0 || refusals.length > refusalsBeforeNotFound) {
  const lines = notFoundViolations.length > 0
    ? notFoundViolations.map((v) => `${v.directive} ${v.blockedURI}`)
    : refusals.slice(refusalsBeforeNotFound);
  for (const line of lines) console.error(`  refused: ${line}`);
  fail(
    `the policy refuses the site's own not-found route: ${notFoundViolations.length} ` +
      `securitypolicyviolation event(s), ${refusals.length - refusalsBeforeNotFound} console refusal(s)`,
  );
}
// The served bytes, not the hydrated DOM: `next-route-announcer` gets its `style` attribute from
// CSSOM after hydration, which CSP does not police, and counting it would report a refusal risk
// where there is none. What the policy sees is the document as it arrives.
const notFoundHtml = await (await fetch(`http://127.0.0.1:${PORT}/no-such-path`)).text();
const inlineStyles = /<style[\s>]/i.test(notFoundHtml) || /\sstyle\s*=/i.test(notFoundHtml);
if (inlineStyles) {
  fail("the not-found route's served document carries an inline style or style attribute, which style-src 'self' refuses");
}

console.log(`check-csp-browser: ${version.Browser}, headless, ${where} served from the build with
  the headers out of ${policyLabel} (a proxy; next start does not apply them)
  policy     : ${served}
  scripts    : ${page.scripts} (${page.external} external, ${page.inline} inline), window.__next_f is an object
  violations : 0 securitypolicyviolation events, 0 console refusals
  not-found  : /no-such-path answered 404, 0 violations, no inline style or style attribute in its served bytes
  header     : concealed at scrollY 900 (translate: ${concealedTranslate}), back at scrollY 300
  banner     : no X-Powered-By on the document response
This is a browser, not a model: what it cannot see is the deployed response headers, because
only the host applies them.`);

cleanup();
process.exit(0);
