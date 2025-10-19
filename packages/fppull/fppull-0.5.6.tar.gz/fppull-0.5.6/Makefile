.ONESHELL:
.DEFAULT_GOAL := help

# Defaults you can override: make report-top SEASON=2025 WEEKS=1-3
PY ?= python
VENV ?= .venv
ACT := source $(VENV)/bin/activate
SEASON ?= 2025
WEEKS  ?= 1-3
GROUP  ?=
TOP    ?= 10
MIN_WEEKS ?=

## help: List available targets
help:
	@grep -E "^[a-zA-Z0-9_.-]+:.*?##" Makefile | awk -F":|##" '{printf "  %-15s %s\n", $$1, $$NF}' | sort

## venv: Create local virtualenv (.venv)
venv:
	@test -d $(VENV) || $(PY) -m venv $(VENV)

## fmt: Run Black formatter
fmt:
	$(ACT); black .

## lint: Run Ruff linter
lint:
	$(ACT); ruff check .

## test: Run unit tests (fallback to pytest if script missing)
test:
	$(ACT); ( ./scripts/ci.sh test || pytest -q )

## contracts: Run contract tests (fallback to pytest contract dir)
contracts:
	$(ACT); ( ./scripts/ci.sh contracts || pytest -q tests/contract )

## ci: fmt + lint + tests + contracts
ci: fmt lint test contracts

## report-top: Pull weekly stats, fetch scoring, compute points, summarize
report-top:
	set -euo pipefail; \
	$(ACT); \
	# 1) Pull raw/joined weekly stats
	$(PY) -m fppull.cli.pull_range --season $(SEASON) --weeks $(WEEKS) --out-dir data/processed; \
	IN=data/processed/season_$(SEASON)_joined.csv; \
	# 2) Ensure scoring table exists for this season/league
	PYTHONPATH=src $(PY) -m fppull.fetch_espn_scoring; \
	SCORING=data/processed/season_$(SEASON)/espn/scoring_table.csv; \
	# 3) Compute points using league scoring
	NORM=data/processed/season_$(SEASON)_joined.with_points.csv; \
	echo "IN=$$IN  SCORING=$$SCORING  OUT=$$NORM"; \
	PYTHONPATH=src $(PY) -m fppull.cli.calc_points_from_joined --input "$$IN" --season $(SEASON) --scoring "$$SCORING" --out "$$NORM"; \
	# 4) Summarize
	GB=""; [ -n "$(GROUP)" ] && GB="--group-by $(GROUP)"; \
	MW=""; [ -n "$(MIN_WEEKS)" ] && MW="--min-weeks $(MIN_WEEKS)"; \
	$(PY) -m fppull.cli.report_top --in "$$NORM" $$GB $$MW --top $(TOP)

## release-tag: Create & push tag vX.Y.Z (use like: make release-tag V=1.0.1)
release-tag:
	@[ -n "$(V)" ] || { echo "Usage: make release-tag V=1.0.1"; exit 1; }
	git tag -a v$(V) -m v$(V) && git push origin v$(V)

## release-verify: Check GH release assets + PyPI version (V required)
release-verify:
	@[ -n "$(V)" ] || { echo "Usage: make release-verify V=1.0.1"; exit 1; }
	@OWNER_REPO=$$(git config --get remote.origin.url | sed -E 's#.*/([^/]+/[^/]+)\.git#\1#'); \
	echo "== GitHub Release assets for v$(V) =="; \
	gh release view v$(V) --repo "$$OWNER_REPO" --json assets --jq '.assets[].name'; \
	echo; echo "== PyPI latest =="; \
	python -c 'import json, urllib.request as u; print(json.load(u.urlopen("https://pypi.org/pypi/fppull/json", timeout=10))["info"]["version"])'

.PHONY: help venv fmt lint test contracts ci report-top release-tag release-verify

