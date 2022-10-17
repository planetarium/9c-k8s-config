import os
import re
from typing import Callable, Dict, Iterator, List, Optional, Tuple

import yaml


class ManifestManager:
    CONFIGMAP_VERSIONS = r"configmap-versions.yaml"
    KUSTOMIZATION = r"kustomization.yaml"
    MINER = r"miner-([0-9]+)\.yaml"
    HEADLESS = r"remote-headless-([0-9]+)\.yaml"

    FILES = frozenset([CONFIGMAP_VERSIONS, KUSTOMIZATION, MINER, HEADLESS])

    def __init__(self, repo_infos, base_dir: str, *, apv: str) -> None:
        self.repo_map: Dict[str, Tuple[str, str]] = {
            repo_info[0]: (repo_info[1], repo_info[2])
            for repo_info in repo_infos
        }
        self.base_dir = base_dir
        self.apv = apv

    def replace_manifests(self, files: List[str]) -> Iterator[str]:
        for file in files:
            yield self.match(file)

    def match(self, file: str):
        replacement: Dict[str, Callable] = {
            self.CONFIGMAP_VERSIONS: self.replace_configmap_versions,
            self.KUSTOMIZATION: self.replace_kustomization,
            self.MINER: self.replace_miner,
            self.HEADLESS: self.replace_headless,
        }

        for r in self.FILES:
            m = re.match(r, file)

            if m:
                groups = m.groups()
                if groups:
                    replacement[r](int(groups[0]))
                else:
                    replacement[r]()

    def replace_configmap_versions(self) -> str:
        with open(os.path.join(self.base_dir, "configmap-versions.yaml")) as f:
            doc = yaml.safe_load(f)
            doc["data"]["APP_PROTOCOL_VERSION"] = self.apv
            new_doc = yaml.safe_dump(doc)
        return new_doc

    def replace_kustomization(self) -> str:
        IMAGE_NAME_MAP = {
            "kustomization-ninechronicles-headless": "NineChronicles.Headless",
            "kustomization-ninechronicles-dataprovider": "NineChronicles.DataProvider",
            "kustomization-libplanet-seed": "libplanet-seed",
            "kustomization-ninechronicles-snapshot": "NineChronicles.Snapshot",
            "kustomization-ninechronicles-onboarding": "9c-onboarding",
        }

        with open(os.path.join(self.base_dir, "kustomization.yaml")) as f:
            doc = yaml.safe_load(f)
            for image in doc["images"]:
                try:
                    commit = self.repo_map[IMAGE_NAME_MAP[image["name"]]][1]

                    image["newTag"] = f"git-{commit}"
                except KeyError:
                    pass
            new_doc = yaml.safe_dump(doc, sort_keys=False)
        return new_doc

    def replace_miner(self, index: Optional[int] = None) -> str:
        filename = f"miner-{index}.yaml" if index else f"miner.yaml"

        return self.replace_headless_image(filename)

    def replace_headless(self, index: Optional[int]) -> str:
        filename = (
            f"remote-headless-{index}.yaml"
            if index
            else f"remote-headless.yaml"
        )
        return self.replace_headless_image(filename)

    def replace_headless_image(self, filename: str):
        tag, commit = self.repo_map["NineChronicles.Headless"]
        if tag.startswith("internal"):
            image = f"planetariumhq/ninechronicles-headless:git-{commit}"
        else:
            image = f"planetariumhq/ninechronicles-headless:v{self.apv.split('/')[0]}"

        with open(os.path.join(self.base_dir, filename)) as f:
            doc = yaml.safe_load(f)

            doc["spec"]["template"]["spec"]["containers"][0]["image"] = image

            new_doc = yaml.safe_dump(doc, sort_keys=False)
        return new_doc
