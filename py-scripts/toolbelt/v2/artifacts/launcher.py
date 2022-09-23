import json
import os
import tarfile
import tempfile
import zipfile

from py7zr import SevenZipFile

from toolbelt.client.aws import S3File
from toolbelt.planet.apv import Apv
from toolbelt.v2 import ARTIFACT_BUCKET, RELEASE_BUCKET

ARTIFACTS = ["Windows.zip", "MacOS.tar.gz", "Linux.tar.gz"]


def release_launcher(apv: Apv, sha: str, network: str, mode: str):
    # aggregation of functions below
    artifact_s3 = S3File(ARTIFACT_BUCKET)
    release_s3 = S3File(RELEASE_BUCKET)
    apv_no = apv.version
    path = tempfile.TemporaryDirectory()
    new_config = generate_new_config(release_s3, apv, path.name)
    for file in ARTIFACTS:
        download_launcher(artifact_s3, sha, file, path.name)
        os_name = file.split(".")[0]
        config_path = get_launcher_config(os_name)
        update_config(f"{path.name}/{config_path}", new_config)
        upload_launcher(release_s3, apv_no, sha, file, path.name, network, mode)

    upload_config(release_s3, path.name, network, mode)
    path.cleanup()


def download_launcher(s3: S3File, sha: str, file: str, path: str):
    os_name, extension = split_filename(file)
    s3.download(f"9c-launcher/{sha}/{file}", path)
    print(f"[INFO] Downloaded {path}/{file}")
    if extension == "tar.gz":
        zip = tarfile.open(f"{path}/{file}")
        zip.extractall(f"{path}/{os_name}")
        zip.close()
    else:
        with SevenZipFile(f"{path}/{file}", mode="r") as archive:
            archive.extractall(path=f"{path}/{os_name}")


def get_launcher_config(os_name: str):
    if os_name in ["Windows", "Linux"]:
        return f"{os_name}/resources/app/config.json"
    elif os_name == "MacOS":
        return f"{os_name}/Nine Chronicles.app/Contents/Resources/app/config.json"
    else:
        raise ValueError(
            "Unsupported artifact name format: artifact name should be one of (MacOS.tar.gz, Linux.tar.gz)"
        )


def update_config(config_path: str, config: str):
    with open(config_path, "w") as f:
        f.seek(0)
        json.dump(config, f, indent=4)
        f.truncate()


def upload_launcher(
    s3: S3File,
    apv_no: str,
    sha: str,
    file: str,
    path: str,
    network: str,
    mode: str,
):
    os_name, extension = split_filename(file)
    if extension == "tar.gz":
        with tarfile.open(f"{path}/{file}", "w:gz") as zip:
            for arcname in os.listdir(f"{path}/{os_name}"):
                name = os.path.join(path, os_name, arcname)
                zip.add(name, arcname=arcname)
    else:
        with zipfile.ZipFile(f"{path}/{file}", mode="w") as archive:
            for p, _, files in os.walk(f"{path}/{os_name}"):
                for f in files:
                    filename = os.path.join(p, f)
                    archive.write(
                        filename=filename,
                        arcname=filename.removeprefix(f"{path}/{os_name}"),
                    )
    mode_path = f"{mode}/" if mode != "" else ""
    s3.upload(f"{path}/{file}", f"{network}/{mode_path}v{apv_no}/launcher/{sha}/")
    s3.upload(f"{path}/{file}", f"{network}/{mode_path}v{apv_no}/launcher/v1/")
    print(f"[INFO] Uploaded {network}/v{apv_no}/launcher")


def generate_new_config(s3: S3File, apv: Apv, path: str):
    s3.download("internal/config.json", path)
    with open(f"{path}/config.json", mode="r+") as f:
        doc = json.load(f)
        doc["AppProtocolVersion"] = apv.raw
        doc["BlockchainStoreDirName"] = f"9c-internal-rc-v{apv.version}-{apv.timestamp}"
        f.seek(0)
        json.dump(doc, f, indent=4)
        f.truncate()
        return doc


def upload_config(s3: S3File, path: str, network: str, mode: str):
    s3.upload(f"{path}/config.json", f"{network}/{mode}")
    print(f"[INFO] Uploaded new {network}/config.json")


def split_filename(filename: str) -> (str, str):
    splited = filename.split(".", 1)
    return splited


if __name__ == "__main__":
    sha = "d8c9300bd3da9eef087056204350cd6813257c11"
    apv = "100326"
    s3 = S3File(ARTIFACT_BUCKET)
    download_launcher(s3, sha)
    config_path = get_launcher_config("Linux")
    update_config(config_path, apv)
    # upload_launcher(apv, sha, 'package')
