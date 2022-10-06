import yaml


def get_old_internal_apv(config_path: str) -> str:
    with open(config_path) as f:
        doc = yaml.safe_load(f)
        return doc["data"]["APP_PROTOCOL_VERSION"]
