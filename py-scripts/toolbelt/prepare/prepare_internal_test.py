import os
import tempfile
import zipfile
import shutil
from datetime import datetime
from typing import Optional

import toolbelt.client.slack as slack
import toolbelt.client.aws as aws

from toolbelt.planet.apv import Planet
from toolbelt.prepare.update_internal_yamls import (
    update_internal_yamls
)
from toolbelt.repo.release_9c_repos import (
    release_9c_repos,
    get_repos_head_commit,
)
from toolbelt.repo.github_commit_url import PlanetariumGitHubCommitURL

def build_windows_zip(
    version: str, apv: str, timestamp: str, launcher_commit_hash: str
) -> str:
    assert version.startswith("v"), f"{version}"

    temp_dir = tempfile.TemporaryDirectory()

    print("[Info] Download Windows.zip")
    bucket_name = "9c-artifacts"
    s3_file = aws.S3File(bucket_name)
    src_filepath = f"9c-launcher/{launcher_commit_hash}/Windows.zip"
    dst_dir_path = temp_dir.name
    windows_filepath = s3_file.download(src_filepath, dst_dir_path)

    print("[Info] Uncompress Windows.zip")
    windows_extract_dir_path = os.path.join(temp_dir.name, "Windows")
    with zipfile.ZipFile(windows_filepath, "r") as zip_ref:
        zip_ref.extractall(windows_extract_dir_path)

    config_json = f"""{{
  "GenesisBlockPath": "https://download.nine-chronicles.com/genesis-block-9c-main",
  "StoreType": "rocksdb",
  "AppProtocolVersion": "{apv}",
  "TrustedAppProtocolVersionSigners": [
    "02529a61b9002ba8f21c858224234af971e962cac9bd7e6b365e71e125c6463478"
  ],
  "IceServerStrings": [
    "turn://0ed3e48007413e7c2e638f13ddd75ad272c6c507e081bd76a75e4b7adc86c9af:0apejou+ycZFfwtREeXFKdfLj2gCclKzz5ZJ49Cmy6I=@turn-us.planetarium.dev:3478"
  ],
  "PeerStrings": [
    "027bd36895d68681290e570692ad3736750ceaab37be402442ffb203967f98f7b6,9c-internal-tcp.planetarium.dev,31236"
  ],
  "NoTrustedStateValidators": true,
  "BlockchainStoreDirName": "9c-internal-rc-{version}-{timestamp}",
  "NoMiner": true,
  "Confirmations": 0,
  "Workers": 500,
  "Mixpanel": true,
  "Sentry": true,
  "MuteTeaser": true,
  "BlockchainStoreDirParent": "",
  "AwsSecretKey": "lmgIuUDboAP6kHl2hpoZ4mvXkRPk+k5qj9vOvKq9",
  "AwsAccessKey": "AKIAUU3S3PEZFVKH626P",
  "AwsRegion": "ap-northeast-2",
  "HeadlessArgs": [
    "--tip-timeout=120",
    "--minimum-broadcast-target=30",
    "--bucket-size=20",
    "--chain-tip-stale-behavior-type=reboot",
    "--network-type=Internal"
  ],
  "Network": "internal",
  "UseRemoteHeadless": true,
  "SnapshotPaths": [
    "https://snapshots.nine-chronicles.com/internal"
  ],
  "RemoteNodeList": [
    "9c-internal-rpc-1.nine-chronicles.com,80,31238"
  ],
  "DataProviderUrl": "https://api.9c.gg/graphql"
}}
"""
    config_filepath = os.path.join(
        windows_extract_dir_path, "resources", "app", "config.json"
    )
    with open(config_filepath, "w") as f:
        f.write(config_json)

    new_windows_filename = (
        f'{version}-internal-{apv.split("/")[0]}-{launcher_commit_hash}'
    )
    print(f"[Info] Compress {new_windows_filename}.zip")
    shutil.make_archive(new_windows_filename, "zip", windows_extract_dir_path)
    return f"{new_windows_filename}.zip"


def prepare_internal_test(version: str, apv: Optional[str] = None):
    assert version.startswith("v"), f"{version}"

    timestamp = datetime.utcnow().strftime("%Y-%m-%d")

    # 1. Create rc-branch from development branch of 9c repositories
    # 2. Bump submodule of 9c repositories on rc-branch
    # 3. Update notion page of release version
    version, properties_origin = release_9c_repos(version)

    properties = {}
    for property, commit_hash in properties_origin.items():
        commit_url = (
            f"https://github.com/planetarium/{property}/commit/{commit_hash}"
        )
        properties[property] = PlanetariumGitHubCommitURL(commit_url)

    properties.update(
        get_repos_head_commit(["libplanet-seed", "NineChronicles.Snapshot"])
    )
    properties["libplanet.Seed"] = properties["libplanet-seed"]

    # 4. Create release version branch of 9c-k8s-config repository
    # 5. Generate a new APV for internal.
    # 6. Update .yaml files for internal from notion page on release version branch
    internal_new_apv_str = update_internal_yamls(
        version, timestamp, properties, apv
    )

    # 7. Build windows.zip with new APV for internal
    launcher_commit_hash = properties["9c-launcher"].commit_hash
    new_built_windows_zip_filename = build_windows_zip(
        version, internal_new_apv_str, timestamp, launcher_commit_hash
    )
    print(f"[Info] Upload {new_built_windows_zip_filename} to slack")
    slack.upload_file("9c-internal", new_built_windows_zip_filename)
