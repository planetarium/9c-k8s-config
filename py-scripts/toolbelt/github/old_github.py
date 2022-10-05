import base64

import requests
import yaml

from toolbelt.config import config

__all__ = (
    "get_pull_request_head",
    "create_branch",
    "get_path_content",
    "update_path_content",
    "create_pull_request",
    "get_repository_branch_head",
)


REPOSITORY_OWNER = "planetarium"

headers = {
    "Authorization": f"token {config.github_token}",
    "Accept": "application/vnd.github.v3+json",
}


def get_pull_request_head(repo_name, pull_num):
    # https://docs.github.com/en/rest/reference/pulls#get-a-pull-request
    api_url = f"https://api.github.com/repos/{REPOSITORY_OWNER}/{repo_name}/pulls/{pull_num}"

    response = requests.get(api_url, headers=headers)
    if response.status_code != 200:
        print(f"[Error] response: {response.status_code}, {response.text}")
        raise Exception(f"GitHub API Response: {response.status_code}")
    response_json = response.json()
    return response_json["head"]


def get_path_content(repo_name, path, branch_name):
    # https://docs.github.com/en/rest/reference/repos#get-repository-content
    # https://stackoverflow.com/questions/60903841/how-to-get-a-file-from-specific-commit-hash-using-github-apis
    api_url = f"https://api.github.com/repos/{REPOSITORY_OWNER}/{repo_name}/contents/{path}?ref={branch_name}"

    response = requests.get(api_url, headers=headers)
    if response.status_code != 200:
        print(f"[Error] response: {response.status_code}, {response.text}")
        raise Exception(f"GitHub API Response: {response.status_code}")
    response_json = response.json()
    content = (
        base64.b64decode(response_json["content"]).decode("utf-8")
        if "content" in response_json
        else None
    )
    return response_json["sha"], content


def update_path_content(repo_name, path, message, content, sha, branch):
    # https://docs.github.com/en/rest/reference/repos#create-or-update-file-contents
    api_url = f"https://api.github.com/repos/{REPOSITORY_OWNER}/{repo_name}/contents/{path}"

    data = {
        "message": message,
        "content": base64.b64encode(content.encode("utf-8")).decode("utf-8"),
        "sha": sha,
        "branch": branch,
    }
    response = requests.put(api_url, headers=headers, json=data)
    if response.status_code != 200:
        print(f"[Error] response: {response.status_code}, {response.text}")
        raise Exception(f"GitHub API Response: {response.status_code}")
    response_json = response.json()
    print(
        f"[Info] Update https://github.com/{REPOSITORY_OWNER}/{repo_name}/blob/{branch}/{path}"
    )
    return response_json["commit"]


def get_repository_branch_head(repo_name, branch_name):
    api_url = f"https://api.github.com/repos/{REPOSITORY_OWNER}/{repo_name}/git/refs/heads/{branch_name}"

    response = requests.get(api_url, headers=headers)
    if response.status_code != 200:
        print(f"[Error] response: {response.status_code}, {response.text}")
        raise Exception(f"GitHub API Response: {response.status_code}")
    response_json = response.json()
    return response_json["object"]


def check_if_pull_exist(
    repo_name, branch_name, target_branch, merged_pull=False
):
    page = 1
    base_label = f"{REPOSITORY_OWNER}:{target_branch}"
    while True:
        # https://docs.github.com/en/rest/reference/pulls#list-pull-requests
        api_url = f"https://api.github.com/repos/{REPOSITORY_OWNER}/{repo_name}/pulls?state=all&per_page=100&page={page}"
        response = requests.get(api_url, headers=headers)
        if response.status_code != 200:
            print(f"[Error] response: {response.status_code}, {response.text}")
            raise Exception(f"GitHub API Response: {response.status_code}")

        response_json = response.json()
        if not response_json:
            break

        for pull in response_json:
            head_repo_owner, head_branch = pull["head"]["label"].split(":")
            if (
                branch_name == head_branch
                and base_label == pull["base"]["label"]
            ):
                if merged_pull and not pull["merged_at"]:
                    continue

                pull_num = pull["number"]
                print(
                    f"[Debug] Already created - https://github.com/{REPOSITORY_OWNER}/{repo_name}/pull/{pull_num}"
                )
                return pull

        page += 1

    return None


