import toolbelt.client.github as github

from . import repositories
from .github_commit_url import PlanetariumGitHubCommitURL


def release_9c_repos(version):
    assert version.startswith("v"), f"{version}"

    branch_name = f"rc-{version}"

    for repository in repositories.keys():
        ref_branch = (
            "main" if repository == "NineChronicles.RPC.Shared" else "development"
        )

        github.create_branch(repository, ref_branch, branch_name)

    properties = {}
    for parent_repo, submodule in repositories.items():
        for submodule_repo, submodule_path in submodule.items():
            github.bump_submodule_branch(
                parent_repo, submodule_repo, submodule_path, branch_name
            )

        object = github.get_repository_branch_head(parent_repo, branch_name)
        properties.update({parent_repo: object["sha"]})

    return version, properties


def get_repos_head_commit(repo_list: list, branch: str = "main"):
    properties = {}

    for r in repo_list:
        object = github.get_repository_branch_head(r, branch)

        properties[r] = PlanetariumGitHubCommitURL(
            f"https://github.com/planetarium/{r}/commit/{object['sha']}"
        )

    return properties
