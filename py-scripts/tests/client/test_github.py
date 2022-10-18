import base64

from toolbelt.client import GithubClient

repo = "9c-k8s-config"
org = "planetarium"


def test_get_tags(requests_mock, github_tags_sample, mocker):
    client = GithubClient("test token", org=org, repo=repo)
    mocker.patch("time.sleep")

    requests_mock.get(
        f"/repos/{client.org}/{client.repo}/tags?page=1",
        json=github_tags_sample,
    )
    requests_mock.get(
        f"/repos/{client.org}/{client.repo}/tags?page=2",
        json=[],
    )

    count = 0
    for r in client.get_tags():
        assert r[0]["name"]
        count += 1

    assert count == 1


def test_get_path_content(requests_mock, github_path_content_sample):
    client = GithubClient("test token", org=org, repo=repo)
    path = "9c-internal/configmap-versions.yaml"

    requests_mock.get(
        f"/repos/{client.org}/{client.repo}/contents/{path}",
        json=github_path_content_sample,
    )

    content, r = client.get_path_content(path, "main")

    assert r == github_path_content_sample
    assert content == base64.b64decode(r["content"]).decode("utf-8")
