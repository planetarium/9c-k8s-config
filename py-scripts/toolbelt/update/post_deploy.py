import sys

import yaml

import toolbelt.client.aws as aws
import toolbelt.client.github as github


def get_apv_headless_image(repo_name, pull_num):
    head = github.get_pull_request_head(repo_name, pull_num)

    path = "9c-main/remote-headless-1.yaml"
    sha, content = github.get_path_content(repo_name, path, head["sha"])

    doc = next(yaml.safe_load_all(content))
    container = doc["spec"]["template"]["spec"]["containers"][0]
    for i, arg in enumerate(container["args"]):
        apv_arg_option = "--app-protocol-version="
        if arg.startswith(apv_arg_option):
            apv = arg.replace(apv_arg_option, "")
            return apv, container["image"]

    raise Exception("Not Found APV & Headless Image")


def update_s3_download_files(version, apv, docker):
    for bucket_name, version_windows_zip in [
        (
            "9c-release.planetariumhq.com",
            f"main/{version}/launcher/v1/Windows.zip",
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


def update_post_deploy(version):
    repo_name = "k8s-config"
    pull = github.check_if_pull_exist(repo_name, version, "main", merged_pull=True)
    if pull is None:
        print(
            f"There is no merged pull request with branch {version} in repository {repo_name}."
        )
        sys.exit()

    pull_num = pull["number"]
    apv, headless_image = get_apv_headless_image(repo_name, pull_num)
    assert version == "v{}".format(apv.split("/")[0])

    # 1. Update apv.json
    # 2. Update 9c-launcher-config.json
    # 3. Update latest/Windows.zip as <version>/Windows.zip
    # 4. Invalidate CDN
    update_s3_download_files(version, apv, headless_image)

    # 5. Create tag on rc-branch of 9c repositories
    # 6. Create pull request from rc-branch to main & development branch
