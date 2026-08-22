# smoke_test.py — manual sanity check, not part of the real pipeline
import json
from leaguepipeline.riot_client import get_puuid, get_match_ids, get_match
from leaguepipeline.db import get_connection

puuid = get_puuid("your_riot_id", "1234", region="europe")
print("PUUID:", puuid)

match_ids = get_match_ids(puuid, region="europe", count=5)
print("Recent matches:", match_ids)

match_id = match_ids[0]

match = get_match(match_id, region="europe")

with open("sample_match.json", "w") as f:
    json.dump(match, f, indent=2)

print("Saved sample match to disk")

conn = get_connection()
cur = conn.cursor()
cur.execute("SELECT 1;")
print("DB connection works:", cur.fetchone())
cur.close()
conn.close()