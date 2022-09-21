from toolbelt.client.github import get_path_content, update_path_content, create_branch

MANIFEST_REPO = "9c-k8s-config"


def commit_manifests(branch, path, content):
    create_branch(MANIFEST_REPO, "main", branch)
    filename = path.split("/")[-1]
    message = f"{branch}: update {filename}"
    sha, _ = get_path_content(MANIFEST_REPO, path, branch)

    commit = update_path_content(MANIFEST_REPO, path, message, content, sha, branch)

    print(f'[INFO] Commit {commit["sha"]}: {message}')
