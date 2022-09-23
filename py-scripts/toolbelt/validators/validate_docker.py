from typing import Optional, Tuple

import requests

import toolbelt.client.notion as notion

IMAGE_TO_REPOSITORY_MAP = {
    "planetariumhq/ninechronicles-headless": "https://github.com/planetarium/NineChronicles.Headless",
    "planetariumhq/ninechronicles-dataprovider": "https://github.com/planetarium/NineChronicles.DataProvider",
    "planetariumhq/ninechronicles-snapshot": "https://github.com/planetarium/NineChronicles.Snapshot",
    "planetariumhq/libplanet-seed": "https://github.com/planetarium/libplanet-seed",
}

IMAGE_TO_PROJECT_MAP = {
    "planetariumhq/ninechronicles-headless": "NineChronicles.Headless",
    "planetariumhq/ninechronicles-dataprovider": "NineChronicles.DataProvider",
    "planetariumhq/ninechronicles-snapshot": "NineChronicles.Snapshot",
    "planetariumhq/libplanet-seed": "Libplanet.Seed",
}


def validate_container(
    container_conf: dict, release_note: notion.ReleaseNote
) -> Tuple[bool, Optional[str]]:
    image = container_conf["image"]
    repo, tag = image.split(":")
    tag = tag.strip("git-")
    url = f"{IMAGE_TO_REPOSITORY_MAP[repo]}/commit/{tag}"
    notion_property = release_note.properties.get(IMAGE_TO_PROJECT_MAP.get(repo))
    if notion_property != url:
        return (
            False,
            f"It doesn't match with the spec from Notion. (notion={notion_property}, 9c-k8s-config={url})",
        )

    status_code = requests.get(url).status_code
    if status_code == 404:
        return (
            False,
            f"The docker image's git commit doesn't exist on GitHub Repository. (tag={tag})",
        )

    return True, None