def create_pull_request(
    repo_name, branch_name, target_branch, title, description
):
    existed = _check_if_ref_exist(repo_name, "branch", branch_name)
    if not existed:
        print(
            f"[Error] branch not exist - https://github.com/{REPOSITORY_OWNER}/{repo_name}/tree/{branch_name}"
        )
        return None
    pull = check_if_pull_exist(repo_name, branch_name, target_branch)
    if pull:
        assert pull["title"] == title, "{} != {}".format(pull["title"], title)
        return pull["number"]

    object_branch = get_repository_branch_head(repo_name, branch_name)
    object_target = get_repository_branch_head(repo_name, target_branch)
    if object_branch["sha"] == object_target["sha"]:
        print(
            f'[Error] Cannot make a pull request with title "{title}" in repository {repo_name} on the same commit sha.'
        )
        return None

    # https://docs.github.com/en/rest/reference/pulls#create-a-pull-request
    api_url = (
        f"https://api.github.com/repos/{REPOSITORY_OWNER}/{repo_name}/pulls"
    )

    data = {
        "title": title,
        "head": branch_name,
        "base": target_branch,
        "body": description,
    }
    response = requests.post(api_url, headers=headers, json=data)
    if response.status_code == 201:
        response_json = response.json()
    elif response.status_code == 422:
        response_json = response.json()
        print(
            "[Warning] {}".format(response_json["message"])
        )  # No commits between branch_name and target_branch
        return None
    else:
        print(f"[Error] response: {response.status_code}, {response.text}")
        raise Exception(f"GitHub API Response: {response.status_code}")

    pull_num = response_json["number"]
    print(
        f"[Info] Create pull request - https://github.com/{REPOSITORY_OWNER}/{repo_name}/pull/{pull_num}"
    )
    return pull_num


def _check_if_ref_exist(repo_name, ref_type, ref_name):
    if ref_type == "branch":
        refs = "branches"
    elif ref_type == "tag":
        refs = "tags"
    else:
        raise Exception(f"{ref_type}")

    page = 1
    ref_name_list = []
    while True:
        api_url = f"https://api.github.com/repos/{REPOSITORY_OWNER}/{repo_name}/{refs}?per_page=100&page={page}"
        response = requests.get(api_url, headers=headers)
        if response.status_code != 200:
            print(f"[Error] response: {response.status_code}, {response.text}")
            raise Exception(f"GitHub API Response: {response.status_code}")

        response_json = response.json()
        if not response_json:
            break

        ref_name_list += [ref["name"] for ref in response_json]
        page += 1

    if ref_name in ref_name_list:
        print(
            f"[Debug] {ref_type} {ref_name} in repository {repo_name} already exists"
        )
        return True
    return False


def _create_ref(repo_name, ref_type, ref_name, sha):
    if ref_type == "branch":
        ref = f"refs/heads/{ref_name}"
    elif ref_type == "tag":
        ref = f"refs/tags/{ref_name}"
    else:
        raise Exception(f"{ref_type}")

    # https://docs.github.com/en/rest/reference/git#create-a-reference
    api_url = (
        f"https://api.github.com/repos/{REPOSITORY_OWNER}/{repo_name}/git/refs"
    )
    data = {"ref": ref, "sha": sha}
    response = requests.post(api_url, headers=headers, json=data)
    if response.status_code == 201:
        response_json = response.json()
        assert response_json["object"]["sha"] == sha
    elif response.status_code == 422:
        response_json = response.json()
        print(
            "[Warning] {}".format(response_json["message"])
        )  # Reference already exists
    else:
        raise Exception(
            f"[Error] response: {response.status_code}, {response.text}"
        )


