import re
from typing import Optional, Tuple

from toolbelt.client.github import get_tags
from toolbelt.v2.types import Mode


def filter_rc_tags(repo_name, pattern):
    p = re.compile(pattern)
    tags = get_tags(repo_name)
    tags = list(filter(lambda tag: p.match(tag["name"]), tags))
    return [{"name": tag["name"], "sha": tag["commit"]["sha"]} for tag in tags]


def latest_rc_tags(
    repo_name: str,
    *,
    mode: Mode = "test",
    apv: Optional[str] = None,
) -> Tuple[str, str]:
    test_prefix = ""
    rc_suffix = "-rc([0-9]+)"

    if mode == "test":
        test_prefix = "test-"
    elif mode == "production":
        rc_suffix = ""

    if apv:
        pattern = f"{test_prefix}v{apv}{rc_suffix}"
    else:
        pattern = f"{test_prefix}v([0-9]+){rc_suffix}"

    rc_tags = filter_rc_tags(repo_name, pattern)
    try:
        latest = sorted(
            rc_tags, key=lambda tag: re.findall(pattern, tag["name"])[0], reverse=True
        )[0]
    except IndexError:
        raise ValueError(f"No tags filtered from {repo_name}, ex) v1002XX-rc<n>")
    return latest["name"], latest["sha"]


if __name__ == "__main__":
    print(latest_rc_tags("9c-launcher", mode="test"))
