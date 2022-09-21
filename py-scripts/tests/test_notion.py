import pytest
from dataclasses import dataclass

from toolbelt.client.notion import get_release_note_properties


@dataclass(frozen=True)
class NotionReleaseNoteProperties:
    database_id: str
    version: str
    apv: str
    lib9c: str
    libplanet: str
    libplanet_seed: str
    nine_chronicles: str
    nine_chronicles_data_provider: str
    nine_chronicles_headless: str
    nine_chronicles_launcher: str
    nine_chronicles_snapshot: str


@pytest.fixture(params=["v100080", "v100081"])
def version(request):
    if request.param == "v100080":
        return NotionReleaseNoteProperties(
            "v100080",
            "100080/6ec8E598962F1f475504F82fD5bF3410eAE58B9B/MEUCIQCrSQ9v7NZBo5yCyvlHgBXW6lD4p2lFlKqK+aMeoKA.IAIgVkcK6hMCw1E0mf+m7rCf+9XnSL8Apg.joe6I1a8Nw70=/ZHUxNjpXaW5kb3dzQmluYXJ5VXJsdTU2Omh0dHBzOi8vZG93bmxvYWQubmluZS1jaHJvbmljbGVzLmNvbS92MTAwMDgwL1dpbmRvd3MuemlwdTk6dGltZXN0YW1wdTEwOjIwMjEtMDktMzBl",
            "https://github.com/planetarium/lib9c/commit/7b72032b4661531795dcb80458e91db0ac7c184b",
            "https://github.com/planetarium/libplanet/commit/f4bdf0bf922fddfe860ac4bd7924b9ee0b5ce8d3",
            "https://github.com/planetarium/libplanet-seed/commit/08e65a8b4a88b9c53266a92df573641a7b6e50f0",
            "https://github.com/planetarium/NineChronicles/commit/e6f5ee50c074f644238461da22e8e4266be29e63",
            "https://github.com/planetarium/NineChronicles.DataProvider/commit/4fd5255aa9fddc96cf2ec4dbf8728c4747460a21",
            "https://github.com/planetarium/NineChronicles.Headless/commit/75fd246b6c403b31a523408b5936a5ef6d7cf492",
            "https://github.com/planetarium/9c-launcher/commit/1c10c9aae87ca29d1b7352841d2a69422a51c2e0",
            "https://github.com/planetarium/NineChronicles.Snapshot/commit/c82faaea06d826a4a7f0f61770239ab37fb65c93",
        )
    elif request.param == "v100081":
        return NotionReleaseNoteProperties(
            "v100081",
            "100081/6ec8E598962F1f475504F82fD5bF3410eAE58B9B/MEQCIBY+2PYNH4ccQljtgcUE.6VFxsjmC732wnjhwVsdeQN1AiBu75I6Wvugciehz2EE8XqT3kZy8YOvAlfQ8kq6YEAe6A==/ZHUxNjpXaW5kb3dzQmluYXJ5VXJsdTU2Omh0dHBzOi8vZG93bmxvYWQubmluZS1jaHJvbmljbGVzLmNvbS92MTAwMDgxL1dpbmRvd3MuemlwdTE0Om1hY09TQmluYXJ5VXJsdTU3Omh0dHBzOi8vZG93bmxvYWQubmluZS1jaHJvbmljbGVzLmNvbS92MTAwMDgxL21hY09TLnRhci5nenU5OnRpbWVzdGFtcHUyNToyMDIxLTEwLTA3VDEzOjA4OjQyKzAwOjAwZQ==",
            "https://github.com/planetarium/lib9c/commit/e93dc2d224de3f7f1cffffe35e1594c991358dfd",
            "https://github.com/planetarium/libplanet/commit/279076dfe79a1dd2b9658c98dc56242d6ac7447c",
            "https://github.com/planetarium/libplanet-seed/commit/08e65a8b4a88b9c53266a92df573641a7b6e50f0",
            "https://github.com/planetarium/NineChronicles/commit/db0277dc9a2d6f82c5395c57adf133164d078a7b",
            "https://github.com/planetarium/NineChronicles.DataProvider/commit/4282708458976b1042d1fbe5507a79364ef7eda9",
            "https://github.com/planetarium/NineChronicles.Headless/commit/0cd46224ea0cfc9574629cb5a112fae070c5bc51",
            "https://github.com/planetarium/9c-launcher/commit/d4f21d88ae78ab794c51887dc017be3506d4c17b",
            "https://github.com/planetarium/NineChronicles.Snapshot/commit/9ac67e10ef7e6973d13670379728a642c98a37e3",
        )
    else:
        raise Exception(f"Unknown request.param detected: {request.param}")


def test_get_repository_pull_request_content(
    version: NotionReleaseNoteProperties,
):
    properties = get_release_note_properties(version.version)
    assert properties.apv == version.apv
    assert properties.lib9c.url == version.lib9c
    assert properties.libplanet.url == version.libplanet
    assert properties.libplanet_seed.url == version.libplanet_seed
    assert properties.nine_chronicles.url == version.nine_chronicles
    assert (
        properties.nine_chronicles_data_provider.url
        == version.nine_chronicles_data_provider
    )
    assert (
        properties.nine_chronicles_headless.url
        == version.nine_chronicles_headless
    )
    assert (
        properties.nine_chronicles_launcher.url
        == version.nine_chronicles_launcher
    )
    assert (
        properties.nine_chronicles_snapshot.url
        == version.nine_chronicles_snapshot
    )
