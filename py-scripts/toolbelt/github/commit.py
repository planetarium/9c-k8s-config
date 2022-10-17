from toolbelt.constants import MAIN_REPO
from toolbelt.github.old_github import get_path_content, update_path_content


def commit_manifests(branch, path, content):
    filename = path.split("/")[-1]
    message = f"{branch}: update {filename}"
    sha, _ = get_path_content(MAIN_REPO, path, branch)

    return update_path_content(MAIN_REPO, path, message, content, sha, branch)
