import json
import sys
import tempfile
import zipfile
from os import path
from typing import TypedDict

import requests

from toolbelt.client.notion import ReleaseNoteProperties
from toolbelt.planet import Apv
from toolbelt.update import planet

__all__ = ("validate",)


class LauncherConfig(TypedDict):
    AppProtocolVersion: str


def _download_file(url: str) -> str:
    tmpfile = tempfile.mktemp()

    with open(tmpfile, "wb") as f:
        response = requests.get(url, stream=True)
        for content in response.iter_content(4096):
            f.write(content)

    return tmpfile


def _unzip(path: str):
    extract_path = tempfile.mkdtemp()
    with zipfile.ZipFile(path) as z:
        z.extractall(path=extract_path)

    return extract_path


def _load_launcher_config(path: str) -> LauncherConfig:
    with open(path) as f:
        return json.load(f)


def _validate_apv(apv: Apv) -> bool:
    window_binary_url = apv.extra["WindowsBinaryUrl"]
    downloaded_path = _download_file(window_binary_url)
    extracted_path = _unzip(downloaded_path)
    launcher_config = _load_launcher_config(
        path.join(extracted_path, "resources", "app", "config.json")
    )

    if apv.raw != launcher_config["AppProtocolVersion"]:
        return False

    # TODO Check digital signatures

    return True


def validate(properties: ReleaseNoteProperties) -> bool:
    try:
        apv = planet.apv_analyze(properties.apv)
        return _validate_apv(apv)
    except Exception:
        return False


if __name__ == "__main__":
    raw_apv = sys.argv[1]
    apv = planet.apv_analyze(raw_apv)

    returncode = 0
    if _validate_apv(apv):
        returncode = -1

    exit(returncode)
