from src.ingestion.riot_client import get_match, get_puuid, get_match_ids
from collections import deque
from src.ingestion.transform import (
    extract_match_row,
    extract_participant_rows,
)
from src.ingestion.db import (
    get_connection,
    insert_match,
    insert_participants,
    mark_puuid_discovered,
    mark_puuid_done,
    get_pending_puuids,
)

# Queue IDs for standard Summoner's Rift 5v5 modes we actually want to track.
# Excludes Arena (1700), ARAM (450), URF, and other non-standard formats
# that don't fit this schema's role/team assumptions.
ALLOWED_QUEUE_IDS = {
    400,  # Normal Draft
    420,  # Ranked Solo/Duo
    430,  # Normal Blind
    440,  # Ranked Flex
}

def match_already_ingested(conn, match_id: str) -> bool:
    cur = conn.cursor()
    cur.execute("SELECT 1 FROM matches WHERE match_id = %s", (match_id,))
    exists = cur.fetchone() is not None
    cur.close()
    return exists

def ingest_match(conn, match_id: str, region: str = "europe"):
    if match_already_ingested(conn, match_id):
        print(f"Skipping {match_id} — already ingested")
        return None

    print(f"Ingesting {match_id}...")
    match = get_match(match_id, region=region)

    queue_id = match["info"]["queueId"]
    if queue_id not in ALLOWED_QUEUE_IDS:
        print(f"Skipping {match_id} — queue {queue_id} not a tracked mode")
        return None

    match_row = extract_match_row(match_id, match)
    insert_match(conn, match_row)

    participant_rows = extract_participant_rows(match_id, match)
    insert_participants(conn, participant_rows)

    print(f"Done: {match_id} — {len(participant_rows)} participants")
    return match

def ingest_matches(match_ids: list[str], region: str = "europe"):
    conn = get_connection()
    for match_id in match_ids:
        ingest_match(conn, match_id, region=region)
    conn.close()



def crawl(seed_puuids: list[str], region: str = "europe", max_matches: int = 500, matches_per_player: int = 100):
    conn = get_connection()

    for puuid in seed_puuids:
        mark_puuid_discovered(conn, puuid)

    total_matches_ingested = 0

    while total_matches_ingested < max_matches:
        pending = get_pending_puuids(conn, limit=1)
        if not pending:
            print("No more pending players in queue — crawl exhausted.")
            break

        current_puuid = pending[0]
        print(f"\n--- Processing player {current_puuid[:8]}... ({total_matches_ingested} matches so far) ---")

        try:
            match_ids = get_match_ids(current_puuid, region=region, count=matches_per_player)
        except Exception as e:
            print(f"Failed to get match IDs for {current_puuid[:8]}: {e}")
            continue

        for match_id in match_ids:
            if total_matches_ingested >= max_matches:
                break

            if match_already_ingested(conn, match_id):
                continue

            try:
                match_json = ingest_match(conn, match_id, region=region)
                if match_json is None:
                    continue
                total_matches_ingested += 1
            except Exception as e:
                print(f"Failed to ingest {match_id}: {e}")
                continue

            new_puuids = [p["puuid"] for p in match_json["info"]["participants"]]
            for puuid in new_puuids:
                mark_puuid_discovered(conn, puuid)

        mark_puuid_done(conn, current_puuid)

    conn.close()
    print(f"\nCrawl finished. Total matches ingested this run: {total_matches_ingested}")

if __name__ == "__main__":
    my_puuid = get_puuid("brandtop", "1234", region="europe")
    crawl(seed_puuids=[my_puuid], max_matches=3000, matches_per_player=100)

