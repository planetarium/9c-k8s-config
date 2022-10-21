import os

import typer
import yaml

from toolbelt.constants import MAIN_DIR
from toolbelt.k8s import get_apv
from toolbelt.planet import Planet

from .release_infos import copy_to_test_bucket, update_latest, update_root_config

update_app = typer.Typer()


@update_app.command()
def release_infos():
    """
    Run post deploy script
    """

    raw_apv = get_apv(MAIN_DIR)
    apv = Planet.apv_analyze(raw_apv)
    launcher = apv.extra["launcher"].split("/")[1]
    headless_image = get_headless_image()

    copy_to_test_bucket(apv.version, launcher)
    update_latest(apv.version, launcher)
    update_root_config(apv.raw, headless_image)


def get_headless_image() -> str:
    path = os.path.join(MAIN_DIR, "remote-headless-1.yaml")

    with open(path) as f:
        doc = yaml.safe_load(f)
        container = doc["spec"]["template"]["spec"]["containers"][0]["image"]
    return container
