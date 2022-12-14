from typing import Dict, Optional

import structlog
from requests import HTTPError

from toolbelt.client import GithubClient, SlackClient
from toolbelt.config import config
from toolbelt.constants import (
    DP_REPO,
    HEADLESS_REPO,
    INTERNAL_DIR,
    K8S_REPO,
    LAUNCHER_REPO,
    MAIN_DIR,
    PLAYER_REPO,
    RELEASE_BASE_URL,
    SEED_REPO,
)
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


def prepare_release(
    network: Network,
    rc_number: int,
    deploy_number: int,
    *,
    launcher_commit: Optional[str],
    player_commit: Optional[str],
    slack_channel: Optional[str],
):
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
        rc_branch = f"test-rc-v{rc_number}-{deploy_number}"
    else:
        rc_branch = f"rc-v{rc_number}-{deploy_number}"

    repos = [
        (LAUNCHER_REPO, rc_branch),
        (PLAYER_REPO, rc_branch),
        (HEADLESS_REPO, rc_branch),
        (DP_REPO, rc_branch),
        (SEED_REPO, "main"),
    ]

    repo_infos: RepoInfos = get_latest_commits(
        github_client,
        network,
        rc_number,
        repos,
        launcher_commit=launcher_commit,
        player_commit=player_commit,
    )

    apv = create_apv(planet, rc_number, network, repo_infos)
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

    github_client.repo = K8S_REPO

    if config.env == "test":
        target_branch = "ci-test"
    else:
        target_branch = "main"

    MANIFESTS_UPDATER[network](github_client, repo_infos, apv, target_branch)

    if network == "internal":
        for info in repo_infos:
            repo, _, commit = info
            github_client.repo = repo

            try:
                github_client.create_ref(
                    f"refs/tags/internal-v{rc_number}-{deploy_number}-{apv.version}",
                    commit,
                )
            except HTTPError as e:
                logger.info("Failed internal tagging", err=e)

    if slack_channel:
        slack.send_simple_msg(
            slack_channel,
            f"[CI] Finish prepare {network} release",
        )


def create_apv(
    planet: Planet,
    rc_number: int,
    network: Network,
    repo_infos: RepoInfos,
) -> Apv:
    prev_apv = get_apv(APV_DIR_MAP[network])
    prev_apv_detail = planet.apv_analyze(prev_apv)

    apvIncreaseRequired = True
    if network == "main":
        apv_version = rc_number

        if rc_number == prev_apv_detail.version:
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
