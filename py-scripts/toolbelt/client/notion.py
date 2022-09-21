import requests
from dataclasses import dataclass
from typing import Dict

from toolbelt.repo.github_commit_url import PlanetariumGitHubCommitURL

__all__ = (
    "ReleaseNoteProperties",
    "get_release_page",
    "get_release_note_properties",
)


# https://developers.notion.com/docs/working-with-databases
# - https://www.notion.so/{workspace_name}/{database_id}?v={view_id}
RELEASE_DATABASE_ID = "ef54b0a32fb541d79bf905aabe89c7f6"

AUTH_TOKEN = "secret_oIG6BoGq7zPsedesc9A7dejAjpp9emniWX2UWB9ZDHy"
headers = {
    "Authorization": f"Bearer {AUTH_TOKEN}",
    "Notion-Version": "2021-08-16",
}


@dataclass(frozen=True)
class ReleaseNote:
    properties: Dict[str, str]


@dataclass(frozen=True)
class ReleaseNoteProperties:
    apv: str
    lib9c: PlanetariumGitHubCommitURL
    libplanet: PlanetariumGitHubCommitURL
    libplanet_seed: PlanetariumGitHubCommitURL
    nine_chronicles: PlanetariumGitHubCommitURL
    nine_chronicles_headless: PlanetariumGitHubCommitURL
    nine_chronicles_snapshot: PlanetariumGitHubCommitURL
    nine_chronicles_launcher: PlanetariumGitHubCommitURL
    nine_chronicles_data_provider: PlanetariumGitHubCommitURL


def get_release_page(version: str) -> dict:
    assert version.startswith("v"), f"{version}"

    # https://developers.notion.com/reference/post-database-query
    api_url = (
        f"https://api.notion.com/v1/databases/{RELEASE_DATABASE_ID}/query"
    )
    # https://developers.notion.com/reference/page#property-value-object
    data = {
        "filter": {
            "or": [
                {"property": "Version", "title": {"equals": version}},
            ]
        },
    }

    response = requests.post(api_url, headers=headers, json=data)
    if response.status_code != 200:
        print(f"[Error] response.status_code: {response.status_code}")
        raise Exception(f"Notion API Response: {response.status_code}")
    response_json = response.json()
    assert (
        len(response_json["results"]) == 1
    ), f"Multiple version {version} pages"
    page = response_json["results"][0]
    assert (
        version == page["properties"]["Version"]["title"][0]["plain_text"]
        and version in page["url"]
    ), f"Not found the Notion page with version {version}"
    return page


def get_release_note(release_version: str) -> ReleaseNote:
    page: dict = get_release_page(release_version)
    properties = dict(
        (key, value["url"])
        for key, value in page["properties"].items()
        if isinstance(value, dict) and value["type"] == "url"
    )
    release_note = ReleaseNote(properties)
    return release_note


def get_release_note_properties(version: str) -> ReleaseNoteProperties:
    page = get_release_page(version)
    apv = (
        page["properties"]["APV"]["rich_text"][0]["plain_text"]
        if page["properties"]["APV"]["rich_text"]
        else None
    )
    return ReleaseNoteProperties(
        apv,
        PlanetariumGitHubCommitURL(page["properties"]["lib9c"]["url"]),
        PlanetariumGitHubCommitURL(page["properties"]["libplanet"]["url"]),
        PlanetariumGitHubCommitURL(
            page["properties"]["libplanet.Seed"]["url"]
        ),
        PlanetariumGitHubCommitURL(
            page["properties"]["NineChronicles"]["url"]
        ),
        PlanetariumGitHubCommitURL(
            page["properties"]["NineChronicles.Headless"]["url"]
        ),
        PlanetariumGitHubCommitURL(
            page["properties"]["NineChronicles.Snapshot"]["url"]
        ),
        PlanetariumGitHubCommitURL(page["properties"]["9c-launcher"]["url"]),
        PlanetariumGitHubCommitURL(
            page["properties"]["NineChronicles.DataProvider"]["url"]
        ),
    )


def update_release_page_properties(version: str, properties: dict):
    assert version.startswith("v"), f"{version}"

    page = get_release_page(version)
    page_id = page["id"]

    # https://developers.notion.com/reference/patch-page
    api_url = f"https://api.notion.com/v1/pages/{page_id}"
    data = {"properties": {}}
    page_url = page["url"]
    print(f"[Info] Update notion {version} release page - {page_url}")
    for property, commit_hash in properties.items():
        commit_url = (
            f"https://github.com/planetarium/{property}/commit/{commit_hash}"
        )
        print(commit_url)
        data["properties"][property] = {"url": commit_url}

    response = requests.patch(api_url, headers=headers, json=data)
    if response.status_code != 200:
        print(f"[Error] response.status_code: {response.status_code}")
        raise Exception(f"Notion API Response: {response.status_code}")


if __name__ == "__main__":
    import sys
    import json

    if len(sys.argv) != 2:
        print(f"usage: python {sys.argv[0]} <version>")
        sys.exit()

    _version = sys.argv[1]
    assert _version.startswith("v"), f"{_version}"
    _page = get_release_page(_version)

    _apv = _page["properties"]["APV"]["rich_text"][0]["plain_text"]
    print(f"APV: {_apv}")
    _urls = {
        property_name: property_dict["url"]
        for property_name, property_dict in _page["properties"].items()
        if "url" in property_dict
    }
    print(json.dumps(_urls, indent=4, sort_keys=True))
