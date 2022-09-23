import pytest

from toolbelt.client import SlackClient
from toolbelt.client.slack import SLACK_BASE_URL
from toolbelt.exceptions import ResponseError


def test_send_msg_success(requests_mock, post_msg_sample):
    requests_mock.post(SLACK_BASE_URL + "/api/chat.postMessage", json=post_msg_sample)

    client = SlackClient("test token")

    r = client.send_simple_msg("CTESTTESTX", msg="test2")
    assert r["ok"]


def test_send_msg_failure(requests_mock, failure_response_sample):
    requests_mock.post(
        SLACK_BASE_URL + "/api/chat.postMessage", json=failure_response_sample
    )

    client = SlackClient("test token")

    with pytest.raises(ResponseError):
        client.send_simple_msg("CTESTTESTX", msg="test2")