def create_branch(repo_name, ref_branch, branch_name):
    existed = _check_if_ref_exist(repo_name, "branch", ref_branch)
    if not existed:
        print(
            f"[Error] branch not exist - https://github.com/{REPOSITORY_OWNER}/{repo_name}/tree/{ref_branch}"
        )
        return
    existed = _check_if_ref_exist(repo_name, "branch", branch_name)
    if existed:
        return
    object = get_repository_branch_head(repo_name, ref_branch)
    _create_ref(repo_name, "branch", branch_name, object["sha"])
    print(
        f"[Info] Create branch - https://github.com/{REPOSITORY_OWNER}/{repo_name}/tree/{branch_name}"
    )


def get_tags(repo_name):
    response = []

    for page in range(100):
        api_url = f"https://api.github.com/repos/{REPOSITORY_OWNER}/{repo_name}/tags?per_page=100&page={page}"
        r = requests.get(api_url, headers=headers).json()

        if not r:
            break

        response.extend(r)

    return response


def create_tag(repo_name, ref_branch, tag_name):
    existed = _check_if_ref_exist(repo_name, "branch", ref_branch)
    if not existed:
        print(
            f"[Error] branch not exist - https://github.com/{REPOSITORY_OWNER}/{repo_name}/tree/{ref_branch}"
        )
        return
    existed = _check_if_ref_exist(repo_name, "tag", tag_name)
    if existed:
        return
    object = get_repository_branch_head(repo_name, ref_branch)

    # https://docs.github.com/en/rest/reference/git#create-a-tag-object
    api_url = (
        f"https://api.github.com/repos/{REPOSITORY_OWNER}/{repo_name}/git/tags"
    )
    data = {
        "tag": tag_name,
        "message": f"[Bot] {tag_name}",
        "object": object["sha"],
        "type": "commit",
    }
    response = requests.post(api_url, headers=headers, json=data)
    if response.status_code != 201:
        print(f"[Error] response: {response.status_code}, {response.text}")
        raise Exception(f"GitHub API Response: {response.status_code}")
    response_json = response.json()

    # https://stackoverflow.com/questions/15672547/how-to-tag-a-commit-in-api-using-curl-command
    _create_ref(repo_name, "tag", tag_name, response_json["sha"])
    print(
        f"[Info] Create tag - https://github.com/{REPOSITORY_OWNER}/{repo_name}/releases/tag/{tag_name}"
    )


