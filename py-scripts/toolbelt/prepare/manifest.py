from typing import Callable, Dict, List, Tuple
from toolbelt.client import GithubClient
from toolbelt.constants import INTERNAL_DIR, MAIN_DIR, MAIN_REPO
from toolbelt.k8s import ManifestManager
from toolbelt.planet import Apv
from toolbelt.types import Network


def update_internal_manifests(
    github_client: GithubClient,
    repo_infos: List[Tuple[str, str, str]],
    apv: Apv,
    branch: str,
):
    manager = ManifestManager(repo_infos, INTERNAL_DIR, apv=apv.raw)
    files = ["configmap-versions.yaml", "kustomization.yaml"]

    for index, manifest in enumerate(manager.replace_manifests(files)):
        path = f"9c-internal/{files[index]}"
        message = f"INTERNAL: update {files[index]}"
        _, response = github_client.get_content(path, branch)

        github_client.update_content(
            commit=response["sha"],
            path=path,
            branch=branch,
            content=manifest,
            message=message,
        )


def update_main_manifests(
    github_client: GithubClient,
    repo_infos: List[Tuple[str, str, str]],
    apv: Apv,
    branch: str,
):
    manager = ManifestManager(repo_infos, MAIN_DIR, apv=apv.raw)
    configmap = ["configmap-versions.yaml"]
    explorer = ["explorer.yaml"]
    full_state = ["full-state.yaml"]
    snapshot_full = ["snapshot-full.yaml"]
    snapshot_partition_reset = ["snapshot-partition-reset.yaml"]
    snapshot_partition = ["snapshot-partition.yaml"]
    miners = [f"miner-{i}.yaml" for i in range(1, 5)]
    headlesses = [f"remote-headless-{i}.yaml" for i in range(1, 11)] + [
        "remote-headless-31.yaml",
        "remote-headless-99.yaml",
    ]
    files = (
        configmap
        + miners
        + headlesses
        + explorer
        + full_state
        + snapshot_full
        + snapshot_partition_reset
        + snapshot_partition
    )

    for index, manifest in enumerate(manager.replace_manifests(files)):
        path = f"9c-main/{files[index]}"
        message = f"MAIN: update {files[index]}"
        _, response = github_client.get_content(path, branch)

        github_client.update_content(
            commit=response["sha"],
            path=path,
            branch=branch,
            content=manifest,
            message=message,
        )


MANIFESTS_UPDATER: Dict[
    Network,
    Callable[[GithubClient, List[Tuple[str, str, str]], Apv, str], None],
] = {
    "internal": update_internal_manifests,
    "main": update_main_manifests,
}
