#!/usr/bin/env node
// The browser proof for the page's Content-Security-Policy, and for the one behaviour that
// silently depends on it.
//
// scripts/check-csp.py decides the policy against the page's markup in the gate, but a model
// cannot see whether a browser enforces it the way the model assumes: a policy that refuses the
// page's chunks and its inline bootstrap leaves `window.__next_f` undefined, so the page never
// hydrates and SiteHeader's hide-on-scroll does nothing while the accessibility floor describes
// it working. A refused font fails more
// quietly: the model decides `font-src` against the preloads the page carries, and
// only a run like this one can say the glyph files came back rather than the fallback stack.
//
// So this runs one. It serves the built page through a proxy that applies the `headers` block
// out of `vercel.json` (`next start` does not apply it — only the host does), drives headless
// Chromium over CDP, and asserts:
//
//   1. the document response carries the policy from vercel.json, verbatim;
//   2. zero `securitypolicyviolation` events, collected as they happen rather than inferred,
//      with a font named in one of them reported as what it is: `font-display: swap` paints the
//      fallback stack, so refused glyphs read as a typographic choice rather than as a break;
//   3. `window.__next_f` is an object, so the inline bootstrap ran, and the page's scripts
//      therefore executed;
//   4. the page's own fonts arrived: both families resolve, and the body's computed family is
//      Geist rather than the fallback the stack falls back to. `scripts/check-csp.py` decides
//      `font-src` against the preloads, which is a model of the policy; only a browser can say
//      the glyph files were fetched and used;
//   5. the header conceals itself when the page is scrolled down and comes back when it is
//      scrolled up — the React effect, which only runs once the page hydrates. The concealed
//      class is asserted absent from the served bytes first, so what is observed is the
//      effect, not the prerender. React has to be on the node before the scroll, and the
//      scroll is a reader's movement down rather than one jump: the effect records the position
//      it sees when it attaches, so a single jump made before it attaches is a scroll it never
//      hears, which is what this looked like on a machine slower than the one it was written on;
//   6. the document response carries no `X-Powered-By` (next.config.ts's `poweredByHeader`);
//   7. a request for a path no route claims, which is the other page this policy covers, carries
//      zero violations too. The framework's own 404 document carries a `<style>` element and four
//      `style` attributes and `style-src 'self'` refuses all five, which is why this route has to
//      be checked too: `app/not-found.tsx` is styled from `style.css` instead.
//
// It needs a Chromium, which the runner image carries; `scripts/ci-local.sh csp` finds one on
// `PATH` and runs this after the model, and `.github/workflows/ci.yml` runs that same command.
// Every wait is a bounded poll for the state being waited for, so a page that never hydrates
// fails here instead of passing slowly. A failure at or after the hydration step carries the
// page's own state and console, because "the scripts never ran", "hydration did not finish
// inside the wait", "the scroll never moved" and "the effect never fired" share a symptom and
// not a cause.
//
//   npm run build
//   CHROMIUM=/path/to/chromium node scripts/check-csp-browser.mjs
//
// `VERCEL_JSON` points it at another policy file, the same override scripts/check-csp.py takes,
// so it can be run against the policy that caused the defect: that run has to fail.
// `CSP_DEBUG_DEADLINE` is the seconds it waits for the browser's debugging port (30 otherwise).
//
// Exit 0 prints what was observed. Exit 1 names the assertion that failed. Exit 2 means the
// check could not run at all — no Chromium, no build, a port already in use, or a browser that
// never opened its debugging port — and the last of those prints the browser's own account of
// itself rather than only what this check saw, because the two are not the same failure. Exit 2 is
// a failure, not a pass.

import { spawn, spawnSync } from "node:child_process";
import { readFileSync, existsSync, mkdirSync, rmSync } from "node:fs";
import { createServer, request as httpRequest } from "node:http";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const root = dirname(dirname(fileURLToPath(import.meta.url)));
const PORT = Number(process.env.CSP_PORT || 3210); // proxy: the page under its real headers
const UPSTREAM = Number(process.env.CSP_UPSTREAM || 3211); // the built page, via next start
const WINDOW = "1000,900";
// Two bounds over one page state — React reaching the header, then its scroll effect answering a
// scroll — and neither is a sleep. The idle machine this was written on has React on the node by
// the time the load event fires and the conceal 25 ms after a scroll; one starved core was enough
// to move hydration past a scroll made half a second after the load event, and the same
// starvation left a scroll made right after React's mark unheard. 30 s is hundreds of times the
// idle answer and still ends the check with a report rather than hanging it.
const HYDRATION_DEADLINE_SECONDS = 30;
const CONCEAL_DEADLINE_SECONDS = 30;
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

