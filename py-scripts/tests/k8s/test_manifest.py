import shutil
import tempfile

import pytest

from tests.constants import DATA_DIR
from toolbelt.k8s import ManifestManager


def test_replace_manifests(mocker):
    with tempfile.TemporaryDirectory() as tmp_path:
        repo_infos = [
            ("NineChronicles.DataProvider", "v100310-rc1", "dataprovider1"),
            ("NineChronicles.Headless", "v100310-rc1", "headless1"),
        ]
        manager = ManifestManager(repo_infos, tmp_path, apv="10/test")

        files = [
            "configmap-versions.yaml",
            "kustomization.yaml",
            "miner-1.yaml",
            "remote-headless-2.yaml",
        ]
        replace_miner = mocker.patch.object(ManifestManager, "replace_miner")
        replace_headless = mocker.patch.object(ManifestManager, "replace_headless")
        replace_kustomization = mocker.patch.object(
            ManifestManager, "replace_kustomization"
        )
        replace_configmap_versions = mocker.patch.object(
            ManifestManager, "replace_configmap_versions"
        )

        for _ in manager.replace_manifests(files):
            pass

        replace_configmap_versions.assert_called_once()
        replace_kustomization.assert_called_once()
        replace_miner.assert_called_once_with(1)
        replace_headless.assert_called_once_with(2)


@pytest.mark.parametrize(
    "filename,repo_infos,apv",
    [
        (
            "snapshot-full",
            [
                ("NineChronicles.Headless", "v100310-rc1", "headless1"),
            ],
            "10/test",
        ),
        (
            "explorer",
            [
                ("NineChronicles.Headless", "internal-test", "headless1"),
            ],
            "11/testtest",
        ),
        (
            "remote-headless-1",
            [
                ("NineChronicles.Headless", "internal-test", "headless1"),
            ],
            "15/testtest",
        ),
        (
            "full-state",
            [
                ("NineChronicles.Headless", "v100310-rc1", "headless1"),
            ],
            "101233/teststs",
        ),
        (
            "miner-1",
            [
                ("NineChronicles.Headless", "v100310-rc1", "headless1"),
            ],
            "100/test-test",
        ),
        (
            "snapshot-partition-reset",
            [
                ("NineChronicles.Headless", "v100310-rc1", "headless1"),
            ],
            "19/test-test",
        ),
        (
            "snapshot-partition",
            [
                ("NineChronicles.Headless", "v100310-rc1", "headless1"),
            ],
            "1192/test-test",
        ),
        (
            "kustomization",
            [
                ("NineChronicles.DataProvider", None, "dp1"),
                ("libplanet-seed", None, "seed1"),
                ("NineChronicles.Headless", None, "headless1"),
                ("NineChronicles.Snapshot", "v100310-rc1", "snapshot1"),
                ("9c-onboarding", None, "board1"),
            ],
            "10/test",
        ),
        (
            "configmap-versions",
            [],
            "10/test",
        ),
        (
            "tcp-seed-deployment-1",
            [
                ("libplanet-seed", "v100310-rc1", "seed1"),
            ],
            "10/test",
        ),
        (
            "seed-deployment-1",
            [
                ("libplanet-seed", "v100310-rc1", "seed1"),
            ],
            "10/test",
        ),
        (
            "data-provider",
            [
                ("NineChronicles.DataProvider", "v100310-rc1", "dp1"),
            ],
            "10/test",
        ),
        (
            "data-provider-db",
            [
                ("NineChronicles.DataProvider", "v100310-rc1", "dp1"),
            ],
            "10/test",
        ),
    ],
)
def test_replace(filename, repo_infos, apv):
    with open(f"{DATA_DIR}/k8s/{filename}/result-{filename}.yaml", mode="r") as f:
        expect_result = f.read()

    with tempfile.TemporaryDirectory() as tmp_path:
        manager = ManifestManager(
            repo_infos,
            tmp_path,
            apv=apv,
        )

        shutil.copyfile(
            f"{DATA_DIR}/k8s/{filename}/{filename}.yaml",
            f"{tmp_path}/{filename}.yaml",
        )

        for result in manager.replace_manifests([f"{filename}.yaml"]):
            assert result == expect_result
