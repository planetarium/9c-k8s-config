from operator import index
import os
import re
import yaml
from typing import Callable, Dict, Iterator, List, Optional, Tuple


class ManifestManager:
    CONFIGMAP_VERSIONS = r"configmap-versions.yaml"
    KUSTOMIZATION = r"kustomization.yaml"
    MINER = r"miner-([0-9]+)\.yaml"
    HEADLESS = r"remote-headless-([0-9]+)\.yaml"

    FILES = frozenset([CONFIGMAP_VERSIONS, KUSTOMIZATION, MINER, HEADLESS])

    def __init__(
        self, repo_infos, base_dir: str, *, apv: Optional[str] = None
    ) -> None:
        self.repo_map = {
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
        if not self.apv:
            raise ValueError("apv is required!")

        with open(os.path.join(self.base_dir, "configmap-versions.yaml")) as f:
            doc = yaml.safe_load(f)
            doc["data"]["APP_PROTOCOL_VERSION"] = self.apv
            new_doc = yaml.safe_dump(doc)
        return new_doc

    def replace_kustomization(self) -> str:
        with open(os.path.join(self.base_dir, "kustomization.yaml")) as f:
            doc = yaml.safe_load(f)
            for image in doc["images"]:
                if image["name"] == "kustomization-ninechronicles-headless":
                    image[
                        "newTag"
                    ] = f"git-{self.repo_map['NineChronicles.Headless'][1]}"
                elif (
                    image["name"]
                    == "kustomization-ninechronicles-dataprovider"
                ):
                    image[
                        "newTag"
                    ] = f"git-{self.repo_map['NineChronicles.DataProvider'][1]}"
            new_doc = yaml.safe_dump(doc)
        return new_doc

    def replace_miner(self, index: Optional[int]) -> str:
        with open(os.path.join(self.base_dir, f"miner-{index}.yaml")) as f:
            doc = yaml.safe_load(f)
            new_doc = yaml.safe_dump(doc)
        return new_doc

    def replace_headless(self, index: Optional[int]) -> str:
        pass