// A child's own words are the only account of why it did not do what it was started for, so the
// end of each stream is kept rather than drained. Bounded: a browser session is chatty, and what a
// reader of a failure needs is how it ended, not how it began.
const STREAM_TAIL_BYTES = 8 * 1024;

function capture(stream) {
  const captured = { chunks: [], bytes: 0 };
  stream.on("data", (chunk) => {
    captured.bytes += chunk.length;
    captured.chunks.push(chunk);
    let held = captured.chunks.reduce((total, part) => total + part.length, 0);
    while (held > STREAM_TAIL_BYTES && captured.chunks.length > 1) held -= captured.chunks.shift().length;
    // A single write larger than the tail is trimmed inside the chunk: the loop above stops at the
    // last chunk, so a browser that writes a burst in one piece would otherwise keep it whole.
    if (held > STREAM_TAIL_BYTES) captured.chunks[0] = captured.chunks[0].subarray(-STREAM_TAIL_BYTES);
  });
  return captured;
}

// The last `budget` UTF-8 bytes of `text`, cut at a character boundary so the decode adds nothing
// back: a cut inside a character decodes the fragment to U+FFFD and overshoots the bound.
function tailWithinBytes(text, budget) {
  const encoded = Buffer.from(text, "utf8");
  if (encoded.length <= budget) return text;
  let start = encoded.length - budget;
  while (start < encoded.length && (encoded[start] & 0xc0) === 0x80) start += 1;
  return encoded.subarray(start).toString("utf8");
}

function capturedText(captured) {
  const kept = Buffer.concat(captured.chunks);
  let text = kept.toString("utf8").trim();
  if (!text) return null;
  const dropped = captured.bytes - kept.length;
  const marker = dropped > 0 ? `[${dropped} earlier byte(s) dropped]\n` : "";
  // The bound is on what the reader is handed, marker included, so the text is cut to what the
  // marker leaves rather than to a byte count the marker then pushes back over.
  const budget = Math.max(STREAM_TAIL_BYTES - Buffer.byteLength(marker, "utf8"), 0);
  if (Buffer.byteLength(text, "utf8") > budget) text = tailWithinBytes(text, budget);
  return `${marker}${text}`;
}

function spawnChild(command, args, options = {}) {
  const child = spawn(command, args, { stdio: ["ignore", "pipe", "pipe"], ...options });
  child.stdoutTail = capture(child.stdout);
  child.stderrTail = capture(child.stderr);
  child.exit = null;
  child.failure = null;
  child.closed = false;
  child.on("error", (error) => {
    child.failure = error;
  });
  child.on("exit", (code, signal) => {
    child.exit = { code, signal };
  });
  child.on("close", () => {
    child.closed = true;
  });
  children.push(child);
  return child;
}

// The exit event arrives before the last of a child's output does, so a report built the moment
// the process is gone can miss the line that explains it. Bounded, not a sleep-and-hope: a child
// that has not closed its streams by then is reported as it stands.
async function settle(child, milliseconds = 500) {
  const deadline = Date.now() + milliseconds;
  while (!child.closed && Date.now() < deadline) await sleep(25);
}

function describeChild(child) {
  if (child.failure) return `could not be executed (${child.failure.code ?? child.failure.message})`;
  if (!child.exit) return `still running as pid ${child.pid}`;
  const code = child.exit.code === null ? "no exit code" : `exit code ${child.exit.code}`;
  return child.exit.signal ? `${code}, killed by ${child.exit.signal}` : code;
}

// Asked of the binary itself. It is what the runner image's own browser test asserts, and it
// separates "this binary runs and something after it does not" from "this binary does not run".
function selfReportedVersion(command) {
  const probe = spawnSync(command, ["--version"], { timeout: 5_000, encoding: "utf8", maxBuffer: 128 * 1024 });
  if (probe.error) return `--version did not answer (${probe.error.code ?? probe.error.message})`;
  const said = `${probe.stdout ?? ""}${probe.stderr ?? ""}`.trim().split("\n").filter(Boolean).join(" | ");
  if (probe.status !== 0) return `--version exited ${probe.status}${said ? ` and said ${said}` : " with nothing on its streams"}`;
  return said || "--version exited 0 with nothing on its streams";
}

