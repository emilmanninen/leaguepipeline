from unittest.mock import patch, Mock

from leaguepipeline import riot_client


def make_response(status_code, json_body=None, headers=None):
    resp = Mock()
    resp.status_code = status_code
    resp.headers = headers or {}
    resp.json.return_value = json_body
    if status_code == 429:
        resp.raise_for_status.side_effect = AssertionError(
            "raise_for_status should not be called on a 429 — it should be retried"
        )
    else:
        resp.raise_for_status.return_value = None
    return resp


@patch("leaguepipeline.riot_client.throttle")
@patch("leaguepipeline.riot_client.time.sleep")
@patch("leaguepipeline.riot_client.requests.get")
def test_get_match_throttles_again_before_retrying_after_429(mock_get, mock_sleep, mock_throttle):
    rate_limited = make_response(429, headers={"Retry-After": "3"})
    ok = make_response(200, json_body={"info": "match data"})
    mock_get.side_effect = [rate_limited, ok]

    result = riot_client.get_match("MATCH_1")

    assert result == {"info": "match data"}
    assert mock_get.call_count == 2
    # throttle() must run before *every* HTTP attempt, including the retry —
    # not just once before the loop starts.
    assert mock_throttle.call_count == 2
    mock_sleep.assert_called_once_with(3)


@patch("leaguepipeline.riot_client.throttle")
@patch("leaguepipeline.riot_client.time.sleep")
@patch("leaguepipeline.riot_client.requests.get")
def test_get_match_throttle_call_count_matches_request_count_across_repeated_429s(
    mock_get, mock_sleep, mock_throttle
):
    responses = [make_response(429, headers={"Retry-After": "1"}) for _ in range(3)]
    responses.append(make_response(200, json_body={}))
    mock_get.side_effect = responses

    riot_client.get_match("MATCH_1")

    # One throttle() call per actual HTTP request sent, no exceptions.
    assert mock_throttle.call_count == mock_get.call_count == 4


@patch("leaguepipeline.riot_client.throttle")
@patch("leaguepipeline.riot_client.time.sleep")
@patch("leaguepipeline.riot_client.requests.get")
def test_get_match_no_retry_still_throttles_once(mock_get, mock_sleep, mock_throttle):
    mock_get.return_value = make_response(200, json_body={"info": "match data"})

    riot_client.get_match("MATCH_1")

    assert mock_throttle.call_count == 1
    mock_sleep.assert_not_called()
