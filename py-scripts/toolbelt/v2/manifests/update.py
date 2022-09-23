import os

import yaml

from toolbelt.constants import INTERNAL_DIR
from toolbelt.v2.github.commit import commit_manifests

IMAGE_PATH = "9c-internal/kustomization.yaml"
APV_PATH = "9c-internal/configmap-versions.yaml"


def update_manifests(sha: str, apv: str, branch: str):
    update_headless(sha, branch)
    update_apv(apv, branch)


def update_headless(sha: str, branch: str):
    with open(f"../{IMAGE_PATH}") as f:
        doc = yaml.safe_load(f)
        for image in doc["images"]:
            if image["name"] == "kustomization-ninechronicles-headless":
                image["newTag"] = f"git-{sha}"
        new_doc = yaml.safe_dump(doc)
        commit_manifests(branch, IMAGE_PATH, new_doc)


def update_apv(apv: str, branch: str):
    with open(f"../{APV_PATH}") as f:
        doc = yaml.safe_load(f)
        doc["data"]["APP_PROTOCOL_VERSION"] = apv
        new_doc = yaml.safe_dump(doc)
        commit_manifests(branch, APV_PATH, new_doc)