// A reading of what the browser said, printed beside the words themselves so that a wrong reading
// is visible. The shapes are the ones a launch actually fails in: a binary that cannot run at all,
// a library it needs and does not have, a sandbox refusal, a flag it will not take, a wrapper that
// exits before the browser starts, and a browser that starts and never listens.
function readFailure(child, bound) {
  const said = [capturedText(child.stderrTail), capturedText(child.stdoutTail)].filter(Boolean).join("\n");
  if (child.failure) return "the binary is not executable: the path is wrong, it is not a program, or it is not one for this machine";
  if (/error while loading shared libraries|cannot open shared object file|Failed to load (?:NSS|shared)/i.test(said))
    return "a library the browser needs is missing, so it stopped before it could listen";
  if (/No usable sandbox|Failed to move to new namespace|Cannot create user namespace|sandbox[^\n]*fail/i.test(said))
    return "the sandbox refused to start it, which --no-sandbox did not talk it out of";
  if (/unknown flag|unrecognized|bad flag|Unsupported (?:flag|command line)/i.test(said))
    return "the browser refused a flag as one it does not know, so the launch needs a different one";
  if (child.exit?.code === 0 && !child.exit.signal)
    return "the binary exited 0 without listening, which is a wrapper that hands the job to another program rather than the browser itself";
  if (child.exit) return "the browser ended before it listened, and the words above are all it left";
  if (bound) return `the browser bound port ${bound} by its own account, so what failed is this check reaching it rather than the browser starting`;
  return "the browser is still running and never bound the port, so what failed is the wait or the bind rather than the process";
}

