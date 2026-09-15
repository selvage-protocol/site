#!/usr/bin/env bash
#
# Runs the steps of .github/workflows/ci.yml on this machine.
#
#   scripts/ci-local.sh claims   # the `claims` step: the phrases the page must not carry
#   scripts/ci-local.sh links    # the `links` step: lychee over the page and the README
#   scripts/ci-local.sh lint     # actionlint over the workflow files
#   scripts/ci-local.sh all      # lint + claims + links
#
# Keep this in step with the workflow — it runs the same commands, so that a red job is found
# here rather than on a runner. `lint` is local-only: the runner has no nix, and the workflow
# has no actionlint step of its own.
#
# There is no build step and no dependency to install: the page is served as it is, and the two
# checks need python3 and lychee, nothing else. lychee is taken from PATH when it is there (the
# CI job installs it) and from nixpkgs otherwise, so one command runs in both places.
set -euo pipefail

repo_root=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)
cd "$repo_root"

# `/tmp` is a RAM-backed tmpfs on this host, and building there has taken a machine down
# before; keep every artefact inside the checkout.
export TMPDIR="$repo_root/.tmp"
mkdir -p "$TMPDIR"

say() { printf '\n=== %s ===\n' "$*"; }

run_lychee() {
  if command -v lychee >/dev/null 2>&1; then
    lychee "$@"
  else
    nix shell nixpkgs#lychee -c lychee "$@"
  fi
}

job_claims() {
  say "claims: the phrases the page must not carry"
  ./scripts/check-claims.py
}

job_links() {
  say "links: lychee over the page and the README"
  # Named rather than globbed: a glob that matched nothing would check nothing and pass.
  run_lychee --config lychee.toml --no-progress index.html README.md
}

job_lint() {
  say "lint: actionlint over the workflows"
  # The glob is expanded here and a name that matched nothing would be passed through as
  # itself, so an empty workflow directory is an error rather than a silent pass.
  nix shell nixpkgs#actionlint -c actionlint .github/workflows/*.yml
}

case "${1:-all}" in
  claims) job_claims ;;
  links) job_links ;;
  lint) job_lint ;;
  all) job_lint && job_claims && job_links ;;
  *)
    printf 'usage: %s [claims|links|lint|all]\n' "$0" >&2
    exit 2
    ;;
esac