## env-refresh: Refresh ESPN cookies from browser and verify
## env-refresh-dry: Preview cookie refresh without writing
## env-doctor: Print resolved env file + masked cookies
.PHONY: env-refresh env-refresh-dry env-doctor

# 🔄 Refresh cookies from browser and verify they’re loaded.
env-refresh: ## Refresh ESPN cookies from browser and verify
	@echo "🔄 Refreshing ESPN cookies from browser..."
	@$(PY) -m fppull.cli.env_refresh
	@echo
	@echo "🩺 Verifying environment after refresh..."
	@$(PY) -m fppull.cli.env doctor
	@echo
	@echo "✅ Done. Cookies synced and verified."

# 🧪 Dry-run mode — preview what would be written.
env-refresh-dry: ## Preview cookie refresh without writing
	@$(PY) -m fppull.cli.env_refresh --dry-run

# 🩺 Quick doctor check only.
env-doctor: ## Print resolved env file + masked cookies
	@$(PY) -m fppull.cli.env doctor

## ensure-cookies: Verify auth; auto-refresh from browser if needed; verify again
## auth-check: Low-level probe only (no writes)
.PHONY: ensure-cookies auth-check

auth-check: ## Low-level probe (0 OK; nonzero otherwise)
	@$(PY) -m fppull.cli.auth_check

# --- Require league/season context for auth checks ---------------------------
# You can set these in your shell (export …) or in .env loaded by the Python.
# We still guard here to avoid confusing refresh loops.
.PHONY: ensure-ids
ensure-ids:
	@if [ -z "$(LEAGUE_ID)" ]; then \
	  echo "❌ LEAGUE_ID is not set. Use:  make report-top LEAGUE_ID=1543692958  (or put LEAGUE_ID in .env)"; \
	  exit 2; \
	fi
	@if [ -z "$(SEASON)" ]; then \
	  echo "❌ SEASON is not set. Use:  make report-top SEASON=2025  (or put SEASON in .env)"; \
	  exit 2; \
	fi

## ensure-cookies: Verify auth; auto-refresh on 401/redirect; show clear reasons otherwise
.PHONY: ensure-cookies
ensure-cookies: ensure-ids
	@echo "🔐 Checking ESPN auth…"
	@code=0; $(PY) -m fppull.cli.auth_check || code=$$?; \
	case $$code in \
	  0) echo "✅ Auth OK"; exit 0;; \
	  1|5) echo "⛔ Unauthorized/redirect — attempting cookie refresh…"; \
	       $(PY) -m fppull.cli.env_refresh && echo "🔁 Re-checking auth…" && $(PY) -m fppull.cli.auth_check ;; \
	  2) echo "❌ Missing SEASON/LEAGUE_ID (guard should have caught this)"; exit 2;; \
	  3) echo "❌ Missing cookies locally — run: make env-refresh"; exit 3;; \
	  4) echo "🌐 Network error — check connectivity/VPN and retry"; exit 4;; \
	  *) echo "❌ Unexpected probe status $$code"; exit $$code;; \
	esac

# Prehook major workflows
report-top: ensure-cookies
ci: ensure-cookies
test: ensure-cookies
contracts: ensure-cookies

