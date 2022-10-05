from toolbelt.client import GithubClient

repo = "9c-launcher"
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
