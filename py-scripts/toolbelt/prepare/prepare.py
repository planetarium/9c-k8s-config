import os
from typing import List

from toolbelt.client import GithubClient
from toolbelt.config import config
from toolbelt.constants import INTERNAL_DIR
from toolbelt.github.parser import latest_tag
from toolbelt.k8s.apv import get_old_internal_apv
from toolbelt.planet import Apv, Planet, generate_extra
from toolbelt.types import Network

REPOS = (
    "9c-launcher",
    "NineChronicles",
)
PROJECT_NAME_MAP = {"9c-launcher": "launcher", "NineChronicles": "player"}


def prepare_release(
    planet: Planet, network: Network, rc: int, no_create_apv: bool
):
    github_client = GithubClient(
        config.github_token, org="planetarium", repo=""
    )

    projects = []
    for repo in REPOS:
        github_client.repo = repo

        tags = []
        for v in github_client.get_tags(per_page=100):
            tags.extend(v)

        tag = latest_tag(tags, rc, prefix=create_tag_prefix(network))
        projects.append({"tag": tag, "name": PROJECT_NAME_MAP[repo]})

    apv = create_apv(planet, rc, network, projects)
    print(apv.version, apv.extra)
    print(projects)

    # release_launcher(internal_apv, launcher_sha, "internal", mode)
    # copy_players(internal_apv.version, player_sha, "internal", mode)

    # update_manifests(headless_sha, internal_apv.raw, tag[:-4])


def create_tag_prefix(network: Network) -> str:
    prefix = ""

    if network != "main":
        prefix += f"{network}-"

    return prefix


def create_apv(
    planet: Planet, rc: int, network: Network, projects: List[dict]
) -> Apv:
    prev_apv = get_old_internal_apv(
        os.path.join(f"{INTERNAL_DIR}", "configmap-versions.yaml")
    )
    prev_apv_detail = planet.apv_analyze(prev_apv)

    apvIncreaseRequired = True
    if network == "main":
        apv_version = rc

        if rc == prev_apv_detail.version:
            apvIncreaseRequired = False
    else:
        apv_version = prev_apv_detail.version + 1

    commit_map = {}
    for project in projects:
        commit_map[project["name"]] = project["tag"][1]

    extra = generate_extra(
        commit_map, apvIncreaseRequired, prev_apv_detail.extra
    )
    apv = planet.apv_sign(
        apv_version,
        **extra,
    )

    return apv
