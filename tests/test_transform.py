from datetime import datetime, timezone

from leaguepipeline.transform import extract_match_row, extract_participant_rows


def make_match(participants):
    return {
        "info": {
            "gameVersion": "14.14.567890",
            "gameCreation": 1720000000000,
            "queueId": 420,
            "gameDuration": 1800,
            "platformId": "EUW1",
            "participants": participants,
        }
    }


def make_participant(**overrides):
    participant = {
        "puuid": "puuid-1",
        "championId": 1,
        "teamId": 100,
        "teamPosition": "MIDDLE",
        "win": True,
        "kills": 5,
        "deaths": 2,
        "assists": 7,
        "goldEarned": 12000,
        "totalMinionsKilled": 150,
        "neutralMinionsKilled": 10,
        **{f"item{i}": 1000 + i for i in range(7)},
    }
    participant.update(overrides)
    return participant


def test_extract_match_row_parses_patch_and_timestamp():
    match = make_match(participants=[])

    row = extract_match_row("MATCH_1", match)

    assert row == (
        "MATCH_1",
        "14.14",
        420,
        1800,
        datetime.fromtimestamp(1720000000000 / 1000, tz=timezone.utc),
        "EUW1",
    )


def test_extract_participant_rows_computes_items_and_cs():
    match = make_match(participants=[make_participant()])

    rows = extract_participant_rows("MATCH_1", match)

    assert rows == [
        (
            "MATCH_1",
            "puuid-1",
            1,
            100,
            "MIDDLE",
            True,
            5,
            2,
            7,
            12000,
            [1000, 1001, 1002, 1003, 1004, 1005, 1006],
            160,
        )
    ]


def test_extract_participant_rows_handles_multiple_participants():
    match = make_match(
        participants=[
            make_participant(puuid="puuid-1", teamId=100),
            make_participant(puuid="puuid-2", teamId=200, win=False),
        ]
    )

    rows = extract_participant_rows("MATCH_1", match)

    assert len(rows) == 2
    assert [row[1] for row in rows] == ["puuid-1", "puuid-2"]
    assert rows[1][3] == 200
    assert rows[1][5] is False
