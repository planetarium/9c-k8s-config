import os

from toolbelt.constants import INTERNAL_DIR
from toolbelt.v2.artifacts.launcher import release_launcher
from toolbelt.v2.artifacts.player import copy_players
from toolbelt.v2.github.parser import latest_rc_tags
from toolbelt.k8s_update.update import update_manifests
from toolbelt.v2.planet.apv import generate_internal_apv, get_old_internal_apv
from toolbelt.types import Mode


def internal_release(tag: str, mode: Mode = ""):
    old_apv = get_old_internal_apv(
        os.path.join(f"{INTERNAL_DIR}", "configmap-versions.yaml")
    )

    # get tag, sha from repository
    launcher_tag, launcher_sha = latest_rc_tags("9c-launcher", mode=mode)
    player_tag, player_sha = latest_rc_tags("NineChronicles", mode=mode)
    headless_tag, headless_sha = latest_rc_tags(
        "NineChronicles.Headless", mode=mode
    )

    print("Tags", launcher_tag, player_tag, headless_tag)
    print()
    print("Commit sha", launcher_sha, player_sha, headless_sha)
    print()

    internal_apv = generate_internal_apv(old_apv, launcher_sha, player_sha)

    print("Generated", internal_apv)
    print()

    # # artifact
    release_launcher(internal_apv, launcher_sha, "internal", mode)
    copy_players(internal_apv.version, player_sha, "internal", mode)

    # # manifest
    update_manifests(headless_sha, internal_apv.raw, tag[:-4])


if __name__ == "__main__":
    internal_release("test-v100300-rc1")
