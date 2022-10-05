import json

import pytest

from tests.constants import DATA_DIR


@pytest.fixture
def slack_failure_response_sample():
    with open(f"{DATA_DIR}/client/slack/failureResponse.json", mode="r") as f:
        data = f.read()

    return json.loads(data)


@pytest.fixture
def slack_post_msg_sample():
    with open(
        f"{DATA_DIR}/client/slack/postMessageResponse.json", mode="r"
    ) as f:
        data = f.read()

    return json.loads(data)


@pytest.fixture
def github_tags_sample():
    with open(f"{DATA_DIR}/client/github/tags.json", mode="r") as f:
        data = f.read()

    return json.loads(data)
