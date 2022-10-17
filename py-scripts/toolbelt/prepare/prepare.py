from typing import Dict, List, Optional, Tuple

import structlog

from toolbelt.client import GithubClient, SlackClient
from toolbelt.config import config
from toolbelt.constants import INTERNAL_DIR, MAIN_DIR, RELEASE_BASE_URL
from toolbelt.github.parser import latest_tag
from toolbelt.k8s.apv import get_apv
from toolbelt.k8s.manifest import UPDATE_MANIFESTS
from toolbelt.planet import Apv, Planet, generate_extra
from toolbelt.types import Network
from toolbelt.utils.url import build_download_url

from .copy_machine import COPY_MACHINE

logger = structlog.get_logger(__name__)

REPOS = (
    "9c-launcher",
    "NineChronicles",
    "NineChronicles.Headless",
    "NineChronicles.DataProvider",
)
PROJECT_NAME_MAP = {"9c-launcher": "launcher", "NineChronicles": "player"}
APV_DIR_MAP: Dict[Network, str] = {"internal": INTERNAL_DIR, "main": MAIN_DIR}


def prepare_release(network: Network, rc: int, *, slack_channel: Optional[str]):
    planet = Planet(config.key_address, config.key_passphrase)
    slack = SlackClient(config.slack_token)

    logger.info(f"Start prepare release", network=network, isTest=config.env == "test")
    if slack_channel:
        slack.send_simple_msg(
            slack_channel,
            f"[CI] Start prepare {network} release",
        )

    github_client = GithubClient(config.github_token, org="planetarium", repo="")

    repo_infos: List[Tuple[str, str, str]] = []
    for repo in REPOS:
        github_client.repo = repo

        tags = []
        for v in github_client.get_tags(per_page=100):
            tags.extend(v)

        tag = latest_tag(tags, rc, prefix=create_tag_prefix(network))
        repo_infos.append((repo, *tag))

        logger.info(f"Found tag", repo=repo, tag=tag)

    apv = create_apv(planet, rc, network, repo_infos)
    logger.info(f"Confirmed apv_version", version=apv.version, extra=apv.extra)

    bucket_prefix = ""
    if config.env == "test":
        bucket_prefix = "ci-test/"

    logger.info("Start player, launcher artifacts copy")
    for info in repo_infos:
        repo, tag, commit = info

        try:
            COPY_MACHINE[PROJECT_NAME_MAP[repo]](
                apv=apv,
                commit=commit,
                network=network,
                prefix=bucket_prefix,
            )
            logger.info(f"Finish copy", repo=repo)

            download_url = build_download_url(
                RELEASE_BASE_URL,
                network,
                apv.version,
                PROJECT_NAME_MAP[repo],
                commit,
                "Windows.zip",
            )
            if slack_channel:
                slack.send_simple_msg(
                    slack_channel,
                    f"[CI] Prepared binary - {download_url}",
                )
        except KeyError:
            pass

    if config.env == "test":
        branch = f"test-rc-v{rc}"
    else:
        branch = f"rc-v{rc}"

    UPDATE_MANIFESTS[network](repo_infos, branch, apv)

    if slack_channel:
        slack.send_simple_msg(
            slack_channel,
            f"[CI] Finish prepare {network} release",
        )


def create_tag_prefix(network: Network) -> str:
    prefix = ""

    if network != "main":
        prefix += f"{network}-"

    return prefix


def create_apv(
    planet: Planet,
    rc: int,
    network: Network,
    repo_infos: List[Tuple[str, str, str]],
) -> Apv:
    prev_apv = get_apv(APV_DIR_MAP[network])
    prev_apv_detail = planet.apv_analyze(prev_apv)

    apvIncreaseRequired = True
    if network == "main":
        apv_version = rc

        if rc == prev_apv_detail.version:
            apvIncreaseRequired = False
    else:
        apv_version = prev_apv_detail.version + 1

    commit_map = {}
    for info in repo_infos:
        repo, _, commit = info
        try:
            commit_map[PROJECT_NAME_MAP[repo]] = commit
        except KeyError:
            pass

    extra = generate_extra(commit_map, apvIncreaseRequired, prev_apv_detail.extra)
    apv = planet.apv_sign(
        apv_version,
        **extra,
    )

    return apv
