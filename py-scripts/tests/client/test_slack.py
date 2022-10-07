import pytest

from toolbelt.client import SlackClient
from toolbelt.exceptions import ResponseError


def test_send_msg_success(requests_mock, slack_post_msg_sample):
    requests_mock.post("/api/chat.postMessage", json=slack_post_msg_sample)

    client = SlackClient("test token")

    r = client.send_simple_msg("CTESTTESTX", msg="test2")
    assert r["ok"]


def test_send_msg_failure(requests_mock, slack_failure_response_sample):
    requests_mock.post("/api/chat.postMessage", json=slack_failure_response_sample)

    client = SlackClient("test token")

    with pytest.raises(ResponseError):
        client.send_simple_msg("CTESTTESTX", msg="test2")
