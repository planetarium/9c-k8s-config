from typing import Dict, Optional

import structlog

from toolbelt.client import GithubClient, SlackClient
from toolbelt.config import config
from toolbelt.constants import INTERNAL_DIR, MAIN_DIR, MAIN_REPO, RELEASE_BASE_URL
from toolbelt.k8s.apv import get_apv
from toolbelt.planet import Apv, Planet, generate_extra
from toolbelt.types import Network, RepoInfos
from toolbelt.utils.url import build_download_url

from .copy_machine import COPY_MACHINE
from .manifest import MANIFESTS_UPDATER
from .repos import get_latest_commits

logger = structlog.get_logger(__name__)

PROJECT_NAME_MAP = {"9c-launcher": "launcher", "NineChronicles": "player"}
APV_DIR_MAP: Dict[Network, str] = {"internal": INTERNAL_DIR, "main": MAIN_DIR}


def prepare_release(network: Network, rc: int, *, slack_channel: Optional[str]):
    planet = Planet(config.key_address, config.key_passphrase)
    slack = SlackClient(config.slack_token)
    github_client = GithubClient(config.github_token, org="planetarium", repo="")

    logger.info(f"Start prepare release", network=network, isTest=config.env == "test")
    if slack_channel:
        slack.send_simple_msg(
            slack_channel,
            f"[CI] Start prepare {network} release",
        )

    if config.env == "test":
        rc_branch = f"test-rc-v{rc}"
    else:
        rc_branch = f"rc-v{rc}"

    repo_infos: RepoInfos = get_latest_commits(github_client, network, rc_branch, rc)

    apv = create_apv(planet, rc, network, repo_infos)
    logger.info(f"Confirmed apv_version", version=apv.version, extra=apv.extra)

    bucket_prefix = ""
    if config.env == "test":
        bucket_prefix = "ci-test/"

    logger.info("Start player, launcher artifacts copy")
    for info in repo_infos:
        repo, _, commit = info

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

    github_client.repo = MAIN_REPO

    if config.env == "test":
        target_branch = f"test-rc-v{rc}"
    else:
        target_branch = "main"

    MANIFESTS_UPDATER[network](github_client, repo_infos, apv, target_branch)

    if slack_channel:
        slack.send_simple_msg(
            slack_channel,
            f"[CI] Finish prepare {network} release",
        )


def create_apv(
    planet: Planet,
    rc: int,
    network: Network,
    repo_infos: RepoInfos,
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
