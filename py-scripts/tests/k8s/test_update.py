import shutil
import tempfile

from tests.constants import DATA_DIR
from toolbelt.k8s.update import update_apv, update_internal_images


def test_update_apv(mocker):
    mocker.patch("toolbelt.github.commit.commit_manifests")

    with open(f"{DATA_DIR}/k8s/result-configmap-versions.yaml", mode="r") as f:
        expect_result = f.read()

    with tempfile.TemporaryDirectory() as tmp_path:
        shutil.copyfile(
            f"{DATA_DIR}/k8s/configmap-versions.yaml",
            f"{tmp_path}/configmap-versions.yaml",
        )
        mocker.patch("toolbelt.constants.INTERNAL_DIR", tmp_path)

        result = update_apv("10/testtest", "test branch")

        assert result == expect_result


def test_update_internal_images(mocker):
    mocker.patch("toolbelt.github.commit.commit_manifests")

    with open(f"{DATA_DIR}/k8s/result-kustomization.yaml", mode="r") as f:
        expect_result = f.read()

    with tempfile.TemporaryDirectory() as tmp_path:
        shutil.copyfile(
            f"{DATA_DIR}/k8s/kustomization.yaml",
            f"{tmp_path}/kustomization.yaml",
        )
        mocker.patch("toolbelt.constants.INTERNAL_DIR", tmp_path)

        result = update_internal_images(
            [
                ("NineChronicles.DataProvider", "test tag", "dataprovider1"),
                ("NineChronicles.Headless", "test tag", "headless1"),
            ],
            "test branch",
        )

        assert result == expect_result
