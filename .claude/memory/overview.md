---
name: overview
description: What leaguepipeline is, its stack, repo layout, and entry points — read this first.
metadata:
  type: project
---

Python 3.12 crawler that ingests League of Legends match data from Riot's API into a
Postgres (Supabase) database, using a queue-based BFS crawl (`crawl_queue` table) seeded
from one player's PUUID. Sister project [[leaguefrontend-integration|is the Next.js frontend]]
that reads the same database directly — see that file for the contract between them.

- Entry point: `python -m src.ingestion.ingest` (runs `crawl()` in [ingest.py](../../src/ingestion/ingest.py)) — not `crawler.py`, despite what the frontend's README says.
- Reference-data seeding: `python -m src.ingestion.seed_reference_data` (Data Dragon champions/items) — see [[schema-pipeline-debt]] for a bug that currently breaks this.
- DB setup requires **both** `schema.sql` and `add_crawl_state.sql` — `crawl_queue` lives in the latter, separate from the main schema file.
- Queue-mode filtering (`ALLOWED_QUEUE_IDS` in `ingest.py`) intentionally excludes Arena/ARAM/URF — only 5v5 Summoner's Rift modes (400/420/430/440) are tracked, since the schema's role/team assumptions don't fit other modes.
- Env vars: `RIOT_API_KEY`, `DATABASE_URL` (`.env`, loaded via `python-dotenv`).
- `riot_client.py`'s throttling (100 req/120s, 0.6s min gap) assumes a personal/dev Riot API key's rate limits — would need adjusting for a production key.

Related: [[schema-pipeline-debt]], [[leaguefrontend-integration]].
