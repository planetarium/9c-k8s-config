import pytest

from toolbelt.repo.github_commit_url import PlanetariumGitHubCommitURL


@pytest.mark.parametrize(
    "url",
    [
        "https://github.com",
        "https://github.com/",
        "https://github.com/planetarium/NineChronicles/",
        "https://github.com/planetarium/NineChronicles/commits",
        "https://github.com/planetarium/NineChronicles/commit/COMMIT/additional",
    ],
)
def test_github_commit_url_validate(url):
    with pytest.raises(ValueError):
        PlanetariumGitHubCommitURL(url)


@pytest.mark.parametrize(
    ["url", "commit_hash"],
    [
        [
            "https://github.com/planetarium/9c-launcher/commit/67e890641ea0cd3caf40a1002557e4e4703f7eec",
            "67e890641ea0cd3caf40a1002557e4e4703f7eec",
        ],
        [
            "https://github.com/planetarium/NineChronicles/commit/81059d625289d7b35aaf7c272e2be6f8b4fb4cb4",
            "81059d625289d7b35aaf7c272e2be6f8b4fb4cb4",
        ],
    ],
)
def test_commit_hash(url, commit_hash):
    github_commit_url = PlanetariumGitHubCommitURL(url)
    assert commit_hash == github_commit_url.commit_hash
