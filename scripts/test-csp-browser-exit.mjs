#!/usr/bin/env node
// The exit path of `scripts/check-csp-browser.mjs` is the one thing about it a browser cannot
// prove: whether the children it started were killed and their streams and statuses had settled
// before the process ended. This drives the real check through its CLI — a copy of the real file,
// in a root of its own — with a fake `next` and a fake Chromium, and reads the directory the check
// writes when `CSP_EVIDENCE_DIR` names one.
//
// The fake children are ordinary programs this test writes. Nothing here starts a browser, and the
// only network is 127.0.0.1 on ports the test picked and bound itself. The check is asked to fail
// at the debugging-port wait, which is the first place it has both children running; a regression
// in the cleanup-before-exit would leave a status without a close and a stream tail in place of a
// whole stream, and this would fail rather than pass.
//
// Every failure here unwinds through an awaited cleanup rather than calling `process.exit` where
// the assertion failed: a case that owns a descendant holding a pipe open must still reap it, and
// the exit status is chosen only once the harness has settled. Each fixture's check is started in
// its own process group and every group this run owns is killed on the way out, so an assertion
// that fires in the middle of a case leaves nothing running. The descendants a check cannot reap
// itself end on their own bounded timer, so a harness killed outright still leaves nothing behind.
//
// A self-test run is the one case that owns a tree of its own: this harness starts it as a
// process-group leader and its checkers inherit that group, so the parent owns the whole tree from
// the one pid it launched and takes it down on a failure, an error or its own deadline alike.

import { spawn } from "node:child_process";
import {
  copyFileSync,
  existsSync,
  mkdirSync,
  mkdtempSync,
  readFileSync,
  readdirSync,
  writeFileSync,
} from "node:fs";
import { createServer } from "node:http";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const here = dirname(fileURLToPath(import.meta.url));
const repo = dirname(here);
const selfPath = fileURLToPath(import.meta.url);
const checkerSource = join(here, "check-csp-browser.mjs");
const mode = process.argv[2];
// This file started as a child of the supervisor below is a self-test run. Its checkers must not
// lead groups of their own: they inherit the harness's group so the parent owns the whole tree.
const selfTestMode = typeof mode === "string" && mode.startsWith("--self-test");
// Comfortably past the 8 KiB tail the check keeps for its own report, so a stream that reads whole
// is not a stream that happened to fit in the tail.
const STREAM_BYTES = 12 * 1024;
// A fake that hangs keeps the check waiting; it ends on a bounded timer rather than an interval, so
// a harness killed outright still leaves no process behind. A check that is itself killed cannot
// reap a grandchild, and the held descendant is the one the check does not own.
const LINGER_MS = 120_000;
const holderProgram = `setTimeout(() => {}, ${LINGER_MS});`;

function fail(message) {
  // Thrown, not printed-and-exited: the finally blocks of the case that owns a held pipe run, and
  // the top level turns this into a status only after the whole harness has settled.
  throw new Error(message);
}

function assert(condition, message) {
  if (!condition) fail(message);
}

