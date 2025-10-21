#!/usr/bin/env bash
set -euo pipefail

echo "guard: HEAD=$(git rev-parse --short HEAD || echo unknown)"

# 0) Static checks: existence + banner + argument forwarding (no eval)
test -x scripts/release-cut.sh
grep -q '=== DRY-RUN MODE' scripts/release-cut.sh

awk '
  BEGIN { infunc=0; ok=0 }
  /^run\(\)[[:space:]]*\{/ { infunc=1; next }
  infunc && /\}/           { infunc=0; next }
  infunc && /\$@/          { ok=1 }
  END { exit ok ? 0 : 1 }
' scripts/release-cut.sh

! grep -Eq 'eval[[:space:]]+(\$@|\$\*)' scripts/release-cut.sh

# 1) Preflight cleanliness: do not proceed if the tree is dirty
if ! git diff --quiet; then
  echo "guard: repo not clean before dry-run"
  git status --porcelain
  exit 1
fi

# 2) Plain dry-run (no tracing, no pipes, no redirections)
rc=0
./scripts/release-cut.sh v0.0.0 v0.0.0 --dry-run || rc=$?
echo "guard: release-cut.sh (dry-run) exit code=$rc"

# 3) Sanity: dry-run must not change files
if ! git diff --quiet; then
  echo "guard: dry-run changed files"
  git --no-pager diff
  exit 1
fi

exit "$rc"

# ci: no-op to retrigger guard workflow

# ci: no-op retrigger

# ci: PR-trigger smoke test
