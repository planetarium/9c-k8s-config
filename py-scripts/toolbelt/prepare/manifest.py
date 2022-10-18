from typing import List, Tuple

from toolbelt.constants import INTERNAL_DIR, MAIN_DIR
from toolbelt.k8s import ManifestManager
from toolbelt.planet import Apv


def update_internal_manifests(
    repo_infos: List[Tuple[str, str, str]], apv: Apv, branch: str
):
    manager = ManifestManager(repo_infos, INTERNAL_DIR, apv=apv.raw)

    for manifest in manager.replace_manifests(
        ["configmap-versions.yaml", "kustomization.yaml"]
    ):
        pass


def update_main_manifests(
    repo_infos: List[Tuple[str, str, str]], apv: Apv, branch: str
):
    manager = ManifestManager(repo_infos, MAIN_DIR, apv=apv.raw)

    for manifest in manager.replace_manifests(
        ["configmap-versions.yaml", "kustomization.yaml"]
    ):
        pass


MANIFESTS_UPDATER = {
    "internal": update_internal_manifests,
    "main": update_main_manifests,
}
