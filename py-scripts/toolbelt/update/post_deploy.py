import toolbelt.client.aws as aws


def update_s3_download_files(version, apv, docker, launcher_sha):
    for bucket_name, version_windows_zip in [
        (
            "9c-release.planetariumhq.com",
            f"main/{version}/launcher/{launcher_sha}/Windows.zip",
        ),
        (
            "9c-test",
            f"{version}/Windows.zip",
        ),
    ]:
        s3_file = aws.S3File(bucket_name)

        apv_json_file = "apv.json"
        apv_json_data = {"apv": apv, "docker": docker}
        s3_file.update(apv_json_file, apv_json_data)

        nc_launcher_config_json_file = "9c-launcher-config.json"
        nc_launcher_config_json_data = {
            "AppProtocolVersion": apv,
        }
        s3_file.update(nc_launcher_config_json_file, nc_launcher_config_json_data)

        latest_windows_zip_file = "latest/Windows.zip"
        s3_file.copy(version_windows_zip, latest_windows_zip_file)

        path_list = [
            apv_json_file,
            nc_launcher_config_json_file,
            latest_windows_zip_file,
        ]
        invalidation_id = aws.create_invalidation(path_list)
        print(f"[Info] Invalidation created successfully with Id: {invalidation_id}")


def update_post_deploy(version: str, apv: str, headless_image: str, launcher_sha: str):
    assert version == "v{}".format(apv.split("/")[0])

    update_s3_download_files(version, apv, headless_image, launcher_sha)