function sleep(ms) {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

async function freePort() {
  const server = createServer();
  await new Promise((resolve) => server.listen(0, "127.0.0.1", resolve));
  const { port } = server.address();
  await new Promise((resolve) => server.close(resolve));
  return port;
}

async function portFree(port) {
  const server = createServer();
  return new Promise((resolve) => {
    server.on("error", () => resolve(false));
    server.listen(port, "127.0.0.1", () => server.close(() => resolve(true)));
  });
}

async function gone(pid, milliseconds = 3_000) {
  const deadline = Date.now() + milliseconds;
  for (;;) {
    try {
      process.kill(pid, 0);
    } catch (error) {
      if (error.code === "ESRCH") return true;
      throw error;
    }
    if (Date.now() > deadline) return false;
    await sleep(25);
  }
}

async function groupGone(pid, milliseconds = 5_000) {
  if (typeof pid !== "number") return true;
  const deadline = Date.now() + milliseconds;
  for (;;) {
    try {
      process.kill(-pid, 0);
    } catch (error) {
      if (error.code === "ESRCH") return true;
      throw error;
    }
    if (Date.now() > deadline) return false;
    await sleep(25);
  }
}

function killGroup(child, signal = "SIGKILL") {
  if (!child || typeof child.pid !== "number") return;
  try {
    // A detached child leads a group of its own; a supervised self-test's checker has no group of
    // its own, so only the member is killed here and the group owner takes the rest.
    process.kill(selfTestMode ? child.pid : -child.pid, signal);
  } catch (error) {
    if (error.code !== "ESRCH") throw error;
  }
}

// What a live pid is, for the identity check below: uid, command line and start time, so a pid that
// has been reused by an unrelated process is recognised as not ours rather than killed.
function procFacts(pid) {
  try {
    const cmdline = readFileSync(`/proc/${pid}/cmdline`, "utf8").split("\0").filter(Boolean).join(" ");
    const status = readFileSync(`/proc/${pid}/status`, "utf8");
    const uid = /^Uid:\s+(\d+)/m.exec(status)?.[1] ?? null;
    const stat = readFileSync(`/proc/${pid}/stat`, "utf8");
    const fields = stat.slice(stat.lastIndexOf(")") + 2).split(" ");
    return { cmdline, uid, starttime: fields[19] ?? null };
  } catch {
    return null;
  }
}

function writeProgram(path, source) {
  writeFileSync(path, `#!${process.execPath}\n${source}`, { mode: 0o700 });
}

function fakeNext() {
  return `import { createServer } from "node:http";
const args = process.argv.slice(2);
const port = Number(args[args.indexOf("-p") + 1]);
const body = "N".repeat(${STREAM_BYTES});
process.stdout.write(\`\${body}\\n\`);
process.stderr.write(\`\${body}\\n\`);
const server = createServer((request, response) => {
  response.writeHead(200, { "content-type": "text/html; charset=utf-8" });
  response.end("<!doctype html><title>fake</title>");
});
server.listen(port, "127.0.0.1");
// A listening server owns a handle of its own, so it ends itself rather than
// relying on a kill: an owner killed outright cannot reap it, and this bounds how
// long it lingers.
setTimeout(() => process.exit(0), ${LINGER_MS});
`;
}

function fakeChromium() {
  return `const args = process.argv.slice(2);
if (args.length === 1 && args[0] === "--version") {
  process.stdout.write("Fake Chromium 1.0.0\\n");
  process.exit(0);
}
const body = "C".repeat(${STREAM_BYTES});
process.stdout.write(\`\${body}\\n\`);
process.stderr.write(\`\${body}\\n\`);
// Never opens a debugging port; the check is meant to time out on it.
setTimeout(() => {}, ${LINGER_MS});
`;
}

// A descendant that keeps the checker's read ends open: the upstream is killed, but its streams
// never close, so `close` never arrives and the capture is incomplete.
function fakeNextHoldingPipe(pidFile) {
  return `import { spawn } from "node:child_process";
import { writeFileSync } from "node:fs";
import { createServer } from "node:http";
const holder = spawn(process.execPath, ["-e", ${JSON.stringify(holderProgram)}], { stdio: ["ignore", "inherit", "inherit"] });
holder.unref();
writeFileSync(${JSON.stringify(pidFile)}, String(holder.pid));
const args = process.argv.slice(2);
const port = Number(args[args.indexOf("-p") + 1]);
const server = createServer((request, response) => {
  response.writeHead(200, { "content-type": "text/html; charset=utf-8" });
  response.end("<!doctype html><title>fake</title>");
});
server.listen(port, "127.0.0.1");
// A listening server owns a handle of its own, so it ends itself rather than
// relying on a kill: an owner killed outright cannot reap it, and this bounds how
// long it lingers.
setTimeout(() => process.exit(0), ${LINGER_MS});
`;
}

// A browser that announces itself and then never opens the debugging port, so the check waits for
// a signal instead of giving up on the port first.
function fakeChromiumReady(readyFile) {
  return `import { writeFileSync } from "node:fs";
if (process.argv.includes("--version")) {
  process.stdout.write("Fake Chromium 1.0.0\\n");
  process.exit(0);
}
writeFileSync(${JSON.stringify(readyFile)}, "ready\\n");
setTimeout(() => {}, ${LINGER_MS});
`;
}

// Every fixture this run makes, so a failure at any point can still reap each one's descendants.
const fixtures = new Set();
// Every check this run has started and not yet seen close. They are started detached, in a process
// group of their own, so a check the harness has to kill outright can still have its children
// reached through the group.
const checkers = new Set();

// A root the check reads as its own: the real checker under `scripts/`, a build marker, a policy
// file and the two fake children where the check looks for them.
function makeFixture({ next = () => fakeNext(), chromium = () => fakeChromium() } = {}) {
  const fixture = mkdtempSync(join(repo, ".tmp", "csp-browser-exit-"));
  fixtures.add(fixture);
  mkdirSync(join(fixture, "scripts"));
  copyFileSync(checkerSource, join(fixture, "scripts", "check-csp-browser.mjs"));
  mkdirSync(join(fixture, ".next"));
  writeFileSync(join(fixture, ".next", "BUILD_ID"), "test\n");
  writeFileSync(
    join(fixture, "vercel.json"),
    `${JSON.stringify({
      headers: [
        {
          source: "/(.*)",
          headers: [{ key: "Content-Security-Policy", value: "default-src 'self'" }],
        },
      ],
    })}\n`,
  );
  mkdirSync(join(fixture, "node_modules", ".bin"), { recursive: true });
  writeProgram(join(fixture, "node_modules", ".bin", "next"), next(fixture));
  mkdirSync(join(fixture, "bin"));
  writeProgram(join(fixture, "bin", "chromium"), chromium(fixture));
  for (const role of ["home", "temp", "config", "cache", "data", "state", "runtime"]) {
    mkdirSync(join(fixture, "private", role), { recursive: true, mode: 0o700 });
  }
  return fixture;
}

function checkerEnv(fixture, { port, upstream, debug, evidence }) {
  return {
    PATH: "/nonexistent",
    HOME: join(fixture, "private", "home"),
    TMPDIR: join(fixture, "private", "temp"),
    XDG_CONFIG_HOME: join(fixture, "private", "config"),
    XDG_CACHE_HOME: join(fixture, "private", "cache"),
    XDG_DATA_HOME: join(fixture, "private", "data"),
    XDG_STATE_HOME: join(fixture, "private", "state"),
    XDG_RUNTIME_DIR: join(fixture, "private", "runtime"),
    NEXT_TELEMETRY_DISABLED: "1",
    CHROMIUM: join(fixture, "bin", "chromium"),
    CSP_PORT: String(port),
    CSP_UPSTREAM: String(upstream),
    CSP_DEBUG_PORT: String(debug),
    CSP_DEBUG_DEADLINE: "1",
    CSP_EVIDENCE_DIR: evidence,
  };
}

function runChecker(fixture, env, milliseconds = 60_000) {
  return spawnChecker(fixture, env, milliseconds).done;
}

function spawnChecker(fixture, env, milliseconds = 60_000) {
  const child = spawn(process.execPath, [join(fixture, "scripts", "check-csp-browser.mjs")], {
    env,
    // A supervised self-test's checkers share the harness group the parent launched, so the parent
    // owns the whole tree from one pid; a normal run's checkers lead groups of their own.
    detached: !selfTestMode,
  });
  checkers.add(child);
  let stdout = "";
  let stderr = "";
  child.stdout.on("data", (chunk) => (stdout += chunk));
  child.stderr.on("data", (chunk) => (stderr += chunk));
  const done = new Promise((resolve, reject) => {
    const timer = setTimeout(() => {
      // The check did not end on its own; take its whole group down, including any child it started
      // and cannot reap after the kill, before reporting why.
      killGroup(child);
      reject(new Error(`the check did not end within ${milliseconds} ms; stderr was:\n${stderr}`));
    }, milliseconds);
    child.on("error", (error) => {
      clearTimeout(timer);
      checkers.delete(child);
      reject(error);
    });
    child.on("close", (code, signal) => {
      clearTimeout(timer);
      checkers.delete(child);
      resolve({ code, signal, stdout, stderr });
    });
  });
  // A case can throw before it awaits this; the rejection is reported by the harness, not as an
  // unhandled rejection that would take the cleanup down with it.
  done.catch(() => {});
  return { child, done };
}

async function waitForFile(path, milliseconds = 10_000) {
  const deadline = Date.now() + milliseconds;
  while (!existsSync(path)) {
    if (Date.now() > deadline) fail(`the fixture never produced ${path}`);
    await sleep(25);
  }
}

// The descendant that holds the pipe is the only child the check does not own, so the test reaps
// it; every fixture that starts one calls this from a finally. The pid is confirmed to be this
// run's holder before it is signalled, so a reused pid is left alone.
async function reapHolder(fixture) {
  const pidFile = join(fixture, "holder.pid");
  if (!existsSync(pidFile)) return;
  const pid = Number(readFileSync(pidFile, "utf8"));
  if (!Number.isInteger(pid) || pid <= 0) return;
  const facts = procFacts(pid);
  if (facts === null) return;
  if (facts.uid !== String(process.getuid()) || !facts.cmdline.includes(holderProgram)) return;
  try {
    process.kill(pid, "SIGKILL");
  } catch (error) {
    if (error.code !== "ESRCH") throw error;
  }
  assert(await gone(pid), `descendant pid ${pid} survived SIGKILL`);
}

// The last resort for a failure in the middle of a case: kill any check still running, through its
// group so its children go with it, then reap every fixture's held descendant.
async function cleanupOwned() {
  for (const child of [...checkers]) {
    killGroup(child);
    // A supervised self-test's checker is not a group leader; its descendants stay in the parent's
    // group and are taken down with it, so only the member itself is waited on here.
    await (selfTestMode ? gone(child.pid) : groupGone(child.pid));
  }
  for (const fixture of fixtures) await reapHolder(fixture);
}

function readJson(path) {
  return JSON.parse(readFileSync(path, "utf8"));
}

function childDirs(evidence) {
  return readdirSync(evidence)
    .filter((name) => /^\d+-/.test(name))
    .sort();
}

// Case 1: both children are running when the check gives up on the debugging port. This is the
// status that must survive, and the two statuses and two whole streams that must be there with it.
async function debuggingPortFailure() {
  const fixture = makeFixture();
  const port = await freePort();
  const upstream = await freePort();
  const debug = await freePort();
  const evidence = join(fixture, "evidence-debug");
  const env = checkerEnv(fixture, { port, upstream, debug, evidence });
  const result = await runChecker(fixture, env);

  assert(result.code === 2, `the check exited ${result.code} (${result.signal ?? "no signal"}), not 2`);
  assert(
    result.stderr.includes("never opened a debugging port"),
    `the check did not report the debugging-port wait; stderr was:\n${result.stderr}`,
  );

  const requested = readJson(join(evidence, "requested-exit.json"));
  assert(requested.code === 2, `the requested status was ${requested.code}, not 2`);

  const dirs = childDirs(evidence);
  assert(dirs.length === 2, `the evidence names ${dirs.length} child(ren), not 2: ${dirs.join(", ")}`);
  const labels = dirs.map((name) => name.replace(/^\d+-/, ""));
  assert(labels.includes("upstream") && labels.includes("chromium"), `unexpected child labels: ${labels.join(", ")}`);

  const expected = { upstream: "N".repeat(STREAM_BYTES), chromium: "C".repeat(STREAM_BYTES) };
  for (const dir of dirs) {
    const label = dir.replace(/^\d+-/, "");
    const path = join(evidence, dir);
    const status = readJson(join(path, "status.json"));
    assert(status.exit !== null, `${label}: no exit status at all`);
    assert(status.close !== null, `${label}: no close status, so the streams were not settled before exit`);
    assert(status.close.signal === "SIGKILL", `${label}: closed by ${status.close.signal ?? "no signal"}, not SIGKILL`);
    assert(await gone(status.pid), `${label}: pid ${status.pid} is still running, so it was not reaped`);
    for (const stream of ["stdout", "stderr"]) {
      const whole = readFileSync(join(path, stream));
      const wanted = Buffer.from(`${expected[label]}\n`, "utf8");
      assert(
        whole.length === wanted.length,
        `${label} ${stream}: ${whole.length} bytes retained, not the whole ${wanted.length}`,
      );
      assert(whole.equals(wanted), `${label} ${stream}: the retained bytes are not the child's whole stream`);
    }
  }
  return fixture;
}

// Case 2: the failure lands before any child is started — the proxy port already answers. The
// requested status must still be recorded, and no child status may be invented for a child that
// was never run.
async function occupiedPortFailure() {
  const fixture = makeFixture();
  const port = await freePort();
  const upstream = await freePort();
  const debug = await freePort();
  const evidence = join(fixture, "evidence-occupied");
  const squatter = createServer((request, response) => {
    response.writeHead(200, { "content-type": "text/html" });
    response.end("not this check");
  });
  await new Promise((resolve) => squatter.listen(port, "127.0.0.1", resolve));
  try {
    const env = checkerEnv(fixture, { port, upstream, debug, evidence });
    const result = await runChecker(fixture, env);
    assert(result.code === 2, `the port-occupied check exited ${result.code}, not 2`);
    assert(result.stderr.includes("already answers"), `the check did not report the answered port; stderr was:\n${result.stderr}`);
    const requested = readJson(join(evidence, "requested-exit.json"));
    assert(requested.code === 2, `the requested status was ${requested.code}, not 2`);
    assert(childDirs(evidence).length === 0, "a child status was written although no child was started");
  } finally {
    await new Promise((resolve) => squatter.close(resolve));
  }
  return fixture;
}

// Evidence that cannot be written must fail closed: a run that cannot record where it was does not
// read as a clean one. The requested status is written before the children, so it survives a
// failure to retain them.
async function evidenceFailureIsFailClosed() {
  const fixture = makeFixture();
  const port = await freePort();
  const upstream = await freePort();
  const debug = await freePort();
  const evidence = join(fixture, "evidence-blocked");
  mkdirSync(evidence, { mode: 0o700 });
  // The first child's directory is a plain file: the status can be recorded, the child cannot.
  writeFileSync(join(evidence, "0-upstream"), "not a directory\n");
  const env = checkerEnv(fixture, { port, upstream, debug, evidence });
  const result = await runChecker(fixture, env);
  assert(result.code === 74, `the check exited ${result.code}, not 74, when its child evidence could not be written`);
  const requested = readJson(join(evidence, "requested-exit.json"));
  assert(requested.code === 2, `the requested status was lost with the evidence: ${requested.code}, not 2`);
  return fixture;
}

// Case 4: a child's own descendant keeps its pipe open, so `close` never arrives inside the
// settle. The capture is incomplete: the check must fail closed with 74 while the status it asked
// for stays readable, and it must not invent a close for a stream that never closed.
async function incompleteCaptureFailsClosed() {
  const fixture = makeFixture({ next: (f) => fakeNextHoldingPipe(join(f, "holder.pid")) });
  try {
    const port = await freePort();
    const upstream = await freePort();
    const debug = await freePort();
    const evidence = join(fixture, "evidence-held");
    const env = checkerEnv(fixture, { port, upstream, debug, evidence });
    const result = await runChecker(fixture, env);
    assert(result.code === 74, `the check exited ${result.code} (${result.signal ?? "no signal"}), not 74, with a child's streams still open`);
    const requested = readJson(join(evidence, "requested-exit.json"));
    assert(requested.code === 2, `the requested status was ${requested.code}, not 2`);
    const held = readJson(join(evidence, "0-upstream", "status.json"));
    assert(held.exit !== null, "upstream: no exit status at all");
    assert(held.close === null, "upstream: a close status was invented although its streams never closed");
    const chromium = readJson(join(evidence, "1-chromium", "status.json"));
    assert(chromium.close !== null, "chromium: no close status, so the streams were not settled before exit");
  } finally {
    await reapHolder(fixture);
  }
  return fixture;
}

// Case 5: a signal arrives while the main path is still failing from the debugging-port wait. The
// first caller latches the record: the later giveUp(2) must not rewrite the requested 130, and the
// incomplete capture still turns the exit into 74.
async function shutdownLatchSurvivesLaterFailure() {
  const fixture = makeFixture({
    next: (f) => fakeNextHoldingPipe(join(f, "holder.pid")),
    chromium: (f) => fakeChromiumReady(join(f, "chrome.ready")),
  });
  try {
    const port = await freePort();
    const upstream = await freePort();
    const debug = await freePort();
    const evidence = join(fixture, "evidence-race");
    const env = checkerEnv(fixture, { port, upstream, debug, evidence });
    env.CSP_DEBUG_DEADLINE = "30";
    const { child, done } = spawnChecker(fixture, env);
    await waitForFile(join(fixture, "chrome.ready"));
    child.kill("SIGINT");
    const result = await done;
    assert(result.code === 74, `the interrupted check exited ${result.code} (${result.signal ?? "no signal"}), not 74, with a child's streams still open`);
    const requested = readJson(join(evidence, "requested-exit.json"));
    assert(requested.code === 130, `a later failure rewrote the requested status to ${requested.code}; the first request was 130`);
    const held = readJson(join(evidence, "0-upstream", "status.json"));
    assert(held.close === null, "upstream: a close status was invented although its streams never closed");
  } finally {
    await reapHolder(fixture);
  }
  return fixture;
}

// ---- The cleanup path itself ----------------------------------------------------------------

// A held-pipe fixture with its check running and the descendant's pid already written. Shared by the
// two self-tests below, which fail the harness on purpose.
async function startHeldCheck({ debugDeadline = "1", milliseconds = 60_000 } = {}) {
  const fixture = makeFixture({ next: (f) => fakeNextHoldingPipe(join(f, "holder.pid")) });
  const port = await freePort();
  const upstream = await freePort();
  const debug = await freePort();
  const env = checkerEnv(fixture, { port, upstream, debug, evidence: join(fixture, "evidence-held") });
  env.CSP_DEBUG_DEADLINE = debugDeadline;
  const { child, done } = spawnChecker(fixture, env, milliseconds);
  const pidFile = join(fixture, "holder.pid");
  await waitForFile(pidFile);
  const holder = Number(readFileSync(pidFile, "utf8"));
  return { fixture, env, child, done, holder, ports: [port, upstream, debug] };
}

// Records what this child owns, then fails an assertion in the middle of a case that has a
// descendant holding a pipe. The record outlives the failure, so the parent can confirm the unwind
// reaped the group and the descendant. The group is this child's own, which the parent launched as
// a process-group leader; under supervision a checker leads no group of its own.
async function selfTestFailure(outFile) {
  const run = await startHeldCheck();
  writeFileSync(outFile, `${JSON.stringify({ group: process.pid, holder: run.holder, ports: run.ports })}\n`);
  assert(false, "deliberate failure with a held pipe; the cleanup must still run");
}

// Records what this child owns, then lets the harness's own deadline kill the check. The rejection
// must unwind into the same cleanup.
async function selfTestTimeout(outFile) {
  const run = await startHeldCheck({ debugDeadline: "30", milliseconds: 1_500 });
  writeFileSync(outFile, `${JSON.stringify({ group: process.pid, holder: run.holder, ports: run.ports })}\n`);
  await run.done;
}

// Owns a checker, its fake upstream, the held descendant and the ports, records what that is and
// then never finishes. The supervisor's own deadline, not the checker's, has to take the tree down
// even though this run never wrote the complete record the other self-tests leave.
async function selfTestStall(outFile) {
  const run = await startHeldCheck({ debugDeadline: "300", milliseconds: 300_000 });
  writeFileSync(`${outFile}.partial`, `${JSON.stringify({ group: process.pid, holder: run.holder, ports: run.ports })}\n`);
  await new Promise(() => {});
}

// The two cleanup scenarios are run as children of this file, so the negative outcome is real: the
// child really exits non-zero, and the parent really observes that nothing it owned is still alive
// and no port it used is still held. The child is its own process-group leader and the checkers it
// starts inherit that group, so the parent owns the whole tree from the pid it launched and reaps
// it whichever way the child ends. Nothing here overrides `process.exit`.
async function runCleanupSelfTest(flag, expect) {
  const outFile = join(mkdtempSync(join(repo, ".tmp", "csp-exit-selftest-")), "owned.json");
  const child = spawn(process.execPath, [selfPath, flag, outFile], {
    stdio: ["ignore", "pipe", "pipe"],
    detached: true,
  });
  checkers.add(child);
  let stderr = "";
  child.stderr.on("data", (chunk) => (stderr += chunk));
  let result = null;
  let failure = null;
  try {
    result = await new Promise((resolve, reject) => {
      const timer = setTimeout(() => {
        reject(new Error(`${flag}: the self-test child did not end within 30 s`));
      }, 30_000);
      child.on("error", (error) => {
        clearTimeout(timer);
        reject(error);
      });
      child.on("close", (code, signal) => {
        clearTimeout(timer);
        resolve({ code, signal });
      });
    });
  } catch (error) {
    failure = error;
  } finally {
    // The parent owns the group from launch, so it takes the whole tree down -- a deadline that
    // killed the child before its own cleanup ran, an error, or a plain failure -- and waits for it
    // before reporting anything. The record below is read only to check what the child named. A
    // group that survives is a cleanup failure and stays in `checkers`, so the run's last-resort
    // cleanup can still reach it; registration is dropped only once the tree is confirmed gone.
    killGroup(child);
    if (await groupGone(child.pid)) {
      checkers.delete(child);
    } else {
      failure = failure ?? new Error(`${flag}: the self-test group ${child.pid} survived cleanup; stderr was:\n${stderr}`);
    }
  }
  if (failure) throw failure;
  assert(result.code !== 0, `${flag}: the self-test child exited ${result.code}, so the scenario never failed`);
  assert(stderr.includes(expect), `${flag}: the child did not fail through the expected path; stderr was:\n${stderr}`);
  assert(existsSync(outFile), `${flag}: the child left no record of what it owned`);
  const owned = readJson(outFile);
  assert(await groupGone(owned.group), `${flag}: the check's process group ${owned.group} is still alive`);
  if (owned.holder) assert(await gone(owned.holder), `${flag}: the held descendant ${owned.holder} is still alive`);
  for (const port of owned.ports) assert(await portFree(port), `${flag}: port ${port} is still occupied`);
}

// The supervisor's own deadline, not the checker's: a run that owns a checker, its fake upstream,
// the held descendant and the ports and then stalls. The parent must take the whole tree down from
// the group it launched even though the run never wrote the complete record, and nothing it owned
// may still be alive or hold a port. The partial record it did write only names what to check, so
// the cleanup never depends on reading it.
async function runSupervisorTimeoutSelfTest() {
  const outFile = join(mkdtempSync(join(repo, ".tmp", "csp-exit-stall-")), "owned.json");
  const partial = `${outFile}.partial`;
  const milliseconds = 6_000;
  const child = spawn(process.execPath, [selfPath, "--self-test-stall", outFile], {
    stdio: ["ignore", "ignore", "pipe"],
    detached: true,
  });
  checkers.add(child);
  let stderr = "";
  child.stderr.on("data", (chunk) => (stderr += chunk));
  let timedOut = false;
  let failure = null;
  try {
    await new Promise((resolve, reject) => {
      const timer = setTimeout(() => {
        timedOut = true;
        resolve();
      }, milliseconds);
      child.on("error", (error) => {
        clearTimeout(timer);
        reject(error);
      });
      child.on("close", () => {
        clearTimeout(timer);
        resolve();
      });
    });
  } catch (error) {
    failure = error;
  } finally {
    // The whole tree goes down from the group the parent launched; the deadline must not leave the
    // checker or its descendants alive because the child never wrote a complete record of them.
    // The child stays in `checkers` so the run's own last-resort cleanup can reach it too.
    killGroup(child);
    if (!(await groupGone(child.pid))) {
      failure = failure ?? new Error(`--self-test-stall: the supervisor group ${child.pid} survived cleanup; stderr was:\n${stderr}`);
    }
  }
  if (failure) throw failure;
  assert(timedOut, `--self-test-stall: the child ended on its own within ${milliseconds} ms; the supervisor deadline was not exercised`);
  assert(existsSync(partial), "--self-test-stall: the child left no partial record of what it owned");
  const owned = readJson(partial);
  assert(await groupGone(child.pid), "--self-test-stall: the supervisor group is still alive");
  assert(await gone(owned.holder), `--self-test-stall: the held descendant ${owned.holder} is still alive`);
  for (const port of owned.ports) assert(await portFree(port), `--self-test-stall: port ${port} is still occupied`);
  // Removed only once the tree is confirmed gone: on a failure the run's last-resort cleanup still
  // holds it, so a bug in this case reaps what it started rather than orphaning it.
  checkers.delete(child);
}

async function main() {
  const completed = [];
  completed.push(await debuggingPortFailure());
  completed.push(await occupiedPortFailure());
  completed.push(await evidenceFailureIsFailClosed());
  completed.push(await incompleteCaptureFailsClosed());
  completed.push(await shutdownLatchSurvivesLaterFailure());
  await runCleanupSelfTest("--self-test-failure", "deliberate failure with a held pipe");
  await runCleanupSelfTest("--self-test-timeout", "did not end within");
  await runSupervisorTimeoutSelfTest();
  return completed;
}

let failure = null;
let completed = null;
try {
  if (mode === "--self-test-failure") {
    await selfTestFailure(process.argv[3]);
  } else if (mode === "--self-test-timeout") {
    await selfTestTimeout(process.argv[3]);
  } else if (mode === "--self-test-stall") {
    await selfTestStall(process.argv[3]);
  } else {
    completed = await main();
  }
} catch (error) {
  failure = error;
} finally {
  // The status is chosen after this: nothing exits from the middle of a case, so every fixture's
  // group and every held descendant is reaped even when an assertion fired.
  await cleanupOwned();
}
if (failure) {
  console.error(`test-csp-browser-exit: FAILED: ${failure.message}`);
  process.exit(1);
}
if (completed) {
  console.log(
    "test-csp-browser-exit: the check reaped both children, retained both whole streams and both " +
      "literal statuses, kept requested status 2 across a debugging-port failure and an occupied " +
      "port, failed closed when its evidence could not be written or a child's streams never closed, " +
      "and kept its first requested status 130 when a later failure tried to rewrite it; a deliberate " +
      "assertion failure, a killed check and a stalled supervisor each left no process and no port behind",
  );
  for (const fixture of completed) console.log(`  fixture: ${fixture}`);
}
process.exit(0);
