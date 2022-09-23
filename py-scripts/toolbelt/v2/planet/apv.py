from datetime import datetime

import yaml

from toolbelt.config import INTERNAL_PASSPHRASE
from toolbelt.planet.apv import Apv, Planet


def get_old_internal_apv(config_path: str) -> str:
    with open(config_path) as f:
        doc = yaml.safe_load(f)
        return doc["data"]["APP_PROTOCOL_VERSION"]


def generate_internal_apv(old_apv: str, launcher_sha: str, player_sha: str) -> Apv:
    planet = Planet()
    apv_no = old_apv.split("/")[0]
    timestamp = datetime.utcnow().strftime("%Y-%m-%d")

    assert apv_no.isdigit()

    internal_old_apv = planet.analyze_apv(old_apv)
    print(f"Old APV: {internal_old_apv.raw}")
    new_apv = planet.sign_apv_v2(
        INTERNAL_PASSPHRASE,
        "internal",
        int(apv_no) + 1,
        timestamp,
        launcher_sha,
        player_sha,
    )
    print(f"New APV: {new_apv.raw}")
    return new_apv


if __name__ == "__main__":
    old_apv = get_old_internal_apv()
    new_apv = generate_internal_apv(old_apv)
    print(new_apv.raw)
