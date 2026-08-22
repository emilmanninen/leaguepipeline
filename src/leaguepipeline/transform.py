from datetime import datetime, timezone

def extract_match_row(match_id: str, match_json: dict) -> tuple:
    info = match_json["info"]

    # gameVersion looks like "14.14.567890" — we only want "14.14"
    version_parts = info["gameVersion"].split(".")
    patch = f"{version_parts[0]}.{version_parts[1]}"

    game_creation_ts = datetime.fromtimestamp(
        info["gameCreation"] / 1000, tz=timezone.utc
    )

    return (
        match_id,
        patch,
        info["queueId"],
        info["gameDuration"],
        game_creation_ts,
        info["platformId"],
    )

def extract_participant_rows(match_id: str, match_json: dict) -> list[tuple]:
    participants = match_json["info"]["participants"]
    rows = []

    for p in participants:
        items = [p[f"item{i}"] for i in range(7)]
        cs = p["totalMinionsKilled"] + p["neutralMinionsKilled"]

        row = (
            match_id,
            p["puuid"],
            p["championId"],
            p["teamId"],
            p["teamPosition"],   # -> role
            p["win"],
            p["kills"],
            p["deaths"],
            p["assists"],
            p["goldEarned"],
            items,
            cs,
        )
        rows.append(row)

    return rows



