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


@pytest.fixture
def github_path_content_sample():
    with open(f"{DATA_DIR}/client/github/path_content.json", mode="r") as f:
        data = f.read()

    return json.loads(data)


@pytest.fixture
def github_get_ref_sample():
    with open(f"{DATA_DIR}/client/github/get_ref.json", mode="r") as f:
        data = f.read()

    return json.loads(data)


@pytest.fixture
def github_create_ref_sample():
    with open(f"{DATA_DIR}/client/github/create_ref.json", mode="r") as f:
        data = f.read()

    return json.loads(data)


@pytest.fixture
def github_update_content_sample():
    with open(f"{DATA_DIR}/client/github/update_content.json", mode="r") as f:
        data = f.read()

    return json.loads(data)
