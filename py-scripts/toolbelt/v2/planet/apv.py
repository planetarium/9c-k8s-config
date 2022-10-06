from datetime import datetime

import yaml

from toolbelt.update import planet


def generate_internal_apv(old_apv: str, launcher_sha: str, player_sha: str):
    apv_no = old_apv.split("/")[0]
    timestamp = datetime.utcnow().strftime("%Y-%m-%d")

    assert apv_no.isdigit()

    internal_old_apv = planet.apv_analyze(old_apv)
    print(f"Old APV: {internal_old_apv.raw}")
    new_apv = planet.apv_sign(
        int(apv_no) + 1,
        timestamp=timestamp,
        launcher=launcher_sha,
        player=player_sha,
    )
    print(f"New APV: {new_apv.raw}")
    return new_apv
