import yaml

import toolbelt.client.github as github
from toolbelt.repo import repositories
from toolbelt.repo.release_9c_repos import get_repos_head_commit
from toolbelt.update.update_k8s_yaml import (
    update_data_provider_yaml,
    update_general_yaml,
    update_headless_yaml,
    update_snapshot_partition_reset_yaml,
    update_snapshot_yaml,
)


def _update_main_yamls(repo_name, branch_name, properties, apv: str):
    assert apv, f"{apv}"

    k8s_config_files = {
        "general": [
            "9c-main/explorer.yaml",
            # planetariumhq/ninechronicles-headless - yaml['items'][0]['spec']['template']['spec']['containers'][0]['image']
            # apv - yaml['items'][0]['spec']['template']['spec']['containers'][0]['args']...startswith(--app-protocol-version=)
            "9c-main/full-state.yaml",
            # planetariumhq/ninechronicles-headless - yaml['spec']['template']['spec']['containers'][0]['image']
            # apv - yaml['spec']['template']['spec']['containers'][0]['args']...startswith(--app-protocol-version=)
            "9c-main/miner-1.yaml",
            "9c-main/miner-2.yaml",
            "9c-main/miner-3.yaml",
            "9c-main/miner-4.yaml",
            # planetariumhq/ninechronicles-headless - yaml['spec']['template']['spec']['containers'][0]['image']
            # apv - yaml['spec']['template']['spec']['containers'][0]['args']...startswith(--app-protocol-version=)
            "9c-main/remote-headless-1.yaml",
            "9c-main/remote-headless-2.yaml",
            "9c-main/remote-headless-3.yaml",
            "9c-main/remote-headless-4.yaml",
            "9c-main/remote-headless-5.yaml",
            "9c-main/remote-headless-6.yaml",
            "9c-main/remote-headless-7.yaml",
            "9c-main/remote-headless-8.yaml",
            "9c-main/remote-headless-9.yaml",
            "9c-main/remote-headless-10.yaml",
            "9c-main/remote-headless-11.yaml",
            "9c-main/remote-headless-12.yaml",
            "9c-main/remote-headless-13.yaml",
            "9c-main/remote-headless-14.yaml",
            "9c-main/remote-headless-15.yaml",
            "9c-main/remote-headless-16.yaml",
            "9c-main/remote-headless-17.yaml",
            "9c-main/remote-headless-18.yaml",
            "9c-main/remote-headless-19.yaml",
            "9c-main/remote-headless-20.yaml",
            "9c-main/remote-headless-21.yaml",
            "9c-main/remote-headless-22.yaml",
            "9c-main/remote-headless-23.yaml",
            "9c-main/remote-headless-24.yaml",
            "9c-main/remote-headless-25.yaml",
            "9c-main/remote-headless-26.yaml",
            "9c-main/remote-headless-27.yaml",
            "9c-main/remote-headless-28.yaml",
            "9c-main/remote-headless-29.yaml",
            "9c-main/remote-headless-30.yaml",
            "9c-main/remote-headless-31.yaml",
            "9c-main/remote-headless-99.yaml",
            # planetariumhq/ninechronicles-headless - yaml['spec']['template']['spec']['containers'][0]['image']
            # apv - yaml['spec']['template']['spec']['containers'][0]['args']...startswith(--app-protocol-version=)
            "9c-main/seed-deployment-1.yaml",
            "9c-main/seed-deployment-2.yaml",
            "9c-main/seed-deployment-3.yaml",
            "9c-main/tcp-seed-deployment-1.yaml",
            "9c-main/tcp-seed-deployment-2.yaml",
            "9c-main/tcp-seed-deployment-3.yaml",
            # planetariumhq/libplanet-seed - yaml['spec']['template']['spec']['containers'][0]['image']
            # apv - yaml['spec']['template']['spec']['containers'][0]['args']...startswith(--app-protocol-version=)
        ],
        "data-provider": [
            "9c-main/data-provider.yaml",
            "9c-main/data-provider-db.yaml",
            "9c-main/data-provider-test.yaml",
            # planetariumhq/ninechronicles-dataprovider - yaml['spec']['template']['spec']['containers'][0]['image']
            # apv - yaml['spec']['template']['spec']['containers'][0]['env']...['value']
        ],
        "snapshot-partition-reset": [
            "9c-main/snapshot-partition-reset.yaml",
            # planetariumhq/ninechronicles-headless
            #  - yaml['spec']['initContainers'][0]['image']
            #  - yaml['spec']['initContainers'][2]['image']
            # planetariumhq/ninechronicles-snapshot
            #  - yaml['spec']['initContainers'][1]['image']
            #  - yaml['spec']['initContainers'][3]['image']
            # apv
            #  - yaml['spec']['initContainers'][0]['args'][0]
            #  - yaml['spec']['initContainers'][1]['args'][0]
            #  - yaml['spec']['initContainers'][2]['args'][0]
            #  - yaml['spec']['initContainers'][3]['args'][0]
        ],
        "snapshot": [
            "9c-main/snapshot-partition.yaml",
            # planetariumhq/ninechronicles-headless - yaml['spec']['jobTemplate']['spec']['template']['spec']['initContainers'][0]['image']
            # planetariumhq/ninechronicles-snapshot - yaml['spec']['jobTemplate']['spec']['template']['spec']['containers'][0]['image']
            # apv
            #  - yaml['spec']['jobTemplate']['spec']['template']['spec']['initContainers'][0]['args'][0]
            #  - yaml['spec']['jobTemplate']['spec']['template']['spec']['containers'][0]['args'][0]
            "9c-main/snapshot-full.yaml",
            # planetariumhq/ninechronicles-headless - yaml['spec']['jobTemplate']['spec']['template']['spec']['initContainers'][0]['image']
            # planetariumhq/ninechronicles-snapshot - yaml['spec']['jobTemplate']['spec']['template']['spec']['containers'][0]['image']
            # apv
            #  - yaml['spec']['jobTemplate']['spec']['template']['spec']['initContainers'][0]['args'][0]
            #  - yaml['spec']['jobTemplate']['spec']['template']['spec']['containers'][0]['args'][0]
        ],
    }
    for category, paths in k8s_config_files.items():
        if category == "general":
            for path in paths:
                container_image = (
                    properties["libplanet.Seed"].docker_image
                    if "deployment" in path
                    else properties["NineChronicles.Headless"].docker_image
                )
                update_general_yaml(repo_name, path, branch_name, apv, container_image)
        elif category == "headless":
            for path in paths:
                update_headless_yaml(
                    repo_name,
                    path,
                    branch_name,
                    apv,
                    properties["NineChronicles.Headless"].docker_image,
                )
        elif category == "data-provider":
            for path in paths:
                update_data_provider_yaml(
                    repo_name,
                    path,
                    branch_name,
                    apv,
                    properties["NineChronicles.DataProvider"].docker_image,
                )
        elif category == "snapshot-partition-reset":
            for path in paths:
                update_snapshot_partition_reset_yaml(
                    repo_name,
                    path,
                    branch_name,
                    apv,
                    properties["NineChronicles.Headless"].docker_image,
                    properties["NineChronicles.Snapshot"].docker_image,
                )
        elif category == "snapshot":
            for path in paths:
                update_snapshot_yaml(
                    repo_name,
                    path,
                    branch_name,
                    apv,
                    properties["NineChronicles.Headless"].docker_image,
                    properties["NineChronicles.Snapshot"].docker_image,
                )
        else:
            raise Exception(f"Unknown category detected: {category}")


