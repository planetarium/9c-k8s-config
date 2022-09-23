from toolbelt.client.aws import S3File
from toolbelt.v2 import ARTIFACT_BUCKET, RELEASE_BUCKET


def copy_players(apv_no, sha, network, mode):
    s3 = S3File(ARTIFACT_BUCKET)
    path_prefix = "release-test/" if mode == "test" else ""
    mode_path = f"{mode}/" if mode != "" else ""
    players = s3.get_files(f"{path_prefix}{sha}")
    if not players:
        raise ValueError(f"No player artifacts in s3 bucket path {path_prefix}{sha}")
    for file in players:
        s3.copy_from_bucket(
            f"{path_prefix}{sha}/{file}",
            RELEASE_BUCKET,
            f"{network}/{mode_path}v{apv_no}/player/{sha}/{file}",
        )
        s3.copy_from_bucket(
            f"{path_prefix}{sha}/{file}",
            RELEASE_BUCKET,
            f"{network}/{mode_path}v{apv_no}/player/v1/{file}",
        )
        print(f"[INFO] Copied new {network}/v{apv_no}/player/")
