import pytest
import yaml
from dataclasses import dataclass


from toolbelt.client.github import (
    get_pull_request_head,
    get_path_content,
)


@dataclass(frozen=True)
class GitHubPullRequestHeadContents:
    repo_name: str
    pull_num: int
    sha: str
    path: str
    name: str
    apv: str
    image: str


@pytest.fixture(params=["v100081", "v100082"])
def version(request):
    if request.param == "v100081":
        return GitHubPullRequestHeadContents(
            "9c-k8s-config",
            273,
            "d74263b3525bb8580708553a273a22312bb61f2c",
            "9c-main/full-state.yaml",
            "main-full-state",
            "--app-protocol-version=100081/6ec8E598962F1f475504F82fD5bF3410eAE58B9B/MEQCIBY+2PYNH4ccQljtgcUE.6VFxsjmC732wnjhwVsdeQN1AiBu75I6Wvugciehz2EE8XqT3kZy8YOvAlfQ8kq6YEAe6A==/ZHUxNjpXaW5kb3dzQmluYXJ5VXJsdTU2Omh0dHBzOi8vZG93bmxvYWQubmluZS1jaHJvbmljbGVzLmNvbS92MTAwMDgxL1dpbmRvd3MuemlwdTE0Om1hY09TQmluYXJ5VXJsdTU3Omh0dHBzOi8vZG93bmxvYWQubmluZS1jaHJvbmljbGVzLmNvbS92MTAwMDgxL21hY09TLnRhci5nenU5OnRpbWVzdGFtcHUyNToyMDIxLTEwLTA3VDEzOjA4OjQyKzAwOjAwZQ==",
            "planetariumhq/ninechronicles-headless:git-0cd46224ea0cfc9574629cb5a112fae070c5bc51",
        )
    elif request.param == "v100082":
        return GitHubPullRequestHeadContents(
            "9c-k8s-config",
            277,
            "4b2f82d37a074860897132959dd749cd8f22e7df",
            "9c-main/full-state.yaml",
            "main-full-state",
            "--app-protocol-version=100082/6ec8E598962F1f475504F82fD5bF3410eAE58B9B/MEUCIQCYwrua7COV0DY181JT+RdciDSNAdxUyaDx8JvlKtpARwIgSRoxhfnqGW6UGD0K22HZbEnUB..bl5zeh.CZFidDL2Y=/ZHUxNjpXaW5kb3dzQmluYXJ5VXJsdTU2Omh0dHBzOi8vZG93bmxvYWQubmluZS1jaHJvbmljbGVzLmNvbS92MTAwMDgyL1dpbmRvd3MuemlwdTE0Om1hY09TQmluYXJ5VXJsdTU3Omh0dHBzOi8vZG93bmxvYWQubmluZS1jaHJvbmljbGVzLmNvbS92MTAwMDgyL21hY09TLnRhci5nenU5OnRpbWVzdGFtcHUyNToyMDIxLTEwLTIyVDEyOjIxOjE0KzAwOjAwZQ==",
            "planetariumhq/ninechronicles-headless:git-cffc5fc294fbb8545c7ba684d4bcac1393405794",
        )
    else:
        raise Exception(f"Unknown request.param detected: {request.param}")


def test_get_repository_pull_request_content(
    version: GitHubPullRequestHeadContents,
):
    head = get_pull_request_head(version.repo_name, version.pull_num)
    assert head["sha"] == version.sha

    sha, content = get_path_content(
        version.repo_name, version.path, head["sha"]
    )
    doc = yaml.safe_load(content)
    for container in doc["spec"]["template"]["spec"]["containers"]:
        assert version.apv in container["args"]
        assert container["name"] == version.name
        assert container["image"] == version.image
