import os
import re
from typing import Callable, Dict, Iterator, List, Optional, Tuple

import yaml


class ManifestManager:
    CONFIGMAP_VERSIONS = r"configmap-versions\.yaml"
    KUSTOMIZATION = r"kustomization\.yaml"
    EXPLORER = r"explorer\.yaml"

    MINERS = r"miner-([0-9]+)\.yaml"
    HEADLESSES = r"remote-headless-([0-9]+)\.yaml"
    FULL_STATES = r"full-state-([0-9]+)\.yaml"
    MINER = r"miner\.yaml"
    HEADLESS = r"remote-headless\.yaml"
    FULL_STATE = r"full-state\.yaml"

    SNAPSHOT_FULL = r"snapshot-full\.yaml"
    SNAPSHOT_PARTITION = r"snapshot-partition\.yaml"
    SNAPSHOT_PARTITION_RESET = r"snapshot-partition-reset\.yaml"

    TCP_SEED_DEPLOYMENT = r"tcp-seed-deployment-([0-9+])\.yaml"
    SEED_DEPLOYMENT = r"seed-deployment-([0-9+])\.yaml"

    DATA_PROVIDER = r"data-provider\.yaml"
    DATA_PROVIDER_DB = r"data-provider-db\.yaml"

    FILES = frozenset(
        [
            CONFIGMAP_VERSIONS,
            KUSTOMIZATION,
            MINERS,
            HEADLESSES,
            EXPLORER,
            MINER,
            HEADLESS,
            FULL_STATE,
            SNAPSHOT_FULL,
            SNAPSHOT_PARTITION,
            SNAPSHOT_PARTITION_RESET,
            DATA_PROVIDER,
            DATA_PROVIDER_DB,
        ]
    )

    def __init__(self, repo_infos, base_dir: str, *, apv: str) -> None:
        self.repo_map: Dict[str, Tuple[str, str]] = {
            repo_info[0]: (repo_info[1], repo_info[2]) for repo_info in repo_infos
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
            self.MINERS: self.replace_miner,
            self.HEADLESSES: self.replace_headless,
            self.EXPLORER: self.replace_explorer,
            self.MINER: self.replace_miner,
            self.HEADLESS: self.replace_headless,
            self.FULL_STATE: self.replace_full_state,
            self.SNAPSHOT_FULL: self.replace_snapshot_full,
            self.SNAPSHOT_PARTITION: self.replace_snapshot_partition,
            self.SNAPSHOT_PARTITION_RESET: self.replace_snapshot_partition_reset,
            self.TCP_SEED_DEPLOYMENT: self.replace_tcp_seed,
            self.SEED_DEPLOYMENT: self.replace_seed,
            self.DATA_PROVIDER: self.replace_data_provider,
            self.DATA_PROVIDER_DB: self.replace_data_provider_db,
        }

        for r in self.FILES:
            m = re.match(r, file)

            if m:
                groups = m.groups()
                if groups:
                    return replacement[r](int(groups[0]))
                else:
                    return replacement[r]()

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
            "kustomization-onboarding-headless": "NineChronicles.Headless",
        }

        with open(os.path.join(self.base_dir, "kustomization.yaml")) as f:
            doc = yaml.safe_load(f)
            for image in doc["images"]:
                try:
                    tag, commit = self.repo_map[IMAGE_NAME_MAP[image["name"]]]

                    if not tag:
                        image["newTag"] = f"git-{commit}"
                    else:
                        image["newTag"] = tag
                except KeyError:
                    pass
            new_doc = yaml.safe_dump(doc, sort_keys=False)
        return new_doc

    def replace_miner(self, index: Optional[int] = None) -> str:
        filename = f"miner-{index}.yaml" if index else f"miner.yaml"

        return self.replace_headless_image(filename)

    def replace_headless(self, index: Optional[int]) -> str:
        filename = f"remote-headless-{index}.yaml" if index else f"remote-headless.yaml"
        return self.replace_headless_image(filename)

    def replace_full_state(self) -> str:
        filename = "full-state.yaml"
        return self.replace_headless_image(filename)

    def replace_headless_image(self, filename: str):
        with open(os.path.join(self.base_dir, filename)) as f:
            doc = yaml.safe_load(f)

            doc["spec"]["template"]["spec"]["containers"][0][
                "image"
            ] = self.get_headless_image()

            new_doc = yaml.safe_dump(doc, sort_keys=False)
        return new_doc

    def replace_explorer(self) -> str:
        filename = "explorer.yaml"

        with open(os.path.join(self.base_dir, filename)) as f:
            doc = yaml.safe_load(f)

            doc["items"][0]["spec"]["template"]["spec"]["containers"][0][
                "image"
            ] = self.get_headless_image()

            new_doc = yaml.safe_dump(doc, sort_keys=False)
        return new_doc

    def replace_snapshot_full(self) -> str:
        filename = "snapshot-full.yaml"

        with open(os.path.join(self.base_dir, filename)) as f:
            doc = yaml.safe_load(f)

            doc["spec"]["jobTemplate"]["spec"]["template"]["spec"]["initContainers"][0][
                "image"
            ] = self.get_headless_image()

            new_doc = yaml.safe_dump(doc, sort_keys=False)
        return new_doc

    def replace_snapshot_partition_reset(self) -> str:
        filename = "snapshot-partition-reset.yaml"

        with open(os.path.join(self.base_dir, filename)) as f:
            doc = yaml.safe_load(f)

            doc["spec"]["jobTemplate"]["spec"]["template"]["spec"]["initContainers"][1][
                "image"
            ] = self.get_headless_image()
            doc["spec"]["jobTemplate"]["spec"]["template"]["spec"]["initContainers"][3][
                "image"
            ] = self.get_headless_image()

            new_doc = yaml.safe_dump(doc, sort_keys=False, width=83)
        return new_doc

    def replace_seed(self, index: Optional[int]):
        filename = f"seed-deployment-{index}.yaml" if index else f"seed-deployment.yaml"
        _, commit = self.repo_map["libplanet-seed"]

        with open(os.path.join(self.base_dir, filename)) as f:
            doc = yaml.safe_load(f)

            doc["spec"]["template"]["spec"]["containers"][0][
                "image"
            ] = f"planetariumhq/libplanet-seed:git-{commit}"

            new_doc = yaml.safe_dump(doc, sort_keys=False)
        return new_doc

    def replace_tcp_seed(self, index: Optional[int]):
        filename = (
            f"tcp-seed-deployment-{index}.yaml"
            if index
            else f"tcp-seed-deployment.yaml"
        )
        _, commit = self.repo_map["libplanet-seed"]

        with open(os.path.join(self.base_dir, filename)) as f:
            doc = yaml.safe_load(f)

            doc["spec"]["template"]["spec"]["containers"][0][
                "image"
            ] = f"planetariumhq/libplanet-seed:git-{commit}"

            new_doc = yaml.safe_dump(doc, sort_keys=False)
        return new_doc

    def replace_data_provider(self):
        filename = "data-provider.yaml"
        _, commit = self.repo_map["NineChronicles.DataProvider"]

        with open(os.path.join(self.base_dir, filename)) as f:
            doc = yaml.safe_load(f)

            doc["spec"]["template"]["spec"]["containers"][0][
                "image"
            ] = f"planetariumhq/ninechronicles-dataprovider:git-{commit}"

            new_doc = yaml.safe_dump(doc, sort_keys=False)
        return new_doc

    def replace_data_provider_db(self):
        filename = "data-provider-db.yaml"
        _, commit = self.repo_map["NineChronicles.DataProvider"]

        with open(os.path.join(self.base_dir, filename)) as f:
            doc = yaml.safe_load(f)

            doc["spec"]["template"]["spec"]["containers"][0][
                "image"
            ] = f"planetariumhq/ninechronicles-dataprovider:git-{commit}"

            new_doc = yaml.safe_dump(doc, sort_keys=False)
        return new_doc

    def replace_snapshot_partition(self) -> str:
        filename = "snapshot-partition.yaml"

        with open(os.path.join(self.base_dir, filename)) as f:
            doc = yaml.safe_load(f)

            doc["spec"]["jobTemplate"]["spec"]["template"]["spec"]["initContainers"][0][
                "image"
            ] = self.get_headless_image()

            new_doc = yaml.safe_dump(doc, sort_keys=False)
        return new_doc

    def get_headless_image(self):
        tag, commit = self.repo_map["NineChronicles.Headless"]
        if tag.startswith("internal"):
            image = f"planetariumhq/ninechronicles-headless:git-{commit}"
        else:
            if not tag:
                raise ValueError("Tag required")
            image = f"planetariumhq/ninechronicles-headless:{tag}"

        return image
