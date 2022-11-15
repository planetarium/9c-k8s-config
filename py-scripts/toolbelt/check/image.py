import requests
import structlog

from toolbelt.client import GithubClient, DockerClient
from toolbelt.config import config
from toolbelt.prepare.repos import get_latest_commits
from toolbelt.types import Network, RepoInfos

logger = structlog.get_logger(__name__)


def check_headless_image(network: Network, rc_number: int, deploy_number: str):
    github_client = GithubClient(config.github_token, org="planetarium", repo="")
    docker_client = DockerClient(
        namespace="planetariumhq",
    )

    if config.env == "test":
        branch = f"test-rc-v{rc_number}-{deploy_number}"
    else:
        branch = f"rc-v{rc_number}-{deploy_number}"

    repo_infos: RepoInfos = get_latest_commits(
        github_client,
        network,
        rc_number,
        (("NineChronicles.Headless", branch),),
    )
    try:
        commit = repo_infos[0][2]
        exists = docker_client.check_image_exists("ninechronicles-headless", f"git-{commit}")
        if exists:
            logger.info(f"Found headless docker image tag git-{commit}")
        else:
            raise ValueError(f"Docker image for tag git-{commit} not in the repository")
    except IndexError:
        raise ValueError(f"No Commit {commit} for input branch")

    if network == "main" and config.env == "production":
        exists = docker_client.check_image_exists("ninechronicles-headless", f"v{rc_number}-{deploy_number}")
        if exists:
            logger.info(f"Found headless docker image tag v{rc_number}-{deploy_number}")
        else:
            raise ValueError(f"Docker image for tag v{rc_number}-{deploy_number} not in the repository")