def _update_onboarding_yamls(repo_name, branch_name, properties, apv: str):
    for filepath in [
        "9c-onboarding/kustomization.yaml",
        "9c-onboarding/configmap-versions.yaml",
    ]:
        sha, content = github.get_path_content(repo_name, filepath, branch_name)
        doc = yaml.safe_load(content)

        if "kustomization" in filepath:
            _, tag = properties["NineChronicles.Snapshot"].docker_image.split(":")
            doc["images"][0]["newTag"] = tag
        elif "configmap-versions" in filepath:
            _, tag = properties["NineChronicles.Snapshot"].docker_image.split(":")
            doc["data"]["APP_PROTOCOL_VERSION"] = apv
        else:
            raise Exception("Unknown file name: {}".format(filepath))

        new_content = yaml.safe_dump(doc)
        if content != new_content:
            message = f"update {filepath}"
            github.update_path_content(
                repo_name, filepath, message, new_content, sha, branch_name
            )


def pull_k8s_repo(version: str, apv: str):
    assert version.startswith("v"), f"{version}"

    branch_name = f"{version}"

    repo_name = "9c-k8s-config"
    github.create_branch(repo_name, "main", branch_name)

    properties = {}
    properties.update(get_repos_head_commit(repositories.keys(), branch_name))
    properties.update(
        get_repos_head_commit(
            [
                "libplanet-seed",
                "NineChronicles.Snapshot",
                "NineChronicles.DataProvider",
            ]
        )
    )
    properties["libplanet.Seed"] = properties["libplanet-seed"]

    _update_main_yamls(repo_name, branch_name, properties, apv)
    _update_onboarding_yamls(repo_name, "main", properties, apv)

    title = f"[Bot] {branch_name}"
    description = f"""
Please **squash and merge**.

1. App Protocol Version
   {apv}
2. Docker Images
   {properties["libplanet.Seed"].docker_image}
   {properties["NineChronicles.Headless"].docker_image}
   {properties["NineChronicles.DataProvider"].docker_image}
   {properties["NineChronicles.Snapshot"].docker_image}
"""

    github.create_pull_request(repo_name, branch_name, "main", title, description)


def prepare_main_deploy(version: str, apv: str):
    assert version.startswith("v"), f"{version}"

    # 1. Create rc-branch from development branch of 9c repositories
    # 2. Bump submodule of 9c repositories on rc-branch
    # 3. Update notion page of release version
    # release_9c_repos(version)

    # 4. Create release version branch of 9c-k8s-config repository
    # 5. Update .yaml files for main from notion page on release version branch
    # 6. Create pull request from release version branch to main branch
    pull_k8s_repo(version, apv)
