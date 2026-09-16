#!/usr/bin/env bash
#
# Runs the steps of .github/workflows/ci.yml on this machine.
#
#   scripts/ci-local.sh typecheck  # tsc --noEmit
#   scripts/ci-local.sh build      # next build
#   scripts/ci-local.sh claims     # build, serve production, fetch / and scan the rendered HTML
#   scripts/ci-local.sh links      # serve production, lychee over the rendered page and the README
#   scripts/ci-local.sh lint       # actionlint over the workflow files
#   scripts/ci-local.sh all        # typecheck + build + claims + links + lint
#
# Keep this in step with the workflow — it runs the same commands, so that a red job is found
# here rather than on a runner.
#
# The claim step scans what the server renders, not the source: it builds, starts the
# production server, fetches `/` over HTTP, saves that HTML and runs the phrase check over it.
# A phrase wrapped across lines or encoded as entities in the served bytes is still one phrase
# to the check. The check is a filter, not a proof: see scripts/check-claims.py.
set -euo pipefail

repo_root=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)
cd "$repo_root"

# `/tmp` is a RAM-backed tmpfs on this host, and building there has taken a machine down
# before; keep every artefact inside the checkout.
export TMPDIR="$repo_root/.tmp"
mkdir -p "$TMPDIR"

export NEXT_TELEMETRY_DISABLED=1

PORT="${PORT:-3100}"
BASE="http://127.0.0.1:${PORT}"
RENDERED="$TMPDIR/rendered.html"

say() { printf '\n=== %s ===\n' "$*"; }

run_lychee() {
  if command -v lychee >/dev/null 2>&1; then
    lychee "$@"
  else
    nix shell nixpkgs#lychee -c lychee "$@"
  fi
}

run_actionlint() {
  if command -v actionlint >/dev/null 2>&1; then
    actionlint "$@"
  else
    nix shell nixpkgs#actionlint -c actionlint "$@"
  fi
}

# Starts the production server in the background, polls / until it answers 200 (bounded: 60
# seconds, reporting the last state on failure), runs the given command, then stops the server.
# Polling the predicate beats sleeping and hoping: a fixed sleep passes before the port is open.
with_server() {
  # A 200 from someone else's server is not readiness: refuse a port that already answers
  # before starting anything, so the scan can never pass against unrelated content.
  if curl -s -o /dev/null --max-time 2 "$BASE/" 2>/dev/null; then
    echo "ci-local: $BASE/ already answers; refusing a port this script did not bind" >&2
    return 1
  fi
  ./node_modules/.bin/next start -p "$PORT" >"$TMPDIR/next.log" 2>&1 &
  local pid=$!
  local ready=0
  for _ in $(seq 1 60); do
    if [ "$(curl -s -o /dev/null -w '%{http_code}' "$BASE/" 2>/dev/null)" = "200" ] \
      && kill -0 "$pid" 2>/dev/null; then
      ready=1
      break
    fi
    sleep 1
  done
  if [ "$ready" != "1" ]; then
    kill "$pid" 2>/dev/null || true
    echo "ci-local: production server did not answer $BASE/ within 60s; last of $TMPDIR/next.log:" >&2
    tail -20 "$TMPDIR/next.log" >&2
    return 1
  fi
  # A signal during the scan must not orphan the server either: without this trap a SIGTERM
  # here leaves `next start` on PORT, and the next run fails at the occupied-port check above.
  cleanup_server() {
    kill "$pid" 2>/dev/null || true
    wait "$pid" 2>/dev/null || true
  }
  trap cleanup_server EXIT
  # `"$@"` runs under `if`, so a red scan still reaches the cleanup below instead of
  # exiting the script with the server orphaned (`set -e` does not fire in a condition).
  local status=0
  if "$@"; then
    status=0
  else
    status=$?
  fi
  cleanup_server
  trap - EXIT
  return "$status"
}

job_typecheck() {
  say "typecheck: tsc --noEmit"
  npm run typecheck
}

job_build() {
  say "build: next build"
  npm run build
}

job_claims() {
  say "claims: known forbidden wordings over the rendered page (a filter, not a proof)"
  # Always rebuilt, so the scan can never pass on a stale page.
  npm run build >/dev/null
  with_server fetch_and_scan
}

fetch_and_scan() {
  curl -sSf "$BASE/" -o "$RENDERED"
  # Named rather than globbed: a scan that reaches no file reports a clean page, so reaching
  # nothing is an error (exit 2) rather than a pass.
  ./scripts/check-claims.py "$RENDERED"
}

all_served() {
  fetch_and_scan && run_lychee --config lychee.toml --no-progress "$BASE/" README.md
}

job_links() {
  say "links: lychee over the rendered page and the README"
  # Always rebuilt, so the check can never pass on a stale page.
  npm run build >/dev/null
  with_server run_lychee --config lychee.toml --no-progress "$BASE/" README.md
}

job_lint() {
  say "lint: actionlint over the workflows"
  # The glob is expanded here and a name that matched nothing would be passed through as
  # itself, so an empty workflow directory is an error rather than a silent pass.
  run_actionlint .github/workflows/*.yml
}

case "${1:-all}" in
  typecheck) job_typecheck ;;
  build) job_build ;;
  claims) job_claims ;;
  links) job_links ;;
  lint) job_lint ;;
  all) job_typecheck && job_build && with_server all_served && job_lint ;;
  *)
    printf 'usage: %s [typecheck|build|claims|links|lint|all]\n' "$0" >&2
    exit 2
    ;;
esac
