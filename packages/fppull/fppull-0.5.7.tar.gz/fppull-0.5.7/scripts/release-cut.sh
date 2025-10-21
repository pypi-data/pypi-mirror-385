#!/usr/bin/env bash
set -euo pipefail

# usage: scripts/release-cut.sh vNEW vPREV [--dry-run] [--confirm] [--force]
DRY=0; CONFIRM=0; FORCE=0
ARGS=()
for a in "$@"; do
  case "$a" in
    --dry-run) DRY=1 ;;
    --confirm) CONFIRM=1 ;;
    --force)   FORCE=1 ;;
    *) ARGS+=("$a") ;;
  esac
done
set -- "${ARGS[@]:-}"

CURR="${1:-}"; PREV="${2:-}"
if [[ -z "${CURR}" || -z "${PREV}" ]]; then
  echo "usage: $0 vNEW vPREV [--dry-run] [--confirm] [--force]" >&2
  exit 2
fi

REPO="${REPO:-${GITHUB_REPOSITORY:-}}"
if [[ -z "$REPO" ]]; then
  REPO="$(gh repo view --json nameWithOwner --jq .nameWithOwner)"
fi
DATE="$(date -u +%Y-%m-%d)"

run() {
  printf '+ %q ' "$@"; printf "\n"
  if [[ "$DRY" -eq 1 ]]; then :; else "$@"; fi
}

# 0) safety: clean tree unless --force

# Dry-run banner
if [[ "$DRY" -eq 1 ]]; then
  echo "=== DRY-RUN MODE: printing commands only; no changes will be made ==="
fi

if [[ "$FORCE" -eq 0 && -n "$(git status --porcelain)" ]]; then
  echo "Working tree dirty. Commit/stash or re-run with --force."; exit 1
fi

# 0.1) tag guard: if tag exists, bail (unless --force, then continue)
if git rev-parse -q --verify "refs/tags/${CURR}" >/dev/null 2>&1; then
  echo "Tag ${CURR} already exists."
  [[ "$FORCE" -eq 1 ]] || exit 0
fi

# 1) ensure clean & on main
run git switch main >/dev/null
run git pull --ff-only

# 2) finalize CHANGELOG section for CURR and open next Unreleased
run perl -0777 -pe "s/^\Q## [${CURR#v}] - Unreleased\E/## [${CURR#v}] - ${DATE}/m" -i CHANGELOG.md
run perl -0777 -pe "s#\\*\\*Full Changelog\\*\\*: https://github.com/.+?/compare/\\Q${PREV}\\E\\.\\.\\.(?:main|v?\\d+\\.\\d+\\.\\d+)#**Full Changelog**: https://github.com/${REPO}/compare/${PREV}...${CURR}#m" -i CHANGELOG.md

# Compute NEXT from CURR (bash-only)
ver="${CURR#v}"; IFS=. read -r maj min pat <<<"$ver"; NEXT="$maj.$min.$((pat+1))"
if ! grep -qE "^## \\[${NEXT}\\] - Unreleased" CHANGELOG.md; then
  run bash -lc "printf '\n## [%s] - Unreleased\n- TBD\n' '$NEXT' >> CHANGELOG.md"
fi
run git add CHANGELOG.md
# commit may no-op; allow it
run git commit -m "changelog: cut ${CURR#v} (dated), add ${NEXT} Unreleased" || true

# 3) tag + release on GitHub
if [[ "$CONFIRM" -eq 1 && "$DRY" -eq 0 ]]; then
  read -r -p "Proceed with tag+release for ${CURR}? [y/N] " ans
  case "$ans" in [yY]|[yY][eE][sS]) ;; *) echo "Aborted."; exit 1;; esac
fi
run git push
run git tag -a "$CURR" -m "$CURR" || true
run git push origin "$CURR"
run gh release create "$CURR" --title "$CURR" --generate-notes || true

# 4) build from tag + upload assets + SHA256 block
run git switch --detach "$CURR" >/dev/null
run rm -rf dist/
# ensure build module exists (only when not dry-run)
if [[ "$DRY" -eq 0 ]]; then
  python - <<'PY' 2>/dev/null || python -m pip install --upgrade build >/dev/null
import build; print("ok")
PY
fi
run python -m build
run gh release upload "$CURR" dist/* --clobber

# SHA256 section & SHAS.txt
if [[ "$DRY" -eq 0 ]]; then
  tmp="$(mktemp -d)"; run gh release download "$CURR" -D "$tmp" >/dev/null
  body="$(mktemp)"; run bash -lc "gh release view '$CURR' --json body --jq .body > '$body'"
  if ! grep -q '^### SHA256' "$body"; then
    if command -v sha256sum >/dev/null 2>&1; then
      sums_cmd="(cd '$tmp' && sha256sum *)"
    else
      sums_cmd="(cd '$tmp' && shasum -a 256 *)"
    fi
    # append sums to body
    bash -lc "{ printf '\n### SHA256\n'; ${sums_cmd}; } >> '$body'"
    run gh release edit "$CURR" -F "$body"
  fi
  # Upload SHAS.txt (always regenerate)
  if command -v sha256sum >/dev/null 2>&1; then
    (cd "$tmp" && sha256sum *) > "$tmp/SHAS.txt"
  else
    (cd "$tmp" && shasum -a 256 *) > "$tmp/SHAS.txt"
  fi
  run gh release upload "$CURR" "$tmp/SHAS.txt" --clobber
  rm -rf "$tmp" "$body"
else
  echo "(dry-run) Skipping SHA256 block and asset upload."
fi

# 5) show the exact workflow run for this tag (informational)
SHA="$(git rev-list -n1 "$CURR" 2>/dev/null || echo)"
WF="Publish to PyPI on tag"
# harmless to run even outside dry-run; still wrap for consistency
run gh run list --workflow "$WF" -L 20 \
  --json databaseId,status,conclusion,headSha,url,displayTitle,createdAt,event \
  --jq 'map(select(.headSha=="'"$SHA"'"))'
