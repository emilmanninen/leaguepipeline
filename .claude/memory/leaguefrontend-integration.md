---
name: leaguefrontend-integration
description: Pointer to the contract between this pipeline and the leaguefrontend consumer — full detail lives in that repo's own memory.
metadata:
  type: project
---

See the `leaguefrontend` repo's `.claude/memory/leaguepipeline-integration.md` for the full
contract: shared-database access (no API layer), which columns/tables the frontend actually
queries, and where drift could bite. Kept here as a pointer so it shows up in this repo's index.