def bump_submodule_branch(
    parent_repo, submodule_repo, submodule_path, branch_name
):
    # https://stackoverflow.com/questions/13551625/git-submodules-in-github-repo
    sha, content = get_path_content(parent_repo, submodule_path, branch_name)

    # https://stackoverflow.com/questions/45789854/how-to-update-a-submodule-to-a-specified-commit-via-github-rest-api
    # https://stackoverflow.com/questions/35765445/how-to-create-submodule-in-github-using-github-rest-api
    object = get_repository_branch_head(parent_repo, branch_name)
    parent_sha = object["sha"]
    object = get_repository_branch_head(submodule_repo, branch_name)
    target_sha = object["sha"]

    if sha == target_sha:
        print(
            f"[Warning] Submodule {submodule_repo} in repository {parent_repo} already bumped"
        )
        return parent_sha

    # https://docs.github.com/en/rest/reference/git#create-a-tree
    api_url = f"https://api.github.com/repos/{REPOSITORY_OWNER}/{parent_repo}/git/trees"
    data = {
        "base_tree": parent_sha,
        "tree": [
            {
                "path": submodule_path,
                "mode": "160000",
                "type": "commit",
                "sha": target_sha,
            }
        ],
    }
    response = requests.post(api_url, headers=headers, json=data)
    if response.status_code != 201:
        print(f"[Error] response: {response.status_code}, {response.text}")
        raise Exception(f"GitHub API Response: {response.status_code}")
    response_json = response.json()
    tree_sha = response_json["sha"]

    api_url = f"https://api.github.com/repos/{REPOSITORY_OWNER}/{parent_repo}/git/commits"
    data = {
        "message": f"Bump {submodule_repo}",
        "tree": tree_sha,
        "parents": [parent_sha],
    }
    response = requests.post(api_url, headers=headers, json=data)
    if response.status_code == 201:
        response_json = response.json()
    elif response.status_code == 422:
        response_json = response.json()
        print("[Warning] {}".format(response_json["message"]))
    else:
        raise Exception(
            f"[Error] response: {response.status_code}, {response.text}"
        )
    commit_sha = response_json["sha"]

    api_url = f"https://api.github.com/repos/{REPOSITORY_OWNER}/{parent_repo}/git/refs/heads/{branch_name}"
    data = {"sha": commit_sha}
    response = requests.patch(api_url, headers=headers, json=data)
    if response.status_code != 200:
        print(f"[Error] response: {response.status_code}, {response.text}")
        raise Exception(f"GitHub API Response: {response.status_code}")
    response_json = response.json()
    object = response_json["object"]
    assert object["sha"] == commit_sha

    print(
        f"[Info] Bump {submodule_repo} - https://github.com/{REPOSITORY_OWNER}/{parent_repo}/commit/{commit_sha}"
    )
    return commit_sha


def download_artifact(repo_name, filepath, artifact_id=None, run_id=None):
    # https://docs.github.com/en/rest/reference/actions#artifacts
    if artifact_id:
        api_url = f"https://api.github.com/repos/{REPOSITORY_OWNER}/{repo_name}/actions/artifacts/{artifact_id}"
    elif run_id:
        api_url = f"https://api.github.com/repos/{REPOSITORY_OWNER}/{repo_name}/actions/runs/{run_id}/artifacts"
    else:
        api_url = f"https://api.github.com/repos/{REPOSITORY_OWNER}/{repo_name}/actions/artifacts?per_page=100"
    response = requests.get(api_url, headers=headers)
    if response.status_code != 200:
        print(f"[Error] response: {response.status_code}, {response.text}")
        raise Exception(f"GitHub API Response: {response.status_code}")
    response_json = response.json()
    if "artifacts" in response_json:
        artifact = None
        for action in response_json["artifacts"]:
            if action["name"] == "artifact":
                artifact = action
                break
        assert artifact
    else:
        artifact = response_json

    # https://docs.github.com/en/rest/reference/actions#download-an-artifact
    response = requests.get(artifact["archive_download_url"], headers=headers)
    if response.status_code != 200:
        print(f"[Error] response: {response.status_code}, {response.text}")
        raise Exception(f"GitHub API Response: {response.status_code}")
    with open(filepath, "wb") as file:
        file.write(response.content)

    return artifact["id"]


if __name__ == "__main__":
    import json
    import sys

    if len(sys.argv) != 2:
        print(f"usage: python {sys.argv[0]} <9c-k8s-config pull #>")
        sys.exit()

    _repo_name = "9c-k8s-config"
    _pull_num = int(sys.argv[1])
    _head = get_pull_request_head(_repo_name, _pull_num)

    _path = "9c-main/full-state.yaml"
    _commit_hash = _head["sha"]
    _sha, _content = get_path_content(_repo_name, _path, _commit_hash)

    _main_full_state = yaml.safe_load(_content)
    for container in _main_full_state["spec"]["template"]["spec"][
        "containers"
    ]:
        print("container {}:".format(container["name"]))
        print("- image: {}".format(container["image"]))
        print(
            "- args: {}".format(
                json.dumps(container["args"], indent=4, sort_keys=True)
            )
        )

    bump_submodule_branch(
        "NineChronicles.Headless", "lib9c", "Lib9c", "rc-v100084"
    )
