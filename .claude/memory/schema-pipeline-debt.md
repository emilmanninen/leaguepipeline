---
name: schema-pipeline-debt
description: Known bugs, dead schema, and test/CI gaps in the ingestion pipeline — decays as items are fixed.
metadata:
  type: project
---

Snapshot as of 2026-08-22 (HEAD 434e6b5). Update as items are fixed.

## Fixed

- **Dead tables**: `schema.sql` defined `timeline_frames`, `timeline_events`, `champion_matchups`,
  `item_win_rates` with no code populating them since their extraction/insert functions were
  removed (commit `428f06e`) — removed the four `CREATE TABLE` statements from `schema.sql`.
  Nothing in this repo or `leaguefrontend` referenced them (confirmed via grep and via the
  frontend's own integration memory).
- **No lint check**: added `ruff` (`test`→ split into `test`/`lint` extras in `pyproject.toml`,
  pinned `ruff==0.16.4`) and a `ruff check .` step in CI before `pytest`. Surfaced the
  `seed_items` NameError below, which was fixed as part of adding the check rather than
  suppressed, so CI starts green.
- **Confirmed bug — `seed_items` NameError**: `seed_reference_data.py` called
  `seed_items(conn, items)` at the bottom of the file, but only `seed_champions` was defined —
  `python -m leaguepipeline.seed_reference_data` raised `NameError` every run. Fixed 2026-08-22:
  added `seed_items()`, mirroring `seed_champions()`, upserting into the `items` table.
- **No packaging**: unpinned `requirements.txt` mixing runtime/test deps, no
  declared Python version, no `pyproject.toml`, no `.env.example`, no CI,
  `print`-as-logging, unused imports — fixed 2026-08-22: added `pyproject.toml`
  (pinned deps, `requires-python = ">=3.12"`, `test` extra for `pytest`),
  `.env.example`, `.github/workflows/ci.yml` (runs `pytest` on push/PR with
  dummy env values), swapped `print()` for `logging` in `ingest.py`/
  `riot_client.py`/`seed_reference_data.py`, removed unused imports (`deque`
  in `ingest.py`, `json` in `transform.py`). Package renamed from the generic
  `src/ingestion` to `src/leaguepipeline` (import as `leaguepipeline`, run as
  `python -m leaguepipeline.ingest`) as part of the same pass. `explore.py`
  (see below) deleted since it was already broken and flagged safe to remove.
- **No CI**: previously no GitHub Actions (or other) workflow existed —
  addressed by the packaging fix above.
- **`riot_client.py` tests fail without `.env`**: `config.py` still
  hard-`KeyError`s if `RIOT_API_KEY`/`DATABASE_URL` are unset at import time
  (unchanged — this is arguably correct fail-fast behavior for required
  secrets), but CI now sets dummy values so `pytest` runs clean without a
  real `.env` present.

- **Split schema files**: `crawl_queue` lived in a separate `add_crawl_state.sql` — merged
  into `schema.sql` 2026-08-18 (no FK dependency on the other tables, so nothing functional
  changed).
- **Throttle bug**: `riot_client.py`'s `get_puuid`/`get_match_ids`/`get_match` called
  `throttle()` once before their 5x retry loop, so a 429 retry fired a real HTTP request
  without re-checking the rate limit — fixed 2026-08-18: `throttle()` moved inside the loop,
  called once per attempt. Regression-tested in `tests/test_riot_client.py` (verified to fail
  against the pre-fix code via `git stash`).
- **Stuck-puuid bug**: `crawl()` in `ingest.py` would `continue` past `mark_puuid_done` when
  `get_match_ids` raised, leaving the puuid `'pending'` forever — `get_pending_puuids` (no
  `ORDER BY`) would likely hand it straight back, wedging the whole crawl on one permanently
  failing puuid (banned/deleted account, etc.) — fixed 2026-08-18: added `mark_puuid_failed()`
  in `db.py` (sets `status = 'failed'`, no schema change needed since `status` is
  unconstrained `TEXT`), called from that `except` block before `continue`. Not
  regression-tested — would need a mocked/real-DB test of `crawl()`'s loop, a bigger lift than
  the throttle fix; tracked under Test coverage below.

## Open

- **Test coverage**: `transform.py` (extract functions) and `riot_client.py` (throttle-per-retry
  behavior only, via mocked `requests`/`throttle`) are unit-tested. `db.py`, `ingest.py`
  (including the stuck-puuid fix above), `seed_reference_data.py` have none.
