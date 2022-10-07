import yaml
import os

# FIXME: Two function is almost same...


def get_apv(dir: str) -> str:
    path = os.path.join(dir, "configmap-versions.yaml")

    with open(path) as f:
        doc = yaml.safe_load(f)
        return doc["data"]["APP_PROTOCOL_VERSION"]
