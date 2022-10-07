from random import random

import pytest

from toolbelt.exceptions import TagNotFoundError
from toolbelt.github.parser import latest_tag


def create_tag(name: str):
    return {
        "name": name,
        "commit": {
            "sha": str(random()),
        },
    }


v100290_rc1 = create_tag("v100290-rc1")
v100290_rc5 = create_tag("v100290-rc5")
v100290_rc10 = create_tag("v100290-rc10")
v100290_rc15 = create_tag("v100290-rc15")
v100302_rc1 = create_tag("v100302-rc1")
v100302_rc2 = create_tag("v100302-rc2")
v100402_rc5 = create_tag("v100402-rc5")
v100402_rc9 = create_tag("v100402-rc9")
v100402_rc14 = create_tag("v100402-rc14")

bad_tag = create_tag("bad-tag")

internal_v100290_rc1 = create_tag("internal-v100290-rc1")
internal_v100290_rc5 = create_tag("internal-v100290-rc5")


@pytest.mark.parametrize(
    "tags,rc,expect_result",
    [
        (
            # check if not sort to use string
            [v100290_rc1, v100290_rc5, v100290_rc10, v100290_rc15],
            100290,
            (v100290_rc15["name"], v100290_rc15["commit"]["sha"]),
        ),
        (
            # check normal case
            [v100302_rc1, v100302_rc2],
            100302,
            (v100302_rc2["name"], v100302_rc2["commit"]["sha"]),
        ),
        (
            # check shuffled case
            [v100290_rc10, v100402_rc5, v100402_rc9, v100302_rc1, bad_tag],
            100402,
            (v100402_rc9["name"], v100402_rc9["commit"]["sha"]),
        ),
    ],
)
def test_latest_tag_normal(tags: list, rc: int, expect_result):
    r = latest_tag(tags, rc, prefix="")
    assert r == expect_result


@pytest.mark.parametrize(
    "tags,rc,err",
    [
        (
            # rc not found
            [v100290_rc10, v100402_rc5, v100402_rc9],
            100002,
            TagNotFoundError,
        ),
        (
            # empty list
            [],
            100302,
            TagNotFoundError,
        ),
    ],
)
def test_latest_tag_failure(tags: list, rc: int, err):
    with pytest.raises(err):
        latest_tag(tags, rc, prefix="")


@pytest.mark.parametrize(
    "tags,rc,expect_result",
    [
        (
            # check if not sort to use string
            [internal_v100290_rc1, internal_v100290_rc5],
            100290,
            (
                internal_v100290_rc5["name"],
                internal_v100290_rc5["commit"]["sha"],
            ),
        ),
    ],
)
def test_latest_tag_prefix(tags: list, rc: int, expect_result):
    r = latest_tag(tags, rc, prefix="internal-")
    assert r == expect_result
