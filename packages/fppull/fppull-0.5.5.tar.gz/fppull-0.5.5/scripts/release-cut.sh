#!/usr/bin/env bash
set -euo pipefail

# usage: scripts/release-cut.sh v0.5.4 v0.5.3
CURR="${1:?usage: $0 <new_tag> <prev_tag>}"
PREV="${2:?usage: $0 <new_tag> <prev_tag>}"
REPO="$(gh repo view --json nameWithOwner --jq .nameWithOwner)"
DATE="$(date -u +%Y-%m-%d)"

# 0) ensure clean & on main
git switch main >/dev/null
git pull --ff-only

# 1) finalize CHANGELOG section for CURR and open next Unreleased
perl -0777 -pe "s/^\Q## [${CURR#v}] - Unreleased\E/## [${CURR#v}] - ${DATE}/m" -i CHANGELOG.md
perl -0777 -pe "s#\*\*Full Changelog\*\*: https://github.com/.+?/compare/\Q${PREV}\E\.\.\.(?:main|v?\d+\.\d+\.\d+)#**Full Changelog**: https://github.com/${REPO}/compare/${PREV}...${CURR}#m" -i CHANGELOG.md

# Compute NEXT from CURR (bash-only, no Python)
ver="${CURR#v}"; IFS=. read -r maj min pat <<<"$ver"; NEXT="$maj.$min.$((pat+1))"

grep -qE "^## \[${NEXT}\] - Unreleased" CHANGELOG.md || printf '\n## [%s] - Unreleased\n- TBD\n' "$NEXT" >> CHANGELOG.md
git add CHANGELOG.md
git commit -m "changelog: cut ${CURR#v} (dated), add ${NEXT} Unreleased" || true

# 2) tag + release on GitHub
git push
git tag -a "$CURR" -m "$CURR" || true
git push origin "$CURR"
gh release create "$CURR" --title "$CURR" --generate-notes || true

# 3) build from tag + upload assets + SHA256 block
git switch --detach "$CURR" >/dev/null
rm -rf dist/
python - <<'PY' 2>/dev/null || python -m pip install --upgrade build >/dev/null
import build; print("ok")
PY
python -m build
gh release upload "$CURR" dist/* --clobber

tmp="$(mktemp -d)"; gh release download "$CURR" -D "$tmp" >/dev/null
body="$(mktemp)"; gh release view "$CURR" --json body --jq .body > "$body"
if ! grep -q '^### SHA256' "$body"; then
  { printf "\n### SHA256\n"; (cd "$tmp" && { sha256sum * 2>/dev/null || shasum -a 256 *; }); } >> "$body"
  gh release edit "$CURR" -F "$body"
fi
rm -rf "$tmp" "$body"

# 4) show the exact workflow run for this tag
SHA="$(git rev-list -n1 "$CURR" 2>/dev/null || echo)"
WF="Publish to PyPI on tag"
gh run list --workflow "$WF" -L 20 \
  --json databaseId,status,conclusion,headSha,url,displayTitle,createdAt,event \
  --jq 'map(select(.headSha=="'"$SHA"'"))'