## report-all: Pull all weeks (default 1-18), compute points, and write a timestamped summary
.PHONY: report-all
report-all: ensure-cookies
	set -euo pipefail; \
	source $(VENV)/bin/activate || true; \
	: "${WEEKS:=1-18}"; \
	: "${TOP:=$(TOP)}"; \
	echo "▶ Running full-season report for SEASON=$(SEASON), WEEKS=$${WEEKS}"; \
	\
	# 1) Pull raw/joined weekly stats
	$(PY) -m fppull.cli.pull_range --season $(SEASON) --weeks "$${WEEKS}" --out-dir data/processed; \
	IN="data/processed/season_$(SEASON)_joined.csv"; \
	\
	# 2) Ensure scoring table exists for this season/league
	PYTHONPATH=src $(PY) -m fppull.fetch_espn_scoring; \
	SCORING="data/processed/season_$(SEASON)/espn/scoring_table.csv"; \
	\
	# 3) Compute points using league scoring
	NORM="data/processed/season_$(SEASON)_joined.with_points.csv"; \
	echo "IN=$${IN}  SCORING=$${SCORING}  OUT=$${NORM}"; \
	PYTHONPATH=src $(PY) -m fppull.cli.calc_points_from_joined --input "$${IN}" --season $(SEASON) --scoring "$${SCORING}" --out "$${NORM}"; \
	\
	# 4) Summarize (and save a copy with a timestamp)
	TS="$$(date +%Y%m%d_%H%M%S)"; \
	OUTDIR="data/processed/season_$(SEASON)"; \
	mkdir -p "$${OUTDIR}"; \
	SUMMARY_TXT="$${OUTDIR}/summary_$${TS}.txt"; \
	echo "📝 Writing summary -> $${SUMMARY_TXT}"; \
	{ \
	  echo "== Summary (SEASON=$(SEASON), WEEKS=$${WEEKS}) =="; \
	  echo; \
	  $(PY) -m fppull.cli.report_top --in "$${NORM}" --top $${TOP}; \
	} | tee "$${SUMMARY_TXT}"; \
	\
	# 5) Keep a timestamped snapshot of the normalized CSV too
	SNAP="$${OUTDIR}/season_$(SEASON)_joined.with_points_$${TS}.csv"; \
	cp "$${NORM}" "$${SNAP}"; \
	echo "✅ Snapshot saved: $${SNAP}"

report-latest: ensure-cookies
	set -euo pipefail; \
	source $(VENV)/bin/activate || true; \
	\
	# 0) Detect latest week (live) using mStatus via a tiny CLI module
	LATEST_WEEK="$$( PYTHONPATH=src $(PY) -m fppull.cli.detect_latest_week )"; \
	if [ "$${LATEST_WEEK}" = "0" ]; then echo "No played weeks detected yet. Exiting."; exit 0; fi; \
	echo "🗓  Latest played week (ESPN): $${LATEST_WEEK}"; \
	\
	# 1) Pull raw/joined weekly stats ONLY for 1..LATEST
	$(PY) -m fppull.cli.pull_range --season $(SEASON) --weeks 1-$${LATEST_WEEK} --out-dir data/processed; \
	IN="data/processed/season_$(SEASON)_joined.csv"; \
	\
	# 2) Ensure scoring exists
	PYTHONPATH=src $(PY) -m fppull.fetch_espn_scoring; \
	SCORING="data/processed/season_$(SEASON)/espn/scoring_table.csv"; \
	\
	# 3) Compute points using league scoring
	NORM="data/processed/season_$(SEASON)_joined.w1-$${LATEST_WEEK}.with_points.csv"; \
	echo "IN=$$IN  SCORING=$$SCORING  OUT=$$NORM"; \
	PYTHONPATH=src $(PY) -m fppull.cli.calc_points_from_joined --input "$$IN" --season $(SEASON) --scoring "$$SCORING" --out "$$NORM"; \
	\
	# 4) Summarize + timestamped copies
	TS="$$(date +%Y%m%d_%H%M%S)"; \
	OUTDIR="data/processed/season_$(SEASON)"; \
	SUMMARY_TXT="$${OUTDIR}/summary_w1-$${LATEST_WEEK}_$${TS}.txt"; \
	SNAP="$${OUTDIR}/season_$(SEASON)_joined.w1-$${LATEST_WEEK}.with_points_$${TS}.csv"; \
	mkdir -p "$${OUTDIR}"; \
	{ echo "== Summary (SEASON=$(SEASON), WEEKS=1-$${LATEST_WEEK}) =="; echo; $(PY) -m fppull.cli.report_top --in "$$NORM" --top $(TOP); } | tee "$${SUMMARY_TXT}"; \
	cp "$$NORM" "$${SNAP}"; \
	echo "✅ Snapshot: $${SNAP}"; \
	echo "📝 Summary : $${SUMMARY_TXT}"

