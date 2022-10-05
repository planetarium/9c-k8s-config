import yaml

import toolbelt.github.old_github as old_github


def _update_general_doc(item, apv, container_image):
    container = item["spec"]["template"]["spec"]["containers"][0]
    container["image"] = container_image
    for i, arg in enumerate(container["args"]):
        args = []
        for a in arg.split():
            apv_arg_option = "--app-protocol-version="
            if a.startswith(apv_arg_option):
                args.append(apv_arg_option + apv)
            else:
                args.append(a)
        container["args"][i] = " ".join(args)


def update_general_yaml(repo_name, path, branch_name, apv, container_image):
    sha, content = old_github.get_path_content(repo_name, path, branch_name)

    doc = yaml.safe_load(content)
    if doc["kind"] == "List":
        for item in doc["items"]:
            assert item["kind"] == "StatefulSet"
            _update_general_doc(item, apv, container_image)
    elif doc["kind"] == "StatefulSet":
        _update_general_doc(doc, apv, container_image)
    elif doc["kind"] == "Deployment":
        _update_general_doc(doc, apv, container_image)
    else:
        raise Exception("Unknown kind detected: {}".format(doc["kind"]))

    new_content = yaml.safe_dump(doc)
    if content == new_content:
        return None
    message = f"update {path}"
    commit = old_github.update_path_content(
        repo_name, path, message, new_content, sha, branch_name
    )
    return commit


def update_headless_yaml(repo_name, path, branch_name, apv, container_image):
    sha, content = old_github.get_path_content(repo_name, path, branch_name)

    docs = yaml.safe_load_all(content)
    updated_docs = []
    for doc in docs:
        _update_general_doc(doc, apv, container_image)
        updated_docs.append(doc)

    new_content = yaml.safe_dump_all(updated_docs)
    if content == new_content:
        return None
    message = f"update {path}"
    commit = old_github.update_path_content(
        repo_name, path, message, new_content, sha, branch_name
    )
    return commit


def update_data_provider_yaml(repo_name, path, branch_name, apv, container_image):
    sha, content = old_github.get_path_content(repo_name, path, branch_name)

    doc = yaml.safe_load(content)
    doc["spec"]["template"]["spec"]["containers"][0]["image"] = container_image
    for env in doc["spec"]["template"]["spec"]["containers"][0]["env"]:
        if env["name"] == "NC_AppProtocolVersionToken":
            env["value"] = apv
            break

    new_content = yaml.safe_dump(doc)
    if content == new_content:
        return None
    message = f"update {path}"
    commit = old_github.update_path_content(
        repo_name, path, message, new_content, sha, branch_name
    )
    return commit


def update_snapshot_partition_reset_yaml(
    repo_name, path, branch_name, apv, headless_image, snapshot_image
):
    sha, content = old_github.get_path_content(repo_name, path, branch_name)

    doc = yaml.safe_load(content)
    assert doc["kind"] == "Pod"
    for container in doc["spec"]["initContainers"]:
        if "headless" in container["name"]:
            container["image"] = headless_image
            container["args"][0] = apv
        elif "snapshot" in container["name"]:
            container["image"] = snapshot_image
            assert container["args"][0] == "temp"
            container["args"][1] = apv
        else:
            raise Exception(
                "Unknown container name detected: {}".format(container["name"])
            )

    new_content = yaml.safe_dump(doc)
    if content == new_content:
        return None
    message = f"update {path}"
    commit = old_github.update_path_content(
        repo_name, path, message, new_content, sha, branch_name
    )
    return commit


def update_snapshot_yaml(
    repo_name, path, branch_name, apv, headless_image, snapshot_image
):
    sha, content = old_github.get_path_content(repo_name, path, branch_name)

    doc = yaml.safe_load(content)
    assert doc["kind"] == "CronJob"

    if "main" in path:
        assert (
            "headless"
            in doc["spec"]["jobTemplate"]["spec"]["template"]["spec"]["initContainers"][
                0
            ]["name"]
        )
        doc["spec"]["jobTemplate"]["spec"]["template"]["spec"]["initContainers"][0][
            "image"
        ] = headless_image
        doc["spec"]["jobTemplate"]["spec"]["template"]["spec"]["initContainers"][0][
            "args"
        ][0] = apv
        assert (
            "snapshot"
            in doc["spec"]["jobTemplate"]["spec"]["template"]["spec"]["containers"][0][
                "name"
            ]
        )
        doc["spec"]["jobTemplate"]["spec"]["template"]["spec"]["containers"][0][
            "image"
        ] = snapshot_image
        doc["spec"]["jobTemplate"]["spec"]["template"]["spec"]["containers"][0]["args"][
            0
        ] = apv
    elif "internal" in path:
        assert (
            "headless"
            in doc["spec"]["jobTemplate"]["spec"]["template"]["spec"]["initContainers"][
                1
            ]["name"]
        )
        doc["spec"]["jobTemplate"]["spec"]["template"]["spec"]["initContainers"][1][
            "image"
        ] = headless_image
        doc["spec"]["jobTemplate"]["spec"]["template"]["spec"]["initContainers"][1][
            "args"
        ][0] = apv
        assert (
            "snapshot"
            in doc["spec"]["jobTemplate"]["spec"]["template"]["spec"]["containers"][0][
                "name"
            ]
        )
        doc["spec"]["jobTemplate"]["spec"]["template"]["spec"]["containers"][0][
            "image"
        ] = snapshot_image
    else:
        raise Exception(f"{path}")

    new_content = yaml.safe_dump(doc)
    if content == new_content:
        return None
    message = f"update {path}"
    commit = old_github.update_path_content(
        repo_name, path, message, new_content, sha, branch_name
    )
    return commit
