import structlog

from toolbelt.client.github import GithubClient
from toolbelt.types import Network, RepoInfos
from toolbelt.utils.parse import latest_tag

REPOS = (
    "9c-launcher",
    "NineChronicles",
    "NineChronicles.Headless",
    "NineChronicles.DataProvider",
)

logger = structlog.get_logger(__name__)


def get_latest_commits(
    github_client: GithubClient, network: Network, branch: str, rc: int
):
    repo_infos: RepoInfos = []
    for repo in REPOS:
        github_client.repo = repo

        if network == "internal":
            r = github_client.get_branch(branch)

            commit = r["commit"]["sha"]
            tag = None
            repo_infos.append((repo, tag, commit))
        elif network == "main":
            r = github_client.get_tags(per_page=100)
            tag, commit = latest_tag(r, rc, prefix=create_tag_prefix(network))

        logger.info(f"Found latest commit", repo=repo, tag=tag, commit=commit)

    return repo_infos


def create_tag_prefix(network: Network) -> str:
    prefix = ""

    if network != "main":
        prefix += f"{network}-"

    return prefix
