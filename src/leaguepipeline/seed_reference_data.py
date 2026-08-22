import logging

import requests
from leaguepipeline.db import get_connection

logger = logging.getLogger(__name__)

def get_latest_version():
    versions = requests.get("https://ddragon.leagueoflegends.com/api/versions.json").json()
    return versions[0]

def fetch_champions(version):
    url = f"https://ddragon.leagueoflegends.com/cdn/{version}/data/en_US/champion.json"
    data = requests.get(url).json()
    return [(int(info["key"]), info["name"], info["id"]) for info in data["data"].values()]

def fetch_items(version):
    url = f"https://ddragon.leagueoflegends.com/cdn/{version}/data/en_US/item.json"
    data = requests.get(url).json()
    # returns list of (item_id: int, name: str)
    return [(int(item_id), info["name"]) for item_id, info in data["data"].items()]

def seed_champions(conn, champions):
    cur = conn.cursor()
    for champion_id, name, riot_id in champions:
        cur.execute(
            """
            INSERT INTO champions (champion_id, name, riot_id)
            VALUES (%s, %s, %s)
            ON CONFLICT (champion_id) DO UPDATE SET name = EXCLUDED.name, riot_id = EXCLUDED.riot_id
            """,
            (champion_id, name, riot_id)
        )
    conn.commit()
    cur.close()

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    version = get_latest_version()
    logger.info("Using Data Dragon version: %s", version)

    champions = fetch_champions(version)
    items = fetch_items(version)
    logger.info("Fetched %d champions, %d items", len(champions), len(items))

    conn = get_connection()
    seed_champions(conn, champions)
    seed_items(conn, items)
    conn.close()

    logger.info("Done seeding champions and items")
