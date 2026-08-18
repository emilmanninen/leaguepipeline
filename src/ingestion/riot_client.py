import requests
from src.ingestion.config import RIOT_API_KEY
import time
from collections import deque

# 100 requests per 2 minutes (120 seconds) is the binding limit
REQUEST_TIMES = deque()
MAX_REQUESTS = 100
WINDOW_SECONDS = 120
MIN_REQUEST_INTERVAL = 0.6  # seconds between requests, keeps pace steady

HEADERS = {"X-Riot-Token": RIOT_API_KEY}

def get_puuid(game_name: str, tag_line: str, region: str = "europe") -> str:
    url = f"https://{region}.api.riotgames.com/riot/account/v1/accounts/by-riot-id/{game_name}/{tag_line}"

    for attempt in range(5):
        throttle()
        resp = requests.get(url, headers=HEADERS)
        if resp.status_code == 429:
            retry_after = int(resp.headers.get("Retry-After", 5))
            print(f"429 on get_puuid, sleeping {retry_after}s (attempt {attempt + 1}/5)")
            time.sleep(retry_after)
            continue
        resp.raise_for_status()
        return resp.json()["puuid"]

    raise Exception(f"get_puuid failed after 5 retries: {game_name}#{tag_line}")

def get_match_ids(puuid: str, region: str = "europe", count: int = 5) -> list[str]:
    url = f"https://{region}.api.riotgames.com/lol/match/v5/matches/by-puuid/{puuid}/ids"

    for attempt in range(5):
        throttle()
        resp = requests.get(url, headers=HEADERS, params={"count": count})
        if resp.status_code == 429:
            retry_after = int(resp.headers.get("Retry-After", 5))
            print(f"429 on get_match_ids, sleeping {retry_after}s (attempt {attempt + 1}/5)")
            time.sleep(retry_after)
            continue
        resp.raise_for_status()
        return resp.json()

    raise Exception(f"get_match_ids failed after 5 retries: {puuid}")

def get_match(match_id: str, region: str = "europe") -> dict:
    url = f"https://{region}.api.riotgames.com/lol/match/v5/matches/{match_id}"

    for attempt in range(5):
        throttle()
        resp = requests.get(url, headers=HEADERS)
        if resp.status_code == 429:
            retry_after = int(resp.headers.get("Retry-After", 5))
            print(f"429 on get_match, sleeping {retry_after}s (attempt {attempt + 1}/5)")
            time.sleep(retry_after)
            continue
        resp.raise_for_status()
        return resp.json()

    raise Exception(f"get_match failed after 5 retries: {match_id}")


def throttle():
    now = time.time()
    while REQUEST_TIMES and now - REQUEST_TIMES[0] > WINDOW_SECONDS:
        REQUEST_TIMES.popleft()

    # Small fixed gap since the last request, evens out the pace
    if REQUEST_TIMES:
        since_last = now - REQUEST_TIMES[-1]
        if since_last < MIN_REQUEST_INTERVAL:
            time.sleep(MIN_REQUEST_INTERVAL - since_last)
            now = time.time()

    # Window-based check, in case the fixed gap alone isn't enough
    if len(REQUEST_TIMES) >= MAX_REQUESTS:
        sleep_time = WINDOW_SECONDS - (now - REQUEST_TIMES[0]) + 0.5
        if sleep_time > 0:
            print(f"Rate limit approaching, sleeping {sleep_time:.1f}s")
            time.sleep(sleep_time)
            now = time.time()
            while REQUEST_TIMES and now - REQUEST_TIMES[0] > WINDOW_SECONDS:
                REQUEST_TIMES.popleft()


    REQUEST_TIMES.append(time.time())