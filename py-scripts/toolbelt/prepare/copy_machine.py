import json
import os
import tarfile
import tempfile
import zipfile

import structlog
from py7zr import SevenZipFile

from toolbelt.client.aws import S3File
from toolbelt.planet.apv import Apv
from toolbelt.types import Network
from toolbelt.utils.url import build_download_url

ARTIFACTS = ["Windows.zip", "macOS.tar.gz", "Linux.tar.gz"]
ARTIFACT_BUCKET = "9c-artifacts"
RELEASE_BUCKET = "9c-release.planetariumhq.com"

unsigned_prefix = "Unsigned"
logger = structlog.get_logger(__name__)


def copy_players(
    *,
    apv: Apv,
    network: Network,
    commit: str,
    prefix: str = "",
):
    s3 = S3File(ARTIFACT_BUCKET)

    for file_name in ARTIFACTS:
        artifact_path = f"{commit}/{file_name}"
        logger.info(f"Start player {artifact_path} copy")

        release_file_name = file_name
        if network == "main":
            release_file_name = unsigned_prefix + file_name

        release_path = (
            prefix
            + build_download_url(
                "", network, apv.version, "player", commit, release_file_name
            )[1:]
        )

        s3.copy_from_bucket(
            artifact_path,
            RELEASE_BUCKET,
            release_path,
        )
        logger.info(f"Finish player {artifact_path} copy")


def copy_launchers(
    *,
    apv: Apv,
    network: Network,
    commit: str,
    prefix: str = "",
):
    artifact_bucket = S3File(ARTIFACT_BUCKET)
    release_bucket = S3File(RELEASE_BUCKET)
    release_path = (
        prefix
        + build_download_url("", network, apv.version, "launcher", commit, "")[1:-1]
    )

    for file_name in ARTIFACTS:
        artifact_path = f"9c-launcher/{commit}/{file_name}"

        os_name, extension = file_name.split(".", 1)

        with tempfile.TemporaryDirectory() as tmp_path:
            logger.info(f"Download launcher {artifact_path}", artifact=file_name)

            download(
                artifact_bucket,
                s3_path=artifact_path,
                path=tmp_path,
                os_name=os_name,
                extension=extension,
            )
            download_path = f"{tmp_path}/{file_name}"
            config_path = get_config_path(os_name)

            release_bucket.download(f"{network}/config.json", tmp_path)
            new_config = generate_new_config(network, apv, tmp_path)

            write_config(f"{tmp_path}/{config_path}", new_config)
            compress_launcher(tmp_path, os_name, extension)
            logger.info(f"Finish overwrite config", artifact=file_name)

            if network == "main":
                renamed_file_path = f"{tmp_path}/{unsigned_prefix}{file_name}"

                os.rename(download_path, renamed_file_path)
                download_path = renamed_file_path

            release_bucket.upload(
                download_path,
                release_path,
            )

            release_bucket.upload(f"{tmp_path}/config.json", f"{prefix}{network}")
            logger.info(
                f"Upload Finish",
                download_path=download_path,
                release_path=release_path,
            )


def download(s3: S3File, *, s3_path: str, path: str, os_name: str, extension: str):
    s3.download(s3_path, path)

    if extension == "tar.gz":
        zip = tarfile.open(f"{path}/{os_name}.{extension}")
        zip.extractall(f"{path}/{os_name}")
        zip.close()
    else:
        with SevenZipFile(f"{path}/{os_name}.{extension}", mode="r") as archive:
            archive.extractall(path=f"{path}/{os_name}")


def get_config_path(os_name: str):
    if os_name in ["Windows", "Linux"]:
        return f"{os_name}/resources/app/config.json"
    elif os_name == "macOS":
        return f"{os_name}/Nine Chronicles.app/Contents/Resources/app/config.json"
    else:
        raise ValueError(
            "Unsupported artifact name format: artifact name should be one of (macOS.tar.gz, Linux.tar.gz)"
        )


def write_config(config_path: str, config: str):
    with open(config_path, "w") as f:
        f.seek(0)
        json.dump(config, f, indent=4)
        f.truncate()


def compress_launcher(
    path: str,
    os_name: str,
    extension: str,
):
    if extension == "tar.gz":
        with tarfile.open(f"{path}/{os_name}.{extension}", "w:gz") as zip:
            for arcname in os.listdir(f"{path}/{os_name}"):
                name = os.path.join(path, os_name, arcname)
                zip.add(name, arcname=arcname)
    else:
        with zipfile.ZipFile(f"{path}/{os_name}.{extension}", mode="w") as archive:
            for p, _, files in os.walk(f"{path}/{os_name}"):
                for f in files:
                    filename = os.path.join(p, f)
                    archive.write(
                        filename=filename,
                        arcname=filename.removeprefix(f"{path}/{os_name}"),
                    )


def generate_new_config(network: Network, apv: Apv, path: str):
    with open(f"{path}/config.json", mode="r+") as f:
        doc = json.load(f)
        doc["AppProtocolVersion"] = apv.raw
        doc[
            "BlockchainStoreDirName"
        ] = f"9c-{network}-rc-v{apv.version}-{apv.extra['timestamp']}"
        f.seek(0)
        json.dump(doc, f, indent=4)
        f.truncate()
        return doc


COPY_MACHINE = {
    "player": copy_players,
    "launcher": copy_launchers,
}
