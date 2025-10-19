#!/usr/bin/env bash
set -u
ver="${1:-}"
if [ -z "$ver" ]; then
  echo "usage: $0 <version>"
  exit 0
fi

# Create milestone if it doesn't already exist (idempotent)
gh api 'repos/:owner/:repo/milestones?state=all' --jq '.[].title' | grep -qx "$ver" || \
gh api -X POST repos/:owner/:repo/milestones -f "title=$ver" -f state=open || true
