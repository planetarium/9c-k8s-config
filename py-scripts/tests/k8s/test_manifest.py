import shutil
import tempfile

from tests.constants import DATA_DIR
from toolbelt.k8s import ManifestManager


def test_replace_manifests(mocker):
    with tempfile.TemporaryDirectory() as tmp_path:
        repo_infos = [
            ("NineChronicles.DataProvider", "test tag", "dataprovider1"),
            ("NineChronicles.Headless", "test tag", "headless1"),
        ]
        manager = ManifestManager(repo_infos, tmp_path, apv="10/test")

        files = [
            "configmap-versions.yaml",
            "kustomization.yaml",
            "miner-1.yaml",
            "remote-headless-2.yaml",
        ]
        replace_miner = mocker.patch.object(ManifestManager, "replace_miner")
        replace_headless = mocker.patch.object(
            ManifestManager, "replace_headless"
        )
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


def test_replace_configmap_versions():
    with open(
        f"{DATA_DIR}/k8s/configmap-versions/result-configmap-versions.yaml",
        mode="r",
    ) as f:
        expect_result = f.read()

    with tempfile.TemporaryDirectory() as tmp_path:
        manager = ManifestManager([], tmp_path, apv="10/test_apv")

        shutil.copyfile(
            f"{DATA_DIR}/k8s/configmap-versions/configmap-versions.yaml",
            f"{tmp_path}/configmap-versions.yaml",
        )
        r = manager.replace_configmap_versions()

        assert r == expect_result


def test_replace_kustomization():
    with open(
        f"{DATA_DIR}/k8s/kustomization/result-kustomization.yaml", mode="r"
    ) as f:
        expect_result = f.read()

    with tempfile.TemporaryDirectory() as tmp_path:
        manager = ManifestManager(
            [
                ("NineChronicles.DataProvider", "test tag", "dataprovider1"),
                ("NineChronicles.Headless", "test tag", "headless1"),
            ],
            tmp_path,
            apv="10/test",
        )

        shutil.copyfile(
            f"{DATA_DIR}/k8s/kustomization/kustomization.yaml",
            f"{tmp_path}/kustomization.yaml",
        )

        result = manager.replace_kustomization()

        assert result == expect_result


def test_replace_miner():
    with open(f"{DATA_DIR}/k8s/miner/result-miner-1.yaml", mode="r") as f:
        expect_result = f.read()

    with tempfile.TemporaryDirectory() as tmp_path:
        manager = ManifestManager(
            [
                ("NineChronicles.Headless", "test tag", "headless1"),
            ],
            tmp_path,
            apv="10/test",
        )

        shutil.copyfile(
            f"{DATA_DIR}/k8s/miner/miner-1.yaml",
            f"{tmp_path}/miner-1.yaml",
        )

        result = manager.replace_miner(1)

        assert result == expect_result
