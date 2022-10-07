import json
import os
import tarfile
import tempfile
import zipfile

import structlog

from toolbelt.client.aws import S3File
from toolbelt.planet.apv import Apv
from toolbelt.types import Network
from toolbelt.utils.url import build_download_url

# from py7zr import SevenZipFile


ARTIFACTS = ["Windows.zip", "macOS.tar.gz", "Linux.tar.gz"]
ARTIFACT_BUCKET = "9c-artifacts"
RELEASE_BUCKET = "9c-release.planetariumhq.com"

unsigned_prefix = "Unsigned"
logger = structlog.get_logger(__name__)


def copy_players(
    *,
    apv_version: int,
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
                "", network, apv_version, "player", commit, release_file_name
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
    apv_version: int,
    network: Network,
    commit: str,
    prefix: str = "",
):
    s3 = S3File(ARTIFACT_BUCKET)

    for file_name in ARTIFACTS:
        artifact_path = f"9c-launcher/{commit}/{file_name}"
        logger.info(f"Start launcher {artifact_path} copy")

        release_file_name = file_name
        if network == "main":
            release_file_name = unsigned_prefix + file_name

        release_path = (
            prefix
            + build_download_url(
                "", network, apv_version, "launcher", commit, release_file_name
            )[1:]
        )

        s3.copy_from_bucket(
            artifact_path,
            RELEASE_BUCKET,
            release_path,
        )
        logger.info(f"Finish launcher {artifact_path} copy")


COPY_MACHINE = {
    "player": copy_players,
    "launcher": copy_launchers,
}

# def release_launcher(apv: Apv, sha: str, network: str, mode: str):
#     # aggregation of functions below
#     artifact_s3 = S3File(ARTIFACT_BUCKET)
#     release_s3 = S3File(RELEASE_BUCKET)
#     apv_no = apv.version
#     path = tempfile.TemporaryDirectory()
#     new_config = generate_new_config(release_s3, apv, path.name)
#     for file in ARTIFACTS:
#         download_launcher(artifact_s3, sha, file, path.name)
#         os_name = file.split(".")[0]
#         config_path = get_launcher_config(os_name)
#         update_config(f"{path.name}/{config_path}", new_config)
#         upload_launcher(
#             release_s3, apv_no, sha, file, path.name, network, mode
#         )

#     upload_config(release_s3, path.name, network, mode)
#     path.cleanup()


# def download_launcher(s3: S3File, sha: str, file: str, path: str):
#     os_name, extension = split_filename(file)
#     s3.download(f"9c-launcher/{sha}/{file}", path)
#     print(f"[INFO] Downloaded {path}/{file}")
#     if extension == "tar.gz":
#         zip = tarfile.open(f"{path}/{file}")
#         zip.extractall(f"{path}/{os_name}")
#         zip.close()
#     else:
#         with SevenZipFile(f"{path}/{file}", mode="r") as archive:
#             archive.extractall(path=f"{path}/{os_name}")


# def get_launcher_config(os_name: str):
#     if os_name in ["Windows", "Linux"]:
#         return f"{os_name}/resources/app/config.json"
#     elif os_name == "MacOS":
#         return (
#             f"{os_name}/Nine Chronicles.app/Contents/Resources/app/config.json"
#         )
#     else:
#         raise ValueError(
#             "Unsupported artifact name format: artifact name should be one of (MacOS.tar.gz, Linux.tar.gz)"
#         )


# def update_config(config_path: str, config: str):
#     with open(config_path, "w") as f:
#         f.seek(0)
#         json.dump(config, f, indent=4)
#         f.truncate()


# def upload_launcher(
#     s3: S3File,
#     apv_no: str,
#     sha: str,
#     file: str,
#     path: str,
#     network: str,
#     mode: str,
# ):
#     os_name, extension = split_filename(file)
#     if extension == "tar.gz":
#         with tarfile.open(f"{path}/{file}", "w:gz") as zip:
#             for arcname in os.listdir(f"{path}/{os_name}"):
#                 name = os.path.join(path, os_name, arcname)
#                 zip.add(name, arcname=arcname)
#     else:
#         with zipfile.ZipFile(f"{path}/{file}", mode="w") as archive:
#             for p, _, files in os.walk(f"{path}/{os_name}"):
#                 for f in files:
#                     filename = os.path.join(p, f)
#                     archive.write(
#                         filename=filename,
#                         arcname=filename.removeprefix(f"{path}/{os_name}"),
#                     )
#     mode_path = f"{mode}/" if mode != "" else ""
#     s3.upload(
#         f"{path}/{file}", f"{network}/{mode_path}v{apv_no}/launcher/{sha}/"
#     )
#     s3.upload(f"{path}/{file}", f"{network}/{mode_path}v{apv_no}/launcher/v1/")
#     print(f"[INFO] Uploaded {network}/v{apv_no}/launcher")


# def generate_new_config(s3: S3File, apv: Apv, path: str):
#     s3.download("internal/config.json", path)
#     with open(f"{path}/config.json", mode="r+") as f:
#         doc = json.load(f)
#         doc["AppProtocolVersion"] = apv.raw
#         doc[
#             "BlockchainStoreDirName"
#         ] = f"9c-internal-rc-v{apv.version}-{apv.timestamp}"
#         f.seek(0)
#         json.dump(doc, f, indent=4)
#         f.truncate()
#         return doc


# def upload_config(s3: S3File, path: str, network: str, mode: str):
#     s3.upload(f"{path}/config.json", f"{network}/{mode}")
#     print(f"[INFO] Uploaded new {network}/config.json")


# def split_filename(filename: str) -> (str, str):
#     splited = filename.split(".", 1)
#     return splited
