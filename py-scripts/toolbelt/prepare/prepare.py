import os
from typing import Optional
from toolbelt.constants import INTERNAL_DIR

from toolbelt.github.parser import latest_rc_tags
from toolbelt.k8s.apv import get_old_internal_apv
from toolbelt.k8s.update import update_manifests
from toolbelt.types import Network
from toolbelt.v2.artifacts.launcher import release_launcher
from toolbelt.v2.artifacts.player import copy_players

PROJECTS = (
    "9c-launcher",
    "NineChronicles",
)


def prepare_release(network: Network, tag: str, no_create_apv: bool):
    exists_apv = get_old_internal_apv(
        os.path.join(f"{INTERNAL_DIR}", "configmap-versions.yaml")
    )

    tags = {project: latest_rc_tags(project) for project in PROJECTS}

    print("Tags", launcher_tag, player_tag, headless_tag)
    print()
    print("Commit sha", launcher_sha, player_sha, headless_sha)
    print()

    internal_apv = generate_internal_apv(exists_apv, launcher_sha, player_sha)

    print("Generated", internal_apv)
    print()

    # # artifact
    release_launcher(internal_apv, launcher_sha, "internal", mode)
    copy_players(internal_apv.version, player_sha, "internal", mode)

    # # manifest
    update_manifests(headless_sha, internal_apv.raw, tag[:-4])