function reportBrowser(command, child, observed, bound) {
  const lines = [
    `  binary     : ${command}`,
    `  version    : ${selfReportedVersion(command)}`,
    `  process    : ${describeChild(child)}`,
    `  endpoint   : ${observed}`,
  ];
  const announced = /^DevTools listening on (\S+)$/m.exec(capturedText(child.stderrTail) ?? "")?.[1];
  if (announced) lines.push(`  devtools   : the browser announced ${announced}, not the endpoint this check waited on`);
  lines.push(`  diagnosis  : ${readFailure(child, bound)}`);
  for (const [label, stream] of [["stdout", child.stdoutTail], ["stderr", child.stderrTail]]) {
    const text = capturedText(stream);
    lines.push(`  ${label}     : ${text ? `the browser's own words, last ${STREAM_TAIL_BYTES / 1024} KiB` : "(nothing)"}`);
    if (text) for (const line of text.split("\n")) lines.push(`      ${line}`);
  }
  return lines.join("\n");
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
    `CHROMIUM must name a Chromium binary (got ${chromium ?? "nothing"}). ` +
      "scripts/ci-local.sh csp finds one on PATH when it is not set, and a host without one " +
      "cannot run this proof",
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
// The wait is a bound, not a guess: what the browser was doing when it expired is what gets
// reported. Chrome opens this port in about a second on an idle machine, and a runner is not one.
const debugDeadlineSeconds = Number(process.env.CSP_DEBUG_DEADLINE || 30);

// The browser the runner image carries and the one its fallback installs both take these flags as
// they stand: the Chromium snapshot the image installs (`Chromium 154.0.8037.0`, snapshot revision
// 1689397) and Google's own 154 build (Chrome for Testing 154.0.8037.92) each open the debugging
// port under this exact invocation.
const browser = spawnChild(chromium, [
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
let attempts = 0;
let observed = `127.0.0.1:${debugPort} was never asked`;
const waitedFrom = Date.now();
for (;;) {
  attempts += 1;
  try {
    const res = await fetch(`http://127.0.0.1:${debugPort}/json/version`);
    if (res.ok) {
      version = await res.json();
      break;
    }
    observed = `127.0.0.1:${debugPort} answered /json/version with HTTP ${res.status}`;
  } catch (error) {
    const reason = error.cause?.code ?? error.cause?.message ?? error.message ?? error.name;
    observed = `127.0.0.1:${debugPort} would not answer /json/version (${reason})`;
  }
  // A process that is already gone will not open the port later, so this reports what it said
  // instead of spending the rest of the deadline on a browser that has exited.
  if (browser.failure || browser.exit) break;
  if (Date.now() - waitedFrom > debugDeadlineSeconds * 1000) {
    observed += `, and did so until the ${debugDeadlineSeconds}s deadline`;
    break;
  }
  await sleep(100);
}
if (!version) {
  if (browser.failure || browser.exit) await settle(browser);
  const waited = ((Date.now() - waitedFrom) / 1000).toFixed(1);
  // The browser writes the port it bound into the profile, and announces the endpoint on stderr:
  // either one is the difference between "it listened somewhere this check did not look" and "it
  // never listened at all".
  const activePortFile = join(profile, "DevToolsActivePort");
  const bound = existsSync(activePortFile)
    ? readFileSync(activePortFile, "utf8").split("\n")[0].trim() || null
    : null;
  if (bound) observed += `; the profile's DevToolsActivePort names port ${bound}`;
  giveUp(
    `CHROMIUM never opened a debugging port (${attempts} attempt(s) over ${waited}s)\n${reportBrowser(chromium, browser, observed, bound)}`,
  );
}

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
// The page's own account of a hydration that went wrong arrives as a console error or warning,
// and it is the one thing no assertion here can reconstruct. Bounded to the last few of those.
const consoleTail = [];
const CONSOLE_TAIL_LINES = 10;
let quietConsoleLines = 0;
function recordConsole(level, text) {
  if (!text) return;
  if (level !== "warning" && level !== "error") {
    quietConsoleLines += 1;
    return;
  }
  consoleTail.push(`${level}: ${text}`);
  if (consoleTail.length > CONSOLE_TAIL_LINES) consoleTail.shift();
}
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
  if (message.method === "Runtime.consoleAPICalled") {
    recordConsole(message.params.type, message.params.args?.map((a) => a.value ?? a.description ?? "").join(" "));
  }
  if (message.method === "Log.entryAdded") recordConsole(message.params.entry?.level, message.params.entry?.text);
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

// What the page was in when an assertion about it failed. "The scripts never ran", "hydration
// did not finish inside the wait", "the scroll never moved" and "the effect never fired" all wear
// one symptom from the outside and leave different states here.
async function pageReport() {
  let state;
  try {
    state = JSON.parse(
      await evaluate(`JSON.stringify({
        readyState: document.readyState,
        nextF: typeof window.__next_f,
        header: (() => {
          const el = document.querySelector('header.site-header');
          if (!el) return null;
          return {
            classes: el.className,
            translate: getComputedStyle(el).translate,
            reactKeys: Object.keys(el).filter((key) => key.startsWith('__react')).length,
          };
        })(),
        scrollY: window.scrollY,
        viewport: window.innerHeight,
        height: document.documentElement.scrollHeight,
      })`),
    );
  } catch (error) {
    return `  page       : could not be read (${error.message})`;
  }
  const lines = [
    `  page       : readyState ${state.readyState}, window.__next_f is ${state.nextF}, ` +
      `scrollY ${state.scrollY} of ${Math.max(0, state.height - state.viewport)} ` +
      `(viewport ${state.viewport}, document ${state.height})`,
  ];
  if (state.header === null) {
    lines.push("  header     : not in the document");
  } else {
    lines.push(
      `  header     : ${state.header.reactKeys > 0 ? "hydrated" : "not hydrated"}, ` +
        `class "${state.header.classes}", translate ${state.header.translate}`,
    );
  }
  lines.push(
    consoleTail.length > 0
      ? `  console    : last ${consoleTail.length} warning(s) and error(s)\n${consoleTail
          .map((line) => `      ${line}`)
          .join("\n")}`
      : `  console    : no warning or error, ${quietConsoleLines} quieter line(s)`,
  );
  return lines.join("\n");
}

// Every assertion about the page, from the hydration step on, fails with this: the state that
// tells those four shapes apart is cheaper to print than to guess at from a job log later.
async function failWithPage(message) {
  fail(`${message}\n${await pageReport()}`);
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
// A refused font is named before the generic assertion below, because it is the one refusal a
// page can carry without looking broken: `font-display: swap` draws the fallback stack in the
// same layout, so the reader sees a font choice rather than a page that failed to load.
const fontRefusals = seen.filter(
  (violation) =>
    /font/i.test(violation.directive ?? "") || /\.woff2?(\?|$)/i.test(violation.blockedURI ?? ""),
);
if (fontRefusals.length > 0) {
  for (const violation of fontRefusals) {
    console.error(`  refused: ${violation.directive} ${violation.blockedURI}`);
  }
  fail(
    `the policy refuses the page's own fonts: ${fontRefusals.length} securitypolicyviolation ` +
      `event(s) naming a font, on ${where}. The glyph files are served from this origin, which ` +
      "is what `font-src 'self'` permits",
  );
}
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

// 4. the page's own fonts arrived. A family that fell back to the system stack paints in the
// same layout, so the glyph files are only observable by asking for them: `check` reports false
// while a face the family name needs is unloaded, and true only once it is loaded. The poll is
// bounded, so a face that never settles fails here rather than passing slowly.
const fontsSettled = await waitFor("[...document.fonts].every((face) => face.status !== 'loading')", 10);
if (!fontsSettled) fail("the page's font faces never finished loading");
const fonts = JSON.parse(
  await evaluate(`JSON.stringify({
    geist: document.fonts.check('16px Geist', 'Selvage'),
    mono: document.fonts.check('16px "JetBrains Mono"', 'selvage/2'),
    loaded: [...document.fonts]
      .filter((face) => face.status === 'loaded')
      .map((face) => face.family.replace(/["']/g, '')),
    body: getComputedStyle(document.body).fontFamily,
  })`),
);
for (const family of ["Geist", "JetBrains Mono"]) {
  if (!fonts.loaded.includes(family)) {
    fail(`${family} never loaded: the stylesheet's face for it was refused or has no glyph file`);
  }
}
if (!fonts.geist) {
  fail("Geist does not resolve on the page: the glyph file was refused or never loaded");
}
if (!fonts.mono) {
  fail('JetBrains Mono does not resolve on the page: the glyph file was refused or never loaded');
}
if (!/^["']?Geist["']?(\s*,|$)/.test(fonts.body)) {
  fail(`the body's computed font family is ${fonts.body}, not Geist: the theme's font variable did not resolve`);
}

// 5. the header's hide-on-scroll, which is the React effect. The served bytes are checked
// first, so what is observed afterwards is the effect and not the prerender.
const servedHtml = await (await fetch(where)).text();
if (servedHtml.includes("-translate-y-full")) {
  fail("the served HTML already carries -translate-y-full, so the concealment is not the effect");
}

// The effect is attached once the page hydrates, which the load event does not wait for, and the
// mark React leaves on the node it hydrated is the only account of that the DOM gives. The wait
// is the point of this step: without it the scroll below can be made into the gap before the
// listener exists, and the effect then records that position as the one it starts from.
const hydrated = await waitFor(
  `(() => {
    const el = document.querySelector('header.site-header');
    return el ? Object.keys(el).some((key) => key.startsWith('__react')) : false;
  })()`,
  HYDRATION_DEADLINE_SECONDS,
);
if (!hydrated) {
  await failWithPage(
    `the page never hydrated: no React mark appeared on the header in ${HYDRATION_DEADLINE_SECONDS}s, so the ` +
      "page's own scripts either never ran or threw",
  );
}

const CONCEALED = "document.querySelector('header.site-header').className.includes('-translate-y-full')";
// A reader's movement, not one jump. The listener records the position it sees when it is
// attached, and the passive phase that attaches it lands after the mark above — on the starved
// core this was written against, a scroll made right after that mark was still missed. Every pass
// therefore moves the page further down than the pass before it, so whichever moment the listener
// arrives, the move after it is one it hears; a page with nothing left below is taken back to the
// top first, which is what a reader does too. The conceal is still the effect answering a scroll;
// nothing here sets it.
const pageBelow = await evaluate("Math.max(0, document.documentElement.scrollHeight - window.innerHeight)");
if (pageBelow <= 64) {
  await failWithPage(
    `the page is ${pageBelow}px taller than the viewport, so there is nowhere past the bar's own ` +
      "height to scroll to and its hide-on-scroll cannot be seen at all",
  );
}
const concealDeadline = Date.now() + CONCEAL_DEADLINE_SECONDS * 1000;
let concealed = false;
let concealedAtY = 0;
while (!concealed && Date.now() < concealDeadline) {
  for (const share of [0.25, 0.5, 0.75, 1]) {
    const top = Math.min(pageBelow, Math.max(65, Math.round(pageBelow * share)));
    await evaluate(`window.scrollTo({ top: ${top}, behavior: 'instant' })`);
    // A scroll the browser accepts and does not make would leave every observation below
    // meaningless, so what the conceal is read against is the page's own position.
    const y = await evaluate("window.scrollY");
    if (y <= 64) {
      await failWithPage(`a scroll to ${top}px left window.scrollY at ${y}, so the page never moved past the bar`);
    }
    concealed = await waitFor(CONCEALED, 2);
    if (concealed) {
      concealedAtY = y;
      break;
    }
    if (Date.now() > concealDeadline) break;
  }
  if (!concealed) await evaluate("window.scrollTo({ top: 0, behavior: 'instant' })");
}
if (!concealed) {
  await failWithPage(
    `the header never concealed itself while the page was scrolled down and down again for ` +
      `${CONCEAL_DEADLINE_SECONDS}s, so the effect is not answering a scroll`,
  );
}
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
const returnedAtY = await evaluate("window.scrollY");
if (!moved) await failWithPage(`the header's translate settled at ${concealedTranslate}, not 0px -100%`);
if (!returned) await failWithPage("the header stayed concealed when scrolled back up");

// 6. no framework banner on the document response
const banner = Object.keys(document_?.headers ?? {}).some((key) => key.toLowerCase() === "x-powered-by");
if (banner) await failWithPage("the document response carries X-Powered-By: next.config.ts should have stopped it");

// 7. the site's own not-found route, served with the same policy. Asserted separately from the
// page above because it is a different document with different markup: the framework's default
// 404 is styled with a `<style>` element and four `style` attributes, every one of which
// `style-src 'self'` refuses, and nothing looked at this route before.
const refusalsBeforeNotFound = refusals.length;
loaded = false;
await send("Page.navigate", { url: `http://127.0.0.1:${PORT}/no-such-path` }, sessionId);
for (let i = 0; i < 120 && !loaded; i += 1) await sleep(100);
if (!loaded) await failWithPage("a request for an unrouted path never fired a load event");
const notFoundStatus = document_?.status;
if (notFoundStatus !== 404) {
  await failWithPage(`a request for an unrouted path answered ${notFoundStatus}, so it did not render the not-found route`);
}
const notFoundViolations = JSON.parse(await evaluate("JSON.stringify(window.__violations ?? null)"));
if (!Array.isArray(notFoundViolations)) {
  await failWithPage("the violation listener never ran on the not-found route, so this check saw nothing there");
}
if (notFoundViolations.length > 0 || refusals.length > refusalsBeforeNotFound) {
  const lines = notFoundViolations.length > 0
    ? notFoundViolations.map((v) => `${v.directive} ${v.blockedURI}`)
    : refusals.slice(refusalsBeforeNotFound);
  for (const line of lines) console.error(`  refused: ${line}`);
  await failWithPage(
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
  await failWithPage(
    "the not-found route's served document carries an inline style or style attribute, which style-src 'self' refuses",
  );
}

console.log(`check-csp-browser: ${version.Browser}, headless, ${where} served from the build with
  the headers out of ${policyLabel} (a proxy; next start does not apply them)
  policy     : ${served}
  scripts    : ${page.scripts} (${page.external} external, ${page.inline} inline), window.__next_f is an object
  fonts      : Geist and JetBrains Mono loaded and resolve, the body's family is ${fonts.body}
  violations : 0 securitypolicyviolation events, 0 console refusals, none naming a font
  not-found  : /no-such-path answered 404, 0 violations, no inline style or style attribute in its served bytes
  header     : concealed at scrollY ${concealedAtY} (translate: ${concealedTranslate}), back at scrollY ${returnedAtY}
  banner     : no X-Powered-By on the document response
This is a browser, not a model: what it cannot see is the deployed response headers, because
only the host applies them, and what it sees that the model cannot is the fonts themselves.`);

cleanup();
process.exit(0);