## report-week: Pull WEEK=N only, compute points, summarize
.PHONY: report-week
report-week: ensure-cookies
	set -euo pipefail; \
	source $(VENV)/bin/activate || true; \
	: "${WEEK?Usage: make report-week WEEK=7}"; \
	\
	# 1) Pull raw/joined weekly stats for the chosen week
	$(PY) -m fppull.cli.pull_range --season $(SEASON) --weeks $${WEEK} --out-dir data/processed; \
	IN="data/processed/season_$(SEASON)_joined.csv"; \
	\
	# 2) Ensure scoring exists for this season/league
	PYTHONPATH=src $(PY) -m fppull.fetch_espn_scoring; \
	SCORING="data/processed/season_$(SEASON)/espn/scoring_table.csv"; \
	\
	# 3) Compute points using league scoring
	NORM="data/processed/season_$(SEASON)_joined.w$${WEEK}.with_points.csv"; \
	echo "IN=$${IN}  SCORING=$${SCORING}  OUT=$${NORM}"; \
	PYTHONPATH=src $(PY) -m fppull.cli.calc_points_from_joined --input "$${IN}" --season $(SEASON) --scoring "$${SCORING}" --out "$${NORM}"; \
	\
	# 4) Summarize (timestamped)
	TS="$$(date +%Y%m%d_%H%M%S)"; \
	OUTDIR="data/processed/season_$(SEASON)"; \
	mkdir -p "$${OUTDIR}"; \
	SUMMARY_TXT="$${OUTDIR}/summary_w$${WEEK}_$${TS}.txt"; \
	{ echo "== Summary (SEASON=$(SEASON), WEEK=$${WEEK}) =="; echo; \
	  $(PY) -m fppull.cli.report_top --in "$${NORM}" --top $(TOP); } | tee "$${SUMMARY_TXT}"; \
	echo "📝 Summary : $${SUMMARY_TXT}"

## open-latest: Show the newest summary and snapshot paths
.PHONY: open-latest
open-latest:
	@set -e; \
	OUTDIR="data/processed/season_$(SEASON)"; \
	echo "== Latest summary =="; \
	ls -t "$$OUTDIR"/summary_w1-* 2>/dev/null | head -1; \
	echo; echo "== Latest snapshot =="; \
	ls -t "$$OUTDIR"/season_$(SEASON)_joined.w1-*.with_points_*.csv 2>/dev/null | head -1

## cleanup-snapshots: Keep only the latest N (default 10) snapshots
.PHONY: cleanup-snapshots
cleanup-snapshots:
	@set -e; \
	OUTDIR="data/processed/season_$(SEASON)"; \
	N="$${N:-10}"; \
	echo "Keeping $$N most recent snapshots in $$OUTDIR"; \
	ls -t "$$OUTDIR"/season_$(SEASON)_joined.w1-*.with_points_*.csv 2>/dev/null | awk "NR>$$N" | xargs -I{} rm -f "{}" || true
## idp-ensure-scoring: Ensure base scoring + merged IDP weights exist
.PHONY: idp-ensure-scoring
idp-ensure-scoring: ensure-cookies
	set -euo pipefail; \
	source $(VENV)/bin/activate || true; \
	OUTDIR="data/processed/season_$(SEASON)/espn"; \
	BASE="$$OUTDIR/scoring_table.csv"; \
	MERGED="$$OUTDIR/scoring_table_with_idp.csv"; \
	mkdir -p "$$OUTDIR"; \
	\
	# 1) Fetch league scoring (base table)
	PYTHONPATH=src $(PY) -m fppull.fetch_espn_scoring; \
	test -f "$$BASE" || { echo "❌ missing $$BASE"; exit 2; } ; \
	\
	# 2) Merge IDP defaults if merged file missing
	if [ ! -f "$$MERGED" ]; then \
	  echo "🔧 Merging IDP defaults into scoring table…"; \
	  $(PY) -m fppull.cli.merge_idp_scoring_defaults \
	    --in "$$BASE" \
	    --defaults config/idp_scoring_defaults.csv \
	    --out "$$MERGED"; \
	fi; \
	\
	# 3) Gate: require slot-17 weights for key statIds
	$(PY) -m fppull.cli.idp_qc_gate --scoring "$$MERGED"

