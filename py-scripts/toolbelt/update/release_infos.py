import structlog

from toolbelt.client.aws import S3File, create_invalidation
from toolbelt.types import Network
from toolbelt.utils.url import build_s3_url

TEST_BUCKET = "9c-test"
RELEASE_BUCKET = "9c-release.planetariumhq.com"

download_distribution_id = "E1HPTSGY2RETN4"
release_distribution_id = "E3SBBH63NSNYX"
logger = structlog.get_logger(__name__)


def copy_to_test_bucket(rc: int, commit: str):
    release_bucket = S3File(RELEASE_BUCKET)

    logger.info("Copy to test bucket")

    release_bucket.copy_from_bucket(
        build_s3_url("main", rc, "launcher", commit, "Windows.zip"),
        TEST_BUCKET,
        f"v{rc}/Windows.zip",
    )
    logger.info("Copy Finish")


def update_latest(rc: int, commit: str):
    test_bucket = S3File(TEST_BUCKET)
    release_bucket = S3File(RELEASE_BUCKET)

    latest_path = "latest/Windows.zip"

    test_bucket.copy(f"v{rc}/Windows.zip", latest_path)
    release_bucket.copy(
        build_s3_url("main", rc, "launcher", commit, "Windows.zip"),
        latest_path,
    )

    invalidation_id = create_invalidation([latest_path], download_distribution_id)
    logger.info("DOWNLOAD - latest invalidation Finish", id=invalidation_id)
    invalidation_id = create_invalidation([latest_path], release_distribution_id)
    logger.info("RELEASE - latest invalidation Finish", id=invalidation_id)
    return invalidation_id


def update_root_config(apv: str, docker_image: str):
    release_bucket = S3File(RELEASE_BUCKET)
    root_config_path = "9c-launcher-config.json"
    apv_json = "apv.json"

    release_bucket.copy(
        "main/config.json",
        root_config_path,
    )

    apv_json_data = {"apv": apv, "docker": docker_image}
    release_bucket.update(apv_json, apv_json_data)

    invalidation_id = create_invalidation(
        [root_config_path, apv_json], download_distribution_id
    )
    logger.info("RELEASE - config invalidation Finish", id=invalidation_id)
