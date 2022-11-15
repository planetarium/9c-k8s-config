import requests
import structlog

from toolbelt.client import GithubClient, DockerClient
from toolbelt.config import config
from toolbelt.prepare.repos import get_latest_commits
from toolbelt.types import Network, RepoInfos

logger = structlog.get_logger(__name__)


def check_headless_image(network: Network, rc: int):
    github_client = GithubClient(config.github_token, org="planetarium", repo="")
    docker_client = DockerClient(
        config.docker_username,
        config.docker_password,
        namespace="planetariumhq",
    )

    if config.env == "test":
        branch = f"test-rc-v{rc}"
    else:
        branch = f"rc-v{rc}"

    repo_infos: RepoInfos = get_latest_commits(
        github_client,
        network,
        rc,
        (("NineChronicles.Headless", branch),),
        launcher_commit="",
        player_commit=""
    )
    try:
        commit = repo_infos[0][2]
        docker_client.check_image_exists("ninechronicles-headless", f"git-{commit}")
        logger.info(f"Found headless docker image tag git-{commit}")
    except IndexError:
        raise ValueError("No Commit for input branch")
