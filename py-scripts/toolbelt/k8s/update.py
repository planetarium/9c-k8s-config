import os
from typing import List, Tuple

import yaml

from toolbelt.config import config
from toolbelt.constants import INTERNAL_DIR
from toolbelt.github.commit import commit_manifests
from toolbelt.planet import Apv

IMAGE_PATH = "9c-internal/kustomization.yaml"
APV_PATH = "9c-internal/configmap-versions.yaml"


def update_internal_manifests(
    repo_infos: List[Tuple[str, str, str]], branch: str, apv: Apv
):
    update_headless(repo_infos, branch)
    update_apv(apv.raw, branch)


def update_main_manifests(
    repo_infos: List[Tuple[str, str, str]], branch: str, apv: Apv
):
    pass


def update_headless(repo_infos: List[Tuple[str, str, str]], branch: str):
    repo_map = {repo_info[0]: (repo_info[1], repo_info[2]) for repo_info in repo_infos}

    with open(os.path.join(INTERNAL_DIR, "kustomization.yaml")) as f:
        doc = yaml.safe_load(f)
        for image in doc["images"]:
            if image["name"] == "kustomization-ninechronicles-headless":
                image["newTag"] = f"git-{repo_map['NineChronicles.Headless']}"
            elif image["name"] == "kustomization-ninechronicles-dataprovider":
                image["newTag"] = f"git-{repo_map['NineChronicles.DataProvider']}"
        new_doc = yaml.safe_dump(doc)
        commit_manifests(branch, IMAGE_PATH, new_doc)


def update_apv(apv: str, branch: str):
    with open(os.path.join(INTERNAL_DIR, "configmap-versions.yaml")) as f:
        doc = yaml.safe_load(f)
        doc["data"]["APP_PROTOCOL_VERSION"] = apv
        new_doc = yaml.safe_dump(doc)
        commit_manifests(branch, APV_PATH, new_doc)


UPDATE_MANIFESTS = {
    "internal": update_internal_manifests,
    "main": update_main_manifests,
}
