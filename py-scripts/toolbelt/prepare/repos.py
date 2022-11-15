from typing import List, Tuple, Optional

import structlog

from toolbelt.client.github import GithubClient
from toolbelt.types import Network, RepoInfos
from toolbelt.utils.parse import latest_tag

VALID_REPOS = (
    "9c-launcher",
    "NineChronicles",
    "NineChronicles.Headless",
    "NineChronicles.DataProvider",
    "libplanet-seed",
)

logger = structlog.get_logger(__name__)


def get_latest_commits(
    github_client: GithubClient,
    network: Network,
    rc: int,
    repos: Tuple[Tuple[str, str]],
    *,
    launcher_commit: Optional[str],
    player_commit: Optional[str]
):
    repo_infos: RepoInfos = []
    for repo, branch in repos:
        if repo not in VALID_REPOS:
            continue
        github_client.repo = repo
        ref = f"heads/{branch}"

        if network == "internal":
            r = github_client.get_ref(ref)

            if launcher_commit and repo == "9c-launcher":
                commit = launcher_commit
            elif player_commit and repo == "NineChronicles":
                commit = player_commit
            else:
                commit = r["object"]["sha"]
            tag = None
        elif network == "main":
            tags = []
            for v in github_client.get_tags(per_page=100):
                tags.extend(v)
            tag, commit = latest_tag(tags, rc, prefix=create_tag_prefix(network))
        repo_infos.append((repo, tag, commit))

        logger.info(f"Found latest commit", repo=repo, tag=tag, commit=commit)

    return repo_infos


def create_tag_prefix(network: Network) -> str:
    prefix = ""

    if network != "main":
        prefix += f"{network}-"

    return prefix