## idp-report-week: Normalize and score an IDP raw file for WEEK
## Usage: make idp-report-week WEEK=7 SEASON=2025 IDP_IN=data/processed/idp_raw_demo.csv
.PHONY: idp-report-week
idp-report-week: ensure-cookies idp-ensure-scoring
	set -euo pipefail; \
	source $(VENV)/bin/activate || true; \
	: "${WEEK?Usage: make idp-report-week WEEK=7 SEASON=$(SEASON) IDP_IN=...}"; \
	: "${IDP_IN?Usage: make idp-report-week WEEK=$(WEEK) SEASON=$(SEASON) IDP_IN=path/to/raw.csv}"; \
	OUTDIR="data/processed/season_$(SEASON)"; \
	ESPN_DIR="$$OUTDIR/espn"; \
	MERGED="$$ESPN_DIR/scoring_table_with_idp.csv"; \
	mkdir -p "$$OUTDIR"; \
	\
	# Normalize
	NORM="$$OUTDIR/idp_norm.w$${WEEK}.csv"; \
	$(PY) -m fppull.cli.idp_normalize \
	  --in "$$IDP_IN" \
	  --out "$$NORM" \
	  --format auto \
	  --season $(SEASON) \
	  --week $${WEEK}; \
	\
	# Score
	TS="$$(date +%Y%m%d_%H%M%S)"; \
	OUT="$$OUTDIR/idp_points.w$${WEEK}_$${TS}.csv"; \
	$(PY) -m fppull.cli.calc_points_idp \
	  --input "$$NORM" \
	  --scoring "$$MERGED" \
	  --out "$$OUT"; \
	echo "✅ IDP points -> $$OUT"

## idp-tests: run only IDP-related unit tests
.PHONY: idp-tests
idp-tests:
	$(ACT); pytest -q tests/unit/test_idp_points.py tests/unit/test_idp_qc_gate.py tests/unit/test_idp_normalize.py

## idp-open-latest: Show newest normalized + scored IDP artifacts
.PHONY: idp-open-latest
idp-open-latest:
	@set -e; \
	OUTDIR="data/processed/season_$(SEASON)"; \
	echo "== Latest IDP norm =="; \
	ls -t "$$OUTDIR"/idp_norm.w*.csv 2>/dev/null | head -1; \
	echo; echo "== Latest IDP points =="; \
	ls -t "$$OUTDIR"/idp_points.w*.csv 2>/dev/null | head -1

## idp-cleanup: Keep only the latest N (default 10) IDP point snapshots
.PHONY: idp-cleanup
idp-cleanup:
	@set -e; \
	OUTDIR="data/processed/season_$(SEASON)"; \
	N="$${N:-10}"; \
	echo "Keeping $$N most recent IDP point files in $$OUTDIR"; \
	ls -t "$$OUTDIR"/idp_points.w*.csv 2>/dev/null | awk "NR>$$N" | xargs -I{} rm -f "{}" || true

## makefile-lint: ensure no unsupported .RECIPEPREFIX or '>' recipe lines (GNU Make 3.81 compat)
.PHONY: makefile-lint
makefile-lint:
	@! grep -nE '^\.(RECIPEPREFIX)' Makefile || (echo "❌ Remove .RECIPEPREFIX for GNU Make 3.81"; exit 1)
ci: makefile-lint
