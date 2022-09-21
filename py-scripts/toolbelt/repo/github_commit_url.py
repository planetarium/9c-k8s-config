from dataclasses import dataclass
from urllib.parse import urlparse

__all__ = ("PlanetariumGitHubCommitURL",)


@dataclass(frozen=True)
class PlanetariumGitHubCommitURL:
    url: str

    @property
    def commit_hash(self) -> str:
        result = urlparse(self.url)
        return result.path.strip("/").split("/")[-1]

    @property
    def docker_image(self) -> str:
        """
        https://hub.docker.com/orgs/planetariumhq/repositories
        planetariumhq / libplanet-explorer
        planetariumhq / libplanet-seed
        planetariumhq / ninechronicles-headless
        planetariumhq / ninechronicles-dataprovider
        planetariumhq / ninechronicles-snapshot
        planetariumhq / 9c-ethereum-bridge
        planetariumhq / 9c-tx-nonce-checker
        planetariumhq / 9c-tx-repeater
        planetariumhq / nekoyume-unity
        """

        result = urlparse(self.url)
        path = result.path.replace(".", "-").lower()
        org, repo, commit, sha = path.strip("/").split("/")
        assert repo in [
            "libplanet-seed",
            "ninechronicles-headless",
            "ninechronicles-dataprovider",
            "ninechronicles-snapshot",
        ]
        assert org == "planetarium" and commit == "commit"
        return f"planetariumhq/{repo}:git-{sha}"

    def _validate(self):
        result = urlparse(self.url)
        path = result.path.strip("/").split("/")
        if (
            result.scheme in ("http", "https")
            and result.hostname == "github.com"
            and len(path) == 4
            and path[2] == "commit"
        ):
            return

        raise ValueError("Expected GitHub commit page url", self.url)

    def __post_init__(self):
        self._validate()
