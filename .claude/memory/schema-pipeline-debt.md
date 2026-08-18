---
name: schema-pipeline-debt
description: Known bugs, dead schema, and test/CI gaps in the ingestion pipeline — decays as items are fixed.
metadata:
  type: project
---

Snapshot as of 2026-08-18 (HEAD 7324e30). Update as items are fixed.

- **Dead tables**: `schema.sql` still defines `timeline_frames`, `timeline_events`,
  `champion_matchups`, `item_win_rates`, but no code populates them — the extraction/insert
  functions for these were removed (commit `428f06e`) without updating the schema.
  [explore.py](../../explore.py) (a leftover scratch script at repo root, not part of the
  pipeline) still imports the now-deleted functions (`extract_frame_rows`, `extract_event_rows`,
  `build_participant_id_map`, `insert_frames`, `insert_events`) and would fail on import —
  safe to delete or should be clearly marked scratch-only.
- **Confirmed bug**: `seed_reference_data.py` calls `seed_items(conn, items)` at the bottom of
  the file, but only `seed_champions` is defined — `python -m src.ingestion.seed_reference_data`
  raises `NameError` every run.
- **Test coverage**: only `transform.py`'s `extract_match_row`/`extract_participant_rows` are
  unit-tested. `db.py`, `ingest.py`, `riot_client.py`, `seed_reference_data.py` have none.
- **No CI**: no GitHub Actions (or other) workflow in this repo — contrast with
  `leaguefrontend`, which runs tests on every push/PR.
